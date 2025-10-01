"""Data validation utilities for API responses.

Implements Requirement: Data Quality Validation from data-integration spec.
Provides schema validation, range checking, and outlier detection.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Validation rule for a field."""

    field_name: str
    required: bool = True
    field_type: type | tuple[type, ...] | None = None
    min_value: float | None = None
    max_value: float | None = None
    allowed_values: list[Any] | None = None
    custom_validator: Callable[[Any], bool] | None = None


@dataclass
class ValidationResult:
    """Result of data validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    validated_data: Dict[str, Any] | None = None


class DataValidator:
    """
    Data quality validator for API responses.

    Provides schema validation, range checking, and outlier detection
    to ensure data reliability across all connectors.

    Example:
        >>> validator = DataValidator("demographics")
        >>> validator.add_rule("population", required=True, field_type=int, min_value=0)
        >>> result = validator.validate({"population": 50000})
        >>> if result.is_valid:
        ...     # Use result.validated_data
    """

    def __init__(self, schema_name: str) -> None:
        """
        Initialize validator with schema name.

        Args:
            schema_name: Identifier for this validation schema
        """
        self.schema_name = schema_name
        self._rules: Dict[str, ValidationRule] = {}

    def add_rule(
        self,
        field_name: str,
        *,
        required: bool = True,
        field_type: type | tuple[type, ...] | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        allowed_values: list[Any] | None = None,
        custom_validator: Callable[[Any], bool] | None = None,
    ) -> None:
        """
        Add a validation rule for a field.

        Args:
            field_name: Name of the field to validate
            required: Whether field must be present
            field_type: Expected type(s) for the field
            min_value: Minimum allowed value (for numeric fields)
            max_value: Maximum allowed value (for numeric fields)
            allowed_values: List of allowed values (for enum-like fields)
            custom_validator: Custom validation function (returns True if valid)
        """
        rule = ValidationRule(
            field_name=field_name,
            required=required,
            field_type=field_type,
            min_value=min_value,
            max_value=max_value,
            allowed_values=allowed_values,
            custom_validator=custom_validator,
        )
        self._rules[field_name] = rule

        logger.debug(f"Added validation rule for {self.schema_name}.{field_name}")

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate data against defined rules.

        Args:
            data: Dictionary of data to validate

        Returns:
            ValidationResult with is_valid, errors, warnings, and validated_data
        """
        errors: List[str] = []
        warnings: List[str] = []
        validated_data: Dict[str, Any] = {}

        # Check required fields
        for field_name, rule in self._rules.items():
            if rule.required and field_name not in data:
                errors.append(f"Missing required field: {field_name}")
                continue

            # Skip validation if field not present and not required
            if field_name not in data:
                continue

            value = data[field_name]

            # Type validation
            if rule.field_type is not None and value is not None:
                if not isinstance(value, rule.field_type):
                    errors.append(
                        f"Field '{field_name}' has invalid type. "
                        f"Expected {rule.field_type}, got {type(value).__name__}"
                    )
                    continue

            # Range validation (for numeric types)
            if isinstance(value, (int, float)) and value is not None:
                if rule.min_value is not None and value < rule.min_value:
                    errors.append(
                        f"Field '{field_name}' value {value} is below minimum {rule.min_value}"
                    )
                    continue

                if rule.max_value is not None and value > rule.max_value:
                    errors.append(
                        f"Field '{field_name}' value {value} exceeds maximum {rule.max_value}"
                    )
                    continue

            # Allowed values validation
            if rule.allowed_values is not None and value not in rule.allowed_values:
                errors.append(
                    f"Field '{field_name}' value '{value}' not in allowed values: "
                    f"{rule.allowed_values}"
                )
                continue

            # Custom validation
            if rule.custom_validator is not None:
                try:
                    if not rule.custom_validator(value):
                        errors.append(f"Field '{field_name}' failed custom validation")
                        continue
                except Exception as e:
                    errors.append(
                        f"Field '{field_name}' custom validator raised exception: {e}"
                    )
                    continue

            # Field passed all validations
            validated_data[field_name] = value

        # Check for unexpected fields (warning only)
        for field_name in data:
            if field_name not in self._rules:
                warnings.append(f"Unexpected field in data: {field_name}")
                # Still include in validated data
                validated_data[field_name] = data[field_name]

        # Log results
        if errors:
            logger.error(
                f"Validation failed for {self.schema_name}: {len(errors)} error(s)"
            )
            for error in errors:
                logger.error(f"  - {error}")

        if warnings:
            logger.warning(
                f"Validation warnings for {self.schema_name}: {len(warnings)} warning(s)"
            )
            for warning in warnings:
                logger.warning(f"  - {warning}")

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            validated_data=validated_data if is_valid else None,
        )

    def validate_or_raise(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data and raise exception if invalid.

        Convenience method for strict validation.

        Args:
            data: Dictionary of data to validate

        Returns:
            Validated data dictionary

        Raises:
            ValueError: If validation fails
        """
        result = self.validate(data)

        if not result.is_valid:
            error_msg = f"Validation failed for {self.schema_name}:\n"
            error_msg += "\n".join(f"  - {err}" for err in result.errors)
            raise ValueError(error_msg)

        return result.validated_data  # type: ignore[return-value]


# Common validators for reuse across connectors


def create_demographic_validator() -> DataValidator:
    """
    Create validator for Census demographic data.

    Returns:
        DataValidator configured for demographic fields
    """
    validator = DataValidator("demographics")

    validator.add_rule("population", required=True, field_type=int, min_value=0)
    validator.add_rule(
        "median_age",
        required=False,
        field_type=(int, float),
        min_value=0,
        max_value=120,
    )
    validator.add_rule(
        "median_income", required=False, field_type=(int, float), min_value=0
    )
    validator.add_rule(
        "bachelor_degree_pct",
        required=False,
        field_type=(int, float),
        min_value=0,
        max_value=100,
    )
    validator.add_rule(
        "unemployment_rate",
        required=False,
        field_type=(int, float),
        min_value=0,
        max_value=100,
    )

    return validator


def create_economic_validator() -> DataValidator:
    """
    Create validator for BEA/BLS economic data.

    Returns:
        DataValidator configured for economic fields
    """
    validator = DataValidator("economics")

    validator.add_rule("gdp", required=False, field_type=(int, float), min_value=0)
    validator.add_rule(
        "gdp_growth_rate",
        required=False,
        field_type=(int, float),
        min_value=-50,
        max_value=50,
    )
    validator.add_rule("employment", required=False, field_type=int, min_value=0)
    validator.add_rule(
        "unemployment_rate",
        required=False,
        field_type=(int, float),
        min_value=0,
        max_value=100,
    )
    validator.add_rule(
        "average_wage", required=False, field_type=(int, float), min_value=0
    )

    return validator


def create_location_validator() -> DataValidator:
    """
    Create validator for geographic location data.

    Returns:
        DataValidator configured for location fields
    """
    validator = DataValidator("location")

    validator.add_rule(
        "latitude", required=True, field_type=(int, float), min_value=-90, max_value=90
    )
    validator.add_rule(
        "longitude",
        required=True,
        field_type=(int, float),
        min_value=-180,
        max_value=180,
    )
    validator.add_rule(
        "state_fips",
        required=False,
        field_type=str,
        custom_validator=lambda x: len(x) == 2,
    )
    validator.add_rule(
        "county_fips",
        required=False,
        field_type=str,
        custom_validator=lambda x: len(x) == 5,
    )

    return validator


def detect_outliers(
    values: list[float],
    *,
    method: str = "iqr",
    threshold: float = 1.5,
) -> list[int]:
    """
    Detect outliers in a list of numeric values.

    Args:
        values: List of numeric values
        method: Outlier detection method ("iqr" or "zscore")
        threshold: Threshold for outlier detection
            - For "iqr": multiplier for IQR (default 1.5)
            - For "zscore": number of standard deviations (default 1.5)

    Returns:
        List of indices where outliers are detected

    Raises:
        ValueError: If method is unknown or values is empty
    """
    if not values:
        raise ValueError("Cannot detect outliers in empty list")

    if len(values) < 3:
        logger.warning("Outlier detection with < 3 values may not be meaningful")
        return []

    outlier_indices: list[int] = []

    if method == "iqr":
        # Interquartile range method
        sorted_values = sorted(values)
        n = len(sorted_values)

        q1_idx = n // 4
        q3_idx = 3 * n // 4

        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1

        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        for i, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                outlier_indices.append(i)
                logger.warning(
                    f"Outlier detected at index {i}: {value} "
                    f"(bounds: {lower_bound:.2f} - {upper_bound:.2f})"
                )

    elif method == "zscore":
        remaining = list(enumerate(values))
        iterations = 0
        max_iterations = len(values)

        while remaining and iterations < max_iterations:
            iterations += 1
            sample = [value for _, value in remaining]
            mean = sum(sample) / len(sample)
            variance = sum((x - mean) ** 2 for x in sample) / len(sample)
            std_dev = variance**0.5

            if std_dev == 0:
                logger.warning("Zero standard deviation, cannot compute z-scores")
                break

            iteration_outliers = []
            for index, value in remaining:
                z_score = abs((value - mean) / std_dev)
                if z_score > threshold:
                    outlier_indices.append(index)
                    iteration_outliers.append((index, value))
                    logger.warning(
                        f"Outlier detected at index {index}: {value} "
                        f"(z-score: {z_score:.2f}, threshold: {threshold})"
                    )

            if not iteration_outliers:
                break

            remaining = [item for item in remaining if item not in iteration_outliers]

        outlier_indices.sort()

    else:
        raise ValueError(f"Unknown outlier detection method: {method}")

    return outlier_indices

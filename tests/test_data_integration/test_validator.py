"""Tests for data validation functionality."""

from __future__ import annotations

import pytest

from Claude45_Demo.data_integration.validator import (
    DataValidator,
    ValidationResult,
    create_demographic_validator,
    create_economic_validator,
    create_location_validator,
    detect_outliers,
)


@pytest.fixture
def simple_validator():
    """Create a simple validator for testing."""
    validator = DataValidator("test_schema")
    validator.add_rule("name", required=True, field_type=str)
    validator.add_rule("age", required=True, field_type=int, min_value=0, max_value=150)
    validator.add_rule(
        "score", required=False, field_type=(int, float), min_value=0, max_value=100
    )
    return validator


def test_validator_initialization():
    """Test creating a validator."""
    validator = DataValidator("test_schema")
    assert validator.schema_name == "test_schema"


def test_add_rule():
    """Test adding validation rules."""
    validator = DataValidator("test")
    validator.add_rule("field1", required=True, field_type=str)

    # Should not raise error
    assert "field1" in validator._rules


def test_validate_valid_data(simple_validator):
    """Test validation with valid data."""
    data = {"name": "Alice", "age": 30, "score": 85.5}

    result = simple_validator.validate(data)

    assert result.is_valid
    assert len(result.errors) == 0
    assert result.validated_data == data


def test_validate_missing_required_field(simple_validator):
    """Test validation with missing required field."""
    data = {"age": 30}  # Missing "name"

    result = simple_validator.validate(data)

    assert not result.is_valid
    assert any("name" in err for err in result.errors)
    assert result.validated_data is None


def test_validate_missing_optional_field(simple_validator):
    """Test validation with missing optional field."""
    data = {"name": "Bob", "age": 25}  # Missing optional "score"

    result = simple_validator.validate(data)

    assert result.is_valid
    assert "score" not in result.validated_data


def test_validate_wrong_type(simple_validator):
    """Test validation with wrong field type."""
    data = {"name": "Charlie", "age": "thirty"}  # age should be int

    result = simple_validator.validate(data)

    assert not result.is_valid
    assert any("type" in err.lower() for err in result.errors)


def test_validate_below_min_value(simple_validator):
    """Test validation with value below minimum."""
    data = {"name": "David", "age": -5}  # age below min_value=0

    result = simple_validator.validate(data)

    assert not result.is_valid
    assert any("below minimum" in err for err in result.errors)


def test_validate_above_max_value(simple_validator):
    """Test validation with value above maximum."""
    data = {"name": "Eve", "age": 200}  # age above max_value=150

    result = simple_validator.validate(data)

    assert not result.is_valid
    assert any("exceeds maximum" in err for err in result.errors)


def test_validate_allowed_values():
    """Test validation with allowed values constraint."""
    validator = DataValidator("test")
    validator.add_rule(
        "status", required=True, allowed_values=["active", "inactive", "pending"]
    )

    # Valid value
    result = validator.validate({"status": "active"})
    assert result.is_valid

    # Invalid value
    result = validator.validate({"status": "unknown"})
    assert not result.is_valid
    assert any("not in allowed values" in err for err in result.errors)


def test_validate_custom_validator():
    """Test validation with custom validator function."""

    def is_even(value):
        return value % 2 == 0

    validator = DataValidator("test")
    validator.add_rule("number", required=True, custom_validator=is_even)

    # Valid (even)
    result = validator.validate({"number": 4})
    assert result.is_valid

    # Invalid (odd)
    result = validator.validate({"number": 3})
    assert not result.is_valid
    assert any("custom validation" in err for err in result.errors)


def test_validate_custom_validator_exception():
    """Test that exceptions in custom validator are caught."""

    def bad_validator(value):
        raise RuntimeError("Validator error")

    validator = DataValidator("test")
    validator.add_rule("field", required=True, custom_validator=bad_validator)

    result = validator.validate({"field": "test"})

    assert not result.is_valid
    assert any("raised exception" in err for err in result.errors)


def test_validate_unexpected_field(simple_validator):
    """Test validation with unexpected field."""
    data = {"name": "Frank", "age": 40, "extra_field": "unexpected"}

    result = simple_validator.validate(data)

    assert result.is_valid  # Still valid
    assert len(result.warnings) == 1
    assert any("Unexpected field" in warn for warn in result.warnings)
    assert "extra_field" in result.validated_data  # Still included


def test_validate_multiple_errors(simple_validator):
    """Test validation with multiple errors."""
    data = {"age": -10, "score": 150}  # Missing name, age < 0, score > 100

    result = simple_validator.validate(data)

    assert not result.is_valid
    assert len(result.errors) >= 3


def test_validate_none_value_with_type_check():
    """Test that None values are handled correctly with type checking."""
    validator = DataValidator("test")
    validator.add_rule("field", required=False, field_type=int)

    # None should be allowed for optional field
    result = validator.validate({"field": None})
    assert result.is_valid


def test_validate_or_raise_valid():
    """Test validate_or_raise with valid data."""
    validator = DataValidator("test")
    validator.add_rule("value", required=True, field_type=int)

    data = {"value": 42}
    validated = validator.validate_or_raise(data)

    assert validated == data


def test_validate_or_raise_invalid():
    """Test validate_or_raise with invalid data."""
    validator = DataValidator("test")
    validator.add_rule("value", required=True, field_type=int)

    data = {"value": "not_an_int"}

    with pytest.raises(ValueError, match="Validation failed"):
        validator.validate_or_raise(data)


def test_create_demographic_validator():
    """Test demographic validator factory."""
    validator = create_demographic_validator()

    # Valid data
    data = {
        "population": 100000,
        "median_age": 35.5,
        "median_income": 65000,
        "bachelor_degree_pct": 42.3,
    }

    result = validator.validate(data)
    assert result.is_valid


def test_demographic_validator_invalid_percentage():
    """Test demographic validator with invalid percentage."""
    validator = create_demographic_validator()

    data = {"population": 50000, "bachelor_degree_pct": 150}  # > 100%

    result = validator.validate(data)
    assert not result.is_valid


def test_create_economic_validator():
    """Test economic validator factory."""
    validator = create_economic_validator()

    # Valid data
    data = {
        "gdp": 1000000000,
        "gdp_growth_rate": 2.5,
        "employment": 50000,
        "unemployment_rate": 4.2,
        "average_wage": 55000,
    }

    result = validator.validate(data)
    assert result.is_valid


def test_economic_validator_negative_gdp():
    """Test economic validator rejects negative GDP."""
    validator = create_economic_validator()

    data = {"gdp": -1000}

    result = validator.validate(data)
    assert not result.is_valid


def test_create_location_validator():
    """Test location validator factory."""
    validator = create_location_validator()

    # Valid data
    data = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "state_fips": "06",
        "county_fips": "06037",
    }

    result = validator.validate(data)
    assert result.is_valid


def test_location_validator_invalid_coordinates():
    """Test location validator with invalid coordinates."""
    validator = create_location_validator()

    # Invalid latitude (> 90)
    data = {"latitude": 95.0, "longitude": 0.0}
    result = validator.validate(data)
    assert not result.is_valid

    # Invalid longitude (< -180)
    data = {"latitude": 0.0, "longitude": -200.0}
    result = validator.validate(data)
    assert not result.is_valid


def test_location_validator_invalid_fips():
    """Test location validator with invalid FIPS codes."""
    validator = create_location_validator()

    # Invalid state_fips (not 2 digits)
    data = {"latitude": 0.0, "longitude": 0.0, "state_fips": "6"}
    result = validator.validate(data)
    assert not result.is_valid

    # Invalid county_fips (not 5 digits)
    data = {"latitude": 0.0, "longitude": 0.0, "county_fips": "6037"}
    result = validator.validate(data)
    assert not result.is_valid


def test_detect_outliers_iqr_method():
    """Test outlier detection using IQR method."""
    values = [10, 12, 14, 13, 11, 100, 15, 14, 13, 12]  # 100 is outlier

    outliers = detect_outliers(values, method="iqr", threshold=1.5)

    assert 5 in outliers  # Index of 100


def test_detect_outliers_zscore_method():
    """Test outlier detection using z-score method."""
    values = [10, 12, 14, 13, 11, 100, 15, 14, 13, 12]  # 100 is outlier

    outliers = detect_outliers(values, method="zscore", threshold=2.0)

    assert 5 in outliers  # Index of 100


def test_detect_outliers_no_outliers():
    """Test outlier detection with no outliers."""
    values = [10, 11, 12, 13, 14, 15]

    outliers = detect_outliers(values, method="iqr")

    assert len(outliers) == 0


def test_detect_outliers_empty_list():
    """Test outlier detection with empty list."""
    with pytest.raises(ValueError, match="empty list"):
        detect_outliers([], method="iqr")


def test_detect_outliers_small_list():
    """Test outlier detection with small list (warning logged)."""
    values = [10, 100]

    # Should not raise, but may log warning
    outliers = detect_outliers(values, method="iqr")

    assert isinstance(outliers, list)


def test_detect_outliers_zero_stddev():
    """Test outlier detection when all values are the same."""
    values = [10, 10, 10, 10, 10]

    outliers = detect_outliers(values, method="zscore")

    # Should return empty list (no outliers when stddev=0)
    assert len(outliers) == 0


def test_detect_outliers_unknown_method():
    """Test outlier detection with unknown method."""
    values = [10, 12, 14]

    with pytest.raises(ValueError, match="Unknown outlier detection method"):
        detect_outliers(values, method="unknown")


def test_detect_outliers_multiple_outliers():
    """Test outlier detection with multiple outliers."""
    values = [10, 11, 12, 13, 150, 200, 14, 15]

    # Use z-score method which is more sensitive for extreme outliers
    outliers = detect_outliers(values, method="zscore", threshold=1.5)

    assert len(outliers) >= 2
    assert 4 in outliers  # 150
    assert 5 in outliers  # 200


def test_validation_result_structure():
    """Test ValidationResult dataclass structure."""
    result = ValidationResult(
        is_valid=True,
        errors=[],
        warnings=["warning1"],
        validated_data={"field": "value"},
    )

    assert result.is_valid
    assert result.errors == []
    assert result.warnings == ["warning1"]
    assert result.validated_data == {"field": "value"}

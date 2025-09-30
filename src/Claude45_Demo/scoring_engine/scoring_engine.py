"""Weighted scoring engine for investment analysis."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Calculate composite investment scores using weighted components.

    Combines market analysis, geographic analysis, and risk assessment
    into final investment attractiveness scores.
    """

    DEFAULT_WEIGHTS = {
        "supply_constraint": 0.30,
        "innovation_employment": 0.30,
        "urban_convenience": 0.20,
        "outdoor_access": 0.20,
    }

    EXTREME_RISK_THRESHOLD = 0.85

    def calculate_composite_score(
        self,
        component_scores: dict[str, float | None],
        weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """
        Calculate composite market score with weighted components.

        Implements:
        - Req: Weighted Composite Scoring
        - Scenario: Default weighted score calculation
        - Scenario: Custom weight configuration
        - Scenario: Missing component handling

        Args:
            component_scores: Dict of component scores (0-100 or None if missing)
            weights: Optional custom weights (default: 30/30/20/20)

        Returns:
            Dict with composite score, components, weights, metadata

        Raises:
            ValueError: If weights don't sum to 1.0 or all components missing
        """
        if weights is None:
            weights = self.DEFAULT_WEIGHTS.copy()

        # Validate weights sum to 1.0 (within tolerance)
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0, got {weight_sum:.3f}. " f"Weights: {weights}"
            )

        # Filter to available components
        available = {k: v for k, v in component_scores.items() if v is not None}
        missing = [k for k, v in component_scores.items() if v is None]

        if not available:
            raise ValueError("At least one component score must be provided")

        # Redistribute weights for missing components
        available_weight_sum = sum(weights[k] for k in available if k in weights)
        adjusted_weights = {
            k: weights.get(k, 0) / available_weight_sum
            for k in available
            if k in weights
        }

        # Calculate weighted average
        composite_score = sum(available[k] * adjusted_weights[k] for k in available)

        return {
            "score": round(composite_score, 1),
            "components": component_scores,
            "weights": adjusted_weights,
            "metadata": {
                "complete": len(missing) == 0,
                "missing_components": missing,
                "n_components": len(available),
                "weight_adjusted": len(missing) > 0,
            },
        }

    def apply_risk_adjustment(
        self, market_score: float, risk_multiplier: float
    ) -> dict[str, Any]:
        """
        Apply risk multiplier to market score.

        Implements:
        - Req: Risk-Adjusted Scoring
        - Scenario: Risk multiplier application
        - Scenario: Extreme risk exclusion

        Args:
            market_score: Base market score (0-100)
            risk_multiplier: Risk adjustment factor (0.9-1.1 typical)

        Returns:
            Dict with final score, risk adjustment details, and exclusion flags
        """
        final_score = market_score * risk_multiplier
        points_change = final_score - market_score

        # Check for extreme risk
        is_extreme_risk = risk_multiplier < self.EXTREME_RISK_THRESHOLD
        flagged_non_fit = is_extreme_risk

        result = {
            "final_score": round(final_score, 1),
            "market_score": round(market_score, 1),
            "risk_multiplier": risk_multiplier,
            "risk_adjustment": {
                "points_lost": (
                    round(abs(points_change), 1) if points_change < 0 else 0.0
                ),
                "points_gained": round(points_change, 1) if points_change > 0 else 0.0,
            },
            "flagged_non_fit": flagged_non_fit,
            "exclusion_reason": "extreme_risk" if is_extreme_risk else None,
        }

        if flagged_non_fit:
            logger.warning(
                f"Market flagged as non-fit: risk_multiplier={risk_multiplier:.2f} "
                f"(threshold={self.EXTREME_RISK_THRESHOLD})"
            )

        return result

    def normalize_linear(
        self, value: float, min_val: float, max_val: float, inverse: bool = False
    ) -> float:
        """
        Normalize value to 0-100 using linear scaling.

        Implements:
        - Req: Normalization Functions
        - Scenario: Linear normalization

        Args:
            value: Raw value to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value
            inverse: If True, reverse scale (lower is better)

        Returns:
            Normalized score 0-100
        """
        if max_val == min_val:
            return 50.0  # Return mid-point if range is zero

        # Linear scaling to 0-1
        normalized = (value - min_val) / (max_val - min_val)

        # Clamp to 0-1
        normalized = max(0.0, min(1.0, normalized))

        # Apply inverse if specified
        if inverse:
            normalized = 1.0 - normalized

        # Scale to 0-100
        return round(normalized * 100.0, 1)

    def normalize_percentile(
        self, target_value: float, all_values: list[float]
    ) -> float:
        """
        Normalize value using percentile rank.

        Implements:
        - Req: Normalization Functions
        - Scenario: Percentile-based normalization

        Args:
            target_value: Value to rank
            all_values: List of all values for comparison

        Returns:
            Percentile score 0-100
        """
        if not all_values:
            return 50.0

        # Sort values
        sorted_values = sorted(all_values)

        # Count values less than target
        count_below = sum(1 for v in sorted_values if v < target_value)

        # Calculate percentile rank
        percentile = (count_below / len(sorted_values)) * 100.0

        return round(percentile, 1)

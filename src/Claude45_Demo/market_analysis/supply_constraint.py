"""Supply constraint calculator for market analysis."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SupplyConstraintCalculator:
    """Calculate supply constraint scores for residential submarkets."""

    DEFAULT_WEIGHTS = {
        "permit_elasticity": 0.40,
        "topographic_constraint": 0.35,
        "regulatory_friction": 0.25,
    }

    def calculate_permit_elasticity(
        self,
        annual_permits: list[int],
        total_households: int,
        vacancy_rate: float,
        median_time_on_market_days: int,
    ) -> float:
        """Calculate permit elasticity score (0-100)."""
        avg_permits = sum(annual_permits) / len(annual_permits)
        permits_per_1k = (avg_permits / total_households) * 1000

        # Inverse scoring: lower permits = higher constraint
        if permits_per_1k <= 5.0:
            base_score = 100.0
        elif permits_per_1k >= 20.0:
            base_score = 0.0
        else:
            base_score = 100.0 - ((permits_per_1k - 5.0) / 15.0) * 100.0

        # Adjustments for vacancy and absorption
        vacancy_adj = (
            10.0 if vacancy_rate < 0.04 else -10.0 if vacancy_rate > 0.08 else 0.0
        )
        absorption_adj = (
            5.0
            if median_time_on_market_days < 30
            else -5.0 if median_time_on_market_days > 60 else 0.0
        )

        return max(0.0, min(100.0, base_score + vacancy_adj + absorption_adj))

    def calculate_topographic_constraint(
        self,
        slope_pct_steep: float,
        protected_land_pct: float,
        floodplain_pct: float,
        wetland_buffer_pct: float,
        airport_restriction_pct: float,
    ) -> float:
        """Calculate topographic constraint score (0-100)."""
        total_constrained = (
            slope_pct_steep
            + protected_land_pct
            + floodplain_pct
            + wetland_buffer_pct
            + airport_restriction_pct
        )

        if total_constrained >= 60.0:
            score = 100.0
        elif total_constrained <= 10.0:
            score = (total_constrained / 10.0) * 20.0
        else:
            score = 20.0 + ((total_constrained - 10.0) / 50.0) * 80.0

        return max(0.0, min(100.0, score))

    def calculate_regulatory_friction(
        self,
        median_permit_to_coo_days: int,
        has_inclusionary_zoning: bool,
        has_design_review: bool,
        has_parking_minimums: bool,
        has_utility_moratorium: bool,
    ) -> float:
        """Calculate regulatory friction score (0-100)."""
        if median_permit_to_coo_days <= 180:
            timeline_score = 20.0
        elif median_permit_to_coo_days >= 450:
            timeline_score = 80.0
        else:
            timeline_score = 20.0 + ((median_permit_to_coo_days - 180) / 270.0) * 60.0

        barrier_score = sum(
            [
                5.0 if has_inclusionary_zoning else 0.0,
                5.0 if has_design_review else 0.0,
                5.0 if has_parking_minimums else 0.0,
                5.0 if has_utility_moratorium else 0.0,
            ]
        )

        return max(0.0, min(100.0, timeline_score + barrier_score))

    def calculate_composite_score(
        self,
        permit_elasticity: float | None,
        topographic_constraint: float | None,
        regulatory_friction: float | None,
        weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """Calculate composite supply constraint score."""
        if weights is None:
            weights = self.DEFAULT_WEIGHTS.copy()

        components = {
            "permit_elasticity": permit_elasticity,
            "topographic_constraint": topographic_constraint,
            "regulatory_friction": regulatory_friction,
        }

        available = {k: v for k, v in components.items() if v is not None}
        missing = [k for k, v in components.items() if v is None]

        if not available:
            raise ValueError("At least one component score must be provided")

        total_weight = sum(weights[k] for k in available)
        adjusted_weights = {k: weights[k] / total_weight for k in available}

        composite_score = sum(available[k] * adjusted_weights[k] for k in available)

        return {
            "score": round(composite_score, 1),
            "components": components,
            "weights": adjusted_weights,
            "metadata": {
                "complete": len(missing) == 0,
                "missing_components": missing,
                "n_components": len(available),
            },
        }

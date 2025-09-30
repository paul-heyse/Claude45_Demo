"""Risk multiplier calculation for underwriting adjustments.

Combines all risk factors into a single multiplier (0.9-1.1) that adjusts
market scores or cap rates.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RiskMultiplierCalculator:
    """Calculate composite risk multiplier for underwriting."""

    # Risk factor weights
    WEIGHTS = {
        "wildfire": 0.25,
        "flood": 0.25,
        "regulatory": 0.30,
        "insurance": 0.20,
    }

    def __init__(self) -> None:
        """Initialize risk multiplier calculator."""
        logger.info("RiskMultiplierCalculator initialized")

    def calculate_risk_multiplier(
        self, risk_scores: dict[str, float]
    ) -> dict[str, Any]:
        """Calculate risk multiplier from component scores.

        Args:
            risk_scores: Dictionary with wildfire_score, flood_score,
                        regulatory_score, insurance_cost_score (all 0-100)

        Returns:
            Dictionary with multiplier (0.9-1.1), cap rate adjustment, flags
        """
        # Calculate weighted composite risk (0-100)
        composite_risk = 0
        for component, weight in self.WEIGHTS.items():
            score_key = f"{component}_score"
            if score_key in risk_scores:
                composite_risk += risk_scores[score_key] * weight

        # Map composite risk (0-100) to multiplier (0.9-1.1)
        # Risk 0 = 0.9 multiplier (favorable)
        # Risk 50 = 1.0 multiplier (baseline)
        # Risk 100 = 1.1 multiplier (high risk)
        multiplier = 0.9 + (composite_risk / 100) * 0.2

        # Round to 2 decimals
        multiplier = round(multiplier, 2)

        # Cap rate adjustment (+50 bps per 0.05 multiplier above 1.0)
        cap_rate_adjustment_bps = int((multiplier - 1.0) / 0.05 * 50)

        # Market exclusion flag for extreme risk
        wildfire_extreme = risk_scores.get("wildfire_score", 0) > 90
        flood_extreme = risk_scores.get("flood_score", 0) > 90

        exclude_market = wildfire_extreme or flood_extreme

        if exclude_market:
            recommendation = "Market exclusion recommended - extreme hazard risk"
        elif multiplier >= 1.08:
            recommendation = "High risk - proceed only with significant premium"
        elif multiplier >= 1.04:
            recommendation = "Moderate risk - apply multiplier to scoring"
        else:
            recommendation = "Low risk - favorable market characteristics"

        return {
            "risk_multiplier": multiplier,
            "composite_risk_score": int(composite_risk),
            "cap_rate_adjustment_bps": cap_rate_adjustment_bps,
            "exclude_market": exclude_market,
            "recommendation": recommendation,
            "component_scores": risk_scores,
        }

    def estimate_insurance_cost_multiplier(
        self, hazard_scores: dict[str, float]
    ) -> dict[str, Any]:
        """Estimate insurance cost as % of replacement cost.

        Args:
            hazard_scores: Dictionary with wildfire, flood, hail, wind scores

        Returns:
            Dictionary with insurance cost estimate and multiplier
        """
        # Base insurance cost: 0.3% of replacement cost
        base_cost_pct = 0.3

        # Add premiums for each hazard
        wildfire_premium = hazard_scores.get("wildfire_score", 0) / 100 * 0.8
        flood_premium = hazard_scores.get("flood_score", 0) / 100 * 0.6
        hail_premium = hazard_scores.get("hail_score", 0) / 100 * 0.5

        total_cost_pct = base_cost_pct + wildfire_premium + flood_premium + hail_premium

        # Cap at 3% of replacement cost
        total_cost_pct = min(3.0, total_cost_pct)

        # Insurance cost multiplier vs. baseline
        insurance_multiplier = total_cost_pct / base_cost_pct

        return {
            "insurance_cost_pct_replacement": round(total_cost_pct, 2),
            "insurance_multiplier": round(insurance_multiplier, 2),
            "base_cost_pct": base_cost_pct,
            "wildfire_premium_pct": round(wildfire_premium, 2),
            "flood_premium_pct": round(flood_premium, 2),
            "hail_premium_pct": round(hail_premium, 2),
        }

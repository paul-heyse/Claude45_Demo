"""Regulatory friction and entitlement risk assessment.

Estimates permitting complexity, zoning constraints, and policy risk for
development projects.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RegulatoryFrictionAnalyzer:
    """Analyze regulatory friction and policy risk."""

    def __init__(self) -> None:
        """Initialize regulatory friction analyzer."""
        logger.info("RegulatoryFrictionAnalyzer initialized")

    def estimate_permit_timeline(
        self,
        jurisdiction: str,
        project_type: str = "multifamily",
        mock_permit_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Estimate permitting timeline using historical data.

        Args:
            jurisdiction: City/county name
            project_type: Type of project (multifamily, mixed-use, etc.)
            mock_permit_data: Optional mock permit data for testing

        Returns:
            Dictionary with median timeline, friction score
        """
        if mock_permit_data is None:
            raise ValueError("Production permit API not yet implemented")

        median_days = mock_permit_data["median_days_to_permit"]
        percentile_90_days = mock_permit_data.get("p90_days", median_days * 1.5)

        # Score based on timeline (higher days = higher friction)
        if median_days >= 180:  # 6+ months = high friction
            friction_score = 85
            friction_level = "high"
        elif median_days >= 120:  # 4-6 months
            friction_score = 65
            friction_level = "moderate-high"
        elif median_days >= 60:  # 2-4 months
            friction_score = 40
            friction_level = "moderate"
        else:  # < 2 months = low friction
            friction_score = 20
            friction_level = "low"

        return {
            "jurisdiction": jurisdiction,
            "median_days_to_permit": median_days,
            "p90_days": percentile_90_days,
            "friction_score": friction_score,
            "friction_level": friction_level,
        }

    def assess_zoning_complexity(
        self,
        parcel_data: dict[str, Any],
        mock_zoning: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Assess zoning code complexity and overlay districts.

        Args:
            parcel_data: Parcel information
            mock_zoning: Optional mock zoning data for testing

        Returns:
            Dictionary with zoning complexity score and constraints
        """
        if mock_zoning is None:
            raise ValueError("Production zoning API not yet implemented")

        base_zone = mock_zoning["base_zone"]
        overlay_districts = mock_zoning.get("overlay_districts", [])
        design_review_required = mock_zoning.get("design_review_required", False)
        height_limit_ft = mock_zoning.get("height_limit_ft")
        far_limit = mock_zoning.get("far_limit")
        parking_min = mock_zoning.get("parking_minimum_per_unit")
        inclusionary_zoning = mock_zoning.get("inclusionary_zoning", False)

        # Base complexity score
        complexity_score = 20

        # Add complexity for overlay districts
        complexity_score += len(overlay_districts) * 15

        # Add complexity for design review
        if design_review_required:
            complexity_score += 20

        # Add complexity for inclusionary zoning
        if inclusionary_zoning:
            complexity_score += 15

        # Cap at 100
        complexity_score = min(100, complexity_score)

        # Identify restrictive constraints
        constraints = []
        if height_limit_ft and height_limit_ft < 45:  # < 4 stories
            constraints.append(f"Height limit: {height_limit_ft} ft")
        if far_limit and far_limit < 2.0:
            constraints.append(f"Low FAR: {far_limit}")
        if parking_min and parking_min > 1.5:
            constraints.append(f"High parking: {parking_min}/unit")

        return {
            "base_zone": base_zone,
            "overlay_districts": overlay_districts,
            "design_review_required": design_review_required,
            "inclusionary_zoning": inclusionary_zoning,
            "complexity_score": complexity_score,
            "constraints": constraints,
        }

    def assess_policy_risk(
        self,
        jurisdiction: str,
        mock_policy: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Assess rent control and tenant protection policy risk.

        Args:
            jurisdiction: City/county name
            mock_policy: Optional mock policy data for testing

        Returns:
            Dictionary with policy risk level and flags
        """
        if mock_policy is None:
            raise ValueError("Production policy database not yet implemented")

        rent_control = mock_policy.get("rent_control", False)
        just_cause_eviction = mock_policy.get("just_cause_eviction", False)
        rent_increase_limit_pct = mock_policy.get("rent_increase_limit_pct")
        political_climate = mock_policy.get("political_climate", "neutral")

        # Calculate policy risk score
        risk_score = 20  # Base

        if rent_control:
            risk_score += 40
        if just_cause_eviction:
            risk_score += 20
        if political_climate == "tenant_favorable":
            risk_score += 20

        # Determine risk level
        if risk_score >= 70:
            risk_level = "high"
        elif risk_score >= 50:
            risk_level = "moderate"
        else:
            risk_level = "low"

        return {
            "jurisdiction": jurisdiction,
            "rent_control": rent_control,
            "just_cause_eviction": just_cause_eviction,
            "rent_increase_limit_pct": rent_increase_limit_pct,
            "political_climate": political_climate,
            "policy_risk_score": risk_score,
            "risk_level": risk_level,
        }

    def calculate_composite_regulatory_risk(
        self, components: dict[str, float]
    ) -> dict[str, Any]:
        """Calculate overall regulatory friction from components.

        Args:
            components: Dictionary with permit_friction, zoning_complexity,
                       policy_risk scores

        Returns:
            Dictionary with composite score and risk level
        """
        # Weighted: Permits 40%, Zoning 35%, Policy 25%
        composite_score = int(
            components.get("permit_friction_score", 0) * 0.40
            + components.get("zoning_complexity_score", 0) * 0.35
            + components.get("policy_risk_score", 0) * 0.25
        )

        if composite_score >= 70:
            risk_level = "high"
            recommendation = "Avoid or require significant feasibility premium"
        elif composite_score >= 50:
            risk_level = "moderate"
            recommendation = "Proceed with extended timeline buffer"
        else:
            risk_level = "low"
            recommendation = "Favorable regulatory environment"

        return {
            "composite_regulatory_score": composite_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "components": components,
        }

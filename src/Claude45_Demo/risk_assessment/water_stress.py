"""Water availability and stress assessment for CO/UT/ID.

Evaluates water rights, drought risk, and supply constraints.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from Claude45_Demo.data_integration.drought_monitor import DroughtMonitorConnector

logger = logging.getLogger(__name__)


class WaterStressAnalyzer:
    """Analyze water availability and drought risk."""

    def __init__(
        self, *, drought_connector: Optional[DroughtMonitorConnector] = None
    ) -> None:
        """Initialize water stress analyzer.

        Args:
            drought_connector: Optional Drought Monitor connector for real data
        """
        self.drought_connector = drought_connector
        logger.info("WaterStressAnalyzer initialized")

    def assess_water_rights(
        self,
        state: str,
        county_fips: str,
        mock_rights: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Assess water rights availability by state.

        Args:
            state: State code (CO, UT, ID)
            county_fips: County FIPS code
            mock_rights: Optional mock water rights data

        Returns:
            Dictionary with water rights status and availability score
        """
        if mock_rights is None:
            raise ValueError("Production water rights API not yet implemented")

        has_decreed_rights = mock_rights.get("has_decreed_rights", False)
        municipal_supply = mock_rights.get("municipal_supply", True)
        augmentation_required = mock_rights.get("augmentation_required", False)
        tap_fees_per_unit = mock_rights.get("tap_fees_per_unit", 0)

        # Score based on water availability (lower = more constrained)
        if has_decreed_rights and not augmentation_required:
            availability_score = 90  # Strong water rights
        elif municipal_supply and not augmentation_required:
            availability_score = 70  # Municipal supply available
        elif augmentation_required:
            availability_score = 40  # Augmentation complexity
        else:
            availability_score = 20  # Limited availability

        # Adjust for high tap fees (indicator of scarcity)
        if tap_fees_per_unit > 15000:
            availability_score = max(0, availability_score - 20)

        return {
            "state": state,
            "has_decreed_rights": has_decreed_rights,
            "municipal_supply": municipal_supply,
            "augmentation_required": augmentation_required,
            "tap_fees_per_unit": tap_fees_per_unit,
            "availability_score": availability_score,
        }

    def assess_drought_risk(
        self,
        county_fips: str,
        lookback_years: int = 10,
        mock_drought: dict[str, Any] | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> dict[str, Any]:
        """Assess drought frequency and water stress.

        Args:
            county_fips: County FIPS code
            lookback_years: Years to analyze
            mock_drought: Optional mock drought data
            latitude: Optional latitude for location-based lookup
            longitude: Optional longitude for location-based lookup

        Returns:
            Dictionary with drought metrics and stress score
        """
        # Try to use real Drought Monitor connector first
        if (
            self.drought_connector is not None
            and mock_drought is None
            and latitude is not None
            and longitude is not None
        ):
            try:
                drought_data = self.drought_connector.assess_water_stress(
                    latitude, longitude, lookback_weeks=lookback_years * 52
                )

                return {
                    "county_fips": county_fips,
                    "current_drought_level": drought_data["current_drought_level"],
                    "drought_category": drought_data["current_category"],
                    "stress_score": drought_data["risk_score"],
                    "water_stress_detected": drought_data["water_stress_detected"],
                    "severe_stress": drought_data["severe_stress"],
                    "lookback_years": lookback_years,
                    "data_source": "U.S. Drought Monitor",
                }
            except Exception as e:
                logger.warning(
                    f"Drought Monitor connector failed: {e}, using mock data"
                )

        # Fall back to mock data
        if mock_drought is None:
            raise ValueError(
                "Production drought monitor API not configured and no mock data provided"
            )

        pct_years_in_drought = mock_drought["pct_years_in_moderate_plus_drought"]
        groundwater_overdraft = mock_drought.get("groundwater_overdraft", False)
        usgs_stress_index = mock_drought.get("usgs_stress_index", 0.3)

        # Score based on drought frequency (higher = more stress)
        if pct_years_in_drought >= 70:  # Chronic drought
            stress_score = 85
        elif pct_years_in_drought >= 50:
            stress_score = 65
        elif pct_years_in_drought >= 30:
            stress_score = 45
        else:
            stress_score = 25

        # Adjust for groundwater overdraft
        if groundwater_overdraft:
            stress_score = min(100, stress_score + 15)

        chronic_drought = pct_years_in_drought >= 50

        return {
            "pct_years_in_drought": pct_years_in_drought,
            "chronic_drought": chronic_drought,
            "groundwater_overdraft": groundwater_overdraft,
            "usgs_stress_index": usgs_stress_index,
            "drought_stress_score": stress_score,
            "lookback_years": lookback_years,
        }

    def calculate_composite_water_risk(
        self, components: dict[str, float]
    ) -> dict[str, Any]:
        """Calculate overall water stress risk.

        Args:
            components: Dictionary with availability_score (inverted) and
                       drought_stress_score

        Returns:
            Dictionary with composite score and risk level
        """
        # Invert availability score (high availability = low risk)
        availability_risk = 100 - components.get("availability_score", 50)

        # Weighted: Availability 60%, Drought 40%
        composite_score = int(
            availability_risk * 0.60 + components.get("drought_stress_score", 0) * 0.40
        )

        if composite_score >= 70:
            risk_level = "high"
            recommendation = "Water supply constraints significant"
        elif composite_score >= 50:
            risk_level = "moderate"
            recommendation = "Monitor water availability and drought conditions"
        else:
            risk_level = "low"
            recommendation = "Adequate water supply"

        return {
            "composite_water_risk_score": composite_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "components": components,
        }

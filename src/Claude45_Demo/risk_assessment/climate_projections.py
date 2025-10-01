"""Climate projection adjustments for forward-looking risk assessment.

Incorporates climate change projections from NOAA, USGS, and IPCC scenarios
to adjust current risk scores for long-term (10+ year) investment horizons.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ClimateProjectionAnalyzer:
    """Analyze climate change projections for risk adjustment."""

    # Climate projection scenarios (based on IPCC)
    SCENARIOS = {
        "RCP2.6": {"name": "Low emissions", "adjustment_factor": 1.0},
        "RCP4.5": {"name": "Moderate emissions", "adjustment_factor": 1.15},
        "RCP8.5": {"name": "High emissions", "adjustment_factor": 1.25},
        "SSP2": {"name": "Middle-of-the-road", "adjustment_factor": 1.15},
    }

    def __init__(self) -> None:
        """Initialize climate projection analyzer."""
        logger.info("ClimateProjectionAnalyzer initialized")

    def adjust_wildfire_risk(
        self,
        current_wildfire_score: float,
        region: str,
        scenario: str = "RCP4.5",
        mock_projection: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Apply forward-looking climate adjustment to wildfire risk.

        Implements:
        - Req: Climate Projection Adjustments
        - Scenario: Future wildfire risk trend

        Args:
            current_wildfire_score: Current wildfire risk score (0-100)
            region: Geographic region (e.g., "Colorado_Front_Range", "California")
            scenario: Climate scenario (RCP2.6, RCP4.5, RCP8.5, SSP2)
            mock_projection: Optional mock projection data for testing

        Returns:
            Dictionary with climate-adjusted wildfire score and metadata
        """
        if mock_projection is None:
            raise ValueError("Production NOAA/USGS climate API not yet implemented")

        # Extract projection data
        fire_season_increase_days = mock_projection.get("fire_season_increase_days", 0)
        intensity_increase_pct = mock_projection.get("intensity_increase_pct", 0)
        projection_year = mock_projection.get("projection_year", 2050)

        # Get scenario adjustment factor
        scenario_data = self.SCENARIOS.get(scenario, self.SCENARIOS["RCP4.5"])
        scenario_factor = scenario_data["adjustment_factor"]

        # Calculate climate adjustment
        # Base adjustment from fire season length increase
        season_adjustment = (fire_season_increase_days / 30) * 10  # ~3% per 10 days

        # Add adjustment from intensity increase
        intensity_adjustment = intensity_increase_pct * 0.5  # 50% of intensity increase

        # Total adjustment (cap at +20% per spec)
        total_adjustment_pct = min(
            20, (season_adjustment + intensity_adjustment) * scenario_factor
        )

        # Apply adjustment to current score
        adjusted_score = current_wildfire_score * (1 + total_adjustment_pct / 100)
        adjusted_score = min(100, adjusted_score)

        # Determine confidence level
        if projection_year <= 2040:
            confidence = "high"
        elif projection_year <= 2060:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "climate_adjusted_wildfire_score": int(adjusted_score),
            "current_score": int(current_wildfire_score),
            "adjustment_pct": round(total_adjustment_pct, 1),
            "projection_source": "NOAA/USGS",
            "scenario": scenario,
            "scenario_description": scenario_data["name"],
            "projection_year": projection_year,
            "confidence": confidence,
            "fire_season_increase_days": fire_season_increase_days,
            "intensity_increase_pct": intensity_increase_pct,
        }

    def adjust_drought_risk(
        self,
        current_drought_score: float,
        region: str,
        scenario: str = "RCP4.5",
        investment_horizon_years: int = 10,
        mock_projection: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Apply forward-looking climate adjustment to drought risk.

        Implements:
        - Req: Climate Projection Adjustments
        - Scenario: Drought frequency projection

        Args:
            current_drought_score: Current drought stress score (0-100)
            region: Geographic region
            scenario: Climate scenario
            investment_horizon_years: Investment holding period
            mock_projection: Optional mock projection data for testing

        Returns:
            Dictionary with climate-adjusted drought score and metadata
        """
        if mock_projection is None:
            raise ValueError("Production USGS water stress API not yet implemented")

        # Extract projection data
        supply_demand_imbalance_pct = mock_projection.get(
            "supply_demand_imbalance_pct", 0
        )
        drought_frequency_increase = mock_projection.get(
            "drought_frequency_increase_pct", 0
        )
        projection_year = mock_projection.get("projection_year", 2050)

        # Get scenario adjustment factor
        scenario_data = self.SCENARIOS.get(scenario, self.SCENARIOS["RCP4.5"])
        scenario_factor = scenario_data["adjustment_factor"]

        # Calculate climate adjustment
        # Supply-demand imbalance is primary driver
        imbalance_adjustment = supply_demand_imbalance_pct * 0.3

        # Drought frequency increase
        frequency_adjustment = drought_frequency_increase * 0.2

        # Total adjustment
        total_adjustment_pct = (
            imbalance_adjustment + frequency_adjustment
        ) * scenario_factor

        # Apply adjustment (for long-hold investments only)
        if investment_horizon_years >= 10:
            adjusted_score = current_drought_score * (1 + total_adjustment_pct / 100)
            adjustment_applied = True
        else:
            adjusted_score = current_drought_score
            adjustment_applied = False
            total_adjustment_pct = 0

        adjusted_score = min(100, adjusted_score)

        # Flag critical supply-demand imbalance
        critical_imbalance = supply_demand_imbalance_pct > 20

        return {
            "climate_adjusted_drought_score": int(adjusted_score),
            "current_score": int(current_drought_score),
            "adjustment_pct": round(total_adjustment_pct, 1),
            "adjustment_applied": adjustment_applied,
            "investment_horizon_years": investment_horizon_years,
            "projection_source": "USGS Water Availability",
            "scenario": scenario,
            "scenario_description": scenario_data["name"],
            "projection_year": projection_year,
            "supply_demand_imbalance_pct": supply_demand_imbalance_pct,
            "critical_imbalance": critical_imbalance,
            "drought_frequency_increase_pct": drought_frequency_increase,
        }

    def calculate_composite_climate_adjustment(
        self,
        current_risk_scores: dict[str, float],
        climate_adjustments: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate overall climate-adjusted risk scores.

        Args:
            current_risk_scores: Dictionary with current risk scores
            climate_adjustments: Dictionary with wildfire and drought adjustments

        Returns:
            Dictionary with climate-adjusted composite scores
        """
        adjusted_scores = current_risk_scores.copy()

        # Apply wildfire adjustment if available
        if "wildfire" in climate_adjustments:
            wildfire_adj = climate_adjustments["wildfire"]
            adjusted_scores["wildfire_score"] = wildfire_adj[
                "climate_adjusted_wildfire_score"
            ]

        # Apply drought adjustment if available
        if "drought" in climate_adjustments:
            drought_adj = climate_adjustments["drought"]
            adjusted_scores["drought_score"] = drought_adj[
                "climate_adjusted_drought_score"
            ]

        # Calculate adjustment summary
        adjustments_applied = []
        if "wildfire" in climate_adjustments:
            adjustments_applied.append(
                f"Wildfire: +{climate_adjustments['wildfire']['adjustment_pct']}%"
            )
        if "drought" in climate_adjustments:
            if climate_adjustments["drought"]["adjustment_applied"]:
                adjustments_applied.append(
                    f"Drought: +{climate_adjustments['drought']['adjustment_pct']}%"
                )

        return {
            "climate_adjusted_scores": adjusted_scores,
            "adjustments_applied": adjustments_applied,
            "climate_scenarios": {
                k: v["scenario"] for k, v in climate_adjustments.items()
            },
            "notes": "Climate adjustments reflect forward-looking risk through 2050",
        }

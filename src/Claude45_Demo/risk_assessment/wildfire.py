"""Wildfire risk assessment using USFS WHP, LANDFIRE, and fire history.

Assesses wildfire exposure in the wildland-urban interface using USFS Wildfire
Hazard Potential, LANDFIRE fuel models, historical fire perimeters, and WUI
classification.
"""

from __future__ import annotations

import logging
from typing import Any

from Claude45_Demo.data_integration.nasa_firms import NASAFIRMSConnector

logger = logging.getLogger(__name__)


class WildfireRiskAnalyzer:
    """Analyze wildfire risk for property locations."""

    # High-risk fuel types (timber and brush have high fire intensity)
    HIGH_RISK_FUELS = {"timber", "brush", "chaparral", "conifer"}

    def __init__(self, firms_api_key: str | None = None) -> None:
        """
        Initialize wildfire risk analyzer.

        Args:
            firms_api_key: NASA FIRMS API key (optional, for production use)
        """
        logger.info("WildfireRiskAnalyzer initialized")

        # Initialize FIRMS connector if key provided
        self.firms_connector = None
        if firms_api_key:
            self.firms_connector = NASAFIRMSConnector(api_key=firms_api_key)
            logger.info("NASA FIRMS connector initialized for production use")

    def assess_wildfire_hazard_potential(
        self,
        latitude: float,
        longitude: float,
        mock_whp: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Assess USFS Wildfire Hazard Potential for location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            mock_whp: Optional mock WHP data for testing

        Returns:
            Dictionary with mean/max WHP, normalized score, risk category
        """
        if mock_whp is None:
            raise ValueError("Production USFS WHP API not yet implemented")

        mean_whp = mock_whp["mean_whp"]
        max_whp = mock_whp["max_whp"]

        # Normalize WHP (1-5 scale) to 0-100 score
        # WHP 1 = 20, WHP 5 = 100 (linear interpolation)
        whp_score = 20 + (mean_whp - 1) * 20

        # Determine risk category
        if whp_score >= 80:
            risk_category = "very_high"
        elif whp_score >= 60:
            risk_category = "high"
        elif whp_score >= 40:
            risk_category = "moderate"
        else:
            risk_category = "low"

        return {
            "mean_whp": mean_whp,
            "max_whp": max_whp,
            "whp_score": int(whp_score),
            "risk_category": risk_category,
        }

    def analyze_fuel_models(
        self,
        latitude: float,
        longitude: float,
        mock_fuel_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze LANDFIRE fuel models in surrounding area.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            mock_fuel_data: Optional mock fuel data for testing

        Returns:
            Dictionary with fuel types, high-risk percentage, fuel score
        """
        if mock_fuel_data is None:
            raise ValueError("Production LANDFIRE API not yet implemented")

        fuel_types = mock_fuel_data["fuel_types"]

        # Calculate percentage of high-risk fuels
        high_risk_pct = sum(
            pct for fuel, pct in fuel_types.items() if fuel in self.HIGH_RISK_FUELS
        )

        # Score based on high-risk fuel percentage (0-100)
        fuel_score = int(high_risk_pct)

        # Identify dominant fuel types (>20% of area)
        dominant_fuel_types = [fuel for fuel, pct in fuel_types.items() if pct > 20]

        return {
            "fuel_types": fuel_types,
            "high_risk_fuel_pct": high_risk_pct,
            "fuel_score": fuel_score,
            "dominant_fuel_types": dominant_fuel_types,
        }

    def assess_fire_history(
        self,
        latitude: float,
        longitude: float,
        lookback_years: int = 20,
        mock_history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Assess historical fire perimeter proximity.

        Note: This uses NASA FIRMS for recent fire activity (last 7-10 days).
        For historical fire perimeters (>10 days), USGS/NIFC MTBS data would be needed.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            lookback_years: Years to look back for fire history
            mock_history: Optional mock fire history for testing

        Returns:
            Dictionary with fire counts, nearest fire distance, history score
        """
        # Try FIRMS API for recent activity if available
        if mock_history is None and self.firms_connector:
            try:
                firms_data = self.firms_connector.analyze_fire_activity(
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=10,
                    lookback_days=7,  # FIRMS limitation
                )

                if firms_data["fire_activity_detected"]:
                    # Convert FIRMS hotspots to fire history format
                    fires_within_10km = firms_data["hotspot_count"]
                    nearest_large_fire_km = firms_data["nearest_hotspot_km"]

                    logger.info(
                        f"NASA FIRMS detected {fires_within_10km} recent hotspots "
                        f"within 10km of ({latitude}, {longitude})"
                    )

                    # Calculate score based on recent activity
                    if fires_within_10km == 0:
                        fire_history_score = 10
                    elif fires_within_10km <= 2:
                        fire_history_score = 40
                    elif fires_within_10km <= 5:
                        fire_history_score = 70
                    else:
                        fire_history_score = 90

                    recent_fire_activity = True

                    return {
                        "fires_within_10km": fires_within_10km,
                        "nearest_large_fire_km": nearest_large_fire_km,
                        "fire_history_score": fire_history_score,
                        "recent_fire_activity": recent_fire_activity,
                        "lookback_years": 1,  # FIRMS only provides recent data
                        "data_source": "NASA_FIRMS_NRT",
                        "note": "Recent hotspot data only (7 days). Historical perimeters require MTBS.",
                    }
                else:
                    # No recent activity, but fall through for historical analysis
                    logger.info("No recent fire activity detected via FIRMS")

            except Exception as e:
                logger.warning(
                    f"NASA FIRMS query failed: {e}, falling back to mock data"
                )
                if mock_history is None:
                    raise ValueError(
                        "Production NASA FIRMS failed and no mock data provided. "
                        "For historical fire perimeters (>10 days), MTBS API integration needed."
                    ) from e

        if mock_history is None:
            raise ValueError(
                "Historical fire perimeter data (MTBS) not yet implemented. "
                "Provide mock_history or use FIRMS connector for recent activity."
            )

        # Count fires within 10km
        fires_within_10km = sum(1 for fire in mock_history if fire["distance_km"] <= 10)

        # Find nearest large fire (>1000 acres)
        large_fires = [f for f in mock_history if f["acres"] > 1000]
        if large_fires:
            nearest_large_fire_km = min(f["distance_km"] for f in large_fires)
        else:
            nearest_large_fire_km = None

        # Calculate history score (0-100)
        if fires_within_10km == 0:
            fire_history_score = 10
        elif fires_within_10km == 1:
            fire_history_score = 40
        elif fires_within_10km == 2:
            fire_history_score = 70
        else:  # 3+ fires
            fire_history_score = 90

        # Boost score if recent fire very close
        if nearest_large_fire_km and nearest_large_fire_km < 5:
            fire_history_score = min(100, fire_history_score + 10)

        recent_fire_activity = fires_within_10km > 0

        return {
            "fires_within_10km": fires_within_10km,
            "nearest_large_fire_km": nearest_large_fire_km,
            "fire_history_score": fire_history_score,
            "recent_fire_activity": recent_fire_activity,
            "lookback_years": lookback_years,
        }

    def classify_wui(
        self,
        latitude: float,
        longitude: float,
        mock_wui: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Classify Wildland-Urban Interface status.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            mock_wui: Optional mock WUI data for testing

        Returns:
            Dictionary with WUI class, risk score, evacuation constraints
        """
        if mock_wui is None:
            raise ValueError("Production USFS WUI API not yet implemented")

        wui_class = mock_wui["classification"]
        evacuation_routes = mock_wui["evacuation_routes"]

        # Score by WUI classification
        if wui_class == "Intermix":
            base_score = 90  # Highest risk
        elif wui_class == "Interface":
            base_score = 60  # Moderate-high risk
        else:  # Non-WUI
            base_score = 20  # Low risk

        # Adjust for evacuation constraints
        evacuation_constraint = evacuation_routes == 1
        if evacuation_constraint:
            wui_risk_score = min(100, base_score + 10)
            notes = "Single access road increases evacuation risk"
        else:
            wui_risk_score = base_score
            notes = f"{evacuation_routes} evacuation routes available"

        return {
            "wui_class": wui_class,
            "wui_risk_score": wui_risk_score,
            "evacuation_constraint": evacuation_constraint,
            "evacuation_routes": evacuation_routes,
            "notes": notes,
        }

    def calculate_composite_wildfire_risk(
        self, components: dict[str, float]
    ) -> dict[str, Any]:
        """Calculate overall wildfire risk from component scores.

        Args:
            components: Dictionary with whp_score, fuel_score, fire_history_score,
                       wui_risk_score

        Returns:
            Dictionary with composite score, risk level, mitigation recommendations
        """
        # Weighted average: WHP 30%, Fuel 25%, History 20%, WUI 25%
        composite_score = int(
            components["whp_score"] * 0.30
            + components["fuel_score"] * 0.25
            + components["fire_history_score"] * 0.20
            + components["wui_risk_score"] * 0.25
        )

        # Determine risk level
        if composite_score >= 80:
            risk_level = "extreme"
            mitigation_required = True
            recommendations = [
                "Defensible space (100ft minimum)",
                "Fire-resistant roofing and siding",
                "Ember-resistant vents",
                "Wildfire insurance (high deductible expected)",
            ]
        elif composite_score >= 60:
            risk_level = "high"
            mitigation_required = True
            recommendations = [
                "Defensible space (30ft minimum)",
                "Fire-resistant landscaping",
                "Wildfire insurance required",
            ]
        elif composite_score >= 40:
            risk_level = "moderate"
            mitigation_required = False
            recommendations = ["Basic defensible space", "Monitor fire season alerts"]
        else:
            risk_level = "low"
            mitigation_required = False
            recommendations = ["Standard building codes sufficient"]

        return {
            "composite_score": composite_score,
            "risk_level": risk_level,
            "mitigation_required": mitigation_required,
            "recommendations": recommendations,
            "components": components,
        }

"""Air quality analysis using EPA AQS and NOAA HMS smoke data.

Assesses air quality risk from PM2.5 pollution and wildfire smoke exposure.
"""

from __future__ import annotations

import logging
from typing import Any

from Claude45_Demo.data_integration.epa_aqs import EPAAQSConnector

logger = logging.getLogger(__name__)


class AirQualityAnalyzer:
    """Analyze air quality risk for property locations."""

    def __init__(
        self,
        epa_email: str | None = None,
        epa_api_key: str | None = None,
    ) -> None:
        """
        Initialize air quality analyzer.

        Args:
            epa_email: EPA AQS registered email (optional, for production use)
            epa_api_key: EPA AQS API key (optional, for production use)
        """
        logger.info("AirQualityAnalyzer initialized")

        # Initialize EPA connector if credentials provided
        self.epa_connector = None
        if epa_email and epa_api_key:
            self.epa_connector = EPAAQSConnector(
                email=epa_email,
                api_key=epa_api_key,
            )
            logger.info("EPA AQS connector initialized for production use")

    def analyze_pm25(
        self,
        latitude: float,
        longitude: float,
        year: int,
        state_code: str | None = None,
        county_code: str | None = None,
        mock_aqs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze PM2.5 air quality using EPA AQS data.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            year: Year to analyze
            state_code: Optional 2-digit state FIPS code (required for production)
            county_code: Optional 3-digit county FIPS code (required for production)
            mock_aqs: Optional mock AQS data for testing

        Returns:
            Dictionary with PM2.5 metrics and risk score
        """
        # Try production API first if configured
        if mock_aqs is None and self.epa_connector and state_code and county_code:
            try:
                epa_data = self.epa_connector.get_pm25_annual_data(
                    state_code=state_code,
                    county_code=county_code,
                    year=year,
                )

                if epa_data["data_available"]:
                    annual_mean = epa_data["annual_mean_pm25"]
                    days_over_35 = epa_data["days_over_35"]
                    # Note: EPA AQS doesn't directly provide smoke days
                    wildfire_smoke_days = 0  # Would need separate NOAA HMS call

                    logger.info(
                        f"Retrieved PM2.5 data from EPA AQS for {state_code}-{county_code}: "
                        f"mean={annual_mean} μg/m³"
                    )
                else:
                    logger.warning(
                        f"No EPA AQS data available for {state_code}-{county_code} {year}"
                    )
                    # Fall through to require mock data
                    raise ValueError("No EPA data available")

            except Exception as e:
                logger.warning(
                    f"EPA AQS query failed: {e}, falling back to mock data requirement"
                )
                if mock_aqs is None:
                    raise ValueError(
                        "Production EPA AQS API failed and no mock data provided. "
                        "Ensure state_code and county_code are correct, or provide mock_aqs."
                    ) from e
                annual_mean = mock_aqs["annual_mean_pm25"]
                days_over_35 = mock_aqs["days_over_35"]
                wildfire_smoke_days = mock_aqs["wildfire_smoke_days"]
        elif mock_aqs is not None:
            # Use mock data for testing
            annual_mean = mock_aqs["annual_mean_pm25"]
            days_over_35 = mock_aqs["days_over_35"]
            wildfire_smoke_days = mock_aqs["wildfire_smoke_days"]
        else:
            raise ValueError(
                "Production EPA AQS API requires epa_email, epa_api_key, state_code, and county_code. "
                "Alternatively, provide mock_aqs for testing."
            )

        # Score based on annual mean PM2.5 (EPA standard: 12 μg/m³)
        if annual_mean >= 15:  # Exceeds WHO guideline
            base_score = 80
        elif annual_mean >= 12:  # Exceeds EPA standard
            base_score = 60
        elif annual_mean >= 9:  # Moderate
            base_score = 40
        else:  # Good air quality
            base_score = 20

        # Adjust for unhealthy days
        if days_over_35 > 10:
            base_score = min(100, base_score + 20)

        # Check wildfire impact
        wildfire_impact = wildfire_smoke_days > 10

        return {
            "annual_mean_pm25": annual_mean,
            "days_over_35": days_over_35,
            "wildfire_smoke_days": wildfire_smoke_days,
            "pm25_risk_score": base_score,
            "wildfire_impact": wildfire_impact,
        }

    def analyze_smoke_days(
        self,
        latitude: float,
        longitude: float,
        lookback_years: int = 5,
        mock_smoke: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyze wildfire smoke days using NOAA HMS data.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            lookback_years: Years to analyze
            mock_smoke: Optional mock smoke data for testing

        Returns:
            Dictionary with smoke days metrics and risk score
        """
        if mock_smoke is None:
            raise ValueError("Production NOAA HMS API not yet implemented")

        total_smoke_days = mock_smoke["total_smoke_days"]
        heavy_smoke_days = mock_smoke["heavy_smoke_days"]
        years_analyzed = mock_smoke["years_analyzed"]

        avg_smoke_days_per_year = total_smoke_days / years_analyzed

        # Score based on average annual smoke days
        if avg_smoke_days_per_year >= 15:  # Chronic exposure
            smoke_risk_score = 90
        elif avg_smoke_days_per_year >= 7:  # High exposure
            smoke_risk_score = 70
        elif avg_smoke_days_per_year >= 5:
            smoke_risk_score = 50
        else:
            smoke_risk_score = 20

        chronic_exposure = avg_smoke_days_per_year >= 7

        return {
            "total_smoke_days": total_smoke_days,
            "heavy_smoke_days": heavy_smoke_days,
            "avg_smoke_days_per_year": int(avg_smoke_days_per_year),
            "smoke_risk_score": smoke_risk_score,
            "chronic_exposure": chronic_exposure,
            "years_analyzed": years_analyzed,
        }

    def calculate_composite_air_quality_risk(
        self, components: dict[str, float]
    ) -> dict[str, Any]:
        """Calculate overall air quality risk from PM2.5 and smoke.

        Args:
            components: Dictionary with pm25_risk_score, smoke_risk_score

        Returns:
            Dictionary with composite score, risk level, recommendations
        """
        # Weighted average: PM2.5 50%, Smoke 50%
        composite_score = int(
            components["pm25_risk_score"] * 0.5 + components["smoke_risk_score"] * 0.5
        )

        # Determine risk level
        if composite_score >= 70:
            risk_level = "high"
            recommendations = [
                "HEPA air filtration systems required",
                "Consider air quality monitoring",
                "Outdoor activity restrictions during smoke events",
            ]
        elif composite_score >= 50:
            risk_level = "moderate"
            recommendations = [
                "Air filtration recommended",
                "Monitor EPA AirNow alerts",
            ]
        else:
            risk_level = "low"
            recommendations = ["Standard ventilation sufficient"]

        return {
            "composite_score": composite_score,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "components": components,
        }

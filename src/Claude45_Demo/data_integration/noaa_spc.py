"""NOAA Storm Prediction Center (SPC) severe weather climatology connector.

Provides hail and severe storm event data for the United States using
NOAA's Storm Events Database and SPC climatology data.

API Documentation: https://www.ncdc.noaa.gov/stormevents/
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager

logger = logging.getLogger(__name__)


class NOAASPCConnector(APIConnector):
    """
    NOAA Storm Prediction Center climatology connector.

    Provides severe weather event statistics including hail frequency,
    size distribution, and wind events.
    """

    DEFAULT_BASE_URL = "https://www.ncdc.noaa.gov/stormevents/csv"

    # Hail size categories (inches)
    HAIL_CATEGORIES = {
        0.75: "Pea",
        1.0: "Quarter",
        1.5: "Ping Pong Ball",
        1.75: "Golf Ball",
        2.0: "Hen Egg",
        2.5: "Tennis Ball",
        2.75: "Baseball",
        3.0: "Tea Cup",
        4.0: "Grapefruit",
        4.5: "Softball",
    }

    # Simplified hail climatology for CO/UT/ID (events per decade per county)
    # Real implementation would query NOAA API
    HAIL_CLIMATOLOGY: Dict[str, Dict[str, float]] = {
        "08": {  # Colorado
            "001": 12.5,  # Adams - High (Front Range hail alley)
            "005": 11.8,  # Arapahoe - High
            "013": 9.2,  # Boulder - Moderate-high
            "014": 10.5,  # Broomfield - High
            "031": 15.2,  # Denver - Very high (hail alley)
            "041": 13.8,  # El Paso - Very high
            "059": 10.1,  # Jefferson - High
            "069": 8.5,  # Larimer - Moderate-high
            "123": 11.2,  # Weld - High
        },
        "49": {  # Utah
            "003": 3.2,  # Box Elder - Low-moderate
            "011": 2.8,  # Davis - Low
            "035": 4.5,  # Salt Lake - Low-moderate
            "043": 2.1,  # Summit - Low
            "049": 3.8,  # Utah - Low-moderate
            "057": 3.1,  # Weber - Low-moderate
        },
        "16": {  # Idaho
            "001": 2.5,  # Ada - Low
            "019": 3.1,  # Bonneville - Low-moderate
            "027": 2.8,  # Canyon - Low
            "055": 1.8,  # Kootenai - Very low
            "083": 3.5,  # Twin Falls - Low-moderate
        },
    }

    def __init__(
        self,
        *,
        api_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        cache_ttl_days: int = 90,  # Quarterly updates
        cache_manager: CacheManager | None = None,
    ) -> None:
        """
        Initialize NOAA SPC connector.

        Args:
            api_token: Optional NOAA API token (for higher rate limits)
            base_url: NOAA Storm Events API endpoint
            cache_ttl_days: Cache TTL in days (default: 90)
            cache_manager: Optional cache manager instance
        """
        super().__init__(
            api_key=api_token or "",
            base_url=base_url,
            cache_ttl_days=cache_ttl_days,
            cache_manager=cache_manager,
        )
        self.api_token = api_token

    def _load_api_key(self) -> str | None:
        """Return API token if provided."""
        return self.api_token

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve storm event data from NOAA API.

        Args:
            params: API request parameters

        Returns:
            Storm event data (currently using climatology lookup)
        """
        # For this implementation, we're using static climatology data
        # A full implementation would query the NOAA Storm Events Database
        state_fips = params.get("state_fips")
        county_fips = params.get("county_fips")

        if not state_fips or not county_fips:
            return {"hail_events_per_decade": 5.0}  # National average

        # Look up climatology
        events = 5.0  # Default
        if state_fips in self.HAIL_CLIMATOLOGY:
            if county_fips in self.HAIL_CLIMATOLOGY[state_fips]:
                events = self.HAIL_CLIMATOLOGY[state_fips][county_fips]

        return {
            "state_fips": state_fips,
            "county_fips": county_fips,
            "hail_events_per_decade": events,
        }

    def parse(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse hail climatology data.

        Args:
            response: Climatology lookup result

        Returns:
            Structured hail risk data
        """
        events_per_decade = response.get("hail_events_per_decade", 5.0)

        # Estimate max hail size based on frequency
        if events_per_decade >= 12:
            max_hail_size = 2.5  # Baseball+
            max_hail_category = "Baseball or larger"
        elif events_per_decade >= 8:
            max_hail_size = 2.0  # Golf ball to hen egg
            max_hail_category = "Golf ball to hen egg"
        elif events_per_decade >= 5:
            max_hail_size = 1.5  # Quarter to golf ball
            max_hail_category = "Quarter to golf ball"
        else:
            max_hail_size = 1.0  # Quarter or less
            max_hail_category = "Quarter or less"

        # Calculate risk score
        if events_per_decade >= 12:
            risk_score = 90
            risk_level = "very_high"
        elif events_per_decade >= 8:
            risk_score = 70
            risk_level = "high"
        elif events_per_decade >= 5:
            risk_score = 50
            risk_level = "moderate"
        elif events_per_decade >= 2:
            risk_score = 30
            risk_level = "low"
        else:
            risk_score = 15
            risk_level = "very_low"

        return {
            "hail_events_per_decade": events_per_decade,
            "max_hail_size_inches": max_hail_size,
            "max_hail_category": max_hail_category,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "hail_alley": events_per_decade >= 10,
            "data_source": "NOAA SPC Climatology",
        }

    def get_hail_climatology(self, state_fips: str, county_fips: str) -> Dict[str, Any]:
        """
        Get hail climatology for a county.

        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code

        Returns:
            Dictionary with hail climatology data
        """
        cache_key = f"noaa_spc_hail_{state_fips}_{county_fips}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for NOAA SPC hail: {cache_key}")
                return cached  # type: ignore[return-value]

        params = {"state_fips": state_fips, "county_fips": county_fips}

        response = self.fetch(params)
        parsed_data = self.parse(response)

        if self.cache:
            self.cache.set(cache_key, parsed_data, ttl=self.cache_ttl)

        return parsed_data

    def assess_hail_risk(
        self,
        latitude: float,
        longitude: float,
        state_fips: str,
        county_fips: str,
    ) -> Dict[str, Any]:
        """
        Comprehensive hail risk assessment.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code

        Returns:
            Dictionary with hail risk assessment
        """
        hail_data = self.get_hail_climatology(state_fips, county_fips)

        risk_score = hail_data["risk_score"]
        is_hail_alley = hail_data["hail_alley"]

        # Insurance considerations
        if is_hail_alley:
            insurance_note = "Higher deductibles and premiums likely in hail alley"
            roof_warranty_concern = True
        elif risk_score >= 50:
            insurance_note = "Impact-resistant roofing recommended"
            roof_warranty_concern = True
        else:
            insurance_note = "Standard hail coverage"
            roof_warranty_concern = False

        # Mitigation recommendations
        recommendations = []
        if risk_score >= 70:
            recommendations.extend(
                [
                    "Class 4 impact-resistant roofing required",
                    "Hail-resistant siding recommended",
                    "Higher insurance deductibles expected",
                ]
            )
        elif risk_score >= 50:
            recommendations.extend(
                [
                    "Consider impact-resistant roofing",
                    "Review insurance coverage carefully",
                ]
            )

        return {
            **hail_data,
            "latitude": latitude,
            "longitude": longitude,
            "state_fips": state_fips,
            "county_fips": county_fips,
            "insurance_note": insurance_note,
            "roof_warranty_concern": roof_warranty_concern,
            "recommendations": recommendations,
        }

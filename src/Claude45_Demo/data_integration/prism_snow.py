"""PRISM/NOAA snow load data connector.

Provides ground snow load data for structural design based on ASCE 7
and PRISM climate normals.

Data Sources:
- PRISM Climate Group (Oregon State University)
- NOAA NCEI Climate Normals
- ASCE 7 Ground Snow Load Maps
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager

logger = logging.getLogger(__name__)


class PRISMSnowConnector(APIConnector):
    """
    PRISM/NOAA snow load data connector.

    Provides ground snow load estimates based on elevation, climate zone,
    and ASCE 7 ground snow load maps.
    """

    # Simplified snow load lookup by elevation and state
    # Format: {state: [(min_elev_ft, max_elev_ft, base_load_psf)]}
    SNOW_LOAD_CURVES: Dict[str, list[tuple[float, float, float]]] = {
        "CO": [  # Colorado - high variability with elevation
            (0, 5000, 20),  # Plains
            (5000, 6500, 30),  # Foothills
            (6500, 8000, 50),  # Lower mountains
            (8000, 9500, 70),  # Mid mountains
            (9500, 11000, 90),  # High mountains
            (11000, 15000, 120),  # Alpine
        ],
        "UT": [  # Utah - moderate mountain loading
            (0, 4500, 15),  # Valleys
            (4500, 6000, 25),  # Foothills
            (6000, 7500, 40),  # Lower mountains
            (7500, 9000, 60),  # Mid mountains
            (9000, 11000, 80),  # High mountains
            (11000, 14000, 100),  # Alpine
        ],
        "ID": [  # Idaho - variable by region
            (0, 4000, 20),  # Southern valleys
            (4000, 5500, 30),  # Foothills
            (5500, 7000, 45),  # Lower mountains
            (7000, 8500, 65),  # Mid mountains
            (8500, 10000, 85),  # High mountains
            (10000, 13000, 110),  # Alpine
        ],
    }

    # Regional snow load modifiers (latitude-based)
    REGIONAL_MODIFIERS = {
        "northern": 1.15,  # Northern ID, mountain regions
        "central": 1.0,  # Central regions
        "southern": 0.85,  # Southern valleys
    }

    def __init__(
        self,
        *,
        cache_ttl_days: int = 365,  # Snow load data rarely changes
        cache_manager: CacheManager | None = None,
    ) -> None:
        """
        Initialize PRISM Snow connector.

        Args:
            cache_ttl_days: Cache TTL in days (default: 365)
            cache_manager: Optional cache manager instance
        """
        super().__init__(
            api_key="",  # No API key needed (using lookup tables)
            base_url="",  # No API endpoint
            cache_ttl_days=cache_ttl_days,
            cache_manager=cache_manager,
        )

    def _load_api_key(self) -> str | None:
        """No API key needed for snow load lookup."""
        return None

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate ground snow load based on location parameters.

        Args:
            params: Dictionary with location parameters:
                    - 'latitude': Location latitude
                    - 'longitude': Location longitude
                    - 'elevation_ft': Site elevation in feet
                    - 'state': State code (CO, UT, ID)

        Returns:
            Dictionary with snow load calculation
        """
        latitude = params.get("latitude", 40.0)
        elevation_ft = params.get("elevation_ft", 5000)
        state = params.get("state", "CO").upper()

        # Get base snow load from elevation curve
        if state not in self.SNOW_LOAD_CURVES:
            # Default to moderate mountain loading
            base_load = 30 + (elevation_ft / 1000) * 8
        else:
            curves = self.SNOW_LOAD_CURVES[state]
            base_load = 20  # Default

            for min_elev, max_elev, load in curves:
                if min_elev <= elevation_ft < max_elev:
                    base_load = load
                    # Interpolate within range
                    range_fraction = (elevation_ft - min_elev) / (max_elev - min_elev)
                    if range_fraction > 0.5:
                        # Add partial increment toward next range
                        base_load += 5 * range_fraction
                    break

        # Apply regional modifier based on latitude
        if latitude >= 44.0:  # Northern regions
            modifier = self.REGIONAL_MODIFIERS["northern"]
        elif latitude <= 37.0:  # Southern regions
            modifier = self.REGIONAL_MODIFIERS["southern"]
        else:
            modifier = self.REGIONAL_MODIFIERS["central"]

        ground_snow_load = base_load * modifier

        return {
            "latitude": latitude,
            "elevation_ft": elevation_ft,
            "state": state,
            "ground_snow_load_psf": round(ground_snow_load, 1),
            "regional_modifier": modifier,
        }

    def parse(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse snow load calculation into risk assessment.

        Args:
            response: Snow load calculation result

        Returns:
            Dictionary with snow load risk data
        """
        ground_snow_load = response["ground_snow_load_psf"]

        # Categorize snow load severity
        if ground_snow_load >= 100:
            load_category = "extreme"
            risk_score = 90
            cost_premium_pct = 20
        elif ground_snow_load >= 70:
            load_category = "very_high"
            risk_score = 75
            cost_premium_pct = 15
        elif ground_snow_load >= 50:
            load_category = "high"
            risk_score = 60
            cost_premium_pct = 10
        elif ground_snow_load >= 30:
            load_category = "moderate"
            risk_score = 40
            cost_premium_pct = 5
        else:
            load_category = "low"
            risk_score = 20
            cost_premium_pct = 0

        return {
            **response,
            "load_category": load_category,
            "risk_score": risk_score,
            "structural_cost_premium_pct": cost_premium_pct,
            "data_source": "ASCE 7 / PRISM Normals",
        }

    def get_snow_load(
        self, latitude: float, longitude: float, elevation_ft: float, state: str = "CO"
    ) -> Dict[str, Any]:
        """
        Get ground snow load for a location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            elevation_ft: Site elevation in feet
            state: State code (CO, UT, ID)

        Returns:
            Dictionary with snow load data
        """
        cache_key = f"prism_snow_{latitude}_{longitude}_{elevation_ft}_{state}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for PRISM snow load: {cache_key}")
                return cached  # type: ignore[return-value]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "elevation_ft": elevation_ft,
            "state": state,
        }

        response = self.fetch(params)
        parsed_data = self.parse(response)

        if self.cache:
            self.cache.set(cache_key, parsed_data, ttl=self.cache_ttl)

        return parsed_data

    def assess_snow_risk(
        self, latitude: float, longitude: float, elevation_ft: float, state: str = "CO"
    ) -> Dict[str, Any]:
        """
        Comprehensive snow load risk assessment.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            elevation_ft: Site elevation in feet
            state: State code (CO, UT, ID)

        Returns:
            Dictionary with snow risk assessment
        """
        snow_data = self.get_snow_load(latitude, longitude, elevation_ft, state)

        ground_snow_load = snow_data["ground_snow_load_psf"]

        # Construction implications
        requires_engineered_design = ground_snow_load >= 50
        winter_construction_premium = 0

        if ground_snow_load >= 70:
            winter_construction_premium = 15  # % premium
        elif ground_snow_load >= 50:
            winter_construction_premium = 10
        elif ground_snow_load >= 30:
            winter_construction_premium = 5

        # Recommendations
        recommendations = []
        if ground_snow_load >= 70:
            recommendations.extend(
                [
                    "Engineered snow load analysis required",
                    "Reinforced roof structure needed",
                    "Snow retention systems recommended",
                    "Avoid winter construction if possible",
                ]
            )
        elif ground_snow_load >= 50:
            recommendations.extend(
                [
                    "Engineered design recommended",
                    "Consider snow load monitoring",
                    "Winter construction timing critical",
                ]
            )
        elif ground_snow_load >= 30:
            recommendations.append("Standard snow load provisions apply")

        return {
            **snow_data,
            "requires_engineered_design": requires_engineered_design,
            "winter_construction_premium_pct": winter_construction_premium,
            "recommendations": recommendations,
        }

"""LANDFIRE Fuel Model API connector.

LANDFIRE provides geospatial data on vegetation, wildland fire, and fuel characteristics.
The 40 Scott and Burgan Fire Behavior Fuel Models (FBFM40) classify fuels by fire behavior.

API Documentation: https://www.landfire.gov/
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager

logger = logging.getLogger(__name__)


class LANDFIREFuelConnector(APIConnector):
    """
    LANDFIRE Fuel Model connector.

    Provides Scott and Burgan Fire Behavior Fuel Models (FBFM40) data
    for wildfire risk assessment.
    """

    # LANDFIRE WCS/WMS endpoint (simplified - real implementation would use actual service)
    DEFAULT_BASE_URL = "https://landfire.gov/arcgis/rest/services"

    # Simplified fuel model categories (FBFM40)
    FUEL_MODELS = {
        # Grass and Grass-dominated (1-9)
        1: {
            "name": "Short Grass",
            "category": "grass",
            "fire_intensity": "low",
            "rate_of_spread": "very_fast",
            "risk_score": 35,
        },
        2: {
            "name": "Timber Grass and Understory",
            "category": "grass",
            "fire_intensity": "moderate",
            "rate_of_spread": "fast",
            "risk_score": 50,
        },
        3: {
            "name": "Tall Grass",
            "category": "grass",
            "fire_intensity": "high",
            "rate_of_spread": "very_fast",
            "risk_score": 65,
        },
        # Shrub (5-7)
        5: {
            "name": "Brush",
            "category": "shrub",
            "fire_intensity": "high",
            "rate_of_spread": "fast",
            "risk_score": 75,
        },
        6: {
            "name": "Dormant Brush",
            "category": "shrub",
            "fire_intensity": "moderate",
            "rate_of_spread": "moderate",
            "risk_score": 60,
        },
        7: {
            "name": "Southern Rough",
            "category": "shrub",
            "fire_intensity": "very_high",
            "rate_of_spread": "fast",
            "risk_score": 85,
        },
        # Timber Litter (8-10)
        8: {
            "name": "Closed Timber Litter",
            "category": "timber",
            "fire_intensity": "low",
            "rate_of_spread": "slow",
            "risk_score": 40,
        },
        9: {
            "name": "Hardwood Litter",
            "category": "timber",
            "fire_intensity": "moderate",
            "rate_of_spread": "moderate",
            "risk_score": 45,
        },
        10: {
            "name": "Timber Litter and Understory",
            "category": "timber",
            "fire_intensity": "moderate",
            "rate_of_spread": "moderate",
            "risk_score": 55,
        },
        # Slash (11-13)
        11: {
            "name": "Light Logging Slash",
            "category": "slash",
            "fire_intensity": "moderate",
            "rate_of_spread": "moderate",
            "risk_score": 60,
        },
        12: {
            "name": "Medium Logging Slash",
            "category": "slash",
            "fire_intensity": "high",
            "rate_of_spread": "fast",
            "risk_score": 75,
        },
        13: {
            "name": "Heavy Logging Slash",
            "category": "slash",
            "fire_intensity": "very_high",
            "rate_of_spread": "moderate",
            "risk_score": 90,
        },
    }

    # Simplified fuel model lookup by region and vegetation
    REGIONAL_FUEL_MODELS: Dict[str, Dict[str, int]] = {
        "CO": {  # Colorado
            "high_elevation": 8,  # Closed timber
            "mid_elevation": 10,  # Timber with understory
            "foothills": 5,  # Brush/chaparral
            "plains": 1,  # Short grass
        },
        "UT": {  # Utah
            "forest": 9,  # Hardwood/conifer mix
            "shrubland": 6,  # Dormant brush/sagebrush
            "desert": 1,  # Sparse grass
        },
        "ID": {  # Idaho
            "forest": 10,  # Timber with understory
            "rangeland": 2,  # Timber grass
            "southern_desert": 1,  # Short grass
        },
    }

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        cache_ttl_days: int = 365,  # Fuel models rarely change
        cache_manager: CacheManager | None = None,
    ) -> None:
        """
        Initialize LANDFIRE Fuel Model connector.

        Args:
            base_url: LANDFIRE WCS/WMS endpoint
            cache_ttl_days: Cache TTL in days (default: 365)
            cache_manager: Optional cache manager instance
        """
        super().__init__(
            api_key="",  # No API key needed
            base_url=base_url,
            cache_ttl_days=cache_ttl_days,
            cache_manager=cache_manager,
        )

    def _load_api_key(self) -> str | None:
        """No API key needed for LANDFIRE."""
        return None

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Query LANDFIRE for fuel model at location.

        Args:
            params: Query parameters including:
                    - 'latitude': Location latitude
                    - 'longitude': Location longitude
                    - 'elevation_ft': Optional elevation in feet

        Returns:
            Fuel model data

        Note:
            Real implementation would query LANDFIRE WCS/WMS service.
            This implementation uses simplified regional lookup.
        """
        latitude = params.get("latitude", 40.0)
        longitude = params.get("longitude", -105.0)
        elevation_ft = params.get("elevation_ft", 5000)

        # Determine state from longitude
        if -109.05 <= longitude <= -102.05:
            state = "CO"
        elif -114.05 <= longitude <= -109.05:
            state = "UT"
        elif -117.24 <= longitude <= -111.05:
            state = "ID"
        else:
            state = "CO"  # Default

        # Determine vegetation type from elevation
        if state == "CO":
            if elevation_ft > 9000:
                veg_type = "high_elevation"
            elif elevation_ft > 7000:
                veg_type = "mid_elevation"
            elif elevation_ft > 5500:
                veg_type = "foothills"
            else:
                veg_type = "plains"
        elif state == "UT":
            if elevation_ft > 7000:
                veg_type = "forest"
            elif elevation_ft > 4500:
                veg_type = "shrubland"
            else:
                veg_type = "desert"
        else:  # Idaho
            if elevation_ft > 6000:
                veg_type = "forest"
            elif elevation_ft > 4000:
                veg_type = "rangeland"
            else:
                veg_type = "southern_desert"

        # Get fuel model
        fuel_model = self.REGIONAL_FUEL_MODELS.get(state, {}).get(veg_type, 2)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "state": state,
            "vegetation_type": veg_type,
            "fuel_model": fuel_model,
            "elevation_ft": elevation_ft,
        }

    def parse(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse fuel model query result.

        Args:
            response: Raw fuel model query result

        Returns:
            Structured fuel model data
        """
        fuel_model = response.get("fuel_model", 2)
        model_info = self.FUEL_MODELS.get(fuel_model, self.FUEL_MODELS[2])

        return {
            "latitude": response["latitude"],
            "longitude": response["longitude"],
            "fuel_model": fuel_model,
            "fuel_model_name": model_info["name"],
            "fuel_category": model_info["category"],
            "fire_intensity": model_info["fire_intensity"],
            "rate_of_spread": model_info["rate_of_spread"],
            "fuel_score": model_info["risk_score"],
            "vegetation_type": response.get("vegetation_type"),
            "data_source": "LANDFIRE FBFM40",
        }

    def get_fuel_model(
        self, latitude: float, longitude: float, elevation_ft: float = 5000
    ) -> Dict[str, Any]:
        """
        Get fuel model for a location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            elevation_ft: Site elevation in feet

        Returns:
            Dictionary with fuel model data
        """
        cache_key = f"landfire_fuel_{latitude}_{longitude}_{elevation_ft}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for LANDFIRE fuel: {cache_key}")
                return cached  # type: ignore[return-value]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "elevation_ft": elevation_ft,
        }

        response = self.fetch(params)
        parsed_data = self.parse(response)

        if self.cache:
            self.cache.set(cache_key, parsed_data, ttl=self.cache_ttl)

        return parsed_data

    def assess_fuel_risk(
        self, latitude: float, longitude: float, elevation_ft: float = 5000
    ) -> Dict[str, Any]:
        """
        Comprehensive fuel model risk assessment.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            elevation_ft: Site elevation in feet

        Returns:
            Dictionary with fuel risk assessment
        """
        fuel_data = self.get_fuel_model(latitude, longitude, elevation_ft)

        fuel_score = fuel_data["fuel_score"]
        fuel_category = fuel_data["fuel_category"]
        fire_intensity = fuel_data["fire_intensity"]
        rate_of_spread = fuel_data["rate_of_spread"]

        # Determine overall risk level
        if fuel_score >= 80:
            risk_level = "extreme"
        elif fuel_score >= 60:
            risk_level = "high"
        elif fuel_score >= 40:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Fuel treatment recommendations
        recommendations = []
        if fuel_category == "slash":
            recommendations.extend(
                [
                    "Remove or reduce slash accumulation",
                    "Consider prescribed burning",
                    "Chip or masticate woody debris",
                ]
            )
        elif fuel_category == "shrub" and fuel_score >= 70:
            recommendations.extend(
                [
                    "Reduce shrub density through thinning",
                    "Create fuel breaks around structures",
                    "Maintain defensible space aggressively",
                ]
            )
        elif fuel_category == "timber" and fuel_score >= 50:
            recommendations.extend(
                [
                    "Thin understory vegetation",
                    "Prune ladder fuels",
                    "Maintain forest health",
                ]
            )
        elif fuel_category == "grass":
            recommendations.extend(
                [
                    "Mow or graze to reduce fuel load",
                    "Create firebreaks",
                    "Maintain irrigation if possible",
                ]
            )

        # Fire behavior notes
        if rate_of_spread in ["very_fast", "fast"]:
            behavior_note = (
                "Rapid fire spread expected; early detection and evacuation critical"
            )
        else:
            behavior_note = "Slower fire spread allows more suppression time"

        if fire_intensity in ["very_high", "high"]:
            intensity_note = "High flame lengths; difficult direct attack"
        else:
            intensity_note = "Lower flame lengths; direct attack feasible"

        return {
            **fuel_data,
            "risk_level": risk_level,
            "behavior_note": behavior_note,
            "intensity_note": intensity_note,
            "recommendations": recommendations,
        }

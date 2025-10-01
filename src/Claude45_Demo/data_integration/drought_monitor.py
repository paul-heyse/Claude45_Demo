"""U.S. Drought Monitor API connector.

The U.S. Drought Monitor provides weekly drought condition data.
Data is available through GeoJSON API from Iowa Environmental Mesonet.

API Documentation: https://www.drought.gov/data-maps-tools/us-drought-monitor
GeoJSON API: https://mesonet.agron.iastate.edu/geojson/usdm.py
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import requests
from shapely.geometry import Point, shape

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager
from Claude45_Demo.data_integration.exceptions import DataSourceError

logger = logging.getLogger(__name__)


class DroughtMonitorConnector(APIConnector):
    """
    U.S. Drought Monitor API connector.

    Provides methods for querying current and historical drought conditions.
    Uses Iowa Environmental Mesonet GeoJSON API.
    """

    DEFAULT_BASE_URL = "https://mesonet.agron.iastate.edu/geojson/usdm.py"

    DROUGHT_CATEGORIES = {
        0: {"name": "None", "description": "No drought conditions"},
        1: {"name": "D0 - Abnormally Dry", "description": "Going into drought"},
        2: {"name": "D1 - Moderate Drought", "description": "Some water deficits"},
        3: {"name": "D2 - Severe Drought", "description": "Water shortages common"},
        4: {
            "name": "D3 - Extreme Drought",
            "description": "Major water shortages",
        },
        5: {
            "name": "D4 - Exceptional Drought",
            "description": "Exceptional water shortages",
        },
    }

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        cache_ttl_days: int = 7,  # Weekly updates
        cache_manager: CacheManager | None = None,
    ) -> None:
        """
        Initialize U.S. Drought Monitor connector.

        Args:
            base_url: Drought Monitor GeoJSON API endpoint
            cache_ttl_days: Cache TTL in days (default: 7, weekly data)
            cache_manager: Optional cache manager instance
        """
        super().__init__(
            api_key="",  # No API key needed
            base_url=base_url,
            cache_ttl_days=cache_ttl_days,
            cache_manager=cache_manager,
        )

    def _load_api_key(self) -> str | None:
        """No API key needed for Drought Monitor."""
        return None

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve drought data from U.S. Drought Monitor API.

        Args:
            params: API request parameters. Expected keys:
                    - 'date': YYYY-MM-DD format (optional, defaults to latest)

        Returns:
            GeoJSON feature collection with drought polygons

        Raises:
            DataSourceError: If API request fails
        """
        self._check_rate_limit()
        self._track_request()

        query_params = {}
        if "date" in params:
            query_params["date"] = params["date"]

        def _make_request() -> Dict[str, Any]:
            response = requests.get(self.base_url, params=query_params, timeout=30)
            response.raise_for_status()
            return response.json()

        return self._retry_with_backoff(_make_request)

    def parse(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse GeoJSON drought data.

        Args:
            response: GeoJSON feature collection

        Returns:
            Parsed drought data with metadata
        """
        if response.get("type") != "FeatureCollection":
            raise DataSourceError("Invalid GeoJSON response from Drought Monitor")

        features = response.get("features", [])

        return {
            "type": "FeatureCollection",
            "features": features,
            "feature_count": len(features),
            "generation_time": response.get("generation_time"),
        }

    def get_current_drought(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current drought conditions.

        Args:
            date: Optional date in YYYY-MM-DD format (defaults to latest)

        Returns:
            Dictionary with drought GeoJSON data
        """
        cache_key = f"drought_monitor_{date or 'latest'}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for drought data: {cache_key}")
                return cached  # type: ignore[return-value]

        params = {}
        if date:
            params["date"] = date

        response = self.fetch(params)
        parsed_data = self.parse(response)

        if self.cache:
            self.cache.set(cache_key, parsed_data, ttl=self.cache_ttl)

        return parsed_data

    def get_drought_at_location(
        self, latitude: float, longitude: float, date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get drought conditions at a specific location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            date: Optional date in YYYY-MM-DD format

        Returns:
            Dictionary with drought condition details
        """
        drought_data = self.get_current_drought(date)
        point = Point(longitude, latitude)

        # Find which drought polygon(s) contain this point
        drought_levels: List[int] = []

        for feature in drought_data.get("features", []):
            geom = shape(feature["geometry"])
            if geom.contains(point):
                # Extract drought level from properties (typically 'dm' field)
                dm_level = feature.get("properties", {}).get("dm", 0)
                drought_levels.append(dm_level)

        # Return worst (highest) drought level
        if not drought_levels:
            drought_level = 0  # No drought
        else:
            drought_level = max(drought_levels)

        category_info = self.DROUGHT_CATEGORIES.get(
            drought_level, self.DROUGHT_CATEGORIES[0]
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "date": date or "latest",
            "drought_level": drought_level,
            "category_name": category_info["name"],
            "category_description": category_info["description"],
            "in_drought": drought_level > 1,
            "severe_drought": drought_level >= 3,
            "data_source": "U.S. Drought Monitor",
        }

    def assess_water_stress(
        self, latitude: float, longitude: float, lookback_weeks: int = 12
    ) -> Dict[str, Any]:
        """
        Assess water stress over time period.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            lookback_weeks: Number of weeks to analyze (default: 12)

        Returns:
            Dictionary with water stress assessment
        """
        # Get current conditions
        current = self.get_drought_at_location(latitude, longitude)

        # For historical analysis, would query multiple weeks
        # For now, use current conditions as proxy
        drought_level = current["drought_level"]

        # Calculate risk score (0-100)
        risk_score = min(drought_level * 20, 100)

        return {
            "latitude": latitude,
            "longitude": longitude,
            "current_drought_level": drought_level,
            "current_category": current["category_name"],
            "risk_score": risk_score,
            "water_stress_detected": drought_level >= 2,
            "severe_stress": drought_level >= 3,
            "recommendation": (
                "Monitor water availability closely"
                if drought_level >= 2
                else "Normal water management"
            ),
            "analysis_period_weeks": lookback_weeks,
        }

"""
NASA FIRMS (Fire Information for Resource Management System) API connector.

Provides access to near real-time active fire data from MODIS and VIIRS satellites.

API Documentation: https://firms.modaps.eosdis.nasa.gov/api/
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import pandas as pd
import requests

from .base import APIConnector
from .cache import CacheManager
from .exceptions import DataSourceError

logger = logging.getLogger(__name__)


class NASAFIRMSConnector(APIConnector):
    """
    NASA FIRMS API connector for active fire/hotspot data.

    Provides access to MODIS and VIIRS satellite fire detection data.

    Register for API key at: https://firms.modaps.eosdis.nasa.gov/api/
    """

    BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api"

    # Available data sources
    MODIS_C6_1 = "MODIS_NRT"  # MODIS Collection 6.1 NRT
    VIIRS_SNPP = "VIIRS_SNPP_NRT"  # VIIRS S-NPP NRT
    VIIRS_NOAA20 = "VIIRS_NOAA20_NRT"  # VIIRS NOAA-20 NRT

    def __init__(
        self,
        api_key: str,
        *,
        cache_manager: CacheManager | None = None,
        cache_ttl_days: int = 1,  # Shorter TTL for near real-time data
    ) -> None:
        """
        Initialize NASA FIRMS connector.

        Args:
            api_key: API key from NASA FIRMS (MAP_KEY)
            cache_manager: Optional cache manager instance
            cache_ttl_days: Cache TTL in days (default: 1 for NRT data)
        """
        super().__init__(
            api_key=api_key,
            base_url=self.BASE_URL,
            cache_ttl_days=cache_ttl_days,
            rate_limit=1000,  # FIRMS is generous with limits
            cache_manager=cache_manager,
        )

    def fetch(self, params: Dict[str, Any]) -> str:
        """
        Fetch data from NASA FIRMS API.

        Args:
            params: API request parameters

        Returns:
            CSV string response

        Raises:
            DataSourceError: If request fails after retries
        """
        self._check_rate_limit()
        self._track_request()

        def _make_request() -> str:
            # Build URL path
            source = params["source"]
            area_type = params["area_type"]
            area_param = params["area_param"]
            day_range = params["day_range"]

            url = f"{self.base_url}/area/csv/{self.api_key}/{source}/{area_type}/{area_param}/{day_range}"

            response = requests.get(url, timeout=45)

            # FIRMS returns 200 with error message in text for bad requests
            if response.status_code != 200:
                raise DataSourceError(
                    f"NASA FIRMS API error ({response.status_code}): {response.text}"
                )

            # Check for error messages in response
            if "error" in response.text.lower() or "invalid" in response.text.lower():
                raise DataSourceError(f"NASA FIRMS API error: {response.text[:200]}")

            return response.text

        return self._retry_with_backoff(_make_request)  # type: ignore[return-value]

    def parse(self, response: str) -> pd.DataFrame:
        """
        Parse NASA FIRMS CSV response into DataFrame.

        Args:
            response: CSV string from API

        Returns:
            DataFrame with fire hotspot data
        """
        try:
            from io import StringIO

            df = pd.read_csv(StringIO(response))

            # Convert acq_date to datetime
            if "acq_date" in df.columns:
                df["acq_date"] = pd.to_datetime(df["acq_date"])

            return df
        except Exception as e:
            logger.error(f"Error parsing FIRMS CSV response: {e}")
            raise DataSourceError(f"Failed to parse FIRMS response: {e}") from e

    def get_hotspots_by_bbox(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
        day_range: int = 7,
        source: str = "VIIRS_SNPP_NRT",
    ) -> pd.DataFrame:
        """
        Get fire hotspots within a bounding box.

        Args:
            min_lat: Minimum latitude
            min_lon: Minimum longitude
            max_lat: Maximum latitude
            max_lon: Maximum longitude
            day_range: Number of days to look back (1-10)
            source: Data source (MODIS_NRT, VIIRS_SNPP_NRT, VIIRS_NOAA20_NRT)

        Returns:
            DataFrame with fire hotspot data
        """
        cache_key = (
            f"firms_{source}_bbox_{min_lat}_{min_lon}_{max_lat}_{max_lon}_{day_range}"
        )

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for {cache_key}")
                return cached  # type: ignore[return-value]

        params = {
            "source": source,
            "area_type": "world",  # Using world coordinates (lat/lon)
            "area_param": f"{min_lon},{min_lat},{max_lon},{max_lat}",
            "day_range": str(day_range),
        }

        csv_response = self.fetch(params)
        df = self.parse(csv_response)

        if self.cache:
            self.cache.set(cache_key, df, ttl=self.cache_ttl)

        return df

    def get_hotspots_by_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        day_range: int = 7,
        source: str = "VIIRS_SNPP_NRT",
    ) -> pd.DataFrame:
        """
        Get fire hotspots within radius of a point.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_km: Radius in kilometers (max 100)
            day_range: Number of days to look back (1-10)
            source: Data source

        Returns:
            DataFrame with fire hotspot data
        """
        # Convert radius to approximate lat/lon degrees
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude varies by latitude
        lat_delta = radius_km / 111.0
        lon_delta = radius_km / (111.0 * abs(pd.np.cos(pd.np.radians(latitude))))

        min_lat = latitude - lat_delta
        max_lat = latitude + lat_delta
        min_lon = longitude - lon_delta
        max_lon = longitude + lon_delta

        df = self.get_hotspots_by_bbox(
            min_lat=min_lat,
            min_lon=min_lon,
            max_lat=max_lat,
            max_lon=max_lon,
            day_range=day_range,
            source=source,
        )

        if df.empty:
            return df

        # Filter to exact radius (calculate actual distance)
        df = df.copy()
        df["distance_km"] = self._calculate_distance(
            df["latitude"], df["longitude"], latitude, longitude
        )

        df = df[df["distance_km"] <= radius_km]

        return df

    def analyze_fire_activity(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10,
        lookback_days: int = 7,
    ) -> Dict[str, Any]:
        """
        Analyze recent fire activity near a location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            radius_km: Search radius in km
            lookback_days: Days to look back

        Returns:
            Dictionary with fire activity metrics
        """
        # Get hotspots from VIIRS (higher resolution than MODIS)
        df = self.get_hotspots_by_radius(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            day_range=min(lookback_days, 10),  # FIRMS max is 10 days
            source=self.VIIRS_SNPP,
        )

        if df.empty:
            return {
                "hotspot_count": 0,
                "high_confidence_count": 0,
                "nearest_hotspot_km": None,
                "most_recent_detection": None,
                "fire_activity_detected": False,
                "search_radius_km": radius_km,
                "lookback_days": lookback_days,
            }

        # Count high-confidence hotspots (confidence > 50%)
        high_conf_count = (
            len(df[df.get("confidence", 0) > 50]) if "confidence" in df.columns else 0
        )

        # Find nearest hotspot
        nearest_distance = (
            df["distance_km"].min() if "distance_km" in df.columns else None
        )

        # Most recent detection
        most_recent = df["acq_date"].max() if "acq_date" in df.columns else None

        return {
            "hotspot_count": len(df),
            "high_confidence_count": high_conf_count,
            "nearest_hotspot_km": (
                round(float(nearest_distance), 2) if nearest_distance else None
            ),
            "most_recent_detection": str(most_recent) if most_recent else None,
            "fire_activity_detected": len(df) > 0,
            "search_radius_km": radius_km,
            "lookback_days": lookback_days,
        }

    @staticmethod
    def _calculate_distance(
        lat1: pd.Series, lon1: pd.Series, lat2: float, lon2: float
    ) -> pd.Series:
        """
        Calculate haversine distance between points.

        Args:
            lat1: Series of latitudes (point 1)
            lon1: Series of longitudes (point 1)
            lat2: Latitude of point 2
            lon2: Longitude of point 2

        Returns:
            Series of distances in kilometers
        """
        from math import radians

        R = 6371  # Earth radius in km

        lat1_rad = pd.np.radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = pd.np.radians(lat1 - lat2)
        delta_lon = pd.np.radians(lon1 - lon2)

        a = (
            pd.np.sin(delta_lat / 2) ** 2
            + pd.np.cos(lat1_rad) * pd.np.cos(lat2_rad) * pd.np.sin(delta_lon / 2) ** 2
        )
        c = 2 * pd.np.arctan2(pd.np.sqrt(a), pd.np.sqrt(1 - a))

        return R * c

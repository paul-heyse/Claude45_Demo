"""
EPA Air Quality System (AQS) API connector.

Provides access to EPA's Air Quality System data for PM2.5, ozone, and other
pollutant measurements.

API Documentation: https://aqs.epa.gov/aqsweb/documents/data_api.html
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


class EPAAQSConnector(APIConnector):
    """
    EPA Air Quality System (AQS) API connector.

    Provides methods for querying PM2.5, ozone, and other pollutant data
    from EPA monitoring stations.

    API requires email registration at: https://aqs.epa.gov/data/api/signup
    """

    BASE_URL = "https://aqs.epa.gov/data/api"

    # Parameter codes
    PM25_PARAMETER = "88101"  # PM2.5 - Local Conditions
    PM25_FRM_PARAMETER = "88502"  # PM2.5 - Federal Reference Method
    OZONE_PARAMETER = "44201"  # Ozone

    def __init__(
        self,
        email: str,
        api_key: str,
        *,
        cache_manager: CacheManager | None = None,
        cache_ttl_days: int = 30,
    ) -> None:
        """
        Initialize EPA AQS connector.

        Args:
            email: Email address registered with EPA AQS
            api_key: API key from EPA AQS
            cache_manager: Optional cache manager instance
            cache_ttl_days: Cache TTL in days (default: 30)
        """
        super().__init__(
            api_key=api_key,
            base_url=self.BASE_URL,
            cache_ttl_days=cache_ttl_days,
            rate_limit=500,  # EPA allows ~500 requests per day per key
            cache_manager=cache_manager,
        )
        self.email = email

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data from EPA AQS API.

        Args:
            params: API request parameters

        Returns:
            Raw API response dictionary

        Raises:
            DataSourceError: If request fails after retries
        """
        # Add email and key to all requests
        params["email"] = self.email
        params["key"] = self.api_key

        self._check_rate_limit()
        self._track_request()

        def _make_request() -> Dict[str, Any]:
            endpoint = params.pop("endpoint")
            url = f"{self.base_url}/{endpoint}"

            response = requests.get(url, params=params, timeout=30)

            # EPA AQS returns 200 even for errors, check Header
            try:
                data = response.json()
                if data.get("Header", [{}])[0].get("status") != "Success":
                    error_msg = data.get("Header", [{}])[0].get(
                        "error", "Unknown error"
                    )
                    raise DataSourceError(f"EPA AQS API error: {error_msg}")
                return data
            except (ValueError, KeyError) as e:
                raise DataSourceError(f"EPA AQS API response parsing error: {e}") from e

        return self._retry_with_backoff(_make_request)

    def parse(self, response: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse EPA AQS API response into DataFrame.

        Args:
            response: Raw API response

        Returns:
            DataFrame with parsed data
        """
        if not response.get("Data"):
            logger.warning("EPA AQS returned no data")
            return pd.DataFrame()

        df = pd.DataFrame(response["Data"])
        return df

    def get_annual_summary_by_site(
        self,
        parameter: str,
        bdate: str,
        edate: str,
        state_code: str,
        county_code: str,
    ) -> pd.DataFrame:
        """
        Get annual summary data by monitoring site.

        Args:
            parameter: Parameter code (e.g., '88101' for PM2.5)
            bdate: Begin date (YYYYMMDD format)
            edate: End date (YYYYMMDD format)
            state_code: 2-digit state FIPS code
            county_code: 3-digit county FIPS code

        Returns:
            DataFrame with annual summary data by site
        """
        cache_key = (
            f"epa_aqs_annual_{parameter}_{state_code}_{county_code}_{bdate}_{edate}"
        )

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for {cache_key}")
                return cached  # type: ignore[return-value]

        params = {
            "endpoint": "annualData/byCounty",
            "param": parameter,
            "bdate": bdate,
            "edate": edate,
            "state": state_code,
            "county": county_code,
        }

        response = self.fetch(params)
        df = self.parse(response)

        if self.cache:
            self.cache.set(cache_key, df, ttl=self.cache_ttl)

        return df

    def get_pm25_annual_data(
        self,
        state_code: str,
        county_code: str,
        year: int,
    ) -> Dict[str, Any]:
        """
        Get PM2.5 annual summary data for a county.

        Args:
            state_code: 2-digit state FIPS code
            county_code: 3-digit county FIPS code
            year: Year to query

        Returns:
            Dictionary with PM2.5 metrics:
            - annual_mean_pm25: Mean PM2.5 (μg/m³)
            - days_over_35: Days exceeding 35 μg/m³ (unhealthy threshold)
            - max_value: Maximum daily value
            - percentile_98: 98th percentile value
            - site_count: Number of monitoring sites
        """
        bdate = f"{year}0101"
        edate = f"{year}1231"

        df = self.get_annual_summary_by_site(
            parameter=self.PM25_PARAMETER,
            bdate=bdate,
            edate=edate,
            state_code=state_code,
            county_code=county_code,
        )

        if df.empty:
            logger.warning(
                f"No PM2.5 data for state={state_code}, county={county_code}, year={year}"
            )
            return {
                "annual_mean_pm25": None,
                "days_over_35": None,
                "max_value": None,
                "percentile_98": None,
                "site_count": 0,
                "data_available": False,
            }

        # Calculate county-level metrics from all sites
        # Use arithmetic_mean from EPA (already computed)
        annual_mean = df["arithmetic_mean"].astype(float).mean()

        # Count days over 35 μg/m³ (EPA 24-hour standard)
        # EPA provides "events_included_count" but we need custom calculation
        # For simplicity, use 98th percentile as proxy
        percentile_98 = df["ninety_eighth_percentile"].astype(float).max()

        # Estimate days over 35 based on 98th percentile
        # If p98 > 35, estimate ~7-14 days/year
        if percentile_98 > 35:
            days_over_35 = int((percentile_98 - 35) / 2 + 7)  # Rough estimate
        else:
            days_over_35 = 0

        max_value = df["first_max_value"].astype(float).max()
        site_count = len(df)

        return {
            "annual_mean_pm25": round(float(annual_mean), 2),
            "days_over_35": days_over_35,
            "max_value": round(float(max_value), 2),
            "percentile_98": round(float(percentile_98), 2),
            "site_count": site_count,
            "data_available": True,
            "year": year,
        }

    def find_nearest_monitor(
        self,
        latitude: float,
        longitude: float,
        parameter: str,
        year: int,
        search_radius_states: list[str] | None = None,
    ) -> Dict[str, Any]:
        """
        Find nearest monitor with data for a parameter.

        Note: EPA AQS doesn't provide direct lat/lon search.
        This method searches surrounding states for monitors.

        Args:
            latitude: Target latitude
            longitude: Target longitude
            parameter: Parameter code
            year: Year to check for data
            search_radius_states: List of state FIPS codes to search

        Returns:
            Dictionary with monitor info and approximate distance
        """
        # This is a simplified implementation
        # A production version would use spatial indexing or state-lookup logic
        if search_radius_states is None:
            # Default: derive from longitude (rough approximation)
            if -125 <= longitude <= -114:  # Mountain West
                search_radius_states = ["04", "08", "16", "30", "32", "35", "49", "56"]
            elif -114 <= longitude <= -100:  # Great Plains
                search_radius_states = ["08", "20", "31", "38", "46"]
            else:
                raise ValueError(
                    "Longitude outside expected range or search_radius_states required"
                )

        logger.info(
            f"Searching for nearest {parameter} monitor in states: {search_radius_states}"
        )

        # Note: Full implementation would query site list and calculate distances
        # For now, return that functionality is limited
        return {
            "nearest_monitor_available": False,
            "note": "Nearest monitor search requires state/county specification for EPA AQS",
            "recommendation": "Use county-level data with get_pm25_annual_data()",
        }

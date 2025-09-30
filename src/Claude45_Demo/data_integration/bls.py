"""
Bureau of Labor Statistics (BLS) API connector.

Integrates with BLS public API v2 to retrieve:
- QCEW (Quarterly Census of Employment and Wages) - employment and wages by industry
- LAUS (Local Area Unemployment Statistics) - unemployment rates
- CES (Current Employment Statistics) - employment data

API Documentation: https://www.bls.gov/developers/api_signature_v2.htm
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

from .base import APIConnector
from .cache import CacheManager
from .exceptions import ConfigurationError, ValidationError

logger = logging.getLogger(__name__)


class BLSConnector(APIConnector):
    """
    Connector for Bureau of Labor Statistics APIs.

    Supports QCEW, LAUS, and CES data retrieval with caching.
    Rate limit: 500 requests/day with registered API key.
    """

    def __init__(
        self,
        api_key: Optional[str],
        cache_manager: CacheManager,
        cache_ttl_days: int = 7,
    ):
        """
        Initialize BLS connector.

        Args:
            api_key: BLS API v2 registration key (required)
            cache_manager: Cache manager instance
            cache_ttl_days: Cache TTL in days (default: 7 for economic data)

        Raises:
            ConfigurationError: If API key is not provided
        """
        if not api_key:
            raise ConfigurationError("BLS API key is required")

        super().__init__(
            api_key=api_key,
            base_url="https://api.bls.gov/publicAPI/v2/timeseries/data/",
            cache_ttl_days=cache_ttl_days,
            rate_limit=500,
        )
        self.cache = cache_manager

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data from BLS API.

        Args:
            params: API request parameters

        Returns:
            Raw API response dictionary

        Raises:
            DataSourceError: If request fails after retries
        """
        self._check_rate_limit()
        self._track_request()

        def _make_request() -> Dict[str, Any]:
            response = requests.post(
                self.base_url,
                json=params,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

        return self._retry_with_backoff(_make_request)

    def parse(self, response: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse BLS API response into DataFrame.

        Args:
            response: Raw BLS API response

        Returns:
            Parsed data as DataFrame

        Raises:
            ValidationError: If response format is invalid
        """
        # Validate response structure
        if "status" not in response:
            raise ValidationError("Invalid BLS response: missing 'status' field")

        if response["status"] != "REQUEST_SUCCEEDED":
            error_msg = response.get("message", ["Unknown error"])[0]
            raise ValidationError(f"BLS API error: {error_msg}")

        if "Results" not in response or "series" not in response["Results"]:
            raise ValidationError("Invalid BLS response: missing 'Results' or 'series'")

        # Parse series data
        all_data = []
        for series in response["Results"]["series"]:
            series_id = series.get("seriesID", "unknown")
            for datapoint in series.get("data", []):
                all_data.append(
                    {
                        "series_id": series_id,
                        "year": int(datapoint["year"]),
                        "period": datapoint["period"],
                        "period_name": datapoint["periodName"],
                        "value": float(datapoint["value"]),
                    }
                )

        if not all_data:
            logger.warning("No data returned from BLS API")
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        logger.info(f"Parsed {len(df)} rows from BLS response")
        return df

    def fetch_qcew_employment(
        self,
        area_code: str,
        naics_codes: List[str],
        start_year: int,
        end_year: int,
    ) -> pd.DataFrame:
        """
        Fetch QCEW employment data by NAICS industry code.

        Args:
            area_code: Area FIPS code (e.g., "08031" for Denver County)
            naics_codes: List of NAICS codes (e.g., ["10"] for total, ["5415"] for tech)
            start_year: Start year for data
            end_year: End year for data

        Returns:
            DataFrame with employment data by year and NAICS code

        Example:
            >>> connector = BLSConnector(api_key="...", cache=cache)
            >>> df = connector.fetch_qcew_employment(
            ...     area_code="08031",
            ...     naics_codes=["5415"],  # Computer systems design
            ...     start_year=2019,
            ...     end_year=2021
            ... )
        """
        cache_key = (
            f"bls_qcew_{area_code}_{'_'.join(naics_codes)}_{start_year}_{end_year}"
        )

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"Cache hit for {cache_key}")
            return cached

        # Build series IDs for QCEW
        # Format: ENUAAAA00BB0CC (AA=area, BB=naics, CC=data type)
        series_ids = [f"ENU{area_code}0{naics}010" for naics in naics_codes]

        params = {
            "seriesid": series_ids,
            "startyear": str(start_year),
            "endyear": str(end_year),
            "registrationkey": self.api_key,
        }

        response = self.fetch(params)
        df = self.parse(response)

        # Cache result
        self.cache.set(cache_key, df, ttl=self.cache_ttl)

        return df

    def fetch_laus_unemployment(
        self, area_code: str, start_year: int, end_year: int
    ) -> pd.DataFrame:
        """
        Fetch LAUS unemployment rate data.

        Args:
            area_code: LAUS area code (e.g., "CN0803100000000" for Denver County)
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with monthly unemployment rates

        Example:
            >>> connector = BLSConnector(api_key="...", cache=cache)
            >>> df = connector.fetch_laus_unemployment(
            ...     area_code="CN0803100000000",  # Denver County
            ...     start_year=2022,
            ...     end_year=2023
            ... )
        """
        cache_key = f"bls_laus_{area_code}_{start_year}_{end_year}"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info(f"Cache hit for {cache_key}")
            return cached

        # LAUS series ID format: LAUAAAAAAAAAAAA03 (unemployment rate)
        series_id = f"LAU{area_code}03"

        params = {
            "seriesid": [series_id],
            "startyear": str(start_year),
            "endyear": str(end_year),
            "registrationkey": self.api_key,
        }

        response = self.fetch(params)
        df = self.parse(response)

        # Cache result
        self.cache.set(cache_key, df, ttl=self.cache_ttl)

        return df

    def calculate_location_quotient(
        self, area_code: str, naics_code: str, reference_area: str, year: int
    ) -> float:
        """
        Calculate Location Quotient (LQ) for an industry sector.

        LQ = (Local employment in sector / Local total employment) /
             (National employment in sector / National total employment)

        Args:
            area_code: Local area FIPS code
            naics_code: NAICS industry code
            reference_area: Reference area (typically "US000" for national)
            year: Year for calculation

        Returns:
            Location Quotient (LQ > 1.0 indicates specialization)
        """
        # Fetch local data
        local_sector = self.fetch_qcew_employment(
            area_code=area_code,
            naics_codes=[naics_code],
            start_year=year,
            end_year=year,
        )

        local_total = self.fetch_qcew_employment(
            area_code=area_code, naics_codes=["10"], start_year=year, end_year=year
        )

        # Fetch national data
        national_sector = self.fetch_qcew_employment(
            area_code=reference_area,
            naics_codes=[naics_code],
            start_year=year,
            end_year=year,
        )

        national_total = self.fetch_qcew_employment(
            area_code=reference_area, naics_codes=["10"], start_year=year, end_year=year
        )

        # Calculate LQ
        local_share = local_sector["value"].iloc[0] / local_total["value"].iloc[0]
        national_share = (
            national_sector["value"].iloc[0] / national_total["value"].iloc[0]
        )

        lq = local_share / national_share

        logger.info(f"Location Quotient for {area_code} NAICS {naics_code}: {lq:.2f}")
        return lq

    def calculate_cagr(self, df: pd.DataFrame, years: int) -> float:
        """
        Calculate Compound Annual Growth Rate (CAGR).

        Args:
            df: DataFrame with 'year' and 'value' columns
            years: Number of years for CAGR calculation

        Returns:
            CAGR as decimal (e.g., 0.05 for 5% annual growth)
        """
        df_sorted = df.sort_values("year")
        beginning_value = df_sorted["value"].iloc[0]
        ending_value = df_sorted["value"].iloc[-1]

        cagr = (ending_value / beginning_value) ** (1 / years) - 1

        logger.info(f"CAGR over {years} years: {cagr:.2%}")
        return cagr

    def calculate_moving_average(self, df: pd.DataFrame, window: int = 12) -> pd.Series:
        """
        Calculate moving average for time series data.

        Args:
            df: DataFrame with 'value' column
            window: Window size (default: 12 months)

        Returns:
            Series with moving average values
        """
        return df["value"].rolling(window=window).mean()

    def compare_unemployment_to_benchmarks(
        self,
        county_code: str,
        state_code: str,
        national_code: str,
        year: int,
    ) -> Dict[str, float]:
        """
        Compare county unemployment rate to state and national benchmarks.

        Args:
            county_code: County LAUS code
            state_code: State LAUS code
            national_code: National unemployment series ID
            year: Year for comparison

        Returns:
            Dictionary with county, state, and national rates
        """
        # Fetch all three datasets
        county_df = self.fetch_laus_unemployment(county_code, year, year)
        state_df = self.fetch_laus_unemployment(state_code, year, year)

        # National uses different series ID format
        params = {
            "seriesid": [national_code],
            "startyear": str(year),
            "endyear": str(year),
            "registrationkey": self.api_key,
        }
        national_response = self.fetch(params)
        national_df = self.parse(national_response)

        # Calculate averages
        county_rate = county_df["value"].mean()
        state_rate = state_df["value"].mean()
        national_rate = national_df["value"].mean()

        logger.info(
            f"Unemployment comparison - County: {county_rate:.1f}%, "
            f"State: {state_rate:.1f}%, National: {national_rate:.1f}%"
        )

        return {
            "county_rate": county_rate,
            "state_rate": state_rate,
            "national_rate": national_rate,
            "county_vs_state": county_rate - state_rate,
            "county_vs_national": county_rate - national_rate,
        }

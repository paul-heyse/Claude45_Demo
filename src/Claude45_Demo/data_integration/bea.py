"""Bureau of Economic Analysis (BEA) API connector.

Implements Requirement: BEA Economic Data Integration from data-integration spec.
Provides access to Regional GDP, Personal Income, and Compensation data.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Dict, List, Mapping

import pandas as pd
import requests

from .base import APIConnector
from .exceptions import ConfigurationError, DataSourceError

if TYPE_CHECKING:
    from .cache import CacheManager

logger = logging.getLogger(__name__)


class BEAConnector(APIConnector):
    """
    Connector for Bureau of Economic Analysis Regional API.

    Provides access to:
    - Regional GDP by industry (NAICS-based sectors)
    - Personal Income by geography
    - Compensation data at state and MSA levels

    API Documentation: https://apps.bea.gov/api/
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        cache_manager: CacheManager | None = None,
    ) -> None:
        """
        Initialize BEA connector.

        Args:
            api_key: BEA API key (or set BEA_API_KEY env var)
            cache_manager: Optional cache manager instance

        Raises:
            ConfigurationError: If API key is not provided
        """
        if not api_key:
            api_key = os.getenv("BEA_API_KEY")

        if not api_key:
            raise ConfigurationError(
                "BEA_API_KEY is required. Get one at: "
                "https://apps.bea.gov/api/signup/"
            )

        super().__init__(
            api_key=api_key,
            base_url="https://apps.bea.gov/api/data",
            cache_ttl_days=30,  # BEA data updates quarterly
            rate_limit=100,  # 100 requests per minute for registered keys
            cache_manager=cache_manager,
        )

    def _load_api_key(self) -> str | None:
        """Load BEA API key from environment."""
        return os.getenv("BEA_API_KEY")

    def fetch(self, params: Mapping[str, Any]) -> Dict[str, Any]:
        """
        Fetch data from BEA API.

        Args:
            params: Query parameters for BEA API

        Returns:
            Parsed JSON response

        Raises:
            DataSourceError: If API request fails
        """
        self._check_rate_limit()

        # Add required parameters
        full_params = {
            "UserID": self.api_key,
            "method": "GetData",
            "ResultFormat": "JSON",
            **params,
        }

        try:
            response = requests.get(self.base_url, params=full_params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Check for BEA API errors
            if "BEAAPI" in data and "Error" in data["BEAAPI"]:
                error_detail = data["BEAAPI"]["Error"].get("Detail", "Unknown error")
                raise DataSourceError(f"BEA API error: {error_detail}")

            self._track_request()
            return data

        except requests.exceptions.RequestException as exc:
            logger.error("BEA API request failed: %s", exc)
            raise DataSourceError(f"Failed to fetch BEA data: {exc}") from exc

    def parse(self, response: Dict[str, Any]) -> pd.DataFrame:
        """
        Parse BEA API response into DataFrame.

        Args:
            response: Raw BEA API JSON response

        Returns:
            DataFrame with BEA data

        Raises:
            DataSourceError: If response format is invalid
        """
        try:
            data = response["BEAAPI"]["Results"]["Data"]
            df = pd.DataFrame(data)

            # Convert DataValue to numeric
            if "DataValue" in df.columns:
                df["DataValue"] = pd.to_numeric(
                    df["DataValue"].str.replace(",", ""), errors="coerce"
                )

            return df

        except (KeyError, TypeError, AttributeError) as exc:
            logger.error("Failed to parse BEA response: %s", exc)
            raise DataSourceError(f"Invalid BEA API response format: {exc}") from exc

    def fetch_gdp_by_industry(
        self, geo_fips: str, years: List[int], table_name: str = "SAGDP2N"
    ) -> pd.DataFrame:
        """
        Fetch GDP by industry for a state or MSA.

        Implements Scenario: GDP by industry query from spec.

        Args:
            geo_fips: Geographic FIPS code (state or MSA)
            years: List of years to retrieve
            table_name: BEA table name (default: SAGDP2N for state GDP by industry)

        Returns:
            DataFrame with GDP by industry sector, including:
            - Description: Industry name
            - DataValue: GDP in millions of dollars
            - TimePeriod: Year
            - Additional metadata fields

        Example:
            >>> connector = BEAConnector(api_key="...")
            >>> df = connector.fetch_gdp_by_industry(
            ...     geo_fips="08",  # Colorado
            ...     years=[2020, 2021]
            ... )
            >>> assert "DataValue" in df.columns
        """
        cache_key = f"bea_gdp_{table_name}_{geo_fips}_{'_'.join(map(str, years))}"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info("BEA GDP cache hit: %s", cache_key)
            return cached

        # Fetch from API
        params = {
            "DataSetName": "Regional",
            "TableName": table_name,
            "GeoFips": geo_fips,
            "Year": ",".join(map(str, years)),
        }

        response = self._retry_with_backoff(lambda: self.fetch(params))
        df = self.parse(response)

        # Cache result
        from datetime import timedelta

        self.cache.set(cache_key, df, ttl=timedelta(days=self.cache_ttl.days))

        logger.info(
            "Fetched BEA GDP for %s (%d years, %d rows)", geo_fips, len(years), len(df)
        )

        return df

    def fetch_personal_income(
        self, geo_fips: str, years: List[int], table_name: str = "SAINC1"
    ) -> pd.DataFrame:
        """
        Fetch personal income data for a state or county.

        Implements personal income portion of BEA Economic Data Integration requirement.

        Args:
            geo_fips: Geographic FIPS code
            years: List of years to retrieve
            table_name: BEA table name (default: SAINC1 for personal income summary)

        Returns:
            DataFrame with personal income data

        Example:
            >>> connector = BEAConnector(api_key="...")
            >>> df = connector.fetch_personal_income(
            ...     geo_fips="08031",  # Denver County
            ...     years=[2020, 2021]
            ... )
        """
        cache_key = f"bea_income_{table_name}_{geo_fips}_{'_'.join(map(str, years))}"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.info("BEA income cache hit: %s", cache_key)
            return cached

        # Fetch from API
        params = {
            "DataSetName": "Regional",
            "TableName": table_name,
            "GeoFips": geo_fips,
            "Year": ",".join(map(str, years)),
        }

        response = self._retry_with_backoff(lambda: self.fetch(params))
        df = self.parse(response)

        # Cache result
        from datetime import timedelta

        self.cache.set(cache_key, df, ttl=timedelta(days=self.cache_ttl.days))

        logger.info(
            "Fetched BEA income for %s (%d years, %d rows)",
            geo_fips,
            len(years),
            len(df),
        )

        return df

    def calculate_sector_shares(self, gdp_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate sector shares and growth rates from GDP data.

        Implements "calculates sector shares and growth rates" from spec scenario.

        Args:
            gdp_df: DataFrame from fetch_gdp_by_industry()

        Returns:
            DataFrame with added columns:
            - sector_share: Percentage of total GDP
            - growth_rate: Year-over-year growth rate

        Example:
            >>> df = connector.fetch_gdp_by_industry("08", [2020, 2021])
            >>> shares = connector.calculate_sector_shares(df)
            >>> assert "sector_share" in shares.columns
        """
        if gdp_df.empty:
            return gdp_df

        # Find total GDP rows
        totals = gdp_df[
            gdp_df["Description"].str.contains(
                "All industry total", case=False, na=False
            )
        ]

        # Calculate shares for each year
        result_frames = []

        for year in gdp_df["TimePeriod"].unique():
            year_data = gdp_df[gdp_df["TimePeriod"] == year].copy()
            year_total = totals[totals["TimePeriod"] == year]["DataValue"].iloc[0]

            if year_total and year_total > 0:
                year_data["sector_share"] = year_data["DataValue"] / year_total * 100
            else:
                year_data["sector_share"] = 0.0

            result_frames.append(year_data)

        result = pd.concat(result_frames, ignore_index=True)

        # Calculate growth rates (year-over-year)
        result = result.sort_values(["Description", "TimePeriod"])
        result["growth_rate"] = (
            result.groupby("Description")["DataValue"].pct_change() * 100
        )

        return result

    def identify_dominant_industries(
        self, gdp_df: pd.DataFrame, top_n: int = 5
    ) -> pd.DataFrame:
        """
        Identify dominant and emerging industries.

        Implements "identifies dominant and emerging industries" from spec scenario.

        Args:
            gdp_df: DataFrame from fetch_gdp_by_industry()
            top_n: Number of top industries to return

        Returns:
            DataFrame with top industries by GDP share and growth

        Example:
            >>> df = connector.fetch_gdp_by_industry("08", [2020, 2021])
            >>> dominant = connector.identify_dominant_industries(df, top_n=3)
        """
        # Get latest year data with shares
        shares_df = self.calculate_sector_shares(gdp_df)

        if shares_df.empty:
            return pd.DataFrame()

        latest_year = shares_df["TimePeriod"].max()
        latest = shares_df[shares_df["TimePeriod"] == latest_year].copy()

        # Exclude total row
        latest = latest[
            ~latest["Description"].str.contains(
                "All industry total", case=False, na=False
            )
        ]

        # Sort by sector share and return top N
        top_industries = latest.nlargest(top_n, "sector_share")[
            ["Description", "DataValue", "sector_share", "growth_rate"]
        ].reset_index(drop=True)

        return top_industries

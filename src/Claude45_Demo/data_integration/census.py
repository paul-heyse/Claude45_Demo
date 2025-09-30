"""Census Bureau data connector implementation."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from .base import APIConnector
from .cache import CacheManager
from .exceptions import DataValidationError

logger = logging.getLogger(__name__)


class CensusConnector(APIConnector):
    """Connector for Census Bureau ACS, Building Permits, and BFS data."""

    BASE_URL = "https://api.census.gov/data"
    ACS_PATH_TEMPLATE = "{year}/acs/acs5"
    BPS_PATH = "timeseries/eits/bp"
    BFS_PATH = "timeseries/bfs/bfs"

    ACS_VARIABLES: Dict[str, str] = {
        "population": "B01001_001E",
        "population_moe": "B01001_001M",
        "households": "B11001_001E",
        "median_income": "B19013_001E",
        "median_income_moe": "B19013_001M",
        "bachelors_degree": "B15003_022E",
        "commute_minutes": "B08303_001E",
    }

    def __init__(
        self,
        api_key: str,
        *,
        cache_manager: Optional[CacheManager] = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=self.BASE_URL,
            cache_ttl_days=30,
            rate_limit=500,
            cache_manager=cache_manager,
        )

    def fetch(self, params: Dict[str, Any]) -> Any:  # pragma: no cover - generic usage
        """Generic fetch hook for interface completeness."""
        raise NotImplementedError(
            "Use specialized methods like fetch_acs_demographics instead."
        )

    def parse(self, response: Any) -> Any:  # pragma: no cover - generic usage
        """Return raw response; scenario-specific parsers handle conversion."""
        return response

    # ------------------------------------------------------------------
    # ACS Demographics
    # ------------------------------------------------------------------
    def fetch_acs_demographics(self, *, cbsa: str, year: int) -> pd.DataFrame:
        """Return ACS 5-year estimates for a CBSA with standardized columns."""
        cache_key = f"census_acs_{year}_{cbsa}"
        cached = self.cache.get(cache_key) if self.cache else None
        if cached is not None:
            logger.info("Cache hit for ACS demographics: %s", cache_key)
            return cached

        params = {
            "get": ",".join(["NAME", *self.ACS_VARIABLES.values()]),
            "for": f"metropolitan statistical area/micropolitan statistical area:{cbsa}",
            "key": self.api_key,
        }
        path = self.ACS_PATH_TEMPLATE.format(year=year)
        response = self._retry_with_backoff(lambda: self._make_request(path, params))
        df = self._parse_acs_response(response)

        if self.cache:
            self.cache.set(cache_key, df, ttl=self.cache_ttl)

        return df

    def _parse_acs_response(self, response: List[List[Any]]) -> pd.DataFrame:
        if not response or len(response) < 2:
            raise DataValidationError("Empty ACS response")

        header, rows = response[0], response[1:]
        dataframe = pd.DataFrame(rows, columns=header)

        rename_map = {value: key for key, value in self.ACS_VARIABLES.items()}
        rename_map["NAME"] = "name"
        rename_map["metropolitan statistical area/micropolitan statistical area"] = (
            "cbsa"
        )
        dataframe = dataframe.rename(columns=rename_map)

        numeric_columns = set(self.ACS_VARIABLES.keys()) - {"bachelors_degree"}
        numeric_columns.update({"population_moe", "median_income_moe"})
        for column in numeric_columns:
            if column in dataframe.columns:
                dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

        if "bachelors_degree" in dataframe.columns:
            dataframe["bachelors_degree"] = pd.to_numeric(
                dataframe["bachelors_degree"], errors="coerce"
            )

        return dataframe

    # ------------------------------------------------------------------
    # Building Permits Survey
    # ------------------------------------------------------------------
    def fetch_building_permits(
        self,
        *,
        state_fips: str,
        county_fips: str,
        start_year: int,
        end_year: int,
        households: int,
    ) -> pd.DataFrame:
        """Return monthly building permit counts and rolling averages."""
        cache_key = f"census_bps_{state_fips}_{county_fips}_{start_year}_{end_year}"
        cached = self.cache.get(cache_key) if self.cache else None
        if cached is not None:
            logger.info("Cache hit for building permits: %s", cache_key)
            return cached

        params = {
            "get": "time,period,state,county,structure,value",
            "for": f"county:{county_fips}",
            "in": f"state:{state_fips}",
            "time": f"from {start_year}-01 to {end_year}-12",
            "key": self.api_key,
        }
        response = self._retry_with_backoff(
            lambda: self._make_request(self.BPS_PATH, params)
        )
        df = self._parse_building_permits_response(response, households=households)

        if self.cache:
            self.cache.set(cache_key, df, ttl=self.cache_ttl)

        return df

    def _parse_building_permits_response(
        self,
        response: List[List[Any]],
        *,
        households: int,
    ) -> pd.DataFrame:
        if not response or len(response) < 2:
            raise DataValidationError("Empty building permits response")

        frame = pd.DataFrame(response[1:], columns=response[0])
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce").fillna(0)
        frame["structure"] = frame["structure"].str.upper()

        pivot = (
            frame.pivot_table(
                values="value",
                index="period",
                columns="structure",
                aggfunc="sum",
            )
            .sort_index()
            .fillna(0)
        )

        rename_map = {
            "SFS": "single_family",
            "MFS": "multi_family",
        }
        pivot = pivot.rename(columns=rename_map)
        if "single_family" not in pivot.columns:
            pivot["single_family"] = 0
        if "multi_family" not in pivot.columns:
            pivot["multi_family"] = 0

        pivot["total_permits"] = pivot["single_family"] + pivot["multi_family"]
        rolling_sum = pivot["total_permits"].rolling(window=36, min_periods=12).sum()
        pivot["permits_per_1000_households_3yr_avg"] = (
            (rolling_sum / 3) / households * 1000
        )

        result = pivot.reset_index().rename(columns={"index": "period"})
        result["period"] = result["period"].astype(str)
        return result

    # ------------------------------------------------------------------
    # Business Formation Statistics
    # ------------------------------------------------------------------
    def fetch_business_formation(
        self,
        *,
        cbsa: Optional[str] = None,
        state: Optional[str] = None,
        frequency: str = "quarterly",
    ) -> pd.DataFrame:
        """Return BFS data for a CBSA or state with numeric columns."""
        if not (cbsa or state):
            raise ValueError("Either cbsa or state must be provided")

        region_key = cbsa or state
        cache_key = f"census_bfs_{region_key}_{frequency}"
        cached = self.cache.get(cache_key) if self.cache else None
        if cached is not None:
            logger.info("Cache hit for BFS: %s", cache_key)
            return cached

        params = {
            "get": "time,period,state,ba,hba,bfr",
            "frequency": frequency,
            "key": self.api_key,
        }
        if cbsa:
            params["for"] = (
                f"metropolitan statistical area/micropolitan statistical area:{cbsa}"
            )
        else:
            params["for"] = f"state:{state}"

        response = self._retry_with_backoff(
            lambda: self._make_request(self.BFS_PATH, params)
        )
        df = self._parse_bfs_response(response)

        if self.cache:
            self.cache.set(cache_key, df, ttl=self.cache_ttl)

        return df

    def _parse_bfs_response(self, response: List[List[Any]]) -> pd.DataFrame:
        if not response or len(response) < 2:
            raise DataValidationError("Empty BFS response")

        frame = pd.DataFrame(response[1:], columns=response[0])
        frame = frame.replace({"(NA)": pd.NA, "": pd.NA})

        frame["period"] = frame["time"] + "-" + frame["period"]

        rename_map = {
            "ba": "business_applications",
            "hba": "high_propensity_applications",
            "bfr": "business_formation_rate",
        }
        frame = frame.rename(columns=rename_map)

        for column in rename_map.values():
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

        result_columns = [
            "period",
            "state",
            "business_applications",
            "high_propensity_applications",
            "business_formation_rate",
        ]
        result = frame[result_columns]
        return result.sort_values("period").reset_index(drop=True)

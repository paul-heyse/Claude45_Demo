"""LEHD LODES connector for workplace analytics.

Implements the OpenSpec requirement for integrating Census LODES Workplace
Area Characteristics (WAC) data to provide daytime population metrics.
"""

from __future__ import annotations

import io
import logging
from typing import Any, Mapping

import pandas as pd
import requests

from .base import APIConnector
from .cache import CacheManager
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


class LEHDLODESConnector(APIConnector):
    """Connector for Census LODES Workplace Area Characteristics data."""

    DEFAULT_BASE_URL = "https://lehd.ces.census.gov/data/lodes/LODES7"

    def __init__(
        self,
        *,
        cache_manager: CacheManager | None = None,
        base_url: str = DEFAULT_BASE_URL,
        cache_ttl_days: int = 30,
        rate_limit: int = 1000,
    ) -> None:
        super().__init__(
            api_key=None,
            base_url=base_url,
            cache_ttl_days=cache_ttl_days,
            rate_limit=rate_limit,
            cache_manager=cache_manager,
        )

    def fetch(self, params: Mapping[str, Any]) -> bytes:
        """Download raw WAC CSV bytes for the requested geography."""
        state = params["state"].lower()
        dataset = params.get("dataset", "wac")
        segment = params.get("segment", "S000")
        job_type = params.get("job_type", "JT00")
        year = params["year"]

        path = f"{state}/{dataset}/{state}_{dataset}_{segment}_{job_type}_{year}.csv"

        def _make_request() -> bytes:
            url = self._build_url(path)
            logger.debug("Requesting LODES data from %s", url)
            response = requests.get(url, timeout=45)
            response.raise_for_status()
            return response.content

        return self._retry_with_backoff(_make_request)  # type: ignore[return-value]

    def parse(self, response: bytes) -> pd.DataFrame:
        """Parse raw CSV bytes into a DataFrame with string geocodes."""
        return pd.read_csv(io.BytesIO(response), dtype={"w_geocode": "string"})

    def fetch_daytime_population(
        self,
        *,
        state: str,
        year: int,
        workplace_tract: str,
        residential_population: int,
        segment: str = "S000",
        job_type: str = "JT00",
    ) -> pd.DataFrame:
        """Retrieve WAC metrics and compute daytime/residential ratio."""
        cache_key = (
            f"lodes_wac_{state.lower()}_{workplace_tract}_{segment}_{job_type}_{year}"
        )

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info("Cache hit for %s", cache_key)
                metrics_df = cached.copy()  # type: ignore[assignment]
            else:
                raw_bytes = self.fetch(
                    {
                        "state": state,
                        "dataset": "wac",
                        "segment": segment,
                        "job_type": job_type,
                        "year": year,
                    }
                )
                parsed = self.parse(raw_bytes)
                metrics_df = self._aggregate_metrics(parsed, workplace_tract)
                self.cache.set(cache_key, metrics_df, ttl=self.cache_ttl)
        else:
            raw_bytes = self.fetch(
                {
                    "state": state,
                    "dataset": "wac",
                    "segment": segment,
                    "job_type": job_type,
                    "year": year,
                }
            )
            parsed = self.parse(raw_bytes)
            metrics_df = self._aggregate_metrics(parsed, workplace_tract)

        result = metrics_df.copy()
        if residential_population > 0:
            result["daytime_residential_ratio"] = (
                result["total_jobs"] / residential_population
            )
        else:  # pragma: no cover - defensive branch
            result["daytime_residential_ratio"] = pd.NA

        return result

    def _aggregate_metrics(self, wac_df: pd.DataFrame, tract: str) -> pd.DataFrame:
        """Aggregate WAC metrics for a single workplace tract."""
        filtered = wac_df[wac_df["w_geocode"] == tract]
        if filtered.empty:
            raise ValidationError(
                f"No workplace records found for tract {tract} in LODES WAC dataset"
            )

        result: dict[str, Any] = {
            "workplace_geoid": tract,
            "total_jobs": int(filtered["C000"].sum()),
        }

        for column in filtered.columns:
            if column.startswith("CNS"):
                result[f"jobs_sector_{column}"] = int(filtered[column].sum())
            elif column.startswith("SE"):
                result[f"jobs_earnings_{column}"] = int(filtered[column].sum())
            elif column.startswith("SA"):
                result[f"jobs_age_{column}"] = int(filtered[column].sum())

        return pd.DataFrame([result])

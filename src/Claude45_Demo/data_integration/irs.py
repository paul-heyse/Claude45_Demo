"""Loader for IRS Statistics of Income migration data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

import pandas as pd

from .cache import CacheManager
from .exceptions import DataSourceError, ValidationError


@dataclass(frozen=True)
class MigrationRecord:
    """Represents aggregated migration metrics for a single year."""

    year: int
    inflow_returns: int
    inflow_agi: float
    outflow_returns: int
    outflow_agi: float
    net_migration: int
    net_agi: float
    agi_per_inflow_return: Optional[float]
    agi_per_outflow_return: Optional[float]
    agi_per_net_migrant: Optional[float]


class IRSMigrationLoader:
    """Ingest IRS SOI migration CSVs to produce county-level metrics."""

    INFLOW_FILENAME = "migration_inflows.csv"
    OUTFLOW_FILENAME = "migration_outflows.csv"
    CACHE_TTL_DAYS = 365
    REQUIRED_COLUMNS = {"year", "state_fips", "county_fips", "returns", "agi"}

    def __init__(
        self,
        *,
        data_dir: Path,
        cache_manager: CacheManager | None = None,
        cache_ttl_days: int = CACHE_TTL_DAYS,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.cache = cache_manager
        self.cache_ttl = timedelta(days=cache_ttl_days)

    def load_county_migration(
        self, *, state_fips: str, county_fips: str
    ) -> pd.DataFrame:
        """Return migration metrics for a county across available years."""

        cache_key = f"irs_migration_{state_fips}_{county_fips}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        inflow_df = self._load_csv(self.INFLOW_FILENAME)
        outflow_df = self._load_csv(self.OUTFLOW_FILENAME)

        filtered_inflows = self._filter_and_aggregate(
            inflow_df, state_fips=state_fips, county_fips=county_fips
        )
        filtered_outflows = self._filter_and_aggregate(
            outflow_df, state_fips=state_fips, county_fips=county_fips
        )

        if filtered_inflows.empty and filtered_outflows.empty:
            return pd.DataFrame(
                columns=[
                    "year",
                    "inflow_returns",
                    "inflow_agi",
                    "outflow_returns",
                    "outflow_agi",
                    "net_migration",
                    "net_agi",
                    "agi_per_inflow_return",
                    "agi_per_outflow_return",
                    "agi_per_net_migrant",
                ]
            )

        result = self._merge_and_calculate(filtered_inflows, filtered_outflows)

        if self.cache:
            self.cache.set(cache_key, result, ttl=self.cache_ttl)

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_csv(self, filename: str) -> pd.DataFrame:
        path = self.data_dir / filename
        if not path.exists():
            raise DataSourceError(f"IRS migration CSV not found: {path}")

        df = pd.read_csv(
            path,
            dtype={"state_fips": str, "county_fips": str},
        )

        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValidationError(
                f"IRS migration CSV {filename} missing columns: {', '.join(sorted(missing))}"
            )

        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
        df["returns"] = pd.to_numeric(df["returns"], errors="coerce")
        df["agi"] = pd.to_numeric(df["agi"], errors="coerce")

        df = df.dropna(subset=["year", "returns", "agi"])
        df["year"] = df["year"].astype(int)

        return df

    def _filter_and_aggregate(
        self,
        df: pd.DataFrame,
        *,
        state_fips: str,
        county_fips: str,
    ) -> pd.DataFrame:
        mask = (df["state_fips"] == state_fips) & (df["county_fips"] == county_fips)
        filtered = df.loc[mask]
        if filtered.empty:
            return pd.DataFrame(columns=["year", "returns", "agi"])

        grouped = (
            filtered.groupby("year", as_index=False)
            .agg({"returns": "sum", "agi": "sum"})
            .sort_values("year")
        )
        grouped["returns"] = grouped["returns"].astype(int)
        grouped["agi"] = grouped["agi"].astype(float)
        return grouped

    def _merge_and_calculate(
        self,
        inflows: pd.DataFrame,
        outflows: pd.DataFrame,
    ) -> pd.DataFrame:
        merged = inflows.merge(
            outflows, on="year", how="outer", suffixes=("_in", "_out")
        )
        merged = merged.fillna(0).sort_values("year").reset_index(drop=True)

        merged.rename(
            columns={
                "returns_in": "inflow_returns",
                "agi_in": "inflow_agi",
                "returns_out": "outflow_returns",
                "agi_out": "outflow_agi",
            },
            inplace=True,
        )

        # Ensure integer returns despite fillna producing floats
        merged["inflow_returns"] = merged["inflow_returns"].round().astype(int)
        merged["outflow_returns"] = merged["outflow_returns"].round().astype(int)

        merged["net_migration"] = merged["inflow_returns"] - merged["outflow_returns"]
        merged["net_agi"] = merged["inflow_agi"] - merged["outflow_agi"]

        merged["agi_per_inflow_return"] = merged["inflow_agi"] / merged[
            "inflow_returns"
        ].replace({0: pd.NA})
        merged["agi_per_outflow_return"] = merged["outflow_agi"] / merged[
            "outflow_returns"
        ].replace({0: pd.NA})
        merged["agi_per_net_migrant"] = merged["net_agi"] / merged[
            "net_migration"
        ].replace({0: pd.NA})

        # Convert pandas NA to None-compatible float for serialization
        for column in (
            "agi_per_inflow_return",
            "agi_per_outflow_return",
            "agi_per_net_migrant",
        ):
            merged[column] = merged[column].astype(float)

        return merged[
            [
                "year",
                "inflow_returns",
                "inflow_agi",
                "outflow_returns",
                "outflow_agi",
                "net_migration",
                "net_agi",
                "agi_per_inflow_return",
                "agi_per_outflow_return",
                "agi_per_net_migrant",
            ]
        ]

    def to_records(self, dataframe: pd.DataFrame) -> List[MigrationRecord]:
        """Convert a migration DataFrame into dataclass records."""

        return [MigrationRecord(**row) for row in dataframe.to_dict(orient="records")]

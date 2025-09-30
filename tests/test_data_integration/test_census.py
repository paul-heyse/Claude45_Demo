"""Tests for the Census Bureau data integration capability."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Callable, Dict, List

import pandas as pd
import pytest

from Claude45_Demo.data_integration.cache import CacheManager
from Claude45_Demo.data_integration.census import CensusConnector


@pytest.fixture()
def census_connector(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> CensusConnector:
    """Provide a CensusConnector that uses a temporary cache and bypasses retries."""

    cache = CacheManager(db_path=tmp_path / "census_cache.db")
    connector = CensusConnector(api_key="test-key", cache_manager=cache)

    def immediate_retry(func: Callable, **_: Dict) -> Dict:
        return func()

    monkeypatch.setattr(connector, "_retry_with_backoff", immediate_retry)
    return connector


def test_fetch_acs_demographics_returns_standardized_dataframe(
    census_connector: CensusConnector, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario: ACS demographic retrieval."""

    sample_response: List[List[str]] = [
        [
            "NAME",
            "B01001_001E",
            "B01001_001M",
            "B11001_001E",
            "B19013_001E",
            "B19013_001M",
            "B15003_022E",
            "B08303_001E",
            "state",
            "metropolitan statistical area/micropolitan statistical area",
        ],
        [
            "Denver-Aurora-Lakewood, CO",
            "2932380",
            "1200",
            "1100000",
            "78500",
            "2500",
            "750000",
            "27.5",
            "08",
            "19740",
        ],
    ]

    monkeypatch.setattr(
        census_connector,
        "_make_request",
        lambda url, params: sample_response,
    )

    df = census_connector.fetch_acs_demographics(cbsa="19740", year=2023)

    expected_columns = {
        "name",
        "population",
        "population_moe",
        "households",
        "median_income",
        "median_income_moe",
        "bachelors_degree",
        "commute_minutes",
        "state",
        "cbsa",
    }

    assert expected_columns.issubset(df.columns)
    record = df.iloc[0]
    assert record["population"] == 2932380
    assert record["population_moe"] == 1200
    assert record["median_income"] == 78500
    assert record["commute_minutes"] == pytest.approx(27.5)
    assert df["population"].dtype.kind in {"i", "u"}
    assert df["median_income"].dtype.kind in {"i", "u"}


def test_fetch_building_permits_caches_and_computes_rolling_average(
    census_connector: CensusConnector, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario: Building permits query with caching and rolling average."""

    months = [(year, month) for year in range(2021, 2024) for month in range(1, 13)]

    def build_response() -> List[List[str]]:
        header = [
            "time",
            "period",
            "state",
            "county",
            "structure",
            "value",
        ]
        rows: List[List[str]] = []
        for year, month in months:
            period = f"{year}-{month:02d}"
            rows.append([str(year), period, "08", "031", "SFS", "80"])  # Single family
            rows.append([str(year), period, "08", "031", "MFS", "20"])  # Multi family
        return [header, *rows]

    call_count = {"count": 0}

    def fake_request(url: str, params: Dict) -> List[List[str]]:
        call_count["count"] += 1
        return build_response()

    monkeypatch.setattr(census_connector, "_make_request", fake_request)

    df = census_connector.fetch_building_permits(
        state_fips="08",
        county_fips="031",
        start_year=2021,
        end_year=2023,
        households=240_000,
    )

    assert call_count["count"] == 1
    assert {
        "period",
        "single_family",
        "multi_family",
        "permits_per_1000_households_3yr_avg",
    }.issubset(df.columns)

    latest_row = df.sort_values("period").iloc[-1]
    assert latest_row["single_family"] == 80
    assert latest_row["multi_family"] == 20
    assert latest_row["permits_per_1000_households_3yr_avg"] == pytest.approx(5.0)

    # Second call should leverage cache (no additional API invocation)
    df_cached = census_connector.fetch_building_permits(
        state_fips="08",
        county_fips="031",
        start_year=2021,
        end_year=2023,
        households=240_000,
    )

    assert call_count["count"] == 1
    pd.testing.assert_frame_equal(df, df_cached)
    assert census_connector.cache_ttl == timedelta(days=30)


def test_fetch_business_formation_handles_missing_data(
    census_connector: CensusConnector, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario: Business formation statistics with graceful handling of missing data."""

    response = [
        [
            "time",
            "period",
            "state",
            "ba",
            "hba",
            "bfr",
        ],
        ["2023", "Q1", "08", "120", "80", "2.5"],
        ["2023", "Q2", "08", "(NA)", "(NA)", ""],
    ]

    monkeypatch.setattr(census_connector, "_make_request", lambda url, params: response)

    df = census_connector.fetch_business_formation(cbsa="19740", frequency="quarterly")

    assert {
        "period",
        "business_applications",
        "high_propensity_applications",
        "business_formation_rate",
    }.issubset(df.columns)
    assert df.iloc[0]["business_applications"] == 120
    assert pd.isna(df.iloc[1]["business_applications"])
    assert df["business_formation_rate"].dtype.kind in {"f", "i"}

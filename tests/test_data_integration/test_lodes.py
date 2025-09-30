"""Tests for the LEHD LODES connector.

Covers Requirement: LEHD Workplace Analytics Integration
from openspec/changes/add-aker-investment-platform/specs/data-integration/spec.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pytest

from Claude45_Demo.data_integration.cache import CacheManager
from Claude45_Demo.data_integration.exceptions import ValidationError

SAMPLE_WAC_CSV = (
    """w_geocode,C000,CNS01,CNS02,SE01,SE02,SE03,SA01,SA02,SA03\n"""
    "08031000100,100,40,60,50,30,20,40,30,30\n"
    "08031000100,50,20,30,20,15,15,10,15,25\n"
    "08031000200,10,5,5,4,3,3,3,3,4\n"
)


class DummyResponse:
    """Minimal HTTP response stub for requests.get."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.content = text.encode("utf-8")

    def raise_for_status(self) -> None:  # pragma: no cover - nothing to raise
        return None


@pytest.fixture()
def cache_manager(tmp_path: Path) -> CacheManager:
    return CacheManager(db_path=tmp_path / "lodes_cache.db")


@pytest.fixture()
def connector(cache_manager: CacheManager):
    from Claude45_Demo.data_integration.lodes import LEHDLODESConnector

    return LEHDLODESConnector(cache_manager=cache_manager)


def _patch_requests(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    def _fake_get(url: str, timeout: int = 30):  # pragma: no cover - simple stub
        return DummyResponse(text)

    monkeypatch.setattr("requests.get", _fake_get)


def test_daytime_population_query_returns_expected_dataframe(
    connector, cache_manager, monkeypatch
):
    """Scenario: Daytime population query returns aggregated metrics."""
    _patch_requests(monkeypatch, SAMPLE_WAC_CSV)

    result = connector.fetch_daytime_population(
        state="co",
        year=2021,
        workplace_tract="08031000100",
        residential_population=5000,
    )

    assert result.shape == (1, 11)
    record: Dict[str, float] = result.iloc[0].to_dict()
    assert record["workplace_geoid"] == "08031000100"
    assert record["total_jobs"] == 150
    assert record["jobs_sector_CNS01"] == 60
    assert record["jobs_sector_CNS02"] == 90
    assert record["jobs_earnings_SE01"] == 70
    assert record["jobs_age_SA03"] == 55
    assert pytest.approx(record["daytime_residential_ratio"], rel=1e-6) == 150 / 5000


def test_daytime_population_uses_cache_on_subsequent_calls(
    connector, cache_manager, monkeypatch
):
    """Connector should return cached data without issuing new request."""
    _patch_requests(monkeypatch, SAMPLE_WAC_CSV)
    connector.fetch_daytime_population(
        state="co",
        year=2021,
        workplace_tract="08031000100",
        residential_population=5000,
    )

    def _fail_get(*_, **__):  # pragma: no cover - expectation helper
        raise AssertionError("requests.get should not be called when cache is warm")

    monkeypatch.setattr("requests.get", _fail_get)

    cached = connector.fetch_daytime_population(
        state="co",
        year=2021,
        workplace_tract="08031000100",
        residential_population=6000,
    )

    # Ratio should reflect new residential population while raw jobs unchanged
    assert pytest.approx(cached["daytime_residential_ratio"].iloc[0]) == 150 / 6000


def test_daytime_population_raises_validation_error_for_missing_tract(
    connector, monkeypatch
):
    """Connector should surface validation issues when tract not present."""
    _patch_requests(monkeypatch, SAMPLE_WAC_CSV)

    with pytest.raises(ValidationError):
        connector.fetch_daytime_population(
            state="co",
            year=2021,
            workplace_tract="08031999999",
            residential_population=4000,
        )

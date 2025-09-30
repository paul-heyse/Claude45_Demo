"""Tests for Transitland GTFS connector and analysis."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import pytest

from Claude45_Demo.data_integration.cache import CacheManager
from Claude45_Demo.geo_analysis.transit import TransitlandConnector


@pytest.fixture()
def transit_connector(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> TransitlandConnector:
    """Provide a connector with deterministic cache and no delays."""

    cache = CacheManager(db_path=tmp_path / "transit_cache.db")
    connector = TransitlandConnector(api_key="test-key", cache_manager=cache)

    def immediate_retry(func, **_):
        return func()

    monkeypatch.setattr(connector, "_retry_with_backoff", immediate_retry)
    return connector


def test_stop_density_summary_calculates_metrics(
    transit_connector: TransitlandConnector, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scenario: Transit stop density calculation from Transitland data."""

    sample_response: Dict[str, object] = {
        "meta": {"next": None},
        "stops": [
            {
                "onestop_id": "s-denver-1",
                "name": "Union Station",
                "geometry": {"coordinates": [-104.999, 39.752]},
                "served_by_routes": [
                    {"onestop_id": "r1", "min_headway_minutes": 12},
                    {"onestop_id": "r2", "min_headway_minutes": 18},
                ],
            },
            {
                "onestop_id": "s-denver-2",
                "name": "18th & California",
                "geometry": {"coordinates": [-104.9905, 39.747]},
                "served_by_routes": [{"onestop_id": "r3", "min_headway_minutes": 10}],
            },
            {
                "onestop_id": "s-denver-3",
                "name": "County Line",
                "geometry": {"coordinates": [-104.8701, 39.555]},
                "served_by_routes": [{"onestop_id": "r4", "min_headway_minutes": 25}],
            },
        ],
    }

    monkeypatch.setattr(
        transit_connector,
        "_make_request",
        lambda path, params: sample_response,
    )

    summary = transit_connector.get_stop_density_summary(
        bbox=(-105.05, 39.5, -104.8, 39.9),
        area_sq_km=18.0,
        population=120_000,
    )

    assert summary["stop_count"] == 3
    assert summary["high_frequency_stop_count"] == 2
    assert summary["stops_per_sq_km"] == pytest.approx(3 / 18.0)
    assert summary["stops_per_10k_population"] == pytest.approx(3 / 120_000 * 10_000)
    assert summary["high_frequency_ratio"] == pytest.approx(2 / 3)


def create_gtfs_fixture(gtfs_dir: Path) -> None:
    """Write minimal GTFS files used for service frequency analysis tests."""

    routes = pd.DataFrame(
        [{"route_id": "A", "route_short_name": "A", "route_long_name": "A Line"}]
    )
    trips = pd.DataFrame(
        [
            {"trip_id": "trip1", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip2", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip3", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip4", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip5", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip6", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip7", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip8", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip9", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip10", "route_id": "A", "service_id": "WKD"},
            {"trip_id": "trip11", "route_id": "A", "service_id": "WKND"},
            {"trip_id": "trip12", "route_id": "A", "service_id": "WKND"},
        ]
    )
    stop_times = pd.DataFrame(
        [
            {
                "trip_id": "trip10",
                "arrival_time": "06:00:00",
                "departure_time": "06:00:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip1",
                "arrival_time": "07:00:00",
                "departure_time": "07:00:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip2",
                "arrival_time": "07:15:00",
                "departure_time": "07:15:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip3",
                "arrival_time": "07:30:00",
                "departure_time": "07:30:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip4",
                "arrival_time": "10:00:00",
                "departure_time": "10:00:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip5",
                "arrival_time": "10:20:00",
                "departure_time": "10:20:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip6",
                "arrival_time": "10:40:00",
                "departure_time": "10:40:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip7",
                "arrival_time": "21:30:00",
                "departure_time": "21:30:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip8",
                "arrival_time": "22:15:00",
                "departure_time": "22:15:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip9",
                "arrival_time": "23:00:00",
                "departure_time": "23:00:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip11",
                "arrival_time": "12:00:00",
                "departure_time": "12:00:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
            {
                "trip_id": "trip12",
                "arrival_time": "18:00:00",
                "departure_time": "18:00:00",
                "stop_id": "STOP1",
                "stop_sequence": 1,
            },
        ]
    )
    calendar = pd.DataFrame(
        [
            {
                "service_id": "WKD",
                "monday": 1,
                "tuesday": 1,
                "wednesday": 1,
                "thursday": 1,
                "friday": 1,
                "saturday": 0,
                "sunday": 0,
                "start_date": 20240101,
                "end_date": 20241231,
            },
            {
                "service_id": "WKND",
                "monday": 0,
                "tuesday": 0,
                "wednesday": 0,
                "thursday": 0,
                "friday": 0,
                "saturday": 1,
                "sunday": 1,
                "start_date": 20240101,
                "end_date": 20241231,
            },
        ]
    )

    gtfs_dir.mkdir(parents=True, exist_ok=True)
    routes.to_csv(gtfs_dir / "routes.txt", index=False)
    trips.to_csv(gtfs_dir / "trips.txt", index=False)
    stop_times.to_csv(gtfs_dir / "stop_times.txt", index=False)
    calendar.to_csv(gtfs_dir / "calendar.txt", index=False)


def test_analyze_service_frequency_returns_headways(tmp_path: Path) -> None:
    """Scenario: Service frequency analysis from GTFS stop times."""

    gtfs_dir = tmp_path / "gtfs"
    create_gtfs_fixture(gtfs_dir)

    connector = TransitlandConnector(api_key="test-key")
    results = connector.analyze_service_frequency(gtfs_path=gtfs_dir, route_ids=["A"])

    assert results["weekday_trip_count"] == 10
    assert results["peak_headway_minutes"] == pytest.approx(15.0)
    assert results["offpeak_headway_minutes"] == pytest.approx(20.0)
    assert results["weekday_service_hours"] == pytest.approx((23 * 60 - 6 * 60) / 60)
    assert results["all_day_service"] is True
    assert results["provides_evening_service"] is True
    assert results["has_weekend_service"] is True

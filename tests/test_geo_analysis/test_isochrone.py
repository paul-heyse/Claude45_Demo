"""Tests for the IsochroneCalculator using OpenRouteService-style responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pytest
from shapely.geometry import Point, Polygon

from Claude45_Demo.data_integration.cache import CacheManager
from Claude45_Demo.geo_analysis.isochrone import IsochroneCalculator, IsochroneResult


@dataclass
class DummyORSResponse:
    """Minimal stub to emulate requests.Response."""

    payload: Dict
    status_code: int = 200

    def json(self) -> Dict:  # pragma: no cover - simple accessor
        return self.payload

    def raise_for_status(self) -> None:  # pragma: no cover - simple check
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


WALK_RESPONSE = {
    "features": [
        {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-105.001, 40.000],
                        [-105.001, 40.002],
                        [-104.999, 40.002],
                        [-104.999, 40.000],
                        [-105.001, 40.000],
                    ]
                ],
            },
            "properties": {"summary": {"area": 120000.0}},
        }
    ]
}

DRIVE_RESPONSE = {
    "features": [
        {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-105.010, 40.000],
                        [-105.010, 40.005],
                        [-104.995, 40.005],
                        [-104.995, 40.000],
                        [-105.010, 40.000],
                    ]
                ],
            },
            "properties": {"summary": {"area": 900000.0}},
        }
    ]
}

TRANSIT_WALK_RESPONSE = {
    "features": [
        {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-105.003, 39.999],
                        [-105.003, 40.001],
                        [-105.001, 40.001],
                        [-105.001, 39.999],
                        [-105.003, 39.999],
                    ]
                ],
            },
            "properties": {"summary": {"area": 40000.0}},
        }
    ]
}

TRANSIT_RAIL_RESPONSE = {
    "features": [
        {
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-105.000, 40.001],
                        [-105.000, 40.006],
                        [-104.994, 40.006],
                        [-104.994, 40.001],
                        [-105.000, 40.001],
                    ]
                ],
            },
            "properties": {"summary": {"area": 250000.0}},
        }
    ]
}


@pytest.fixture()
def cache_manager(tmp_path) -> CacheManager:  # type: ignore[no-untyped-def]
    return CacheManager(db_path=tmp_path / "iso_cache.db")


@pytest.fixture()
def calculator(cache_manager: CacheManager) -> IsochroneCalculator:
    return IsochroneCalculator(api_key="test-key", cache_manager=cache_manager)


def _amenities_inside_polygon() -> List[Dict[str, float]]:
    return [
        {"category": "grocery", "lat": 40.0015, "lon": -105.0005},
        {"category": "grocery", "lat": 40.0010, "lon": -104.9995},
        {"category": "pharmacy", "lat": 40.0005, "lon": -105.0005},
        {"category": "school", "lat": 40.0100, "lon": -105.0200},  # outside
    ]


def _population_blocks() -> List[Dict]:
    return [
        {
            "geometry": Polygon(
                [
                    (-105.0009, 40.0001),
                    (-105.0009, 40.0019),
                    (-104.9991, 40.0019),
                    (-104.9991, 40.0001),
                    (-105.0009, 40.0001),
                ]
            ),
            "population": 1000,
        },
        {
            "geometry": Polygon(
                [
                    (-105.010, 40.000),
                    (-105.010, 40.005),
                    (-105.005, 40.005),
                    (-105.005, 40.000),
                    (-105.010, 40.000),
                ]
            ),
            "population": 500,
        },
    ]


@pytest.mark.usefixtures("calculator")
@pytest.mark.parametrize(
    "response_payload,method,expected_mode",
    [
        (WALK_RESPONSE, "calculate_walk_isochrone", "foot-walking"),
        (DRIVE_RESPONSE, "calculate_drive_isochrone", "driving-car"),
    ],
)
@pytest.mark.parametrize("range_minutes", [15, 30])
def test_isochrone_calculation_counts_pois(
    response_payload,
    method,
    expected_mode,
    range_minutes,
    calculator: IsochroneCalculator,
    cache_manager: CacheManager,
    monkeypatch,
):
    """Isochrone results include geometry, POI counts, population, and area."""

    def _fake_post(*_, **__):
        return DummyORSResponse(response_payload)

    monkeypatch.setattr("Claude45_Demo.geo_analysis.isochrone.requests.post", _fake_post)

    amenities = _amenities_inside_polygon()
    population = _population_blocks()

    func = getattr(calculator, method)
    result: IsochroneResult = func(
        latitude=40.0005,
        longitude=-105.0005,
        range_minutes=range_minutes,
        amenities=amenities,
        population_blocks=population,
    )

    assert isinstance(result.geometry, Polygon)
    assert result.travel_mode == expected_mode
    assert result.range_minutes == range_minutes
    assert result.poi_counts["grocery"] == 2
    assert result.poi_counts["pharmacy"] == 1
    assert result.population >= 1000
    assert result.area_sq_km > 0


def test_drive_isochrone_uses_cache(calculator: IsochroneCalculator, monkeypatch) -> None:
    """Second call with same parameters should reuse cached isochrone."""

    call_count = {"value": 0}

    def _fake_post(*_, **__):
        call_count["value"] += 1
        return DummyORSResponse(DRIVE_RESPONSE)

    monkeypatch.setattr("Claude45_Demo.geo_analysis.isochrone.requests.post", _fake_post)

    amenities = _amenities_inside_polygon()
    population = _population_blocks()

    result1 = calculator.calculate_drive_isochrone(
        latitude=40.001,
        longitude=-105.002,
        range_minutes=30,
        amenities=amenities,
        population_blocks=population,
        residential_population=4000,
    )

    result2 = calculator.calculate_drive_isochrone(
        latitude=40.001,
        longitude=-105.002,
        range_minutes=30,
        amenities=amenities,
        population_blocks=population,
        residential_population=8000,
    )

    assert call_count["value"] == 1
    assert result1.population == result2.population
    assert "reach_ratio" in result1.poi_counts
    assert result1.poi_counts["reach_ratio"] > 0


def test_multimodal_isochrone_unions_polygons(
    calculator: IsochroneCalculator, monkeypatch
) -> None:
    """Multimodal calculation unions individual leg isochrones."""

    responses = [DummyORSResponse(TRANSIT_WALK_RESPONSE), DummyORSResponse(TRANSIT_RAIL_RESPONSE)]

    def _fake_post(*_, **__):
        return responses.pop(0)

    monkeypatch.setattr("Claude45_Demo.geo_analysis.isochrone.requests.post", _fake_post)

    amenities = _amenities_inside_polygon()
    population = _population_blocks()

    result = calculator.calculate_multimodal_isochrone(
        latitude=40.0005,
        longitude=-105.0005,
        legs=[
            {"profile": "foot-walking", "range_minutes": 10},
            {"profile": "driving-car", "range_minutes": 20},
        ],
        amenities=amenities,
        population_blocks=population,
    )

    assert result.travel_mode == "foot-walking+driving-car"
    # Geometry should cover both component polygons
    assert result.geometry.contains(Point(-105.002, 40.0005))
    assert result.geometry.contains(Point(-104.995, 40.004))
    assert result.population >= 250
    assert result.area_sq_km > 0

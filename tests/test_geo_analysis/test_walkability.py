"""Tests for walkability scoring module."""

from __future__ import annotations

from Claude45_Demo.geo_analysis.walkability import (
    WalkabilityBreakdown,
    calculate_walkability_breakdown,
    calculate_walkability_score,
)


def test_walkability_breakdown_balances_components() -> None:
    """High amenity coverage and intersections should produce strong scores."""

    breakdown = calculate_walkability_breakdown(
        amenity_counts={"grocery": 5, "pharmacy": 3, "school": 4, "transit": 6},
        intersection_density_per_sqkm=120.0,
        bikeway_score=85.0,
        population_within_isochrone=18000,
        area_sq_km=1.8,
    )

    assert isinstance(breakdown, WalkabilityBreakdown)
    assert 80 <= breakdown.amenity_score <= 100
    assert breakdown.intersection_score > 100 - 1e-3  # capped at 100
    assert breakdown.population_score > 80
    assert 80 <= breakdown.final_score <= 100


def test_walkability_score_handles_sparse_amenities() -> None:
    """Sparse amenities yield much lower walkability scores."""

    score_dense = calculate_walkability_score(
        amenity_counts={"grocery": 4, "pharmacy": 2, "school": 2, "transit": 4},
        intersection_density_per_sqkm=110.0,
        bikeway_score=75.0,
        population_within_isochrone=15000,
        area_sq_km=2.0,
    )

    score_sparse = calculate_walkability_score(
        amenity_counts={"grocery": 1, "pharmacy": 0, "school": 1, "transit": 1},
        intersection_density_per_sqkm=45.0,
        bikeway_score=30.0,
        population_within_isochrone=4000,
        area_sq_km=2.5,
    )

    assert score_dense > score_sparse
    assert score_sparse < 50
    assert score_dense > 70

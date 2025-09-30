"""Tests for street connectivity metrics."""

from __future__ import annotations

from shapely.geometry import LineString, Point

from Claude45_Demo.geo_analysis.connectivity import (
    compute_bikeway_metrics,
    compute_block_size_score,
    compute_intersection_density,
)


def test_intersection_density_and_block_size() -> None:
    intersections = [Point(x, y) for x in range(5) for y in range(4)]
    density = compute_intersection_density(intersections, area_sq_km=2.0)
    assert density == len(intersections) / 2.0

    ideal_score = compute_block_size_score(450)
    off_score = compute_block_size_score(900)
    assert ideal_score == 100.0
    assert off_score < ideal_score


def test_bikeway_metrics_counts_protected_segments() -> None:
    line1 = LineString([(0, 0), (1, 0)])
    line1.tag = "protected"
    line2 = LineString([(0, 0), (0, 2)])
    line2.tag = "painted"

    metrics = compute_bikeway_metrics(
        [line1, line2],
        protected_tags={"protected": True},
        population=50000,
    )

    assert metrics["total_miles"] > 0
    assert 0 < metrics["protected_ratio"] <= 1
    assert metrics["bikeway_score"] > 0

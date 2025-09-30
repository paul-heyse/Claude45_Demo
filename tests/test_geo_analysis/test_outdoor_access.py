"""Tests for outdoor access scoring."""

from __future__ import annotations

from Claude45_Demo.geo_analysis.outdoor_access import (
    OutdoorAccessBreakdown,
    score_outdoor_access,
)
from Claude45_Demo.geo_analysis.trails import TrailSummary


def test_score_outdoor_access_combines_components() -> None:
    trail_summary = TrailSummary(
        nearest_trail_miles=2.5,
        drive_time_minutes=6.0,
        trails_within_30min_miles=42.0,
        trail_miles_per_10k_population=1.2,
    )

    breakdown = score_outdoor_access(
        trail_summary=trail_summary,
        ski_distances_miles=[55.0, 80.0],
        water_distances_miles=[8.0, 12.0],
        public_land_pct=45.0,
    )

    assert isinstance(breakdown, OutdoorAccessBreakdown)
    assert 0 <= breakdown.ski_component <= 100
    assert breakdown.trail_component > breakdown.ski_component
    assert breakdown.final_score > 35


def test_outdoor_access_reflects_poor_conditions() -> None:
    trail_summary = TrailSummary(
        nearest_trail_miles=40.0,
        drive_time_minutes=90.0,
        trails_within_30min_miles=0.5,
        trail_miles_per_10k_population=0.01,
    )

    breakdown = score_outdoor_access(
        trail_summary=trail_summary,
        ski_distances_miles=[200.0],
        water_distances_miles=[70.0],
        public_land_pct=5.0,
    )

    assert breakdown.final_score < 10
    assert breakdown.trail_component < 20
    assert breakdown.ski_component <= 20

"""Tests for trail proximity analyzer."""

from __future__ import annotations

from shapely.geometry import LineString, Point

from Claude45_Demo.geo_analysis.trails import TrailProximityAnalyzer


def test_trail_proximity_summarizes_drive_time() -> None:
    origin = Point(-105.0, 39.7)
    trails = [
        LineString([(-105.05, 39.68), (-105.04, 39.69)]),
        LineString([(-104.9, 39.8), (-104.89, 39.81)]),
        LineString([(-105.2, 39.6), (-105.19, 39.62)]),
    ]

    analyzer = TrailProximityAnalyzer(drive_speed_mph=40.0)
    summary = analyzer.summarize(origin=origin, trails=trails, population=200000)

    assert summary.nearest_trail_miles > 0
    assert summary.drive_time_minutes > 0
    assert summary.trails_within_30min_miles > summary.nearest_trail_miles
    assert summary.trail_miles_per_10k_population > 0

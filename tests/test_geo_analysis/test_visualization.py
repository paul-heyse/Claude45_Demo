"""Tests for visualization helpers."""

from __future__ import annotations

from pathlib import Path

from shapely.geometry import Point

from Claude45_Demo.geo_analysis.visualization import (
    build_feature_collection,
    export_geojson,
)


def test_build_feature_collection_includes_properties(tmp_path: Path) -> None:
    entries = [
        {"geometry": Point(-105.0, 39.7), "score": 85, "name": "Denver"},
        {"geometry": None, "note": "No geometry"},
    ]

    feature_collection = build_feature_collection(entries)
    assert feature_collection["type"] == "FeatureCollection"
    assert len(feature_collection["features"]) == 2
    assert feature_collection["features"][0]["properties"]["score"] == 85

    output_path = tmp_path / "map.json"
    export_geojson(entries, output_path)
    assert output_path.exists()
    assert "FeatureCollection" in output_path.read_text()

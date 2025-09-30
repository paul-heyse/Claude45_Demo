"""Geospatial visualization helpers for exporting analysis results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

from shapely.geometry import mapping


def build_feature_collection(entries: Iterable[Mapping]) -> dict:
    """Return a GeoJSON FeatureCollection for the provided entries."""

    features = []
    for entry in entries:
        geometry = entry.get("geometry")
        properties = {k: v for k, v in entry.items() if k != "geometry"}
        features.append(
            {
                "type": "Feature",
                "geometry": mapping(geometry) if geometry is not None else None,
                "properties": properties,
            }
        )
    return {"type": "FeatureCollection", "features": features}


def export_geojson(entries: Iterable[Mapping], output_path: Path) -> Path:
    """Write the feature collection to disk and return the path."""

    collection = build_feature_collection(entries)
    output_path.write_text(json.dumps(collection))
    return output_path

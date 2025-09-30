"""Intersection density and bikeway connectivity metrics."""

from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from shapely.geometry import LineString, Point


def compute_intersection_density(
    intersections: Sequence[Point], area_sq_km: float
) -> float:
    """Compute intersections per square kilometre."""

    if area_sq_km <= 0:
        return 0.0
    return len(intersections) / area_sq_km


def compute_block_size_score(mean_block_perimeter_m: float) -> float:
    """Return block size score (300-600m considered ideal)."""

    if mean_block_perimeter_m <= 0:
        return 0.0
    if 300 <= mean_block_perimeter_m <= 600:
        return 100.0
    deviation = abs(mean_block_perimeter_m - 450)
    return max(0.0, 100 - deviation / 6)


def compute_bikeway_metrics(
    bikeways: Iterable[LineString],
    *,
    protected_tags: Mapping[str, bool],
    population: int,
) -> dict:
    """Return bikeway totals and protected ratio."""

    total_length_miles = 0.0
    protected_length_miles = 0.0

    for line in bikeways:
        length_miles = line.length * 0.000621371
        total_length_miles += length_miles
        tag = getattr(line, "tag", "")
        if protected_tags.get(tag, False):
            protected_length_miles += length_miles

    miles_per_10k = total_length_miles / population * 10000 if population > 0 else 0.0
    protected_ratio = (
        protected_length_miles / total_length_miles if total_length_miles > 0 else 0.0
    )

    score = min(100.0, miles_per_10k * 10 + protected_ratio * 40)

    return {
        "total_miles": total_length_miles,
        "protected_ratio": protected_ratio,
        "miles_per_10k": miles_per_10k,
        "bikeway_score": score,
    }

"""Outdoor recreation access scoring utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .trails import TrailSummary


@dataclass(frozen=True)
class OutdoorAccessBreakdown:
    trail_component: float
    ski_component: float
    water_component: float
    public_land_component: float
    final_score: float


def _score_distance(
    distance_miles: float, *, ideal: float, max_distance: float
) -> float:
    if distance_miles <= 0:
        return 100.0
    if distance_miles >= max_distance:
        return 0.0
    ratio = distance_miles / ideal
    return max(0.0, min(100.0, (2.0 - ratio) * 50))


def score_outdoor_access(
    *,
    trail_summary: TrailSummary,
    ski_distances_miles: Iterable[float],
    water_distances_miles: Iterable[float],
    public_land_pct: float,
) -> OutdoorAccessBreakdown:
    """Compute outdoor access score using heuristics for each component."""

    trail_component = max(
        0.0,
        min(
            100.0,
            (100 - trail_summary.drive_time_minutes) * 0.6
            + min(trail_summary.trail_miles_per_10k_population * 5, 40.0),
        ),
    )

    ski_component = 0.0
    distances = list(ski_distances_miles)
    if distances:
        nearest = min(distances)
        ski_component = _score_distance(nearest, ideal=30.0, max_distance=120.0)

    water_component = 0.0
    water_list = list(water_distances_miles)
    if water_list:
        nearest_water = min(water_list)
        water_component = _score_distance(nearest_water, ideal=5.0, max_distance=60.0)

    public_land_component = max(0.0, min(public_land_pct, 70.0)) / 70.0 * 100.0

    final_score = (
        trail_component * 0.4
        + ski_component * 0.25
        + water_component * 0.2
        + public_land_component * 0.15
    )

    return OutdoorAccessBreakdown(
        trail_component=trail_component,
        ski_component=ski_component,
        water_component=water_component,
        public_land_component=public_land_component,
        final_score=min(100.0, final_score),
    )

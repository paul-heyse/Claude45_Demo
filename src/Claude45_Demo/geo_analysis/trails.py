"""Trail proximity calculations using simple geospatial heuristics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from shapely.geometry import LineString, Point

MILES_TO_METERS = 1609.34


@dataclass(frozen=True)
class TrailSummary:
    """Summarizes trail access metrics for a submarket."""

    nearest_trail_miles: float
    drive_time_minutes: float
    trails_within_30min_miles: float
    trail_miles_per_10k_population: float


class TrailProximityAnalyzer:
    """Lightweight trail proximity analytics for recreation scoring."""

    def __init__(self, *, drive_speed_mph: float = 35.0) -> None:
        self.drive_speed_mph = drive_speed_mph

    def summarize(
        self,
        *,
        origin: Point,
        trails: Iterable[LineString],
        population: int,
    ) -> TrailSummary:
        distances = [origin.distance(line) for line in trails]
        if not distances:
            return TrailSummary(999.0, 999.0, 0.0, 0.0)

        nearest_meters = min(distances)
        nearest_miles = nearest_meters / MILES_TO_METERS
        drive_time_minutes = (nearest_miles / self.drive_speed_mph) * 60

        max_drive_distance_miles = self.drive_speed_mph * 0.5
        accessible_miles = sum(
            line.length / MILES_TO_METERS
            for line, distance in zip(trails, distances, strict=False)
            if distance / MILES_TO_METERS <= max_drive_distance_miles
        )

        trail_miles_per_10k = (
            accessible_miles / population * 10000 if population > 0 else 0.0
        )

        return TrailSummary(
            nearest_trail_miles=nearest_miles,
            drive_time_minutes=drive_time_minutes,
            trails_within_30min_miles=accessible_miles,
            trail_miles_per_10k_population=trail_miles_per_10k,
        )

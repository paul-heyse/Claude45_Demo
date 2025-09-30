"""Walkability scoring utilities based on amenity and infrastructure metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class WalkabilityBreakdown:
    """Represents the components used to produce the final walkability score."""

    amenity_score: float
    intersection_score: float
    bikeway_score: float
    population_score: float
    final_score: float


def _normalize(
    value: float, target: float, *, inverse: bool = False, cap: float = 100.0
) -> float:
    """Normalize a value to 0-100 relative to a target threshold."""

    if target <= 0:
        return 0.0

    ratio = value / target
    ratio = max(min(ratio, 2.0), 0.0)
    score = ratio * 100 if not inverse else (2.0 - ratio) * 100
    return max(0.0, min(score, cap))


def calculate_walkability_breakdown(
    *,
    amenity_counts: Mapping[str, int],
    intersection_density_per_sqkm: float,
    bikeway_score: float,
    population_within_isochrone: int,
    area_sq_km: float,
) -> WalkabilityBreakdown:
    """Return the component scores used for walkability."""

    essential_categories = {"grocery": 4, "pharmacy": 2, "school": 2, "transit": 4}
    amenity_points = 0.0
    for category, target in essential_categories.items():
        count = amenity_counts.get(category, 0)
        amenity_points += _normalize(count, target)
    amenity_score = amenity_points / len(essential_categories)

    intersection_score = _normalize(intersection_density_per_sqkm, 90.0)
    population_density = population_within_isochrone / area_sq_km if area_sq_km else 0.0
    population_score = _normalize(population_density, 10000.0)

    weighted_final = (
        amenity_score * 0.4
        + intersection_score * 0.25
        + bikeway_score * 0.2
        + population_score * 0.15
    )

    return WalkabilityBreakdown(
        amenity_score=amenity_score,
        intersection_score=intersection_score,
        bikeway_score=max(0.0, min(bikeway_score, 100.0)),
        population_score=population_score,
        final_score=min(100.0, weighted_final),
    )


def calculate_walkability_score(**kwargs) -> float:
    """Convenience wrapper returning only the composite walkability score."""

    breakdown = calculate_walkability_breakdown(**kwargs)
    return breakdown.final_score

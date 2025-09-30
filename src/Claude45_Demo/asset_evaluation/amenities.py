"""Amenity scoring utilities aligned with Aker's outdoor-focused thesis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable


@dataclass(frozen=True)
class AmenityScores:
    outdoor_brand_score: int
    ev_readiness_score: int
    remote_work_score: int
    pet_friendliness_score: int
    notes: Dict[str, str]


OUTDOOR_FEATURE_POINTS = {
    "balconies": 20,
    "gear_storage": 20,
    "bike_ski_storage": 20,
    "dog_wash": 20,
    "mudroom": 20,
}

REMOTE_WORK_FEATURES = {
    "quiet_rooms": 35,
    "micro_offices": 35,
    "mesh_wifi": 20,
    "bookable_conference": 10,
}

PET_FEATURES = {
    "dog_run": 40,
    "dog_wash": 30,
    "pet_policy_friendly": 30,
}


def score_outdoor_brand(features: Dict[str, bool], unique_features: Iterable[str] | None = None) -> int:
    score = sum(points for feature, points in OUTDOOR_FEATURE_POINTS.items() if features.get(feature))
    bonus = 0
    if unique_features:
        bonus = min(20, len(list(unique_features)) * 5)
    return min(100, score + bonus)


def score_ev_readiness(
    *,
    existing_ev_stalls: int,
    total_stalls: int,
    ev_ready_conduit: bool,
    planned_retrofit_cost: float | None = None,
) -> tuple[int, str]:
    if total_stalls <= 0:
        return 0, "No parking data"
    coverage = existing_ev_stalls / total_stalls
    base_score = coverage * 100
    if ev_ready_conduit:
        base_score = max(base_score, 60)
    if planned_retrofit_cost is not None and planned_retrofit_cost <= 1500 * total_stalls * 0.25:
        base_score += 10
    return min(100, int(base_score)), f"EV stalls: {existing_ev_stalls}/{total_stalls}"


def score_remote_work(features: Dict[str, bool], monetization_potential: bool) -> int:
    score = sum(points for feature, points in REMOTE_WORK_FEATURES.items() if features.get(feature))
    if monetization_potential:
        score += 10
    return min(100, score)


def score_pet_friendliness(features: Dict[str, bool], pet_policy: Dict[str, bool]) -> int:
    score = sum(points for feature, points in PET_FEATURES.items() if features.get(feature))
    if pet_policy.get("no_breed_restrictions", False):
        score += 10
    if pet_policy.get("pet_rent", 0) > 0:
        score += 5
    return min(100, score)


def evaluate_amenities(
    *,
    outdoor_features: Dict[str, bool],
    unique_outdoor_features: Iterable[str] | None,
    ev_data: Dict[str, int | bool | float | None],
    remote_work_features: Dict[str, bool],
    monetization_potential: bool,
    pet_features: Dict[str, bool],
    pet_policy: Dict[str, bool],
) -> AmenityScores:
    outdoor_score = score_outdoor_brand(outdoor_features, unique_outdoor_features)
    ev_score, ev_note = score_ev_readiness(
        existing_ev_stalls=int(ev_data.get("existing_ev_stalls", 0)),
        total_stalls=int(ev_data.get("total_stalls", 0)),
        ev_ready_conduit=bool(ev_data.get("ev_ready_conduit", False)),
        planned_retrofit_cost=ev_data.get("planned_retrofit_cost"),
    )
    remote_score = score_remote_work(remote_work_features, monetization_potential)
    pet_score = score_pet_friendliness(pet_features, pet_policy)

    return AmenityScores(
        outdoor_brand_score=outdoor_score,
        ev_readiness_score=ev_score,
        remote_work_score=remote_score,
        pet_friendliness_score=pet_score,
        notes={"ev": ev_note},
    )

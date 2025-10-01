"""Unit mix optimization recommendations for Aker assets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class UnitMixRecommendation:
    mix: Dict[str, float]
    rationale: str
    target_audience: str


class UnitMixOptimizer:
    """Recommend unit mixes based on submarket characteristics."""

    def recommend(
        self, market_data: Dict[str, float | bool | str]
    ) -> UnitMixRecommendation:
        job_core = (
            bool(market_data.get("job_core"))
            or market_data.get("daytime_population_index", 0) > 120
        )
        family_node = (
            market_data.get("family_age_cohort_index", 0) > 110
            and market_data.get("schools_rating", 0) >= 7
        )
        outdoor_access = market_data.get("outdoor_access_score", 0) >= 70
        high_rent_burden = market_data.get("rent_burden", 0) >= 35
        inclusionary = market_data.get("inclusionary_zoning", False)

        if job_core and not family_node:
            mix = {"studio": 0.3, "one_bed": 0.4, "two_bed": 0.25, "three_bed": 0.05}
            rationale = (
                "Proximity to job core favors compact units for young professionals."
            )
            target = "Singles, couples, weekday commuters"
        elif family_node or (
            outdoor_access and market_data.get("remote_worker_share", 0) > 25
        ):
            mix = {"studio": 0.1, "one_bed": 0.3, "two_bed": 0.4, "three_bed": 0.2}
            rationale = "Family and remote-work node supports larger floor plans and flex space."
            target = "Families, remote workers, active lifestyle residents"
        else:
            mix = {"studio": 0.2, "one_bed": 0.4, "two_bed": 0.3, "three_bed": 0.1}
            rationale = "Balanced submarket supports diversified unit mix."
            target = "Blend of workforce, couples, and small families"

        if high_rent_burden or inclusionary:
            mix["studio"] += 0.05
            mix["one_bed"] += 0.05
            mix["two_bed"] -= 0.05
            mix["three_bed"] -= 0.05
            rationale += (
                " Adjusted for affordability targets and inclusionary requirements."
            )

        # Ensure totals sum to 1.0 after adjustments
        total = sum(mix.values())
        mix = {k: round(v / total, 2) for k, v in mix.items()}
        return UnitMixRecommendation(
            mix=mix, rationale=rationale, target_audience=target
        )

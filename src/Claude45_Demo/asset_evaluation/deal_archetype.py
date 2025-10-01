"""Deal archetype classification for multifamily opportunities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ArchetypeResult:
    archetype: str
    score: int
    rent_lift_range: tuple[int, int] | None
    payback_years: float | None
    scope_summary: List[str]
    risk_notes: List[str]


class DealArchetypeClassifier:
    """Classify deals into Aker archetypes (value-add, heavy lift, ground-up)."""

    def classify(self, property_data: Dict[str, Any]) -> ArchetypeResult:
        """Return archetype classification with scope, ROI guidance, and risks."""

        year_built = property_data.get("year_built")
        occupancy = property_data.get("occupancy", 0)
        deferred_maintenance = property_data.get("deferred_maintenance_score", 0)
        systems_condition = property_data.get("systems_condition", "good").lower()
        is_vacant_land = property_data.get("is_vacant_land", False)
        is_ground_up = property_data.get("is_new_construction", False)
        location_type = property_data.get("location_type", "unknown")
        yield_on_cost = property_data.get("yield_on_cost")
        stabilized_cap = property_data.get("stabilized_cap_rate")
        entitlement_complexity = property_data.get("entitlement_complexity", "medium")

        # Ground-up detection first
        if is_vacant_land or is_ground_up:
            spread = None
            if yield_on_cost and stabilized_cap:
                spread = (yield_on_cost - stabilized_cap) * 100
            risk_notes = []
            if entitlement_complexity in {"high", "complex"}:
                risk_notes.append("Entitlement complexity high")
            if spread is not None and spread < 1.5:
                risk_notes.append("Yield-on-cost spread below 150 bps target")

            return ArchetypeResult(
                archetype="ground_up_infill",
                score=70 if not risk_notes else 55,
                rent_lift_range=None,
                payback_years=None,
                scope_summary=[
                    "Assess entitlement timeline",
                    "Model yield-on-cost vs stabilized cap spread",
                    "Evaluate placemaking retail component",
                ],
                risk_notes=risk_notes or ["Standard entitlement risk"],
            )

        # Determine value-add light vs medium vs heavy
        vintage = year_built or 0
        risk_notes: List[str] = []

        if 1985 <= vintage <= 2015 and occupancy >= 0.85 and deferred_maintenance <= 3:
            scope = [
                "Interior refresh (LVP, counters, lighting)",
                "Smart tech + access control",
                "Common area cosmetics",
            ]
            rent_lift = (90, 180)
            payback = 4.0
            score = 85
            archetype = "value_add_light"
        elif (
            occupancy >= 0.7
            and deferred_maintenance <= 6
            and systems_condition in {"fair", "good"}
        ):
            scope = [
                "Comprehensive unit renovation",
                "Systems tune-up (HVAC, plumbing)",
                "Amenity program + exterior refresh",
            ]
            rent_lift = (150, 250)
            payback = 5.5
            score = 75
            archetype = "value_add_medium"
            if systems_condition == "fair":
                risk_notes.append("Systems upgrades required")
        else:
            scope = [
                "Major systems replacement",
                "Envelope repair + rebrand",
                "Unit reconfiguration / space planning",
            ]
            rent_lift = (180, 280)
            payback = 6.5
            score = 60
            archetype = "heavy_lift_reposition"
            if occupancy < 0.6:
                risk_notes.append("Low occupancy - extended downtime")
            if deferred_maintenance > 7:
                risk_notes.append("Significant deferred maintenance backlog")

        if location_type in {"town_center", "urban_node"}:
            score += 5
        if property_data.get("reputation_score", 70) < 50:
            risk_notes.append("Reputation rebuild required")

        score = max(30, min(95, score))

        return ArchetypeResult(
            archetype=archetype,
            score=score,
            rent_lift_range=rent_lift,
            payback_years=payback,
            scope_summary=scope,
            risk_notes=risk_notes,
        )

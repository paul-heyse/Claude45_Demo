"""Parking ratio recommendations based on location and transit context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ParkingRecommendation:
    recommended_ratio: float
    rationale: str
    zoning_check: str


class ParkingAdvisor:
    """Recommend parking ratios aligned with Aker's infill vs suburban thesis."""

    def recommend(self, data: Dict[str, float | bool | str]) -> ParkingRecommendation:
        location_type = data.get("location_type", "suburban")
        transit_headway = data.get("transit_headway_minutes")
        acs_vehicle_per_household = data.get("acs_vehicle_per_household", 1.5)
        zoning_minimum = data.get("zoning_minimum", 1.0)
        unbundled_parking = data.get("unbundled_parking", False)

        if location_type in {"urban_core", "infill"}:
            base_ratio = 0.65
        elif location_type in {"town_center", "transit_node"}:
            base_ratio = 0.8
        else:
            base_ratio = 1.2

        if transit_headway is not None and transit_headway <= 15:
            base_ratio -= 0.15
        if acs_vehicle_per_household < 1.0:
            base_ratio -= 0.1
        if unbundled_parking:
            base_ratio -= 0.05

        base_ratio = max(0.4, round(base_ratio, 2))

        rationale_parts = [
            f"Location type {location_type} baseline",
            f"Transit headway {transit_headway or 'unknown'} min",
            f"ACS vehicles/HH {acs_vehicle_per_household:.2f}",
        ]
        if unbundled_parking:
            rationale_parts.append("Unbundled parking allows lower ratio")

        zoning_note = "Meets zoning minimum"
        if base_ratio < zoning_minimum:
            zoning_note = (
                "Below zoning minimum - pursue shared parking agreement or variance"
            )

        return ParkingRecommendation(
            recommended_ratio=base_ratio,
            rationale="; ".join(rationale_parts),
            zoning_check=zoning_note,
        )

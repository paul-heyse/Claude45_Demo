"""FEMA flood risk analytics utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping, Optional

HIGH_RISK_ZONES = {"A", "AE", "AO", "AH", "VE", "V"}


@dataclass(frozen=True)
class FloodZoneResult:
    zone: str
    risk_category: str
    sfha: Optional[bool]
    risk_score: int
    base_flood_elevation: Optional[float]


class FEMAFloodAnalyzer:
    """Provide lightweight FEMA flood risk analytics for testing purposes."""

    def classify_flood_zone(
        self,
        *,
        latitude: float,
        longitude: float,
        mock_response: Mapping,
    ) -> Mapping[str, Optional[float]]:
        features = mock_response.get("features", []) if mock_response else []
        if not features:
            return {
                "zone": "UNMAPPED",
                "risk_category": "unknown",
                "sfha": None,
                "risk_score": 50,
                "base_flood_elevation": None,
            }

        props = features[0].get("properties", {})
        zone = (props.get("FLD_ZONE") or "UNMAPPED").strip().upper()
        sub_type = (props.get("ZONE_SUBTY") or "").upper()
        sfha_flag = props.get("SFHA_TF")
        base_flood_elevation = props.get("STATIC_BFE")

        if zone in HIGH_RISK_ZONES or sfha_flag == "T":
            risk_category = "high"
            sfha = True
            risk_score = 90
        elif zone == "X" and "0.2" in sub_type:
            risk_category = "moderate"
            sfha = False
            risk_score = 50
        elif zone == "X":
            risk_category = "minimal"
            sfha = False
            risk_score = 20
        else:
            risk_category = "unknown"
            sfha = None
            risk_score = 50

        return {
            "zone": zone,
            "risk_category": risk_category,
            "sfha": sfha,
            "risk_score": risk_score,
            "base_flood_elevation": base_flood_elevation,
        }

    def estimate_flood_insurance(
        self,
        *,
        flood_data: Mapping,
        building_elevation: Optional[float],
        replacement_cost: float,
    ) -> Mapping[str, object]:
        base_bfe = flood_data.get("base_flood_elevation")
        sfha = flood_data.get("sfha", False)
        freeboard_ft: Optional[float] = None
        if base_bfe is not None and building_elevation is not None:
            freeboard_ft = round(building_elevation - base_bfe, 1)

        if sfha:
            premium = max(1000.0, replacement_cost * 0.004)
            if freeboard_ft is not None:
                if freeboard_ft >= 0:
                    discount = min(0.12 * freeboard_ft, 0.5)
                    premium *= 1 - discount
                    premium = min(premium, max(500.0, replacement_cost * 0.003))
                    discount_applied = discount > 0
                else:
                    surcharge = min(abs(freeboard_ft) * 0.25, 1.0)
                    premium *= 1 + surcharge
                    discount_applied = False
            else:
                discount_applied = False
            policy_type = "Standard"
        else:
            premium = 400.0
            discount_applied = False
            policy_type = "Preferred Risk"

        premium_pct = premium / replacement_cost * 100 if replacement_cost else 0.0

        return {
            "annual_premium": round(premium, 2),
            "premium_pct": premium_pct,
            "nfip_eligible": True,
            "policy_type": policy_type,
            "freeboard_ft": freeboard_ft,
            "discount_applied": discount_applied,
            "notes": "Risk Rating 2.0 guidance applied",
        }

    def analyze_historical_floods(
        self,
        *,
        county_fips: str,
        lookback_years: int,
        mock_events: Iterable[Mapping],
    ) -> Mapping[str, object]:
        events = list(mock_events)
        event_count = len(events)
        major_events = sum(
            1 for event in events if event.get("severity", "").lower() == "major"
        )
        chronic_flooding = event_count >= 4
        historical_score = min(100, event_count * 15 + major_events * 10)

        return {
            "event_count": event_count,
            "chronic_flooding": chronic_flooding,
            "presidential_declarations": major_events,
            "historical_score": historical_score,
        }

    def assess_dam_levee_risk(
        self,
        *,
        latitude: float,
        longitude: float,
        search_radius_km: float,
        mock_dams: Iterable[Mapping],
    ) -> Mapping[str, object]:
        dams = list(mock_dams)
        high_hazard = [
            dam
            for dam in dams
            if dam.get("hazard_class") == "H"
            and dam.get("distance_km", 0) <= search_radius_km
        ]

        risk_flag = bool(high_hazard)
        risk_adjustment = 15 * len(high_hazard)
        notes: List[str] = []
        if high_hazard:
            dam = high_hazard[0]
            notes.append(
                f"{dam.get('dam_name', 'Dam')} - {dam.get('condition', 'Unknown')} condition"
            )

        return {
            "high_hazard_dams_nearby": len(high_hazard),
            "risk_flag": risk_flag,
            "risk_adjustment": risk_adjustment,
            "notes": "; ".join(notes) if notes else "",
        }

"""Deal diligence checklist generator."""

from __future__ import annotations

from typing import Dict, List


class DiligenceChecklistBuilder:
    """Generate diligence checklists based on archetype and risk profile."""

    def build(
        self,
        *,
        archetype: str,
        product_type: str,
        risk_flags: Dict[str, bool],
        include_ev: bool,
    ) -> Dict[str, List[str]]:
        sections: Dict[str, List[str]] = {
            "physical": [
                "Roof age and condition",
                "HVAC age and SEER rating",
                "Plumbing leaks and water pressure",
                "Envelope (windows, siding, insulation)",
            ],
            "financial": [
                "T-12 P&L and rent roll reconciliation",
                "Lease audit (terms, expirations, concessions)",
                "Utility recovery and RUBS analysis",
            ],
            "operations": [
                "Lead sources and conversion funnel",
                "Renewal reasons and exit surveys",
                "Turnover cost benchmarking",
            ],
            "reputation": [
                "Online review analysis (volume + rating)",
                "BBB complaints",
                "Resident NPS and survey cadence",
            ],
        }

        if archetype.startswith("value_add"):
            sections["physical"].append("Scope interior upgrade pricing per unit")
            sections["financial"].append("Validate rent lift assumptions ($90-$180/mo)")
        if archetype == "ground_up_infill":
            sections["entitlement"] = [
                "Confirm zoning and design review milestones",
                "Assess inclusionary housing requirements",
                "Review geotech and Phase I ESA reports",
                "Utility capacity and tap fee estimates",
            ]
        if risk_flags.get("wildfire") or risk_flags.get("flood"):
            sections.setdefault("risk_mitigation", []).extend(
                [
                    "Insurance quotes from 3+ carriers",
                    "Mitigation plan (defensible space, flood elevation)",
                    "Emergency preparedness + resident comms",
                ]
            )
        if include_ev:
            sections.setdefault("amenities", []).append(
                "EV retrofit feasibility and cost"
            )
        sections.setdefault("amenities", []).append(
            "Bike storage / dog run feasibility study"
        )

        return sections

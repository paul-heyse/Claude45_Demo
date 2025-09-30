"""CapEx scope and ROI estimation utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ROIResult:
    capex_per_unit: float
    rent_lift: float
    payback_years: float
    notes: str


class CapexEstimator:
    """Estimate ROI for various value-add improvement scopes."""

    def estimate_interior_upgrade(self, unit_sqft: float, scope: Dict[str, bool]) -> ROIResult:
        base_cost = 0.0
        if scope.get("lvp", True):
            base_cost += unit_sqft * 5.0
        if scope.get("countertops", True):
            base_cost += 3500
        if scope.get("lighting", True):
            base_cost += 300
        if scope.get("appliances", False):
            base_cost += 2500

        rent_lift = scope.get("expected_rent_lift", 150)
        payback = base_cost / (rent_lift * 12) if rent_lift else float("inf")
        return ROIResult(
            capex_per_unit=round(base_cost, 2),
            rent_lift=rent_lift,
            payback_years=round(payback, 2),
            notes="Interior scope aligned with value-add light playbook",
        )

    def estimate_common_area_refresh(self, enhancements: Dict[str, bool]) -> ROIResult:
        cost = 0.0
        if enhancements.get("lobby", True):
            cost += 50_000
        if enhancements.get("fitness", True):
            cost += 30_000
        if enhancements.get("package_lockers", True):
            cost += 15_000
        if enhancements.get("signage", True):
            cost += 20_000

        rent_premium = enhancements.get("rent_premium", 30)
        retention_lift = enhancements.get("retention_lift_bps", 150) / 10000
        rent_lift_dollars = rent_premium * 12
        avoided_turnover = retention_lift * 1_200_000  # Example NOI impact for 200 units
        payback = cost / (rent_lift_dollars + avoided_turnover / 5)
        return ROIResult(
            capex_per_unit=round(cost / enhancements.get("unit_count", 200), 2),
            rent_lift=rent_premium,
            payback_years=round(payback, 2),
            notes="Common area refresh improves retention and velocity",
        )

    def estimate_systems_upgrade(self, data: Dict[str, float]) -> ROIResult:
        hvac_cost = data.get("hvac_cost", 1500)
        plumbing_cost = data.get("plumbing_cost", 1200)
        roof_cost = data.get("roof_cost", 900)
        utility_savings = data.get("utility_savings_per_unit", 25)
        avoided_repairs = data.get("avoided_repairs_per_unit", 15)

        total_cost = hvac_cost + plumbing_cost + roof_cost
        annual_benefit = (utility_savings + avoided_repairs) * 12
        payback = total_cost / annual_benefit if annual_benefit else float("inf")
        return ROIResult(
            capex_per_unit=round(total_cost, 2),
            rent_lift=utility_savings,
            payback_years=round(payback, 2),
            notes="Systems upgrade reduces emergency repairs and utilities",
        )

    def estimate_sustainability_roi(self, data: Dict[str, float]) -> ROIResult:
        project_cost = data.get("project_cost_per_unit", 2500)
        utility_savings = data.get("utility_savings_per_month", 18)
        marketing_uplift = data.get("marketing_uplift_rent", 15)
        total_monthly_benefit = utility_savings + marketing_uplift
        payback = project_cost / (total_monthly_benefit * 12) if total_monthly_benefit else float("inf")
        return ROIResult(
            capex_per_unit=project_cost,
            rent_lift=marketing_uplift,
            payback_years=round(payback, 2),
            notes="Sustainability improvements support green positioning",
        )

    def estimate_rent_lift_from_scope(self, archetype: str, scope_intensity: str) -> tuple[int, int]:
        baseline = {
            "value_add_light": (90, 180),
            "value_add_medium": (150, 250),
            "heavy_lift_reposition": (200, 320),
        }
        range_default = baseline.get(archetype, (80, 160))
        if scope_intensity == "high":
            return (int(range_default[0] * 1.1), int(range_default[1] * 1.1))
        if scope_intensity == "low":
            return (int(range_default[0] * 0.8), int(range_default[1] * 0.85))
        return range_default

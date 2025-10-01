"""Operations model support utilities for the asset evaluation module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class NPSImpact:
    nps_score: int
    concession_reduction_bps: int
    pricing_power_bps: int


@dataclass(frozen=True)
class ProgrammingBudget:
    annual_budget: float
    budget_per_door: float
    kpis: Dict[str, str]


@dataclass(frozen=True)
class LeaseUpForecast:
    baseline_days_to_lease: int
    adjusted_days_to_lease: int
    carrying_cost_savings: float


class OperationsSupport:
    """Model NPS, programming, and lease-up benefits tied to Aker brand."""

    def calculate_nps_impact(
        self,
        *,
        review_scores: Dict[str, float],
        before_after: Dict[str, float],
    ) -> NPSImpact:
        current_nps = round(
            sum(review_scores.values()) / len(review_scores) if review_scores else 0
        )
        lift = before_after.get("after", 0) - before_after.get("before", 0)
        concession_reduction = int(max(0, lift / 10) * 25)
        pricing_power = int(max(0, lift / 10) * 20)
        return NPSImpact(
            nps_score=current_nps,
            concession_reduction_bps=concession_reduction,
            pricing_power_bps=pricing_power,
        )

    def recommend_programming_budget(
        self,
        *,
        unit_count: int,
        engagement_level: str,
    ) -> ProgrammingBudget:
        base_per_door = 75.0
        if engagement_level == "high":
            base_per_door = 100.0
        elif engagement_level == "low":
            base_per_door = 50.0
        budget = base_per_door * unit_count
        kpis = {
            "renewal_rate": "Target +200 bps",
            "review_volume": "Increase 20% YoY",
            "referrals": "Track share of new leases from referrals",
        }
        return ProgrammingBudget(
            annual_budget=budget, budget_per_door=base_per_door, kpis=kpis
        )

    def estimate_lease_up_velocity(
        self,
        *,
        baseline_days_to_lease: int,
        brand_bonus_pct: float,
        carrying_cost_per_day: float,
    ) -> LeaseUpForecast:
        adjusted_days = int(baseline_days_to_lease * (1 - brand_bonus_pct))
        adjusted_days = max(10, adjusted_days)
        savings = (baseline_days_to_lease - adjusted_days) * carrying_cost_per_day
        return LeaseUpForecast(
            baseline_days_to_lease=baseline_days_to_lease,
            adjusted_days_to_lease=adjusted_days,
            carrying_cost_savings=round(savings, 2),
        )

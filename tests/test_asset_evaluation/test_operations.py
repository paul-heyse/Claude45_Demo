"""Tests for operations support utilities."""

from Claude45_Demo.asset_evaluation.operations import OperationsSupport


def test_nps_impact_calculates_concession_reduction() -> None:
    ops = OperationsSupport()
    impact = ops.calculate_nps_impact(
        review_scores={"google": 4.4, "yelp": 3.8, "apartments": 4.0},
        before_after={"before": 40, "after": 55},
    )

    assert impact.nps_score > 0
    assert impact.concession_reduction_bps >= 25


def test_programming_budget_and_kpis() -> None:
    ops = OperationsSupport()
    budget = ops.recommend_programming_budget(unit_count=220, engagement_level="high")

    assert budget.annual_budget == 22000.0
    assert "renewal_rate" in budget.kpis


def test_lease_up_velocity_improves_timeline() -> None:
    ops = OperationsSupport()
    forecast = ops.estimate_lease_up_velocity(
        baseline_days_to_lease=120,
        brand_bonus_pct=0.15,
        carrying_cost_per_day=320,
    )

    assert forecast.adjusted_days_to_lease < forecast.baseline_days_to_lease
    assert forecast.carrying_cost_savings > 0

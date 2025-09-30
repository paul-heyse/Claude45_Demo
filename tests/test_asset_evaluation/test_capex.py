"""Tests for CapEx estimator functions."""

from Claude45_Demo.asset_evaluation.capex import CapexEstimator


def test_interior_upgrade_roi() -> None:
    estimator = CapexEstimator()
    result = estimator.estimate_interior_upgrade(
        unit_sqft=820,
        scope={"lvp": True, "countertops": True, "lighting": True, "expected_rent_lift": 160},
    )

    assert 6000 <= result.capex_per_unit <= 12000
    assert 3 <= result.payback_years <= 5


def test_common_area_refresh_returns_budget_per_unit() -> None:
    estimator = CapexEstimator()
    result = estimator.estimate_common_area_refresh({"unit_count": 180})

    assert result.capex_per_unit > 0
    assert result.payback_years > 0


def test_rent_lift_range_adjusts_for_scope() -> None:
    estimator = CapexEstimator()
    high = estimator.estimate_rent_lift_from_scope("value_add_light", "high")
    low = estimator.estimate_rent_lift_from_scope("value_add_medium", "low")

    assert high[0] > 90
    assert low[1] < 250

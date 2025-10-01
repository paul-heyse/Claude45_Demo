"""Tests for construction cost adjustments."""

from __future__ import annotations

from datetime import date

import pytest

from Claude45_Demo.asset_evaluation.construction import ConstructionAdjuster


@pytest.fixture
def adjuster():
    """Create construction adjuster."""
    return ConstructionAdjuster()


def test_winter_premium_no_winter_months(adjuster):
    """Test no premium when construction avoids winter."""
    result = adjuster.adjust_winter_premium(
        start_date=date(2024, 4, 1),  # April start
        end_date=date(2024, 10, 31),  # October end
        base_cost=5_000_000,
        location_type="mountain",
    )

    assert result.winter_months == 0
    assert result.premium_percentage == 0.0
    assert result.premium_amount == 0.0
    assert result.adjusted_cost == 5_000_000
    assert "no winter" in result.notes.lower()


def test_winter_premium_mountain_location(adjuster):
    """Test winter premium for mountain location."""
    result = adjuster.adjust_winter_premium(
        start_date=date(2024, 11, 1),  # Nov start
        end_date=date(2025, 3, 31),  # Mar end
        base_cost=5_000_000,
        location_type="mountain",
    )

    # 5 winter months: Nov, Dec, Jan, Feb, Mar
    assert result.winter_months == 5
    # Mountain: 10% base + 5 months * 2% = 20% (capped)
    assert result.premium_percentage == 0.20
    assert result.premium_amount == 1_000_000  # 20% of 5M
    assert result.adjusted_cost == 6_000_000
    assert "mountain" in result.notes.lower()
    assert "severe" in result.notes.lower()


def test_winter_premium_urban_location(adjuster):
    """Test lower winter premium for urban location."""
    result = adjuster.adjust_winter_premium(
        start_date=date(2024, 12, 1),
        end_date=date(2025, 2, 28),
        base_cost=3_000_000,
        location_type="urban",
    )

    # 3 winter months: Dec, Jan, Feb
    assert result.winter_months == 3
    # Urban: 5% base + 3 months * 1% = 8%
    assert result.premium_percentage == 0.08
    assert result.premium_amount == 240_000
    assert result.adjusted_cost == 3_240_000
    assert "urban" in result.notes.lower()


def test_winter_premium_partial_winter(adjuster):
    """Test premium for partial winter exposure."""
    result = adjuster.adjust_winter_premium(
        start_date=date(2024, 10, 1),  # Oct start
        end_date=date(2025, 1, 31),  # Jan end
        base_cost=4_000_000,
        location_type="suburban",
    )

    # 4 winter months: Nov, Dec, Jan (Oct is not winter)
    assert result.winter_months == 3
    # Suburban: 8% base + 3 months * 1.5% = 12.5%
    assert result.premium_percentage == 0.125
    assert result.premium_amount == 500_000
    assert result.adjusted_cost == 4_500_000


def test_logistics_premium_urban_proximity(adjuster):
    """Test minimal premium for urban-proximate site."""
    result = adjuster.calculate_logistics_premium(
        base_cost=5_000_000,
        distance_to_metro_miles=15,
        elevation_ft=5200,
        accessibility="paved",
        nearest_supplier_miles=10,
    )

    assert result.accessibility_rating == "urban"
    assert result.premium_percentage <= 0.03  # Minimal premium
    assert result.adjusted_cost < 5_200_000
    assert any("urban" in f.lower() for f in result.factors)


def test_logistics_premium_remote_mountain(adjuster):
    """Test high premium for remote mountain site."""
    result = adjuster.calculate_logistics_premium(
        base_cost=5_000_000,
        distance_to_metro_miles=120,  # Remote
        elevation_ft=8500,  # High elevation
        accessibility="4wd_only",  # Difficult access
        nearest_supplier_miles=60,  # Distant suppliers
    )

    assert result.accessibility_rating == "remote"
    assert result.premium_percentage >= 0.12  # Significant premium
    assert result.adjusted_cost > 5_600_000
    assert len(result.factors) >= 4  # Multiple factors contributing
    assert any("remote" in f.lower() for f in result.factors)
    assert any("4wd" in f.lower() for f in result.factors)


def test_logistics_premium_mountain_access(adjuster):
    """Test moderate premium for mountain access site."""
    result = adjuster.calculate_logistics_premium(
        base_cost=4_000_000,
        distance_to_metro_miles=65,
        elevation_ft=7200,
        accessibility="paved",
        nearest_supplier_miles=35,
    )

    assert result.accessibility_rating == "mountain_access"
    assert 0.05 <= result.premium_percentage <= 0.10
    assert result.adjusted_cost > 4_200_000
    assert "mountain" in " ".join(result.factors).lower()


def test_logistics_premium_elevation_impact(adjuster):
    """Test elevation-specific premium."""
    # Low elevation
    low_result = adjuster.calculate_logistics_premium(
        base_cost=5_000_000,
        distance_to_metro_miles=30,
        elevation_ft=5000,
        accessibility="paved",
    )

    # High elevation
    high_result = adjuster.calculate_logistics_premium(
        base_cost=5_000_000,
        distance_to_metro_miles=30,
        elevation_ft=9000,
        accessibility="paved",
    )

    # High elevation should have higher premium
    assert high_result.premium_percentage > low_result.premium_percentage
    assert any("elevation" in f.lower() for f in high_result.factors)


def test_labor_market_tight_market(adjuster):
    """Test high-risk assessment for tight labor market."""
    result = adjuster.assess_labor_market(
        unemployment_rate=0.02,  # 2.0% - very tight
        construction_employment_change=0.08,  # 8% growth
        state="ID",
    )

    assert result.risk_level == "high"
    assert result.risk_score >= 60
    assert result.wage_premium_pct >= 0.20  # 20%+ wage premium
    assert "high risk" in result.recommendation.lower()


def test_labor_market_adequate_supply(adjuster):
    """Test low-risk assessment for adequate labor supply."""
    result = adjuster.assess_labor_market(
        unemployment_rate=0.045,  # 4.5% - adequate
        construction_employment_change=-0.01,  # -1% declining
        state="CO",
    )

    assert result.risk_level == "low"
    assert result.risk_score < 35
    assert result.wage_premium_pct < 0.10
    assert "low risk" in result.recommendation.lower()


def test_labor_market_moderate_risk(adjuster):
    """Test medium-risk assessment."""
    result = adjuster.assess_labor_market(
        unemployment_rate=0.028,  # 2.8% - tight
        construction_employment_change=0.04,  # 4% growth
        state="UT",
    )

    assert result.risk_level == "medium"
    assert 35 <= result.risk_score < 60
    assert 0.08 <= result.wage_premium_pct <= 0.20
    assert "medium risk" in result.recommendation.lower()


def test_labor_market_state_specific_adjustments(adjuster):
    """Test state-specific risk adjustments."""
    # Idaho (highest growth)
    id_result = adjuster.assess_labor_market(
        unemployment_rate=0.03,
        construction_employment_change=0.0,
        state="ID",
    )

    # Colorado (baseline)
    co_result = adjuster.assess_labor_market(
        unemployment_rate=0.03,
        construction_employment_change=0.0,
        state="CO",
    )

    # Idaho should have higher risk score due to in-migration
    assert id_result.risk_score > co_result.risk_score
    assert id_result.wage_premium_pct > co_result.wage_premium_pct


def test_labor_market_employment_trend_impact(adjuster):
    """Test impact of construction employment trends."""
    # Growing employment (high demand)
    growth_result = adjuster.assess_labor_market(
        unemployment_rate=0.035,
        construction_employment_change=0.07,  # 7% growth
        state="CO",
    )

    # Declining employment (lower demand)
    decline_result = adjuster.assess_labor_market(
        unemployment_rate=0.035,
        construction_employment_change=-0.03,  # -3% decline
        state="CO",
    )

    # Growth should indicate higher risk
    assert growth_result.risk_score > decline_result.risk_score
    assert growth_result.wage_premium_pct > decline_result.wage_premium_pct


def test_winter_premium_year_boundary(adjuster):
    """Test winter premium calculation crossing year boundary."""
    result = adjuster.adjust_winter_premium(
        start_date=date(2024, 11, 15),
        end_date=date(2025, 2, 15),
        base_cost=2_000_000,
        location_type="mountain",
    )

    # Should count Nov, Dec, Jan, Feb
    assert result.winter_months == 4
    assert result.premium_percentage > 0
    assert result.adjusted_cost > 2_000_000


def test_logistics_premium_capped_at_15_percent(adjuster):
    """Test that logistics premium is capped at 15%."""
    result = adjuster.calculate_logistics_premium(
        base_cost=10_000_000,
        distance_to_metro_miles=200,  # Extreme distance
        elevation_ft=10000,  # Very high
        accessibility="4wd_only",
        nearest_supplier_miles=100,
    )

    # Should be capped at 15%
    assert result.premium_percentage <= 0.15
    assert result.adjusted_cost <= 11_500_000


def test_labor_market_risk_score_bounds(adjuster):
    """Test that risk score stays within 0-100 bounds."""
    # Extremely tight market
    result = adjuster.assess_labor_market(
        unemployment_rate=0.015,  # 1.5% - extremely tight
        construction_employment_change=0.15,  # 15% growth
        state="ID",
    )

    assert 0 <= result.risk_score <= 100
    assert 0.0 <= result.wage_premium_pct <= 0.25


def test_construction_adjustments_integration(adjuster):
    """Test combined construction adjustments."""
    # Mountain site, winter construction, tight labor
    winter_result = adjuster.adjust_winter_premium(
        start_date=date(2024, 11, 1),
        end_date=date(2025, 4, 30),
        base_cost=5_000_000,
        location_type="mountain",
    )

    logistics_result = adjuster.calculate_logistics_premium(
        base_cost=winter_result.adjusted_cost,  # Apply on top of winter premium
        distance_to_metro_miles=80,
        elevation_ft=8000,
        accessibility="dirt_road",
    )

    labor_result = adjuster.assess_labor_market(
        unemployment_rate=0.028,
        construction_employment_change=0.05,
        state="ID",
    )

    # Verify all adjustments increase costs
    assert winter_result.adjusted_cost > 5_000_000
    assert logistics_result.adjusted_cost > winter_result.adjusted_cost
    assert labor_result.wage_premium_pct > 0
    assert labor_result.risk_level in {"medium", "high"}

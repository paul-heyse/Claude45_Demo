"""Tests for supply constraint calculator."""

import pytest

from Claude45_Demo.market_analysis.supply_constraint import SupplyConstraintCalculator


@pytest.fixture
def calculator() -> SupplyConstraintCalculator:
    """Create supply constraint calculator for testing."""
    return SupplyConstraintCalculator()


def test_calculate_permit_elasticity(calculator: SupplyConstraintCalculator) -> None:
    """Test basic permit elasticity calculation."""
    score = calculator.calculate_permit_elasticity(
        annual_permits=[450, 480, 520],
        total_households=120_000,
        vacancy_rate=0.03,
        median_time_on_market_days=15,
    )
    assert 70 <= score <= 100
    assert isinstance(score, float)


def test_calculate_topographic_constraint(
    calculator: SupplyConstraintCalculator,
) -> None:
    """Test topographic constraint calculation."""
    score = calculator.calculate_topographic_constraint(
        slope_pct_steep=45.0,
        protected_land_pct=35.0,
        floodplain_pct=8.0,
        wetland_buffer_pct=3.0,
        airport_restriction_pct=0.0,
    )
    assert 70 <= score <= 100


def test_calculate_regulatory_friction(calculator: SupplyConstraintCalculator) -> None:
    """Test regulatory friction calculation."""
    score = calculator.calculate_regulatory_friction(
        median_permit_to_coo_days=540,
        has_inclusionary_zoning=True,
        has_design_review=True,
        has_parking_minimums=True,
        has_utility_moratorium=False,
    )
    assert 60 <= score <= 100


def test_calculate_composite_score(calculator: SupplyConstraintCalculator) -> None:
    """Test composite score calculation."""
    composite = calculator.calculate_composite_score(
        permit_elasticity=75.0,
        topographic_constraint=80.0,
        regulatory_friction=70.0,
    )
    assert "score" in composite
    assert 70 <= composite["score"] <= 80
    assert composite["metadata"]["complete"] is True

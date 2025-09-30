"""Tests for market elasticity calculator."""

import pytest

from Claude45_Demo.market_analysis.elasticity import MarketElasticityCalculator


@pytest.fixture
def calculator() -> MarketElasticityCalculator:
    """Create market elasticity calculator for testing."""
    return MarketElasticityCalculator()


def test_vacancy_score(calculator: MarketElasticityCalculator) -> None:
    """Test vacancy rate scoring."""
    result = calculator.calculate_vacancy_score(
        rental_vacancy_rate=0.04, state_avg_vacancy=0.06, national_avg_vacancy=0.065
    )
    assert 70 <= result["score"] <= 100
    assert result["comparisons"]["beats_state_avg"] is True


def test_absorption_score(calculator: MarketElasticityCalculator) -> None:
    """Test absorption rate scoring."""
    result = calculator.calculate_absorption_score(
        permits_3yr_avg=500, population_growth_3yr_pct=6.0, units_delivered_3yr=1500
    )
    assert 60 <= result["score"] <= 100
    assert result["metadata"]["proxy_estimate"] is True


def test_market_momentum_score(calculator: MarketElasticityCalculator) -> None:
    """Test market momentum scoring."""
    result = calculator.calculate_market_momentum_score(
        employment_3yr_cagr=0.025, population_3yr_cagr=0.02, income_3yr_cagr=0.022
    )
    assert 60 <= result["score"] <= 90
    assert "cagr_values" in result

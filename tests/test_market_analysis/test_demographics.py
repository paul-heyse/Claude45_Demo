"""Tests for demographic analyzer."""

import pytest

from Claude45_Demo.market_analysis.demographics import DemographicAnalyzer


@pytest.fixture
def analyzer() -> DemographicAnalyzer:
    """Create demographic analyzer for testing."""
    return DemographicAnalyzer()


def test_population_growth_score(analyzer: DemographicAnalyzer) -> None:
    """Test population growth scoring."""
    result = analyzer.calculate_population_growth_score(
        population_5yr_cagr=0.025,
        population_10yr_cagr=0.02,
        state_avg_5yr_cagr=0.015,
        age_25_44_pct=28.0,
    )
    assert 70 <= result["score"] <= 100
    assert result["components"]["outpace_state"] is True


def test_income_trend_score(analyzer: DemographicAnalyzer) -> None:
    """Test income trend scoring."""
    result = analyzer.calculate_income_trend_score(
        median_hh_income=70000.0, income_5yr_cagr=0.025, cost_of_living_index=105.0
    )
    assert 60 <= result["score"] <= 90


def test_migration_score(analyzer: DemographicAnalyzer) -> None:
    """Test migration pattern scoring."""
    result = analyzer.calculate_migration_score(
        net_migration_3yr=5000, population=200000, avg_agi_per_migrant=65000.0
    )
    assert 50 <= result["score"] <= 100
    assert "migration_rate_pct" in result["metrics"]

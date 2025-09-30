"""Tests for risk multiplier calculation."""

from __future__ import annotations

import pytest


def test_high_risk_multiplier(risk_calculator):
    """Test high risk (1.1 multiplier)."""
    scores = {
        "wildfire_score": 95,
        "flood_score": 85,
        "regulatory_score": 80,
        "insurance_score": 90,
    }

    result = risk_calculator.calculate_risk_multiplier(scores)

    assert result["risk_multiplier"] >= 1.05  # High risk
    assert result["cap_rate_adjustment_bps"] > 0


def test_baseline_risk_multiplier(risk_calculator):
    """Test baseline risk (1.0 multiplier)."""
    scores = {
        "wildfire_score": 50,
        "flood_score": 50,
        "regulatory_score": 50,
        "insurance_score": 50,
    }

    result = risk_calculator.calculate_risk_multiplier(scores)

    assert 0.98 <= result["risk_multiplier"] <= 1.02


def test_extreme_risk_exclusion(risk_calculator):
    """Test market exclusion flag for extreme risk."""
    scores = {
        "wildfire_score": 95,
        "flood_score": 92,
        "regulatory_score": 60,
        "insurance_score": 85,
    }

    result = risk_calculator.calculate_risk_multiplier(scores)

    assert result["exclude_market"] is True


@pytest.fixture
def risk_calculator():
    """Create RiskMultiplierCalculator instance for testing."""
    from Claude45_Demo.risk_assessment.risk_multiplier import RiskMultiplierCalculator

    return RiskMultiplierCalculator()

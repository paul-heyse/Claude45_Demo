"""Tests for weighted scoring engine."""

import pytest

from Claude45_Demo.scoring_engine.scoring_engine import ScoringEngine


@pytest.fixture
def engine() -> ScoringEngine:
    """Create scoring engine for testing."""
    return ScoringEngine()


def test_calculate_weighted_score_default_weights(engine: ScoringEngine) -> None:
    """
    Scenario: Default weighted score calculation
    WHEN the system calculates final score for a submarket
    THEN it applies weights: Supply 30%, Jobs 30%, Urban 20%, Outdoor 20%
    """
    component_scores = {
        "supply_constraint": 85.0,
        "innovation_employment": 75.0,
        "urban_convenience": 80.0,
        "outdoor_access": 90.0,
    }

    result = engine.calculate_composite_score(component_scores)

    # Weighted: 0.3*85 + 0.3*75 + 0.2*80 + 0.2*90 = 25.5 + 22.5 + 16 + 18 = 82
    assert "score" in result
    assert 81 <= result["score"] <= 83
    assert result["metadata"]["complete"] is True


def test_calculate_weighted_score_custom_weights(engine: ScoringEngine) -> None:
    """
    Scenario: Custom weight configuration
    WHEN a user specifies custom weights
    THEN the system validates weights sum to 100%
    """
    component_scores = {
        "supply_constraint": 90.0,
        "innovation_employment": 60.0,
        "urban_convenience": 70.0,
        "outdoor_access": 80.0,
    }

    custom_weights = {
        "supply_constraint": 0.50,  # Emphasize supply
        "innovation_employment": 0.30,
        "urban_convenience": 0.10,
        "outdoor_access": 0.10,
    }

    result = engine.calculate_composite_score(component_scores, weights=custom_weights)

    # Weighted: 0.5*90 + 0.3*60 + 0.1*70 + 0.1*80 = 45 + 18 + 7 + 8 = 78
    assert 77 <= result["score"] <= 79


def test_handles_missing_components(engine: ScoringEngine) -> None:
    """
    Scenario: Missing component handling
    WHEN one or more component scores are unavailable
    THEN the system redistributes missing component's weight proportionally
    """
    component_scores = {
        "supply_constraint": 80.0,
        "innovation_employment": 70.0,
        "urban_convenience": None,  # Missing
        "outdoor_access": None,  # Missing
    }

    result = engine.calculate_composite_score(component_scores)

    # Should redistribute weights and mark as partial
    assert "score" in result
    assert result["metadata"]["complete"] is False
    assert "urban_convenience" in result["metadata"]["missing_components"]
    assert "outdoor_access" in result["metadata"]["missing_components"]


def test_validates_weight_sum(engine: ScoringEngine) -> None:
    """Weights must sum to approximately 1.0."""
    component_scores = {
        "supply_constraint": 80.0,
        "innovation_employment": 70.0,
        "urban_convenience": 75.0,
        "outdoor_access": 85.0,
    }

    invalid_weights = {
        "supply_constraint": 0.40,
        "innovation_employment": 0.40,
        "urban_convenience": 0.10,
        "outdoor_access": 0.05,  # Sum = 0.95, not 1.0
    }

    with pytest.raises(ValueError, match="must sum to 1.0"):
        engine.calculate_composite_score(component_scores, weights=invalid_weights)


def test_applies_risk_multiplier(engine: ScoringEngine) -> None:
    """
    Scenario: Risk multiplier application
    WHEN the system applies risk adjustments to market score
    THEN it calculates risk-adjusted score = market_score × risk_multiplier
    """
    market_score = 85.0
    risk_multiplier = 0.95  # Slight risk penalty

    adjusted = engine.apply_risk_adjustment(market_score, risk_multiplier)

    # 85 * 0.95 = 80.75
    assert 80 <= adjusted["final_score"] <= 81
    assert "risk_adjustment" in adjusted
    assert adjusted["risk_adjustment"]["points_lost"] > 0


def test_flags_extreme_risk(engine: ScoringEngine) -> None:
    """
    Scenario: Extreme risk exclusion
    WHEN a submarket has risk multiplier <0.85
    THEN the system flags market as non-fit
    """
    market_score = 90.0  # Excellent market score
    risk_multiplier = 0.80  # Very high risk

    adjusted = engine.apply_risk_adjustment(market_score, risk_multiplier)

    assert adjusted["flagged_non_fit"] is True
    assert "extreme_risk" in adjusted["exclusion_reason"]


def test_normalization_linear(engine: ScoringEngine) -> None:
    """
    Scenario: Linear normalization
    WHEN a metric has known min/max bounds
    THEN the system applies linear scaling
    """
    # Unemployment rate: 2-10% range, lower is better (inverse)
    score = engine.normalize_linear(value=3.0, min_val=2.0, max_val=10.0, inverse=True)

    # Normalized: (3-2)/(10-2) = 0.125, inverse: 1-0.125 = 0.875, scale to 100: 87.5
    assert 85 <= score <= 90


def test_normalization_percentile(engine: ScoringEngine) -> None:
    """
    Scenario: Percentile-based normalization
    WHEN a metric lacks natural bounds
    THEN the system calculates percentile rank
    """
    values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    target_value = 65

    score = engine.normalize_percentile(target_value, values)

    # 65 is between 60 and 70, should be around 60th percentile
    assert 55 <= score <= 65

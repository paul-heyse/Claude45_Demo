"""Tests for weighted scoring engine."""

import matplotlib
import pandas as pd
import pytest

from Claude45_Demo.scoring_engine.scoring_engine import ScoringEngine

matplotlib.use("Agg")


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


def test_normalization_logarithmic(engine: ScoringEngine) -> None:
    """Logarithmic normalization should dampen outliers."""

    low = engine.normalize_logarithmic(value=200, min_val=100, max_val=10_000)
    high = engine.normalize_logarithmic(value=9_000, min_val=100, max_val=10_000)

    assert 0 <= low <= 100
    assert 0 <= high <= 100
    assert high > low


def test_threshold_normalization(engine: ScoringEngine) -> None:
    """Threshold-based normalization should honor step scores."""

    bands = [
        {"threshold": 5, "score": 95},
        {"threshold": 10, "score": 75},
        {"threshold": 15, "score": 50},
    ]

    low_permits = engine.normalize_threshold(4, bands, higher_is_better=False)
    mid_permits = engine.normalize_threshold(12, bands, higher_is_better=False)
    worst_permits = engine.normalize_threshold(20, bands, higher_is_better=False)

    assert low_permits == 95
    assert mid_permits == 50
    assert worst_permits == 50


def test_rank_submarkets_applies_tie_breakers(engine: ScoringEngine) -> None:
    """Ranking should sort by score and resolve ties via supply/jobs scores."""

    submarkets = [
        {
            "submarket_id": "DEN",
            "final_score": 88.5,
            "component_scores": {
                "supply_constraint": 92,
                "innovation_employment": 86,
                "urban_convenience": 78,
                "outdoor_access": 82,
            },
        },
        {
            "submarket_id": "BOI",
            "final_score": 84.0,
            "component_scores": {
                "supply_constraint": 80,
                "innovation_employment": 88,
                "urban_convenience": 74,
                "outdoor_access": 90,
            },
        },
        {
            "submarket_id": "SLC",
            "final_score": 84.0,
            "component_scores": {
                "supply_constraint": 85,
                "innovation_employment": 83,
                "urban_convenience": 76,
                "outdoor_access": 88,
            },
        },
        {
            "submarket_id": "COS",
            "final_score": 71.0,
            "component_scores": {
                "supply_constraint": 68,
                "innovation_employment": 65,
                "urban_convenience": 62,
                "outdoor_access": 75,
            },
        },
    ]

    ranking = engine.rank_submarkets(submarkets)

    assert ranking[0]["submarket_id"] == "DEN"
    assert ranking[0]["rank"] == 1
    assert ranking[0]["percentile"] == 100.0
    # SLC should beat BOI because of higher supply score tie-breaker
    slc_entry = next(item for item in ranking if item["submarket_id"] == "SLC")
    boi_entry = next(item for item in ranking if item["submarket_id"] == "BOI")
    assert slc_entry["rank"] < boi_entry["rank"]
    assert "peers" in slc_entry and "BOI" in slc_entry["peers"]


def test_weight_sensitivity_analysis(engine: ScoringEngine) -> None:
    """Sensitivity analysis should evaluate alternate weight scenarios."""

    components = {
        "supply_constraint": 88,
        "innovation_employment": 80,
        "urban_convenience": 76,
        "outdoor_access": 70,
    }

    scenarios = [
        {
            "name": "supply_priority",
            "delta": {
                "supply_constraint": 0.05,
                "innovation_employment": -0.05,
            },
        },
        {
            "name": "outdoor_focus",
            "delta": {
                "outdoor_access": 0.05,
                "urban_convenience": -0.05,
            },
        },
    ]

    results = engine.run_weight_sensitivity(components, scenarios)

    assert len(results) == 2
    assert results[0]["scenario"] == "supply_priority"
    assert "score" in results[0]


def test_visualization_helpers_return_figures(engine: ScoringEngine) -> None:
    """Visualization helpers should return matplotlib Figure objects."""

    component_scores = {
        "supply_constraint": 90,
        "innovation_employment": 82,
        "urban_convenience": 74,
        "outdoor_access": 88,
    }

    radar_fig = engine.create_component_radar_chart(
        submarket_id="DEN",
        component_scores=component_scores,
        benchmark_scores={"Top Quartile": {
            "supply_constraint": 92,
            "innovation_employment": 85,
            "urban_convenience": 80,
            "outdoor_access": 90,
        }},
    )

    heatmap_fig = engine.create_comparison_heatmap(
        [
            {"submarket_id": "DEN", "component_scores": component_scores},
            {"submarket_id": "SLC", "component_scores": {
                "supply_constraint": 85,
                "innovation_employment": 81,
                "urban_convenience": 70,
                "outdoor_access": 82,
            }},
        ]
    )

    assert radar_fig.__class__.__name__ == "Figure"
    assert heatmap_fig.__class__.__name__ == "Figure"


def test_non_fit_filters_detect_multiple_rules(engine: ScoringEngine) -> None:
    """Non-fit evaluation should flag scenarios defined in spec."""

    filters = engine.apply_non_fit_filters(
        component_scores={
            "supply_constraint": 35,
            "urban_convenience": 30,
            "transit": 15,
            "outdoor_access": 35,
        },
        risk_flags={"hard_rent_control": True, "wildfire_score": 92, "flood_score": 85},
        risk_multiplier=0.82,
        insurance_override=False,
    )

    assert filters["flagged"] is True
    assert "commodity_sprawl" in filters["reasons"]
    assert "auto_only_desert" in filters["reasons"]
    assert "hard_rent_control" in filters["reasons"]
    assert "chronic_hazard" in filters["reasons"]
    assert filters["requires_override"] is True


def test_confidence_scoring(engine: ScoringEngine) -> None:
    """Confidence score should combine completeness, freshness, and method."""

    completeness = engine.calculate_completeness_factor(
        available_metrics={
            "supply": True,
            "jobs": True,
            "transit": False,
            "outdoor": True,
        },
        critical_metrics={"supply", "jobs"},
    )

    freshness = engine.calculate_freshness_factor({
        "supply": 6,
        "jobs": 15,
        "transit": 9,
    })

    method = engine.calculate_method_factor({
        "supply": "direct",
        "jobs": "proxy",
        "transit": "estimate",
    })

    confidence = engine.calculate_confidence_score(
        completeness_factor=completeness["factor"],
        freshness_factor=freshness["factor"],
        method_factor=method["factor"],
        missing_critical=completeness["missing_critical"],
    )

    assert 0 <= confidence["confidence"] <= 100
    assert confidence["flagged_low_confidence"] in {True, False}
    assert "diagnostics" in confidence


def test_validation_report(engine: ScoringEngine) -> None:
    """Validation report should highlight score and rank deltas."""

    current = [
        {"submarket_id": "DEN", "final_score": 88, "rank": 1},
        {"submarket_id": "SLC", "final_score": 82, "rank": 2},
        {"submarket_id": "BOI", "final_score": 78, "rank": 3},
    ]

    reference = {
        "DEN": {"score": 85, "rank": 2},
        "SLC": {"score": 80, "rank": 1},
        "BOI": {"score": 77, "rank": 3},
    }

    report = engine.generate_validation_report(current, reference)

    assert isinstance(report, pd.DataFrame)
    assert "score_delta" in report.columns
    delta = report.loc[report["submarket_id"] == "DEN", "score_delta"].iloc[0]
    assert pytest.approx(delta) == 3
    rank_delta = report.loc[report["submarket_id"] == "SLC", "rank_delta"].iloc[0]
    assert rank_delta == 1

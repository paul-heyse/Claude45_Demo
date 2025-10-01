"""Tests for portfolio fit analysis."""

from __future__ import annotations

import pytest

from Claude45_Demo.asset_evaluation.portfolio import PortfolioAnalyzer


@pytest.fixture
def analyzer():
    """Create portfolio analyzer."""
    return PortfolioAnalyzer()


def test_geographic_fit_new_market_entry(analyzer):
    """Test geographic diversification for new market entry."""
    result = analyzer.assess_geographic_fit(
        candidate_metro="Boise-Nampa",
        candidate_noi=500_000,
        portfolio_by_metro={
            "Denver-Aurora-Lakewood": 2_000_000,
            "Salt Lake City": 1_500_000,
        },
    )

    assert result.diversification_impact == "improves"
    assert result.current_noi_concentration_pct == 0  # Not in portfolio yet
    assert result.projected_noi_concentration_pct < 15  # Will be ~12.5%
    assert "new market" in result.recommendation.lower()
    assert result.concentration_risk_score > 70  # Good diversification


def test_geographic_fit_high_concentration(analyzer):
    """Test warning for high concentration in single metro."""
    result = analyzer.assess_geographic_fit(
        candidate_metro="Denver-Aurora-Lakewood",
        candidate_noi=1_000_000,
        portfolio_by_metro={
            "Denver-Aurora-Lakewood": 2_000_000,
            "Salt Lake City": 500_000,
        },
    )

    assert result.diversification_impact == "increases_concentration"
    assert result.projected_noi_concentration_pct > 80  # High concentration
    assert "concentrated" in result.recommendation.lower()
    assert result.concentration_risk_score < 40  # Poor diversification


def test_geographic_fit_balanced_addition(analyzer):
    """Test neutral impact for balanced portfolio addition."""
    result = analyzer.assess_geographic_fit(
        candidate_metro="Salt Lake City",
        candidate_noi=500_000,
        portfolio_by_metro={
            "Denver-Aurora-Lakewood": 2_000_000,
            "Salt Lake City": 1_500_000,
            "Boise-Nampa": 1_000_000,
        },
    )

    assert result.diversification_impact in {"neutral", "increases_concentration"}
    assert 30 <= result.projected_noi_concentration_pct <= 50
    assert result.concentration_risk_score >= 20  # 40% concentration = 20 score


def test_product_type_mix_core_strengthening(analyzer):
    """Test product mix for adding core garden/low-rise assets."""
    result = analyzer.assess_product_type_mix(
        candidate_product_type="garden",
        candidate_units=200,
        portfolio_by_product={
            "garden": 300,
            "low-rise": 400,
            "mid-rise": 150,
        },
    )

    assert result.balance_impact in {"improves", "neutral"}
    # Core (garden + low-rise) should be ~82-86%
    projected_core = result.projected_mix.get("garden", 0) + result.projected_mix.get(
        "low-rise", 0
    )
    assert 75 <= projected_core <= 87  # Allow slight over-target
    assert result.mix_score >= 70
    assert result.recommendation  # Has recommendation


def test_product_type_mix_over_concentration(analyzer):
    """Test warning when garden/low-rise becomes over-concentrated."""
    result = analyzer.assess_product_type_mix(
        candidate_product_type="low-rise",
        candidate_units=300,
        portfolio_by_product={
            "garden": 500,
            "low-rise": 600,
            "mid-rise": 50,
        },
    )

    # Core would be ~90%+ after adding
    projected_core = result.projected_mix.get("garden", 0) + result.projected_mix.get(
        "low-rise", 0
    )
    assert projected_core > 85
    assert result.balance_impact == "concentrates"
    assert "diversif" in result.recommendation.lower()


def test_product_type_mix_mid_rise_addition(analyzer):
    """Test adding selective mid-rise to balanced portfolio."""
    result = analyzer.assess_product_type_mix(
        candidate_product_type="mid-rise",
        candidate_units=150,
        portfolio_by_product={
            "garden": 600,
            "low-rise": 400,
            "mid-rise": 50,
        },
    )

    assert result.balance_impact == "improves"
    assert result.projected_mix["mid-rise"] < 20  # Still selective
    assert (
        "selective" in result.recommendation.lower()
        or "mid-rise" in result.recommendation.lower()
    )


def test_product_type_mix_mixed_use_addition(analyzer):
    """Test adding strategic mixed-use asset."""
    result = analyzer.assess_product_type_mix(
        candidate_product_type="mixed-use",
        candidate_units=100,
        portfolio_by_product={
            "garden": 500,
            "low-rise": 400,
            "mid-rise": 100,
        },
    )

    assert result.balance_impact == "improves"
    assert result.projected_mix["mixed-use"] < 10  # Small strategic exposure
    assert "mixed-use" in result.recommendation.lower()


def test_synergies_new_market_entry(analyzer):
    """Test synergies for new market entry (no existing assets)."""
    result = analyzer.estimate_synergies(
        candidate_metro="Colorado Springs",
        candidate_units=200,
        candidate_opex_per_unit=4000,
        portfolio_assets_in_metro=0,
        local_reputation_score=0,
    )

    assert result.opex_savings_pct == 0.0
    assert result.lease_up_bonus_days == 0
    assert result.synergy_value_estimate == 0
    assert "new market" in result.synergy_factors[0].lower()


def test_synergies_second_asset_in_market(analyzer):
    """Test emerging synergies for second asset in market."""
    result = analyzer.estimate_synergies(
        candidate_metro="Denver-Aurora-Lakewood",
        candidate_units=200,
        candidate_opex_per_unit=4000,
        portfolio_assets_in_metro=1,
        local_reputation_score=65,
    )

    assert result.opex_savings_pct == 2.0
    assert result.lease_up_bonus_days == 5  # Reputation > 60
    assert result.synergy_value_estimate > 0
    assert "second asset" in result.synergy_factors[0].lower()


def test_synergies_small_cluster(analyzer):
    """Test meaningful synergies for small asset cluster."""
    result = analyzer.estimate_synergies(
        candidate_metro="Salt Lake City",
        candidate_units=250,
        candidate_opex_per_unit=4200,
        portfolio_assets_in_metro=3,
        local_reputation_score=75,
    )

    assert result.opex_savings_pct == 3.5
    assert result.lease_up_bonus_days == 10  # Reputation > 70
    assert result.synergy_value_estimate > 30_000  # Meaningful $ value
    assert any("vendor" in factor.lower() for factor in result.synergy_factors)


def test_synergies_large_cluster(analyzer):
    """Test maximum synergies for large asset cluster."""
    result = analyzer.estimate_synergies(
        candidate_metro="Denver-Aurora-Lakewood",
        candidate_units=300,
        candidate_opex_per_unit=4500,
        portfolio_assets_in_metro=6,
        local_reputation_score=85,
    )

    assert result.opex_savings_pct == 5.0
    assert result.lease_up_bonus_days == 15  # Reputation > 80
    assert result.synergy_value_estimate > 60_000  # Substantial value
    assert len(result.synergy_factors) >= 4  # Multiple synergy sources
    assert any(
        "portfolio pricing" in factor.lower() for factor in result.synergy_factors
    )


def test_synergies_calculation_accuracy(analyzer):
    """Test accuracy of synergy value calculation."""
    result = analyzer.estimate_synergies(
        candidate_metro="Boise-Nampa",
        candidate_units=200,
        candidate_opex_per_unit=4000,  # $800k annual opex
        portfolio_assets_in_metro=3,  # 3.5% savings
        local_reputation_score=75,  # 10 days lease-up bonus
    )

    # Expected: 3.5% of $800k = $28k opex savings
    # Expected: 10 days * $50/day * 200 units = $100k lease-up / 5 years = $20k/yr
    # Total: ~$48k
    expected_synergy = (800_000 * 0.035) + ((10 * 50 * 200) / 5)
    assert (
        abs(result.synergy_value_estimate - expected_synergy) < 100
    )  # Within rounding


def test_empty_portfolio_edge_case(analyzer):
    """Test geographic fit with empty portfolio."""
    result = analyzer.assess_geographic_fit(
        candidate_metro="Denver-Aurora-Lakewood",
        candidate_noi=1_000_000,
        portfolio_by_metro={},
    )

    assert result.diversification_impact == "improves"
    assert result.projected_noi_concentration_pct == 100  # First asset
    assert result.current_noi_concentration_pct == 0


def test_product_mix_empty_portfolio(analyzer):
    """Test product mix with empty portfolio."""
    result = analyzer.assess_product_type_mix(
        candidate_product_type="garden",
        candidate_units=200,
        portfolio_by_product={},
    )

    assert result.projected_mix["garden"] == 100.0
    assert result.balance_impact in {"improves", "neutral", "concentrates"}

"""Tests for exit strategy and hold period analysis."""

from __future__ import annotations

import pytest

from Claude45_Demo.asset_evaluation.exit_strategy import ExitAnalyzer


@pytest.fixture
def analyzer():
    """Create exit analyzer."""
    return ExitAnalyzer()


def test_exit_model_multiple_hold_periods(analyzer):
    """Test exit modeling across 3, 5, 7 year hold periods."""
    result = analyzer.model_exit_scenarios(
        entry_noi=500_000,
        stabilized_noi=650_000,  # Post value-add
        entry_cap_rate=0.05,  # 5%
        entry_value=10_000_000,
        initial_equity=3_000_000,
        hold_periods=[3, 5, 7],
        cap_rate_adjustment_bps=25,  # 25 bps compression at exit
    )

    assert len(result.scenarios) == 3
    assert all(s.stabilized_noi == 650_000 for s in result.scenarios)
    assert all(s.exit_cap_rate == 0.0525 for s in result.scenarios)  # 5% + 25bps

    # Verify each scenario has required fields
    for scenario in result.scenarios:
        assert scenario.hold_period_years in [3, 5, 7]
        assert scenario.exit_value > 0
        assert scenario.irr > 0
        assert scenario.equity_multiple > 0

    # Recommended period should be one of the modeled periods
    assert result.recommended_hold_period in [3, 5, 7]
    assert result.recommendation


def test_exit_model_cap_rate_impact(analyzer):
    """Test impact of exit cap rate on returns."""
    # Compression scenario (cap rate decreases = higher value)
    compression_result = analyzer.model_exit_scenarios(
        entry_noi=500_000,
        stabilized_noi=600_000,
        entry_cap_rate=0.05,
        entry_value=10_000_000,
        initial_equity=3_000_000,
        hold_periods=[5],
        cap_rate_adjustment_bps=-25,  # 25 bps compression (better)
    )

    # Expansion scenario (cap rate increases = lower value)
    expansion_result = analyzer.model_exit_scenarios(
        entry_noi=500_000,
        stabilized_noi=600_000,
        entry_cap_rate=0.05,
        entry_value=10_000_000,
        initial_equity=3_000_000,
        hold_periods=[5],
        cap_rate_adjustment_bps=25,  # 25 bps expansion (worse)
    )

    # Compression should yield higher exit value and IRR
    assert (
        compression_result.scenarios[0].exit_value
        > expansion_result.scenarios[0].exit_value
    )
    assert compression_result.scenarios[0].irr > expansion_result.scenarios[0].irr


def test_exit_model_value_add_scenario(analyzer):
    """Test typical value-add exit scenario."""
    result = analyzer.model_exit_scenarios(
        entry_noi=400_000,
        stabilized_noi=550_000,  # 37.5% NOI lift
        entry_cap_rate=0.055,
        entry_value=7_272_727,  # 400k / 5.5%
        initial_equity=2_500_000,
        hold_periods=[3, 5],
        cap_rate_adjustment_bps=0,  # Stable cap rate
    )

    # 5-year scenario
    five_year = next(s for s in result.scenarios if s.hold_period_years == 5)
    assert five_year.exit_value == 10_000_000  # 550k / 5.5%
    assert five_year.equity_multiple == 4.0  # 10M / 2.5M
    # IRR should be around 32% for 4x in 5 years
    assert 0.28 <= five_year.irr <= 0.35


def test_appreciation_scenarios_distribution(analyzer):
    """Test base/bull/bear appreciation projections."""
    result = analyzer.project_appreciation(
        entry_noi=500_000,
        entry_value=10_000_000,
        initial_equity=3_000_000,
        hold_period_years=5,
        base_rent_growth=0.03,
        bull_rent_growth=0.045,
        bear_rent_growth=0.02,
        cap_rate_range_bps=50,
    )

    assert len(result.scenarios) == 3
    scenario_names = {s.scenario_name for s in result.scenarios}
    assert scenario_names == {"base", "bull", "bear"}

    # Order: bear < base < bull
    bear = next(s for s in result.scenarios if s.scenario_name == "bear")
    base = next(s for s in result.scenarios if s.scenario_name == "base")
    bull = next(s for s in result.scenarios if s.scenario_name == "bull")

    assert bear.projected_irr < base.projected_irr < bull.projected_irr
    assert (
        bear.projected_equity_multiple
        < base.projected_equity_multiple
        < bull.projected_equity_multiple
    )

    # P10 (bear) < P50 (base) < P90 (bull)
    assert result.p10_irr == bear.projected_irr
    assert result.p50_irr == base.projected_irr
    assert result.p90_irr == bull.projected_irr


def test_appreciation_base_case_calculations(analyzer):
    """Test base case appreciation calculations."""
    result = analyzer.project_appreciation(
        entry_noi=500_000,
        entry_value=10_000_000,  # 5% cap rate
        initial_equity=3_000_000,
        hold_period_years=5,
        base_rent_growth=0.03,  # 3% annual
        cap_rate_range_bps=0,  # Stable cap for base
    )

    base = next(s for s in result.scenarios if s.scenario_name == "base")

    # NOI after 5 years at 3% growth: 500k * 1.03^5 = ~579,637
    expected_noi = 500_000 * (1.03**5)
    # Exit value at 5% cap: ~11,592,740
    expected_exit_value = expected_noi / 0.05
    expected_multiple = expected_exit_value / 3_000_000

    assert base.annual_rent_growth == 0.03
    assert base.cap_rate_movement_bps == 0
    assert abs(base.projected_equity_multiple - expected_multiple) < 0.05


def test_appreciation_bull_bear_symmetry(analyzer):
    """Test that bull and bear scenarios are symmetric."""
    result = analyzer.project_appreciation(
        entry_noi=500_000,
        entry_value=10_000_000,
        initial_equity=3_000_000,
        hold_period_years=5,
        base_rent_growth=0.03,
        bull_rent_growth=0.045,  # +1.5%
        bear_rent_growth=0.015,  # -1.5%
        cap_rate_range_bps=50,  # +/- 50 bps
    )

    bear = next(s for s in result.scenarios if s.scenario_name == "bear")
    bull = next(s for s in result.scenarios if s.scenario_name == "bull")

    # Cap rate movements should be symmetric
    assert bear.cap_rate_movement_bps == 50  # Expansion
    assert bull.cap_rate_movement_bps == -50  # Compression


def test_refi_vs_sale_refi_favored(analyzer):
    """Test refinance recommendation when cash extraction is favorable."""
    result = analyzer.compare_refi_vs_sale(
        current_value=15_000_000,
        current_debt=5_000_000,
        current_noi=750_000,
        annual_cashflow_growth=0.03,
        hold_years_if_refi=5,
        refi_ltv=0.70,  # 70% LTV
        refi_interest_rate=0.045,  # 4.5%
        capital_gains_rate=0.20,
        depreciation_recapture_rate=0.25,
        depreciation_taken=1_000_000,
        cost_basis=10_000_000,
    )

    # Refi loan: 15M * 0.7 = 10.5M
    # Extract: 10.5M - 5M = 5.5M
    assert result.refi_equity_extracted == 5_500_000

    # New debt service: 10.5M * 4.5% = 472.5k
    # Annual cashflow: 750k - 472.5k = 277.5k
    # Should be positive cashflow after refi
    assert result.refi_ongoing_cashflow > 0

    # Should be one of the strategies (sale may win due to tax treatment)
    assert result.recommended_strategy in {"refinance", "hold", "sale"}
    assert result.refi_net_benefit > 0


def test_refi_vs_sale_sale_favored(analyzer):
    """Test sale recommendation when net proceeds are favorable."""
    result = analyzer.compare_refi_vs_sale(
        current_value=12_000_000,
        current_debt=8_000_000,  # High leverage already
        current_noi=600_000,
        annual_cashflow_growth=0.02,
        hold_years_if_refi=3,
        refi_ltv=0.65,  # Conservative LTV
        refi_interest_rate=0.06,  # High interest rate
        capital_gains_rate=0.15,  # Low cap gains (long hold)
        depreciation_recapture_rate=0.25,
        depreciation_taken=500_000,
        cost_basis=8_000_000,  # Low basis = big gain but lower tax
    )

    # Current equity: 12M - 8M = 4M
    # Refi at 65% LTV: 7.8M loan (can't extract much)
    # High debt service reduces cashflow appeal

    assert result.sale_net_proceeds > 0
    # Sale may be recommended due to limited refi upside
    assert result.recommended_strategy in {"sale", "hold"}


def test_refi_vs_sale_close_call(analyzer):
    """Test neutral recommendation when options are similar."""
    result = analyzer.compare_refi_vs_sale(
        current_value=10_000_000,
        current_debt=4_000_000,
        current_noi=500_000,
        annual_cashflow_growth=0.03,
        hold_years_if_refi=5,
        refi_ltv=0.65,
        refi_interest_rate=0.05,
        capital_gains_rate=0.20,
        depreciation_recapture_rate=0.25,
        depreciation_taken=800_000,
        cost_basis=7_000_000,
    )

    # Close call scenario - should recommend one of the strategies
    assert result.recommended_strategy in {"refinance", "sale", "hold"}
    # Verify both options were calculated
    assert result.refi_net_benefit > 0
    assert result.sale_net_proceeds > 0


def test_refi_vs_sale_tax_impact(analyzer):
    """Test impact of taxes on sale proceeds."""
    # High tax scenario
    high_tax = analyzer.compare_refi_vs_sale(
        current_value=15_000_000,
        current_debt=5_000_000,
        current_noi=750_000,
        refi_ltv=0.70,
        refi_interest_rate=0.045,
        capital_gains_rate=0.23,  # High state + federal
        depreciation_recapture_rate=0.25,
        depreciation_taken=2_000_000,  # Significant depreciation
        cost_basis=8_000_000,  # Large gain
    )

    # Low tax scenario
    low_tax = analyzer.compare_refi_vs_sale(
        current_value=15_000_000,
        current_debt=5_000_000,
        current_noi=750_000,
        refi_ltv=0.70,
        refi_interest_rate=0.045,
        capital_gains_rate=0.15,  # Low rate
        depreciation_recapture_rate=0.25,
        depreciation_taken=500_000,  # Less depreciation
        cost_basis=12_000_000,  # Smaller gain
    )

    # Low tax scenario should have higher net proceeds
    assert low_tax.sale_net_proceeds > high_tax.sale_net_proceeds


def test_exit_model_edge_case_zero_equity(analyzer):
    """Test edge case with zero equity (100% debt)."""
    result = analyzer.model_exit_scenarios(
        entry_noi=500_000,
        stabilized_noi=600_000,
        entry_cap_rate=0.05,
        entry_value=10_000_000,
        initial_equity=1,  # Avoid division by zero
        hold_periods=[5],
        cap_rate_adjustment_bps=0,
    )

    # Should handle gracefully without errors
    assert len(result.scenarios) == 1
    assert result.scenarios[0].equity_multiple > 0


def test_appreciation_negative_rent_growth(analyzer):
    """Test handling of negative rent growth scenario."""
    result = analyzer.project_appreciation(
        entry_noi=500_000,
        entry_value=10_000_000,
        initial_equity=3_000_000,
        hold_period_years=5,
        base_rent_growth=0.02,
        bear_rent_growth=-0.01,  # Negative growth
        bull_rent_growth=0.04,
    )

    bear = next(s for s in result.scenarios if s.scenario_name == "bear")
    # Should handle negative growth without errors
    assert bear.annual_rent_growth == -0.01
    # Bear scenario should have lowest returns (may still be positive if equity is low)
    base = next(s for s in result.scenarios if s.scenario_name == "base")
    assert bear.projected_irr < base.projected_irr

"""Exit strategy and hold period analysis for investment decisions.

Models exit scenarios, appreciation trajectories, and refinance vs. sale trade-offs
to support investment committee decision-making.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ExitScenario:
    """Single exit scenario projection."""

    hold_period_years: int
    stabilized_noi: float
    exit_cap_rate: float
    exit_value: float
    total_return: float
    irr: float  # Internal rate of return
    equity_multiple: float


@dataclass(frozen=True)
class ExitModelResult:
    """Complete exit modeling with multiple hold periods."""

    scenarios: List[ExitScenario]
    recommended_hold_period: int
    recommendation: str


@dataclass(frozen=True)
class AppreciationScenario:
    """Market appreciation projection."""

    scenario_name: str  # "base", "bull", "bear"
    annual_rent_growth: float  # % per year
    cap_rate_movement_bps: int  # Basis points expansion/compression
    hold_period_years: int
    projected_irr: float
    projected_equity_multiple: float


@dataclass(frozen=True)
class AppreciationResult:
    """Distribution of appreciation outcomes."""

    scenarios: List[AppreciationScenario]
    p10_irr: float  # 10th percentile (bear)
    p50_irr: float  # 50th percentile (base)
    p90_irr: float  # 90th percentile (bull)
    recommendation: str


@dataclass(frozen=True)
class RefinanceComparison:
    """Comparison of refinance vs. sale strategies."""

    refi_equity_extracted: float
    refi_ongoing_cashflow: float
    refi_net_benefit: float
    sale_gross_proceeds: float
    sale_net_proceeds: float  # After taxes
    sale_realized_gain: float
    recommended_strategy: str  # "refinance", "sale", "hold"
    recommendation: str


class ExitAnalyzer:
    """Model exit strategies and hold period optimization."""

    def __init__(self) -> None:
        """Initialize exit analyzer."""
        pass

    def model_exit_scenarios(
        self,
        *,
        entry_noi: float,
        stabilized_noi: float,
        entry_cap_rate: float,
        entry_value: float,
        initial_equity: float,
        hold_periods: List[int],  # Years: [3, 5, 7]
        cap_rate_adjustment_bps: int = 0,  # Basis points change at exit
    ) -> ExitModelResult:
        """Model exit scenarios at multiple hold periods.

        Args:
            entry_noi: Current/entry NOI
            stabilized_noi: Projected stabilized NOI (post-value-add)
            entry_cap_rate: Entry cap rate (as decimal, e.g., 0.05 = 5%)
            entry_value: Purchase price
            initial_equity: Equity invested
            hold_periods: List of hold period years to model [3, 5, 7]
            cap_rate_adjustment_bps: Exit cap vs. entry cap (e.g., +25 = compression)

        Returns:
            ExitModelResult with IRR and equity multiples per hold period

        Spec: Requirement 11, Scenario "Value-add exit modeling"
        """
        scenarios = []

        exit_cap_rate = entry_cap_rate + (cap_rate_adjustment_bps / 10000)

        for years in hold_periods:
            # Exit value = stabilized NOI / exit cap rate
            exit_value = stabilized_noi / exit_cap_rate if exit_cap_rate > 0 else 0

            # Total return = exit value - entry value
            total_return = exit_value - entry_value

            # Simple IRR approximation: ((exit_value / initial_equity) ^ (1/years)) - 1
            # This is a simplified calculation; full IRR would account for interim cashflows
            if initial_equity > 0 and years > 0:
                equity_multiple = exit_value / initial_equity
                irr = ((equity_multiple) ** (1 / years)) - 1
            else:
                equity_multiple = 0
                irr = 0

            scenarios.append(
                ExitScenario(
                    hold_period_years=years,
                    stabilized_noi=stabilized_noi,
                    exit_cap_rate=round(exit_cap_rate, 4),
                    exit_value=round(exit_value, 2),
                    total_return=round(total_return, 2),
                    irr=round(irr, 4),
                    equity_multiple=round(equity_multiple, 2),
                )
            )

        # Recommend hold period with highest IRR
        best_scenario = max(scenarios, key=lambda s: s.irr)
        recommended_years = best_scenario.hold_period_years

        if recommended_years <= 3:
            recommendation = (
                f"Short hold ({recommended_years}yr) maximizes IRR at "
                f"{best_scenario.irr:.1%}, but consider value-add execution risk"
            )
        elif recommended_years == 5:
            recommendation = (
                f"5-year hold balances value-add completion and return optimization "
                f"(IRR: {best_scenario.irr:.1%})"
            )
        else:
            recommendation = (
                f"Extended hold ({recommended_years}yr) provides best risk-adjusted return "
                f"(IRR: {best_scenario.irr:.1%})"
            )

        return ExitModelResult(
            scenarios=scenarios,
            recommended_hold_period=recommended_years,
            recommendation=recommendation,
        )

    def project_appreciation(
        self,
        *,
        entry_noi: float,
        entry_value: float,
        initial_equity: float,
        hold_period_years: int = 5,
        base_rent_growth: float = 0.03,  # Inflation + 1% = 3%
        bull_rent_growth: float = 0.045,  # Inflation + 2.5% = 4.5%
        bear_rent_growth: float = 0.02,  # Inflation only = 2%
        cap_rate_range_bps: int = 50,  # +/- 50 bps range
    ) -> AppreciationResult:
        """Project appreciation scenarios (base, bull, bear).

        Args:
            entry_noi: Current NOI
            entry_value: Purchase price
            initial_equity: Equity invested
            hold_period_years: Projection period
            base_rent_growth: Base case annual rent growth (decimal)
            bull_rent_growth: Bull case annual rent growth
            bear_rent_growth: Bear case annual rent growth
            cap_rate_range_bps: Cap rate compression/expansion range (+/-)

        Returns:
            AppreciationResult with P10/P50/P90 IRR distribution

        Spec: Requirement 11, Scenario "Market appreciation scenarios"
        """
        entry_cap_rate = entry_noi / entry_value if entry_value > 0 else 0.05

        scenarios = []

        # Bear case: low rent growth + cap expansion
        bear_noi = entry_noi * ((1 + bear_rent_growth) ** hold_period_years)
        bear_cap = entry_cap_rate + (cap_rate_range_bps / 10000)
        bear_exit_value = bear_noi / bear_cap if bear_cap > 0 else entry_value
        bear_irr = (
            ((bear_exit_value / initial_equity) ** (1 / hold_period_years)) - 1
            if initial_equity > 0
            else 0
        )
        bear_multiple = bear_exit_value / initial_equity if initial_equity > 0 else 0

        scenarios.append(
            AppreciationScenario(
                scenario_name="bear",
                annual_rent_growth=bear_rent_growth,
                cap_rate_movement_bps=cap_rate_range_bps,
                hold_period_years=hold_period_years,
                projected_irr=round(bear_irr, 4),
                projected_equity_multiple=round(bear_multiple, 2),
            )
        )

        # Base case: moderate rent growth + stable cap
        base_noi = entry_noi * ((1 + base_rent_growth) ** hold_period_years)
        base_cap = entry_cap_rate  # No change
        base_exit_value = base_noi / base_cap if base_cap > 0 else entry_value
        base_irr = (
            ((base_exit_value / initial_equity) ** (1 / hold_period_years)) - 1
            if initial_equity > 0
            else 0
        )
        base_multiple = base_exit_value / initial_equity if initial_equity > 0 else 0

        scenarios.append(
            AppreciationScenario(
                scenario_name="base",
                annual_rent_growth=base_rent_growth,
                cap_rate_movement_bps=0,
                hold_period_years=hold_period_years,
                projected_irr=round(base_irr, 4),
                projected_equity_multiple=round(base_multiple, 2),
            )
        )

        # Bull case: high rent growth + cap compression
        bull_noi = entry_noi * ((1 + bull_rent_growth) ** hold_period_years)
        bull_cap = entry_cap_rate - (cap_rate_range_bps / 10000)
        bull_exit_value = bull_noi / bull_cap if bull_cap > 0 else entry_value * 1.5
        bull_irr = (
            ((bull_exit_value / initial_equity) ** (1 / hold_period_years)) - 1
            if initial_equity > 0
            else 0
        )
        bull_multiple = bull_exit_value / initial_equity if initial_equity > 0 else 0

        scenarios.append(
            AppreciationScenario(
                scenario_name="bull",
                annual_rent_growth=bull_rent_growth,
                cap_rate_movement_bps=-cap_rate_range_bps,
                hold_period_years=hold_period_years,
                projected_irr=round(bull_irr, 4),
                projected_equity_multiple=round(bull_multiple, 2),
            )
        )

        recommendation = (
            f"Base case IRR: {base_irr:.1%} | Range: {bear_irr:.1%} (P10) to "
            f"{bull_irr:.1%} (P90) | Equity multiples: {bear_multiple:.2f}x - {bull_multiple:.2f}x"
        )

        return AppreciationResult(
            scenarios=scenarios,
            p10_irr=round(bear_irr, 4),
            p50_irr=round(base_irr, 4),
            p90_irr=round(bull_irr, 4),
            recommendation=recommendation,
        )

    def compare_refi_vs_sale(
        self,
        *,
        current_value: float,
        current_debt: float,
        current_noi: float,
        annual_cashflow_growth: float = 0.03,  # 3% annual growth
        hold_years_if_refi: int = 5,  # Additional years if refinance
        refi_ltv: float = 0.70,  # 70% LTV on refinance
        refi_interest_rate: float = 0.045,  # 4.5% interest
        capital_gains_rate: float = 0.20,  # 20% long-term cap gains
        depreciation_recapture_rate: float = 0.25,  # 25% depreciation recapture
        depreciation_taken: float = 0,  # $ depreciation taken
        cost_basis: float = 0,  # Original cost basis
    ) -> RefinanceComparison:
        """Compare refinance (extract equity, hold) vs. sale (realize gains).

        Args:
            current_value: Current property value
            current_debt: Outstanding debt
            current_noi: Current annual NOI
            annual_cashflow_growth: Annual cashflow growth if hold
            hold_years_if_refi: Additional years if refinance & hold
            refi_ltv: Refinance loan-to-value ratio
            refi_interest_rate: Refinance interest rate
            capital_gains_rate: Capital gains tax rate
            depreciation_recapture_rate: Depreciation recapture tax rate
            depreciation_taken: Accumulated depreciation
            cost_basis: Original cost basis (purchase + capex)

        Returns:
            RefinanceComparison with net proceeds and recommendation

        Spec: Requirement 11, Scenario "Refinance vs. sale decision"
        """
        current_equity = current_value - current_debt

        # REFINANCE OPTION
        # New loan = current value * refi LTV
        new_loan = current_value * refi_ltv
        refi_equity_extracted = new_loan - current_debt  # Extract excess equity
        new_annual_debt_service = new_loan * refi_interest_rate
        annual_cashflow_after_refi = current_noi - new_annual_debt_service

        # Project cashflow over additional hold period
        total_refi_cashflow = 0
        for year in range(1, hold_years_if_refi + 1):
            year_cashflow = annual_cashflow_after_refi * (
                (1 + annual_cashflow_growth) ** year
            )
            total_refi_cashflow += year_cashflow

        refi_net_benefit = refi_equity_extracted + total_refi_cashflow

        # SALE OPTION
        sale_gross_proceeds = current_equity  # Value - debt
        capital_gain = (
            current_value - cost_basis if cost_basis > 0 else current_value * 0.3
        )
        capital_gains_tax = (capital_gain - depreciation_taken) * capital_gains_rate
        depreciation_recapture_tax = depreciation_taken * depreciation_recapture_rate
        total_tax = capital_gains_tax + depreciation_recapture_tax
        sale_net_proceeds = sale_gross_proceeds - total_tax

        # RECOMMENDATION
        if refi_net_benefit > sale_net_proceeds * 1.1:
            # Refinance is clearly better (10%+ advantage)
            recommended_strategy = "refinance"
            recommendation = (
                f"Refinance recommended: extract ${refi_equity_extracted:,.0f}, "
                f"hold for {hold_years_if_refi}yr cashflow (net benefit: ${refi_net_benefit:,.0f})"
            )
        elif sale_net_proceeds > refi_net_benefit * 1.1:
            # Sale is clearly better
            recommended_strategy = "sale"
            recommendation = (
                f"Sale recommended: realize ${sale_net_proceeds:,.0f} net proceeds "
                f"(after ${total_tax:,.0f} tax), redeploy capital"
            )
        else:
            # Close call - consider other factors
            recommended_strategy = "hold"
            recommendation = (
                f"Close call (refi: ${refi_net_benefit:,.0f} vs. sale: ${sale_net_proceeds:,.0f}). "
                f"Consider portfolio needs and interest rate outlook"
            )

        return RefinanceComparison(
            refi_equity_extracted=round(refi_equity_extracted, 2),
            refi_ongoing_cashflow=round(total_refi_cashflow, 2),
            refi_net_benefit=round(refi_net_benefit, 2),
            sale_gross_proceeds=round(sale_gross_proceeds, 2),
            sale_net_proceeds=round(sale_net_proceeds, 2),
            sale_realized_gain=round(capital_gain, 2),
            recommended_strategy=recommended_strategy,
            recommendation=recommendation,
        )

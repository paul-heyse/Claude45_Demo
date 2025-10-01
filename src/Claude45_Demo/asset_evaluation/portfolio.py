"""Portfolio fit analysis for strategic asset evaluation.

Assesses how candidate properties fit within Aker's existing portfolio
in terms of geographic diversification, product type mix, and operational synergies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class GeographicFitResult:
    """Result of geographic diversification analysis."""

    concentration_risk_score: int  # 0-100, higher is better (more diversified)
    current_noi_concentration_pct: float  # % NOI in candidate's metro
    projected_noi_concentration_pct: float  # After adding candidate
    diversification_impact: str  # "improves", "neutral", "increases_concentration"
    recommendation: str


@dataclass(frozen=True)
class ProductMixResult:
    """Result of product type mix analysis."""

    mix_score: int  # 0-100, higher is better (more balanced)
    current_mix: Dict[str, float]  # Product type percentages
    projected_mix: Dict[str, float]  # After adding candidate
    balance_impact: str  # "improves", "neutral", "concentrates"
    recommendation: str


@dataclass(frozen=True)
class SynergyResult:
    """Result of operational synergy analysis."""

    synergy_value_estimate: float  # Annual $ value of synergies
    opex_savings_pct: float  # % reduction in operating expenses
    lease_up_bonus_days: int  # Faster lease-up from local brand recognition
    synergy_factors: List[str]  # Reasons for synergies


class PortfolioAnalyzer:
    """Analyze strategic fit of candidate properties within existing portfolio."""

    def __init__(self) -> None:
        """Initialize portfolio analyzer."""
        pass

    def assess_geographic_fit(
        self,
        *,
        candidate_metro: str,
        candidate_noi: float,
        portfolio_by_metro: Dict[str, float],  # metro -> NOI
    ) -> GeographicFitResult:
        """Assess geographic diversification impact of adding candidate.

        Args:
            candidate_metro: Metro area of candidate property (e.g., "Denver-Aurora-Lakewood")
            candidate_noi: Annual NOI of candidate property
            portfolio_by_metro: Current portfolio NOI by metro area

        Returns:
            GeographicFitResult with concentration metrics and recommendation

        Spec: Requirement 10, Scenario "Geographic diversification"
        """
        # Calculate current portfolio metrics
        total_current_noi = sum(portfolio_by_metro.values())
        current_metro_noi = portfolio_by_metro.get(candidate_metro, 0)
        current_concentration = (
            (current_metro_noi / total_current_noi * 100)
            if total_current_noi > 0
            else 0
        )

        # Calculate projected metrics after adding candidate
        total_projected_noi = total_current_noi + candidate_noi
        projected_metro_noi = current_metro_noi + candidate_noi
        projected_concentration = (
            (projected_metro_noi / total_projected_noi * 100)
            if total_projected_noi > 0
            else 100
        )

        # Assess diversification impact
        if current_metro_noi == 0:
            # New market entry
            diversification_impact = "improves"
            recommendation = (
                f"Enters new market {candidate_metro}, improving diversification"
            )
        elif projected_concentration > 40:
            # High concentration threshold
            diversification_impact = "increases_concentration"
            recommendation = (
                f"Adds to already concentrated market (>{projected_concentration:.1f}%), "
                f"consider diversifying to other markets"
            )
        elif projected_concentration > current_concentration + 5:
            # Meaningful increase in concentration
            diversification_impact = "increases_concentration"
            recommendation = (
                f"Increases {candidate_metro} concentration to {projected_concentration:.1f}%, "
                f"monitor portfolio balance"
            )
        elif (
            current_concentration > 30
            and projected_concentration <= current_concentration
        ):
            # Reduces concentration from high level
            diversification_impact = "improves"
            recommendation = f"Helps reduce concentration in {candidate_metro}"
        else:
            diversification_impact = "neutral"
            recommendation = (
                f"Minor impact on diversification ({projected_concentration:.1f}%)"
            )

        # Score: 100 = perfect diversification (no metro >20%), 0 = single metro
        concentration_risk_score = max(
            0, min(100, int(100 - projected_concentration * 2))
        )

        return GeographicFitResult(
            concentration_risk_score=concentration_risk_score,
            current_noi_concentration_pct=round(current_concentration, 2),
            projected_noi_concentration_pct=round(projected_concentration, 2),
            diversification_impact=diversification_impact,
            recommendation=recommendation,
        )

    def assess_product_type_mix(
        self,
        *,
        candidate_product_type: str,
        candidate_units: int,
        portfolio_by_product: Dict[str, int],  # product_type -> unit count
    ) -> ProductMixResult:
        """Assess product type mix balance after adding candidate.

        Args:
            candidate_product_type: Product type (garden, low-rise, mid-rise, mixed-use)
            candidate_units: Unit count of candidate
            portfolio_by_product: Current portfolio unit counts by product type

        Returns:
            ProductMixResult with mix percentages and balance assessment

        Spec: Requirement 10, Scenario "Product type mix"
        """
        # Calculate current mix
        total_current_units = sum(portfolio_by_product.values())
        current_mix = {
            ptype: (units / total_current_units * 100) if total_current_units > 0 else 0
            for ptype, units in portfolio_by_product.items()
        }

        # Calculate projected mix
        total_projected_units = total_current_units + candidate_units
        projected_portfolio = portfolio_by_product.copy()
        projected_portfolio[candidate_product_type] = (
            projected_portfolio.get(candidate_product_type, 0) + candidate_units
        )
        projected_mix = {
            ptype: round(units / total_projected_units * 100, 1)
            for ptype, units in projected_portfolio.items()
        }

        # Target mix per Aker thesis: garden/low-rise 80%, mid-rise 15%, mixed-use 5%
        target_core = 80  # garden + low-rise
        target_select = 15  # mid-rise
        target_mixed = 5  # mixed-use

        projected_core = projected_mix.get("garden", 0) + projected_mix.get(
            "low-rise", 0
        )
        projected_select = projected_mix.get("mid-rise", 0)
        projected_mixed = projected_mix.get("mixed-use", 0)

        # Score based on deviation from target
        core_deviation = abs(projected_core - target_core)
        select_deviation = abs(projected_select - target_select)
        mixed_deviation = abs(projected_mixed - target_mixed)
        total_deviation = core_deviation + select_deviation + mixed_deviation

        mix_score = max(0, int(100 - total_deviation))

        # Assess balance impact
        current_core = current_mix.get("garden", 0) + current_mix.get("low-rise", 0)
        if candidate_product_type in {"garden", "low-rise"}:
            if current_core < 70:
                balance_impact = "improves"
                recommendation = "Strengthens core garden/low-rise portfolio"
            elif current_core > 85:
                balance_impact = "concentrates"
                recommendation = "Consider diversifying to mid-rise or mixed-use"
            else:
                balance_impact = "neutral"
                recommendation = "Maintains balanced product mix"
        elif candidate_product_type == "mid-rise":
            if projected_select < 20:
                balance_impact = "improves"
                recommendation = "Adds selective mid-rise exposure"
            else:
                balance_impact = "concentrates"
                recommendation = "Mid-rise exposure approaching upper limit"
        elif candidate_product_type == "mixed-use":
            balance_impact = "improves"
            recommendation = "Adds strategic mixed-use exposure"
        else:
            balance_impact = "neutral"
            recommendation = "Product type fits within portfolio strategy"

        return ProductMixResult(
            mix_score=mix_score,
            current_mix={k: round(v, 1) for k, v in current_mix.items()},
            projected_mix=projected_mix,
            balance_impact=balance_impact,
            recommendation=recommendation,
        )

    def estimate_synergies(
        self,
        *,
        candidate_metro: str,
        candidate_units: int,
        candidate_opex_per_unit: float,
        portfolio_assets_in_metro: int,  # Count of existing assets in same metro
        local_reputation_score: int,  # 0-100, Aker brand strength in metro
    ) -> SynergyResult:
        """Estimate operational synergies from clustering assets in same market.

        Args:
            candidate_metro: Metro area of candidate
            candidate_units: Unit count
            candidate_opex_per_unit: Annual operating expense per unit
            portfolio_assets_in_metro: Count of existing Aker assets in same metro
            local_reputation_score: Aker brand strength in market (0-100)

        Returns:
            SynergyResult with estimated $ value and operational benefits

        Spec: Requirement 10, Scenario "Operational scale synergies"
        """
        synergy_factors = []
        opex_savings_pct = 0.0
        lease_up_bonus_days = 0

        if portfolio_assets_in_metro == 0:
            # New market entry - no synergies yet
            synergy_factors.append("New market entry - building brand presence")
            opex_savings_pct = 0.0
            lease_up_bonus_days = 0
        elif portfolio_assets_in_metro == 1:
            # Second asset - some synergies begin
            synergy_factors.extend(
                [
                    "Second asset enables vendor negotiations",
                    "Emerging local brand recognition",
                ]
            )
            opex_savings_pct = 2.0
            lease_up_bonus_days = 5 if local_reputation_score > 60 else 0
        elif portfolio_assets_in_metro <= 4:
            # Small cluster - meaningful synergies
            synergy_factors.extend(
                [
                    "Shared vendor contracts and bulk purchasing",
                    "Regional maintenance team efficiency",
                    "Established local brand and referral network",
                ]
            )
            opex_savings_pct = 3.5
            lease_up_bonus_days = 10 if local_reputation_score > 70 else 5
        else:
            # Large cluster - maximum synergies
            synergy_factors.extend(
                [
                    "Portfolio pricing power with vendors",
                    "Dedicated regional operations team",
                    "Strong local brand drives organic lead generation",
                    "Resident transfers between properties",
                ]
            )
            opex_savings_pct = 5.0
            lease_up_bonus_days = 15 if local_reputation_score > 80 else 10

        # Calculate annual synergy value
        annual_opex = candidate_opex_per_unit * candidate_units
        opex_savings = annual_opex * (opex_savings_pct / 100)

        # Lease-up savings (assume $50/day carrying cost per unit during lease-up)
        lease_up_savings = lease_up_bonus_days * 50 * candidate_units

        # Total annual synergy value (opex ongoing, lease-up one-time amortized over 5 years)
        synergy_value_estimate = opex_savings + (lease_up_savings / 5)

        return SynergyResult(
            synergy_value_estimate=round(synergy_value_estimate, 2),
            opex_savings_pct=opex_savings_pct,
            lease_up_bonus_days=lease_up_bonus_days,
            synergy_factors=synergy_factors,
        )

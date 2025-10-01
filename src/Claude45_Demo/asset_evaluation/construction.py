"""Construction and logistics cost adjustments for CO/UT/ID mountain markets.

Applies premiums for winter construction, mountain logistics, and labor market constraints.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class WinterPremiumResult:
    """Winter construction premium calculation."""

    winter_months: int  # Count of Nov-Mar months in schedule
    premium_percentage: float  # % premium to apply
    premium_amount: float  # $ premium
    adjusted_cost: float
    notes: str


@dataclass(frozen=True)
class LogisticsPremiumResult:
    """Mountain logistics premium calculation."""

    accessibility_rating: str  # "urban", "suburban", "mountain_access", "remote"
    premium_percentage: float
    premium_amount: float
    adjusted_cost: float
    factors: list[str]


@dataclass(frozen=True)
class LaborMarketResult:
    """Labor market availability assessment."""

    risk_score: int  # 0-100, higher = more risk
    unemployment_rate: float
    wage_premium_pct: float  # % above baseline wages
    risk_level: str  # "low", "medium", "high"
    recommendation: str


class ConstructionAdjuster:
    """Apply state-specific construction cost adjustments."""

    WINTER_MONTHS = {11, 12, 1, 2, 3}  # Nov-Mar

    def __init__(self) -> None:
        """Initialize construction adjuster."""
        pass

    def adjust_winter_premium(
        self,
        *,
        start_date: date,
        end_date: date,
        base_cost: float,
        location_type: str = "mountain",  # "urban", "suburban", "mountain"
    ) -> WinterPremiumResult:
        """Calculate winter construction premium for Nov-Mar work.

        Args:
            start_date: Construction start date
            end_date: Construction end date
            base_cost: Base construction cost
            location_type: Location type (affects severity of winter impact)

        Returns:
            WinterPremiumResult with premium % and adjusted cost

        Spec: Requirement 8, Scenario "Winter construction premium"
        """
        # Count months in winter period
        winter_months = 0
        current = start_date.replace(day=1)

        while current <= end_date:
            if current.month in self.WINTER_MONTHS:
                winter_months += 1

            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        # Calculate premium based on location type and winter exposure
        if winter_months == 0:
            premium_pct = 0.0
            notes = "No winter months in construction schedule"
        elif location_type == "urban":
            # Urban areas have better access, less severe impact
            premium_pct = 0.05 + (winter_months * 0.01)
            premium_pct = min(premium_pct, 0.10)  # Cap at 10%
            notes = f"Urban location: moderate winter impact ({winter_months} winter months)"
        elif location_type == "suburban":
            premium_pct = 0.08 + (winter_months * 0.015)
            premium_pct = min(premium_pct, 0.15)  # Cap at 15%
            notes = (
                f"Suburban location: significant winter impact ({winter_months} months)"
            )
        else:  # mountain
            premium_pct = 0.10 + (winter_months * 0.02)
            premium_pct = min(premium_pct, 0.20)  # Cap at 20%
            notes = (
                f"Mountain location: severe winter impact ({winter_months} months). "
                f"Consider seasonal shutdown or heated enclosures"
            )

        premium_amount = base_cost * premium_pct
        adjusted_cost = base_cost + premium_amount

        return WinterPremiumResult(
            winter_months=winter_months,
            premium_percentage=round(premium_pct, 4),
            premium_amount=round(premium_amount, 2),
            adjusted_cost=round(adjusted_cost, 2),
            notes=notes,
        )

    def calculate_logistics_premium(
        self,
        *,
        base_cost: float,
        distance_to_metro_miles: float,
        elevation_ft: int,
        accessibility: str = "paved",  # "paved", "dirt_road", "4wd_only"
        nearest_supplier_miles: float = 20,
    ) -> LogisticsPremiumResult:
        """Calculate logistics premium for remote/mountain locations.

        Args:
            base_cost: Base construction cost
            distance_to_metro_miles: Distance to major metro area
            elevation_ft: Site elevation (higher = more challenging)
            accessibility: Road accessibility
            nearest_supplier_miles: Distance to material suppliers

        Returns:
            LogisticsPremiumResult with premium % and factors

        Spec: Requirement 8, Scenario "Mountain logistics premium"
        """
        factors = []
        premium_pct = 0.0

        # Distance premium
        if distance_to_metro_miles < 20:
            accessibility_rating = "urban"
            factors.append("Urban proximity - minimal logistics impact")
        elif distance_to_metro_miles < 50:
            accessibility_rating = "suburban"
            premium_pct += 0.03
            factors.append("Suburban distance - moderate delivery costs")
        elif distance_to_metro_miles < 100:
            accessibility_rating = "mountain_access"
            premium_pct += 0.07
            factors.append("Mountain location - extended delivery routes")
        else:
            accessibility_rating = "remote"
            premium_pct += 0.12
            factors.append("Remote location - significant logistics challenges")

        # Road accessibility premium
        if accessibility == "dirt_road":
            premium_pct += 0.02
            factors.append("Dirt road access - seasonal limitations")
        elif accessibility == "4wd_only":
            premium_pct += 0.04
            factors.append("4WD access only - equipment mobilization premium")

        # Elevation premium (thin air affects equipment, longer travel times)
        if elevation_ft > 8000:
            premium_pct += 0.03
            factors.append("High elevation (>8000ft) - equipment performance reduction")
        elif elevation_ft > 6000:
            premium_pct += 0.015
            factors.append("Moderate elevation (6000-8000ft) - minor equipment impacts")

        # Supplier distance
        if nearest_supplier_miles > 50:
            premium_pct += 0.02
            factors.append(
                f"Distant suppliers ({nearest_supplier_miles:.0f}mi) - bulk order required"
            )

        # Cap premium at 15%
        premium_pct = min(premium_pct, 0.15)

        premium_amount = base_cost * premium_pct
        adjusted_cost = base_cost + premium_amount

        return LogisticsPremiumResult(
            accessibility_rating=accessibility_rating,
            premium_percentage=round(premium_pct, 4),
            premium_amount=round(premium_amount, 2),
            adjusted_cost=round(adjusted_cost, 2),
            factors=factors,
        )

    def assess_labor_market(
        self,
        *,
        unemployment_rate: float,  # Local unemployment rate (decimal)
        construction_employment_change: float = 0.0,  # YoY % change in construction jobs
        state: str = "CO",  # CO, UT, ID
    ) -> LaborMarketResult:
        """Assess labor market availability and wage premium risk.

        Args:
            unemployment_rate: Local unemployment rate (e.g., 0.03 = 3%)
            construction_employment_change: YoY change in construction employment (decimal)
            state: State abbreviation

        Returns:
            LaborMarketResult with risk score and wage premium estimate

        Spec: Requirement 8, Scenario "Labor availability check"
        """
        risk_score = 0
        wage_premium_pct = 0.0

        # Unemployment rate assessment
        if unemployment_rate < 0.025:
            # Very tight labor market
            risk_score += 40
            wage_premium_pct += 0.20
            _ = "Critically tight labor market (<2.5% unemployment)"  # risk_note
        elif unemployment_rate < 0.03:
            # Tight labor market
            risk_score += 25
            wage_premium_pct += 0.15
            _ = "Tight labor market (<3% unemployment)"  # risk_note
        elif unemployment_rate < 0.04:
            # Moderately tight
            risk_score += 15
            wage_premium_pct += 0.08
            _ = "Moderately tight labor market (3-4% unemployment)"  # risk_note
        else:
            # Normal/loose labor market
            risk_score += 5
            wage_premium_pct += 0.02
            _ = "Adequate labor supply (>4% unemployment)"  # risk_note

        # Construction employment trend assessment
        if construction_employment_change > 0.05:
            # Rapidly growing = labor shortage risk
            risk_score += 20
            wage_premium_pct += 0.05
            _ = "Construction employment growing >5% YoY - high demand for labor"  # trend_note
        elif construction_employment_change > 0.02:
            risk_score += 10
            wage_premium_pct += 0.02
            _ = "Construction employment growing 2-5% YoY - moderate demand"  # trend_note
        elif construction_employment_change < -0.02:
            # Declining employment = more available workers
            risk_score -= 10
            wage_premium_pct -= 0.03
            _ = "Construction employment declining - labor availability improving"  # trend_note
        else:
            _ = "Stable construction employment"  # trend_note

        # State-specific adjustments
        if state == "ID":
            # Idaho has seen rapid in-migration and construction boom
            risk_score += 10
            wage_premium_pct += 0.03
            _ = "Idaho market: in-migration driving construction demand"  # state_note
        elif state == "UT":
            # Utah has strong growth and tight labor
            risk_score += 8
            wage_premium_pct += 0.025
            _ = "Utah market: Silicon Slopes growth sustaining labor demand"  # state_note
        else:  # CO
            risk_score += 5
            _ = "Colorado market: established construction workforce"  # state_note

        # Cap risk score and wage premium
        risk_score = max(0, min(100, risk_score))
        wage_premium_pct = max(0.0, min(0.25, wage_premium_pct))

        # Risk level classification
        if risk_score >= 60:
            risk_level = "high"
            recommendation = (
                "High risk: Pre-qualify contractors, consider GMP contracts, buffer schedule "
                "for labor delays. Wage premiums likely 20-25% above baseline."
            )
        elif risk_score >= 35:
            risk_level = "medium"
            recommendation = (
                "Medium risk: Competitive bid environment. Consider incentives for on-time "
                f"completion. Wage premiums ~{wage_premium_pct:.0%} above baseline."
            )
        else:
            risk_level = "low"
            recommendation = (
                "Low risk: Adequate labor supply. Normal procurement process. "
                "Minimal wage premiums expected."
            )

        return LaborMarketResult(
            risk_score=risk_score,
            unemployment_rate=unemployment_rate,
            wage_premium_pct=round(wage_premium_pct, 4),
            risk_level=risk_level,
            recommendation=recommendation,
        )

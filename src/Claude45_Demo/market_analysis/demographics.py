"""Demographic trend analysis for market analysis."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class DemographicAnalyzer:
    """Analyze population growth, income trends, and migration patterns."""

    def calculate_population_growth_score(
        self,
        population_5yr_cagr: float,
        population_10yr_cagr: float,
        state_avg_5yr_cagr: float,
        age_25_44_pct: float,
    ) -> dict[str, Any]:
        """
        Calculate population growth score.

        Implements:
        - Req: Demographic and Economic Trends
        - Scenario: Population growth analysis

        Args:
            population_5yr_cagr: 5-year population CAGR
            population_10yr_cagr: 10-year population CAGR
            state_avg_5yr_cagr: State average 5-year CAGR (for comparison)
            age_25_44_pct: Percentage of population age 25-44 (prime renter cohort)

        Returns:
            Dict with population score and component details
        """
        # Normalize 5-year CAGR: 0% = 0, 2%+ = 100
        if population_5yr_cagr <= 0:
            cagr_5yr_score = 0.0
        elif population_5yr_cagr >= 0.02:
            cagr_5yr_score = 100.0
        else:
            cagr_5yr_score = (population_5yr_cagr / 0.02) * 100.0

        # Bonus for outpacing state average
        if population_5yr_cagr > state_avg_5yr_cagr:
            outpace_bonus = 10.0
        else:
            outpace_bonus = 0.0

        # Normalize 25-44 age cohort: 20% = 50, 30%+ = 100
        if age_25_44_pct <= 20.0:
            age_score = (age_25_44_pct / 20.0) * 50.0
        elif age_25_44_pct >= 30.0:
            age_score = 100.0
        else:
            age_score = 50.0 + ((age_25_44_pct - 20.0) / 10.0) * 50.0

        # Composite: 60% CAGR, 30% age distribution, 10% state comparison
        composite = (cagr_5yr_score * 0.6) + (age_score * 0.3) + (outpace_bonus * 1.0)
        composite = min(100.0, composite)

        return {
            "score": round(composite, 1),
            "components": {
                "cagr_5yr": round(cagr_5yr_score, 1),
                "age_25_44": round(age_score, 1),
                "outpace_state": outpace_bonus > 0,
            },
            "metrics": {
                "population_5yr_cagr": population_5yr_cagr,
                "population_10yr_cagr": population_10yr_cagr,
                "age_25_44_pct": age_25_44_pct,
            },
        }

    def calculate_income_trend_score(
        self,
        median_hh_income: float,
        income_5yr_cagr: float,
        cost_of_living_index: float,
    ) -> dict[str, Any]:
        """
        Calculate income trend score.

        Implements:
        - Req: Demographic and Economic Trends
        - Scenario: Income trend analysis

        Args:
            median_hh_income: Median household income (current)
            income_5yr_cagr: 5-year real income CAGR (inflation-adjusted)
            cost_of_living_index: Cost of living index (100 = national average)

        Returns:
            Dict with income score and details
        """
        # Normalize median income: $50k = 25, $75k+ = 100
        if median_hh_income <= 50000:
            income_level_score = (median_hh_income / 50000) * 25.0
        elif median_hh_income >= 75000:
            income_level_score = 100.0
        else:
            income_level_score = 25.0 + ((median_hh_income - 50000) / 25000) * 75.0

        # Normalize income growth: 0% = 0, 3%+ = 100
        if income_5yr_cagr <= 0:
            growth_score = 0.0
        elif income_5yr_cagr >= 0.03:
            growth_score = 100.0
        else:
            growth_score = (income_5yr_cagr / 0.03) * 100.0

        # Adjust for cost of living (lower is better)
        if cost_of_living_index <= 90:
            col_adjustment = 10.0
        elif cost_of_living_index >= 120:
            col_adjustment = -10.0
        else:
            col_adjustment = 0.0

        composite = (income_level_score * 0.4) + (growth_score * 0.6) + col_adjustment
        composite = max(0.0, min(100.0, composite))

        return {
            "score": round(composite, 1),
            "components": {
                "income_level": round(income_level_score, 1),
                "income_growth": round(growth_score, 1),
            },
            "metrics": {
                "median_hh_income": median_hh_income,
                "income_5yr_cagr": income_5yr_cagr,
                "cost_of_living_index": cost_of_living_index,
            },
        }

    def calculate_migration_score(
        self,
        net_migration_3yr: int,
        population: int,
        avg_agi_per_migrant: float,
    ) -> dict[str, Any]:
        """
        Calculate net migration score.

        Implements:
        - Req: Demographic and Economic Trends
        - Scenario: Net migration patterns

        Args:
            net_migration_3yr: Net in-migration over 3 years (inflows - outflows)
            population: Total population (for calculating migration rate)
            avg_agi_per_migrant: Average AGI per migrant household

        Returns:
            Dict with migration score and details
        """
        # Calculate migration rate (% of population)
        migration_rate = (
            (net_migration_3yr / population) * 100.0 if population > 0 else 0.0
        )

        # Normalize migration rate: -1% = 0, +2% = 100
        if migration_rate <= -1.0:
            rate_score = 0.0
        elif migration_rate >= 2.0:
            rate_score = 100.0
        else:
            rate_score = ((migration_rate + 1.0) / 3.0) * 100.0

        # Normalize AGI: $40k = 25, $75k+ = 100
        if avg_agi_per_migrant <= 40000:
            agi_score = (avg_agi_per_migrant / 40000) * 25.0
        elif avg_agi_per_migrant >= 75000:
            agi_score = 100.0
        else:
            agi_score = 25.0 + ((avg_agi_per_migrant - 40000) / 35000) * 75.0

        # Composite: 70% rate, 30% quality (AGI)
        composite = (rate_score * 0.7) + (agi_score * 0.3)

        return {
            "score": round(composite, 1),
            "components": {
                "migration_rate": round(rate_score, 1),
                "migrant_income": round(agi_score, 1),
            },
            "metrics": {
                "net_migration_3yr": net_migration_3yr,
                "migration_rate_pct": round(migration_rate, 2),
                "avg_agi_per_migrant": avg_agi_per_migrant,
            },
        }

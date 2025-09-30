"""Market elasticity metrics for demand/supply balance analysis."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MarketElasticityCalculator:
    """Calculate market elasticity and demand/supply indicators."""

    def calculate_vacancy_score(
        self,
        rental_vacancy_rate: float,
        state_avg_vacancy: float,
        national_avg_vacancy: float,
    ) -> dict[str, Any]:
        """
        Calculate vacancy rate score (lower vacancy = tighter market = higher score).

        Implements:
        - Req: Market Elasticity Metrics
        - Scenario: Vacancy rate analysis

        Args:
            rental_vacancy_rate: Local rental vacancy rate (0-1)
            state_avg_vacancy: State average vacancy rate (0-1)
            national_avg_vacancy: National average vacancy rate (0-1)

        Returns:
            Dict with vacancy score and comparisons
        """
        # Normalize vacancy inversely: 3% = 100, 5% = 75, 7% = 50, 10%+ = 0
        vacancy_pct = rental_vacancy_rate * 100
        if vacancy_pct <= 3.0:
            score = 100.0
        elif vacancy_pct >= 10.0:
            score = 0.0
        else:
            score = 100.0 - ((vacancy_pct - 3.0) / 7.0) * 100.0

        # Comparison to benchmarks
        beats_state = rental_vacancy_rate < state_avg_vacancy
        beats_national = rental_vacancy_rate < national_avg_vacancy

        return {
            "score": round(score, 1),
            "vacancy_rate": rental_vacancy_rate,
            "comparisons": {
                "beats_state_avg": beats_state,
                "beats_national_avg": beats_national,
                "state_avg": state_avg_vacancy,
                "national_avg": national_avg_vacancy,
            },
        }

    def calculate_absorption_score(
        self,
        permits_3yr_avg: int,
        population_growth_3yr_pct: float,
        units_delivered_3yr: int,
    ) -> dict[str, Any]:
        """
        Calculate market absorption score.

        Implements:
        - Req: Market Elasticity Metrics
        - Scenario: Lease-up velocity proxy

        Args:
            permits_3yr_avg: Average annual permits over 3 years
            population_growth_3yr_pct: 3-year population growth percentage
            units_delivered_3yr: Total units delivered in 3 years

        Returns:
            Dict with absorption score
        """
        # Estimate absorption rate (simplified proxy)
        # Higher population growth + moderate supply = strong absorption
        if population_growth_3yr_pct >= 5.0 and units_delivered_3yr > 0:
            # Strong growth, good supply
            absorption_estimate = min(100.0, (population_growth_3yr_pct / 5.0) * 80.0)
        elif population_growth_3yr_pct >= 5.0 and units_delivered_3yr == 0:
            # Strong growth, constrained supply (excellent)
            absorption_estimate = 100.0
        elif population_growth_3yr_pct < 2.0:
            # Weak growth
            absorption_estimate = (population_growth_3yr_pct / 2.0) * 40.0
        else:
            # Moderate growth
            absorption_estimate = (
                40.0 + ((population_growth_3yr_pct - 2.0) / 3.0) * 40.0
            )

        return {
            "score": round(absorption_estimate, 1),
            "metrics": {
                "permits_3yr_avg": permits_3yr_avg,
                "population_growth_3yr_pct": population_growth_3yr_pct,
                "units_delivered_3yr": units_delivered_3yr,
            },
            "metadata": {"proxy_estimate": True, "confidence": "medium"},
        }

    def calculate_market_momentum_score(
        self,
        employment_3yr_cagr: float,
        population_3yr_cagr: float,
        income_3yr_cagr: float,
    ) -> dict[str, Any]:
        """
        Calculate market momentum score (3-year CAGR trends).

        Implements:
        - Task 3.8: Market momentum tracking

        Args:
            employment_3yr_cagr: 3-year employment CAGR
            population_3yr_cagr: 3-year population CAGR
            income_3yr_cagr: 3-year income CAGR

        Returns:
            Dict with momentum score
        """

        # Normalize each CAGR: 0% = 0, 3%+ = 100
        def normalize_cagr(cagr: float) -> float:
            if cagr <= 0:
                return 0.0
            elif cagr >= 0.03:
                return 100.0
            else:
                return (cagr / 0.03) * 100.0

        employment_score = normalize_cagr(employment_3yr_cagr)
        population_score = normalize_cagr(population_3yr_cagr)
        income_score = normalize_cagr(income_3yr_cagr)

        # Weighted average: employment 40%, population 35%, income 25%
        composite = (
            (employment_score * 0.40)
            + (population_score * 0.35)
            + (income_score * 0.25)
        )

        return {
            "score": round(composite, 1),
            "components": {
                "employment_momentum": round(employment_score, 1),
                "population_momentum": round(population_score, 1),
                "income_momentum": round(income_score, 1),
            },
            "cagr_values": {
                "employment": employment_3yr_cagr,
                "population": population_3yr_cagr,
                "income": income_3yr_cagr,
            },
        }

"""Integration tests for complete market analysis workflow."""

from Claude45_Demo.market_analysis.convenience import UrbanConvenienceScorer
from Claude45_Demo.market_analysis.demographics import DemographicAnalyzer
from Claude45_Demo.market_analysis.elasticity import MarketElasticityCalculator
from Claude45_Demo.market_analysis.employment import EmploymentAnalyzer
from Claude45_Demo.market_analysis.supply_constraint import SupplyConstraintCalculator


class TestMarketAnalysisIntegration:
    """Test complete market analysis workflow."""

    def test_complete_market_analysis_workflow(self) -> None:
        """Test full market analysis for a submarket."""
        # Initialize all analyzers
        supply_calc = SupplyConstraintCalculator()
        employment = EmploymentAnalyzer()
        demographics = DemographicAnalyzer()
        convenience = UrbanConvenienceScorer()
        elasticity = MarketElasticityCalculator()

        # 1. Supply Constraint Analysis
        supply_score = supply_calc.calculate_composite_score(
            permit_elasticity=75.0,
            topographic_constraint=80.0,
            regulatory_friction=70.0,
        )

        assert supply_score["score"] > 0
        assert supply_score["metadata"]["complete"] is True

        # 2. Employment Analysis
        sector_cagr = {
            "tech": 0.035,
            "healthcare": 0.025,
            "education": 0.015,
            "manufacturing": 0.01,
        }
        sector_lq = {
            "tech": 1.3,
            "healthcare": 1.1,
            "education": 1.0,
            "manufacturing": 0.9,
        }

        employment_score = employment.calculate_innovation_employment_score(
            sector_cagr, sector_lq
        )

        assert employment_score["score"] > 0

        # 3. Demographic Analysis
        pop_score = demographics.calculate_population_growth_score(
            population_5yr_cagr=0.02,
            population_10yr_cagr=0.018,
            state_avg_5yr_cagr=0.012,
            age_25_44_pct=27.0,
        )

        income_score = demographics.calculate_income_trend_score(
            median_hh_income=65000.0, income_5yr_cagr=0.02, cost_of_living_index=102.0
        )

        migration_score = demographics.calculate_migration_score(
            net_migration_3yr=3000, population=150000, avg_agi_per_migrant=55000.0
        )

        assert all(
            score["score"] > 0 for score in [pop_score, income_score, migration_score]
        )

        # 4. Urban Convenience Analysis
        accessibility = convenience.calculate_15min_accessibility_score(
            grocery_count=2,
            pharmacy_count=1,
            school_count=3,
            transit_stop_count=5,
            intersection_density_per_sqkm=90.0,
        )

        retail_health = convenience.calculate_retail_health_score(
            daytime_population=10000,
            retail_vacancy_rate=0.07,
            population_density_per_sqkm=2500,
        )

        transit_quality = convenience.calculate_transit_quality_score(
            stops_within_800m=3,
            avg_weekday_headway_min=15.0,
            weekend_service_available=True,
        )

        assert all(
            score["score"] > 0
            for score in [accessibility, retail_health, transit_quality]
        )

        # 5. Market Elasticity Analysis
        vacancy = elasticity.calculate_vacancy_score(
            rental_vacancy_rate=0.045,
            state_avg_vacancy=0.055,
            national_avg_vacancy=0.065,
        )

        momentum = elasticity.calculate_market_momentum_score(
            employment_3yr_cagr=0.022, population_3yr_cagr=0.02, income_3yr_cagr=0.018
        )

        assert vacancy["score"] > 0
        assert momentum["score"] > 0

        # Verify all components can be aggregated
        all_scores = {
            "supply_constraint": supply_score["score"],
            "innovation_employment": employment_score["score"],
            "population_growth": pop_score["score"],
            "income_trend": income_score["score"],
            "migration": migration_score["score"],
            "accessibility": accessibility["score"],
            "retail_health": retail_health["score"],
            "transit_quality": transit_quality["score"],
            "vacancy": vacancy["score"],
            "momentum": momentum["score"],
        }

        # All scores should be numeric and in valid range
        for name, score in all_scores.items():
            assert isinstance(score, (int, float)), f"{name} score not numeric"
            assert 0 <= score <= 100, f"{name} score out of range: {score}"

    def test_edge_case_zero_employment(self) -> None:
        """Test handling of zero employment scenarios."""
        employment = EmploymentAnalyzer()

        lq = employment.calculate_location_quotient(
            local_employment={"tech": 0, "other": 100},
            national_employment={"tech": 1000, "other": 10000},
        )

        assert lq["tech"] == 0.0

    def test_edge_case_negative_cagr(self) -> None:
        """Test handling of negative growth rates."""
        employment = EmploymentAnalyzer()

        cagr = employment.calculate_cagr(start_value=100.0, end_value=90.0, years=3)

        assert cagr < 0

    def test_composite_with_missing_data(self) -> None:
        """Test composite calculations with missing data."""
        supply_calc = SupplyConstraintCalculator()

        result = supply_calc.calculate_composite_score(
            permit_elasticity=80.0,
            topographic_constraint=None,
            regulatory_friction=75.0,
        )

        assert result["metadata"]["complete"] is False
        assert "topographic_constraint" in result["metadata"]["missing_components"]
        assert result["score"] > 0  # Should still calculate from available data

    def test_normalization_boundary_conditions(self) -> None:
        """Test normalization at boundary conditions."""
        demographics = DemographicAnalyzer()

        # Test with extreme values
        result = demographics.calculate_population_growth_score(
            population_5yr_cagr=0.05,  # Very high growth
            population_10yr_cagr=0.04,
            state_avg_5yr_cagr=0.01,
            age_25_44_pct=35.0,  # Very high percentage
        )

        assert result["score"] == 100.0  # Should cap at 100

    def test_data_quality_indicators(self) -> None:
        """Test that data quality metadata is preserved."""
        elasticity = MarketElasticityCalculator()

        result = elasticity.calculate_absorption_score(
            permits_3yr_avg=400, population_growth_3yr_pct=5.5, units_delivered_3yr=1200
        )

        assert "metadata" in result
        assert "proxy_estimate" in result["metadata"]
        assert result["metadata"]["confidence"] in ["low", "medium", "high"]

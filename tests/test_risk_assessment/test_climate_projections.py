"""Tests for climate projection adjustments."""

import pytest

from Claude45_Demo.risk_assessment.climate_projections import (
    ClimateProjectionAnalyzer,
)


@pytest.fixture
def climate_analyzer():
    """Climate projection analyzer fixture."""
    return ClimateProjectionAnalyzer()


class TestWildfireProjections:
    """Test wildfire risk projection adjustments."""

    def test_high_emissions_scenario(self, climate_analyzer):
        """Test wildfire adjustment with high emissions scenario."""
        mock_projection = {
            "fire_season_increase_days": 45,
            "intensity_increase_pct": 25,
            "projection_year": 2050,
        }

        result = climate_analyzer.adjust_wildfire_risk(
            current_wildfire_score=60,
            region="Colorado_Front_Range",
            scenario="RCP8.5",
            mock_projection=mock_projection,
        )

        assert result["climate_adjusted_wildfire_score"] > 60
        assert result["adjustment_pct"] > 0
        assert result["scenario"] == "RCP8.5"
        assert result["confidence"] == "medium"

    def test_low_emissions_scenario(self, climate_analyzer):
        """Test wildfire adjustment with low emissions scenario."""
        mock_projection = {
            "fire_season_increase_days": 15,
            "intensity_increase_pct": 10,
            "projection_year": 2040,
        }

        result = climate_analyzer.adjust_wildfire_risk(
            current_wildfire_score=50,
            region="Utah",
            scenario="RCP2.6",
            mock_projection=mock_projection,
        )

        assert result["climate_adjusted_wildfire_score"] >= 50
        assert result["adjustment_pct"] <= 20  # Capped per spec
        assert result["confidence"] == "high"

    def test_adjustment_capped_at_20_percent(self, climate_analyzer):
        """Test that wildfire adjustment is capped at +20%."""
        mock_projection = {
            "fire_season_increase_days": 90,  # Extreme increase
            "intensity_increase_pct": 50,
            "projection_year": 2050,
        }

        result = climate_analyzer.adjust_wildfire_risk(
            current_wildfire_score=80,
            region="California",
            scenario="RCP8.5",
            mock_projection=mock_projection,
        )

        assert result["adjustment_pct"] == 20  # Capped
        assert result["climate_adjusted_wildfire_score"] <= 100


class TestDroughtProjections:
    """Test drought risk projection adjustments."""

    def test_long_hold_investment(self, climate_analyzer):
        """Test drought adjustment applied for 10+ year investment."""
        mock_projection = {
            "supply_demand_imbalance_pct": 25,
            "drought_frequency_increase_pct": 30,
            "projection_year": 2050,
        }

        result = climate_analyzer.adjust_drought_risk(
            current_drought_score=55,
            region="Colorado_Western_Slope",
            scenario="RCP4.5",
            investment_horizon_years=15,
            mock_projection=mock_projection,
        )

        assert result["adjustment_applied"] is True
        assert result["climate_adjusted_drought_score"] > 55
        assert result["investment_horizon_years"] == 15

    def test_short_hold_no_adjustment(self, climate_analyzer):
        """Test no drought adjustment for short-term investment."""
        mock_projection = {
            "supply_demand_imbalance_pct": 25,
            "drought_frequency_increase_pct": 30,
            "projection_year": 2050,
        }

        result = climate_analyzer.adjust_drought_risk(
            current_drought_score=55,
            region="Colorado_Western_Slope",
            scenario="RCP4.5",
            investment_horizon_years=5,
            mock_projection=mock_projection,
        )

        assert result["adjustment_applied"] is False
        assert result["climate_adjusted_drought_score"] == 55
        assert result["adjustment_pct"] == 0

    def test_critical_imbalance_flag(self, climate_analyzer):
        """Test critical supply-demand imbalance flag."""
        mock_projection = {
            "supply_demand_imbalance_pct": 30,  # >20% triggers flag
            "drought_frequency_increase_pct": 40,
            "projection_year": 2050,
        }

        result = climate_analyzer.adjust_drought_risk(
            current_drought_score=60,
            region="Utah",
            scenario="RCP8.5",
            investment_horizon_years=20,
            mock_projection=mock_projection,
        )

        assert result["critical_imbalance"] is True
        assert result["supply_demand_imbalance_pct"] == 30


class TestCompositeClimateAdjustment:
    """Test composite climate adjustment calculation."""

    def test_wildfire_and_drought_adjustments(self, climate_analyzer):
        """Test composite adjustment with both wildfire and drought."""
        current_risk_scores = {
            "wildfire_score": 65,
            "drought_score": 50,
            "flood_score": 30,
        }

        climate_adjustments = {
            "wildfire": {
                "climate_adjusted_wildfire_score": 75,
                "adjustment_pct": 15.4,
                "scenario": "RCP4.5",
            },
            "drought": {
                "climate_adjusted_drought_score": 58,
                "adjustment_pct": 16.0,
                "adjustment_applied": True,
                "scenario": "RCP4.5",
            },
        }

        result = climate_analyzer.calculate_composite_climate_adjustment(
            current_risk_scores, climate_adjustments
        )

        assert result["climate_adjusted_scores"]["wildfire_score"] == 75
        assert result["climate_adjusted_scores"]["drought_score"] == 58
        assert result["climate_adjusted_scores"]["flood_score"] == 30  # Unchanged
        assert len(result["adjustments_applied"]) == 2

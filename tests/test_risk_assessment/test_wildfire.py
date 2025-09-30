"""Tests for wildfire risk assessment."""

from __future__ import annotations

import pytest


class TestWildfireHazardPotential:
    """Test USFS WHP raster queries and scoring."""

    def test_high_whp_score(self, wildfire_analyzer):
        """Test high WHP score (5 on 1-5 scale → 100 score)."""
        mock_whp_data = {
            "mean_whp": 4.8,
            "max_whp": 5.0,
            "buffer_radius_km": 1.0,
        }

        result = wildfire_analyzer.assess_wildfire_hazard_potential(
            latitude=39.7392,
            longitude=-105.4983,  # Mountain area
            mock_whp=mock_whp_data,
        )

        assert result["mean_whp"] == 4.8
        assert result["max_whp"] == 5.0
        assert result["whp_score"] >= 95  # Very high hazard
        assert result["risk_category"] == "very_high"

    def test_moderate_whp_score(self, wildfire_analyzer):
        """Test moderate WHP score (3 on 1-5 scale → 60 score)."""
        mock_whp_data = {"mean_whp": 3.0, "max_whp": 4.0, "buffer_radius_km": 1.0}

        result = wildfire_analyzer.assess_wildfire_hazard_potential(
            latitude=39.7392,
            longitude=-105.4983,
            mock_whp=mock_whp_data,
        )

        assert result["whp_score"] >= 55
        assert result["whp_score"] <= 65
        assert result["risk_category"] == "high"  # WHP 3 = 60 score = high (>=60)

    def test_low_whp_score(self, wildfire_analyzer):
        """Test low WHP score (1 on 1-5 scale → 20 score)."""
        mock_whp_data = {"mean_whp": 1.2, "max_whp": 2.0, "buffer_radius_km": 1.0}

        result = wildfire_analyzer.assess_wildfire_hazard_potential(
            latitude=39.7392,
            longitude=-104.9903,  # Urban Denver
            mock_whp=mock_whp_data,
        )

        assert result["whp_score"] <= 30
        assert result["risk_category"] == "low"


class TestFuelModelAnalysis:
    """Test LANDFIRE fuel model analysis."""

    def test_high_risk_fuel_types(self, wildfire_analyzer):
        """Test high-risk fuel types (timber, brush)."""
        mock_fuel_data = {
            "fuel_types": {
                "timber": 45,  # % of buffer area
                "brush": 30,
                "grass": 15,
                "urban": 10,
            }
        }

        result = wildfire_analyzer.analyze_fuel_models(
            latitude=39.7392,
            longitude=-105.4983,
            mock_fuel_data=mock_fuel_data,
        )

        assert result["high_risk_fuel_pct"] == 75  # timber + brush
        assert result["fuel_score"] >= 70
        assert "timber" in result["dominant_fuel_types"]

    def test_low_risk_fuel_types(self, wildfire_analyzer):
        """Test low-risk fuel types (grass, urban)."""
        mock_fuel_data = {
            "fuel_types": {
                "grass": 40,
                "urban": 50,
                "agriculture": 10,
            }
        }

        result = wildfire_analyzer.analyze_fuel_models(
            latitude=39.7392,
            longitude=-104.9903,
            mock_fuel_data=mock_fuel_data,
        )

        assert result["high_risk_fuel_pct"] == 0
        assert result["fuel_score"] <= 30


class TestHistoricalFireProximity:
    """Test historical fire perimeter analysis."""

    def test_recent_large_fire_nearby(self, wildfire_analyzer):
        """Test property near recent large fire."""
        mock_fire_history = [
            {"year": 2021, "name": "Caldor Fire", "acres": 221898, "distance_km": 5.2},
            {"year": 2020, "name": "Cameron Peak", "acres": 208913, "distance_km": 8.1},
        ]

        result = wildfire_analyzer.assess_fire_history(
            latitude=39.7392,
            longitude=-105.4983,
            lookback_years=20,
            mock_history=mock_fire_history,
        )

        assert result["fires_within_10km"] == 2
        assert result["nearest_large_fire_km"] == 5.2
        assert result["fire_history_score"] >= 70
        assert result["recent_fire_activity"] is True

    def test_no_recent_fires(self, wildfire_analyzer):
        """Test area with no recent fire history."""
        mock_fire_history = []

        result = wildfire_analyzer.assess_fire_history(
            latitude=39.7392,
            longitude=-104.9903,
            lookback_years=20,
            mock_history=mock_fire_history,
        )

        assert result["fires_within_10km"] == 0
        assert result["nearest_large_fire_km"] is None
        assert result["fire_history_score"] <= 20


class TestWildlandUrbanInterface:
    """Test WUI classification."""

    def test_intermix_wui_high_risk(self, wildfire_analyzer):
        """Test Intermix WUI (highest risk - vegetation + structures)."""
        mock_wui_data = {
            "classification": "Intermix",
            "housing_density": 45,  # homes per sq km
            "vegetation_pct": 70,
            "evacuation_routes": 1,  # Single access road
        }

        result = wildfire_analyzer.classify_wui(
            latitude=39.7392,
            longitude=-105.4983,
            mock_wui=mock_wui_data,
        )

        assert result["wui_class"] == "Intermix"
        assert result["wui_risk_score"] >= 85
        assert result["evacuation_constraint"] is True
        assert "single access" in result["notes"].lower()

    def test_interface_wui_moderate_risk(self, wildfire_analyzer):
        """Test Interface WUI (structures near wildland)."""
        mock_wui_data = {
            "classification": "Interface",
            "housing_density": 120,
            "vegetation_pct": 30,
            "evacuation_routes": 3,
        }

        result = wildfire_analyzer.classify_wui(
            latitude=39.7392,
            longitude=-105.4983,
            mock_wui=mock_wui_data,
        )

        assert result["wui_class"] == "Interface"
        assert 50 <= result["wui_risk_score"] <= 70
        assert result["evacuation_constraint"] is False

    def test_non_wui_low_risk(self, wildfire_analyzer):
        """Test Non-WUI area (urban/low vegetation)."""
        mock_wui_data = {
            "classification": "Non-WUI",
            "housing_density": 500,
            "vegetation_pct": 5,
            "evacuation_routes": 10,
        }

        result = wildfire_analyzer.classify_wui(
            latitude=39.7392,
            longitude=-104.9903,
            mock_wui=mock_wui_data,
        )

        assert result["wui_class"] == "Non-WUI"
        assert result["wui_risk_score"] <= 30


class TestCompositeWildfireRisk:
    """Test overall wildfire risk calculation."""

    def test_extreme_wildfire_risk(self, wildfire_analyzer):
        """Test composite score for extreme wildfire risk property."""
        components = {
            "whp_score": 95,
            "fuel_score": 85,
            "fire_history_score": 75,
            "wui_risk_score": 90,
        }

        result = wildfire_analyzer.calculate_composite_wildfire_risk(components)

        assert result["composite_score"] >= 85
        assert result["risk_level"] == "extreme"
        assert result["mitigation_required"] is True
        assert any(
            "defensible space" in rec.lower() for rec in result["recommendations"]
        )

    def test_low_wildfire_risk(self, wildfire_analyzer):
        """Test composite score for low wildfire risk property."""
        components = {
            "whp_score": 20,
            "fuel_score": 15,
            "fire_history_score": 10,
            "wui_risk_score": 25,
        }

        result = wildfire_analyzer.calculate_composite_wildfire_risk(components)

        assert result["composite_score"] <= 25
        assert result["risk_level"] == "low"
        assert result["mitigation_required"] is False


@pytest.fixture
def wildfire_analyzer():
    """Create WildfireRiskAnalyzer instance for testing."""
    from Claude45_Demo.risk_assessment.wildfire import WildfireRiskAnalyzer

    return WildfireRiskAnalyzer()

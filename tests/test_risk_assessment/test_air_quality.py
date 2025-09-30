"""Tests for air quality analysis."""

from __future__ import annotations

import pytest


class TestPM25Analysis:
    """Test EPA AQS PM2.5 analysis."""

    def test_high_pm25_seasonal_variation(self, air_quality_analyzer):
        """Test high PM2.5 with seasonal wildfire smoke."""
        mock_aqs_data = {
            "annual_mean_pm25": 12.5,
            "max_daily_pm25": 95,
            "days_over_35": 15,  # Unhealthy for sensitive groups
            "wildfire_smoke_days": 25,
        }

        result = air_quality_analyzer.analyze_pm25(
            latitude=39.7392,
            longitude=-105.4983,
            year=2023,
            mock_aqs=mock_aqs_data,
        )

        assert result["annual_mean_pm25"] == 12.5
        assert result["pm25_risk_score"] >= 60  # Elevated risk
        assert result["wildfire_impact"] is True

    def test_low_pm25_good_air_quality(self, air_quality_analyzer):
        """Test low PM2.5 (good air quality)."""
        mock_aqs_data = {
            "annual_mean_pm25": 6.5,
            "max_daily_pm25": 20,
            "days_over_35": 0,
            "wildfire_smoke_days": 0,
        }

        result = air_quality_analyzer.analyze_pm25(
            latitude=39.7392,
            longitude=-104.9903,  # Urban Denver
            year=2023,
            mock_aqs=mock_aqs_data,
        )

        assert result["pm25_risk_score"] <= 30
        assert result["wildfire_impact"] is False


class TestSmokeDaysAnalysis:
    """Test NOAA HMS smoke days analysis."""

    def test_chronic_smoke_exposure(self, air_quality_analyzer):
        """Test area with chronic wildfire smoke exposure."""
        mock_smoke_data = {
            "total_smoke_days": 45,
            "heavy_smoke_days": 12,
            "years_analyzed": 5,
        }

        result = air_quality_analyzer.analyze_smoke_days(
            latitude=39.7392,
            longitude=-105.4983,
            lookback_years=5,
            mock_smoke=mock_smoke_data,
        )

        assert result["avg_smoke_days_per_year"] == 9  # 45 / 5
        assert result["smoke_risk_score"] >= 70
        assert result["chronic_exposure"] is True

    def test_minimal_smoke_exposure(self, air_quality_analyzer):
        """Test area with minimal smoke exposure."""
        mock_smoke_data = {
            "total_smoke_days": 3,
            "heavy_smoke_days": 0,
            "years_analyzed": 5,
        }

        result = air_quality_analyzer.analyze_smoke_days(
            latitude=39.7392,
            longitude=-104.9903,
            lookback_years=5,
            mock_smoke=mock_smoke_data,
        )

        assert result["avg_smoke_days_per_year"] < 1
        assert result["smoke_risk_score"] <= 20
        assert result["chronic_exposure"] is False


class TestCompositeAirQualityRisk:
    """Test overall air quality risk calculation."""

    def test_high_air_quality_risk(self, air_quality_analyzer):
        """Test composite high air quality risk."""
        components = {
            "pm25_risk_score": 75,
            "smoke_risk_score": 80,
        }

        result = air_quality_analyzer.calculate_composite_air_quality_risk(components)

        assert result["composite_score"] >= 75
        assert result["risk_level"] == "high"
        assert any(
            "air filtration" in rec.lower() for rec in result["recommendations"]
        )

    def test_low_air_quality_risk(self, air_quality_analyzer):
        """Test composite low air quality risk."""
        components = {
            "pm25_risk_score": 15,
            "smoke_risk_score": 10,
        }

        result = air_quality_analyzer.calculate_composite_air_quality_risk(components)

        assert result["composite_score"] <= 20
        assert result["risk_level"] == "low"


@pytest.fixture
def air_quality_analyzer():
    """Create AirQualityAnalyzer instance for testing."""
    from Claude45_Demo.risk_assessment.air_quality import AirQualityAnalyzer

    return AirQualityAnalyzer()


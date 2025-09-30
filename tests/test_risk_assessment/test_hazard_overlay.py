"""Tests for multi-hazard overlay system."""

from __future__ import annotations

import pytest


class TestSeismicRisk:
    """Test USGS NSHM seismic risk assessment."""

    def test_high_seismic_risk(self, hazard_analyzer):
        """Test high seismic risk (SDC E)."""
        mock_seismic = {"pga_2pct_50yr": 0.6, "fault_distance_km": 5.0}

        result = hazard_analyzer.assess_seismic_risk(
            latitude=37.7749, longitude=-122.4194, mock_seismic=mock_seismic
        )

        assert result["seismic_design_category"] == "E"
        assert result["seismic_risk_score"] >= 85
        assert result["fault_rupture_zone"] is False

    def test_low_seismic_risk(self, hazard_analyzer):
        """Test low seismic risk (SDC A/B)."""
        mock_seismic = {"pga_2pct_50yr": 0.03, "fault_distance_km": None}

        result = hazard_analyzer.assess_seismic_risk(
            latitude=39.7392, longitude=-104.9903, mock_seismic=mock_seismic
        )

        assert result["seismic_design_category"] == "A"
        assert result["seismic_risk_score"] <= 20


class TestHailRisk:
    """Test NOAA SPC hail risk assessment."""

    def test_hail_alley_high_risk(self, hazard_analyzer):
        """Test hail alley (CO Front Range) high risk."""
        mock_hail = {"hail_events_1inch_plus": 12, "max_hail_size_inches": 2.5}

        result = hazard_analyzer.assess_hail_risk(
            latitude=39.7392, longitude=-104.9903, mock_hail=mock_hail
        )

        assert result["hail_alley"] is True
        assert result["hail_risk_score"] >= 85

    def test_low_hail_risk(self, hazard_analyzer):
        """Test low hail risk area."""
        mock_hail = {"hail_events_1inch_plus": 1, "max_hail_size_inches": 0.75}

        result = hazard_analyzer.assess_hail_risk(
            latitude=47.6062, longitude=-122.3321, mock_hail=mock_hail
        )

        assert result["hail_alley"] is False
        assert result["hail_risk_score"] <= 20


class TestRadonRisk:
    """Test EPA radon zone assessment."""

    def test_zone_1_high_radon(self, hazard_analyzer):
        """Test EPA Zone 1 (high radon potential)."""
        mock_radon = {"epa_radon_zone": 1}

        result = hazard_analyzer.assess_radon_risk(
            county_fips="08031", mock_radon=mock_radon
        )

        assert result["risk_level"] == "high"
        assert result["mitigation_required"] is True
        assert result["mitigation_cost_estimate"] > 0

    def test_zone_3_low_radon(self, hazard_analyzer):
        """Test EPA Zone 3 (low radon potential)."""
        mock_radon = {"epa_radon_zone": 3}

        result = hazard_analyzer.assess_radon_risk(
            county_fips="06037", mock_radon=mock_radon
        )

        assert result["risk_level"] == "low"
        assert result["mitigation_required"] is False


class TestSnowLoad:
    """Test ASCE 7 snow load assessment."""

    def test_heavy_snow_load(self, hazard_analyzer):
        """Test heavy mountain snow loads."""
        mock_snow = {"ground_snow_load_psf": 85}

        result = hazard_analyzer.assess_snow_load(
            latitude=39.7392,
            longitude=-105.4983,
            elevation_ft=9000,
            mock_snow=mock_snow,
        )

        assert result["snow_load_risk_score"] >= 75
        assert result["structural_cost_premium_pct"] >= 10

    def test_low_snow_load(self, hazard_analyzer):
        """Test low snow load area."""
        mock_snow = {"ground_snow_load_psf": 15}

        result = hazard_analyzer.assess_snow_load(
            latitude=39.7392,
            longitude=-104.9903,
            elevation_ft=5280,
            mock_snow=mock_snow,
        )

        assert result["snow_load_risk_score"] <= 20
        assert result["structural_cost_premium_pct"] == 0


class TestCompositeHazardRisk:
    """Test multi-hazard composite scoring."""

    def test_high_composite_risk(self, hazard_analyzer):
        """Test high multi-hazard risk."""
        components = {
            "seismic_risk_score": 85,
            "hail_risk_score": 90,
            "radon_risk_score": 75,
            "snow_load_risk_score": 70,
        }

        result = hazard_analyzer.calculate_composite_hazard_risk(components)

        assert result["composite_hazard_score"] >= 70
        assert result["risk_level"] == "high"

    def test_low_composite_risk(self, hazard_analyzer):
        """Test low multi-hazard risk."""
        components = {
            "seismic_risk_score": 15,
            "hail_risk_score": 10,
            "radon_risk_score": 20,
            "snow_load_risk_score": 15,
        }

        result = hazard_analyzer.calculate_composite_hazard_risk(components)

        assert result["composite_hazard_score"] <= 30
        assert result["risk_level"] == "low"


@pytest.fixture
def hazard_analyzer():
    """Create HazardOverlayAnalyzer instance for testing."""
    from Claude45_Demo.risk_assessment.hazard_overlay import HazardOverlayAnalyzer

    return HazardOverlayAnalyzer()


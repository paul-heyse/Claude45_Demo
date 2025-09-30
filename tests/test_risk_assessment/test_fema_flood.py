"""Tests for FEMA flood zone analysis."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from Claude45_Demo.risk_assessment.fema_flood import FEMAFloodAnalyzer


class TestFEMAFloodZoneClassification:
    """Test FEMA flood zone classification and risk scoring."""

    def test_flood_zone_high_risk_classification(self, flood_analyzer):
        """Test high-risk flood zone (A/AE/VE) classification."""
        # Mock FEMA NFHL response for Zone AE (high risk)
        mock_zone_data = {
            "features": [
                {
                    "properties": {
                        "FLD_ZONE": "AE",
                        "ZONE_SUBTY": None,
                        "STATIC_BFE": 5280.5,  # feet NAVD88
                        "SFHA_TF": "T",  # Special Flood Hazard Area
                    },
                    "geometry": {"type": "Polygon", "coordinates": []},
                }
            ]
        }

        result = flood_analyzer.classify_flood_zone(
            latitude=39.7392,
            longitude=-104.9903,
            mock_response=mock_zone_data,
        )

        assert result["zone"] == "AE"
        assert result["risk_category"] == "high"
        assert result["sfha"] is True
        assert result["risk_score"] >= 80  # High risk zones score 80-100
        assert result["base_flood_elevation"] == 5280.5

    def test_flood_zone_moderate_risk(self, flood_analyzer):
        """Test moderate risk flood zone (X shaded) classification."""
        mock_zone_data = {
            "features": [
                {
                    "properties": {
                        "FLD_ZONE": "X",
                        "ZONE_SUBTY": "0.2 PCT ANNUAL CHANCE FLOOD HAZARD",
                        "STATIC_BFE": None,
                        "SFHA_TF": "F",
                    },
                    "geometry": {"type": "Polygon", "coordinates": []},
                }
            ]
        }

        result = flood_analyzer.classify_flood_zone(
            latitude=39.7392,
            longitude=-104.9903,
            mock_response=mock_zone_data,
        )

        assert result["zone"] == "X"
        assert result["risk_category"] == "moderate"
        assert result["sfha"] is False
        assert 40 <= result["risk_score"] < 60  # Moderate scores 40-60
        assert result["base_flood_elevation"] is None

    def test_flood_zone_minimal_risk(self, flood_analyzer):
        """Test minimal risk flood zone (X unshaded) classification."""
        mock_zone_data = {
            "features": [
                {
                    "properties": {
                        "FLD_ZONE": "X",
                        "ZONE_SUBTY": "AREA OF MINIMAL FLOOD HAZARD",
                        "STATIC_BFE": None,
                        "SFHA_TF": "F",
                    },
                    "geometry": {"type": "Polygon", "coordinates": []},
                }
            ]
        }

        result = flood_analyzer.classify_flood_zone(
            latitude=39.7392,
            longitude=-104.9903,
            mock_response=mock_zone_data,
        )

        assert result["zone"] == "X"
        assert result["risk_category"] == "minimal"
        assert result["sfha"] is False
        assert result["risk_score"] < 30  # Minimal risk scores 0-30

    def test_no_flood_data_available(self, flood_analyzer):
        """Test handling when no flood zone data is available."""
        mock_zone_data = {"features": []}

        result = flood_analyzer.classify_flood_zone(
            latitude=39.7392,
            longitude=-104.9903,
            mock_response=mock_zone_data,
        )

        assert result["zone"] == "UNMAPPED"
        assert result["risk_category"] == "unknown"
        assert result["sfha"] is None
        assert result["risk_score"] == 50  # Default to moderate uncertainty


class TestFEMAFloodInsuranceCostProxy:
    """Test flood insurance cost estimation."""

    def test_nfip_premium_high_risk_sfha(self, flood_analyzer):
        """Test NFIP premium estimation for high-risk SFHA property."""
        flood_data = {
            "zone": "AE",
            "risk_category": "high",
            "sfha": True,
            "base_flood_elevation": 5280.5,
        }
        building_elevation = 5279.0  # Below BFE (negative freeboard)

        result = flood_analyzer.estimate_flood_insurance(
            flood_data=flood_data,
            building_elevation=building_elevation,
            replacement_cost=500_000,
        )

        assert result["annual_premium"] > 1000  # High-risk SFHA
        assert result["premium_pct"] > 0.2  # >0.2% of replacement cost
        assert result["nfip_eligible"] is True
        assert result["freeboard_ft"] == -1.5  # Below BFE
        assert "Risk Rating 2.0" in result["notes"]

    def test_nfip_premium_positive_freeboard(self, flood_analyzer):
        """Test premium reduction for positive freeboard."""
        flood_data = {
            "zone": "AE",
            "risk_category": "high",
            "sfha": True,
            "base_flood_elevation": 5280.5,
        }
        building_elevation = 5283.0  # 2.5 ft above BFE

        result = flood_analyzer.estimate_flood_insurance(
            flood_data=flood_data,
            building_elevation=building_elevation,
            replacement_cost=500_000,
        )

        # Positive freeboard reduces premium
        assert 500 < result["annual_premium"] < 1500
        assert result["freeboard_ft"] == 2.5
        assert result["discount_applied"] is True

    def test_nfip_premium_non_sfha(self, flood_analyzer):
        """Test low preferred risk premium for non-SFHA (Zone X)."""
        flood_data = {
            "zone": "X",
            "risk_category": "minimal",
            "sfha": False,
            "base_flood_elevation": None,
        }

        result = flood_analyzer.estimate_flood_insurance(
            flood_data=flood_data,
            building_elevation=None,
            replacement_cost=500_000,
        )

        # Preferred Risk Policy (low cost)
        assert result["annual_premium"] < 600
        assert result["premium_pct"] < 0.15
        assert result["nfip_eligible"] is True
        assert result["policy_type"] == "Preferred Risk"


class TestHistoricalFloodEvents:
    """Test historical flood event analysis."""

    def test_chronic_flooding_detection(self, flood_analyzer):
        """Test identification of chronic flooding (>3 events in 20 years)."""
        # Mock FEMA disaster declarations + NOAA NCEI data
        mock_events = [
            {"year": 2013, "type": "flood", "severity": "major"},
            {"year": 2015, "type": "flood", "severity": "moderate"},
            {"year": 2019, "type": "flood", "severity": "major"},
            {"year": 2021, "type": "flood", "severity": "moderate"},
        ]

        result = flood_analyzer.analyze_historical_floods(
            county_fips="08031",  # Denver County
            lookback_years=20,
            mock_events=mock_events,
        )

        assert result["event_count"] == 4
        assert result["chronic_flooding"] is True  # >3 events
        assert result["presidential_declarations"] >= 2
        assert result["historical_score"] >= 70  # High historical risk

    def test_no_recent_flooding(self, flood_analyzer):
        """Test counties with no recent flood history."""
        mock_events = []

        result = flood_analyzer.analyze_historical_floods(
            county_fips="08123",  # Weld County (hypothetical)
            lookback_years=20,
            mock_events=mock_events,
        )

        assert result["event_count"] == 0
        assert result["chronic_flooding"] is False
        assert result["historical_score"] < 20  # Low historical risk


class TestDamAndLeveeRisk:
    """Test dam/levee infrastructure risk assessment."""

    def test_high_hazard_dam_proximity(self, flood_analyzer):
        """Test risk flag for high-hazard dam in poor condition."""
        # Mock National Inventory of Dams data
        mock_dams = [
            {
                "dam_name": "Upstream Dam A",
                "distance_km": 8.5,
                "hazard_class": "H",  # High hazard
                "condition": "Fair",
                "year_inspected": 2022,
            }
        ]

        result = flood_analyzer.assess_dam_levee_risk(
            latitude=39.7392,
            longitude=-104.9903,
            search_radius_km=15,
            mock_dams=mock_dams,
        )

        assert result["high_hazard_dams_nearby"] == 1
        assert result["risk_flag"] is True
        assert result["risk_adjustment"] > 0  # Increases flood score
        assert "Fair condition" in result["notes"]

    def test_no_dam_risk(self, flood_analyzer):
        """Test areas with no significant dam risk."""
        mock_dams = []

        result = flood_analyzer.assess_dam_levee_risk(
            latitude=39.7392,
            longitude=-104.9903,
            search_radius_km=15,
            mock_dams=mock_dams,
        )

        assert result["high_hazard_dams_nearby"] == 0
        assert result["risk_flag"] is False
        assert result["risk_adjustment"] == 0


@pytest.fixture
def flood_analyzer():
    """Create FEMAFloodAnalyzer instance for testing."""
    from Claude45_Demo.risk_assessment.fema_flood import FEMAFloodAnalyzer

    return FEMAFloodAnalyzer()


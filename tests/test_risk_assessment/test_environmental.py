"""Tests for environmental compliance risk assessment."""

import pytest

from Claude45_Demo.risk_assessment.environmental import (
    EnvironmentalComplianceAnalyzer,
)


@pytest.fixture
def env_analyzer():
    """Environmental compliance analyzer fixture."""
    return EnvironmentalComplianceAnalyzer()


class TestContaminatedSites:
    """Test contaminated site proximity assessment."""

    def test_superfund_site_nearby(self, env_analyzer):
        """Test high risk score for nearby Superfund site."""
        mock_sites = [
            {
                "name": "Test Superfund Site",
                "site_type": "Superfund",
                "distance_km": 0.5,
                "active_remediation": True,
                "uncontrolled_release": False,
            }
        ]

        result = env_analyzer.assess_nearby_contaminated_sites(
            latitude=40.0, longitude=-105.0, search_radius_km=1.0, mock_sites=mock_sites
        )

        assert result["environmental_risk_score"] >= 80
        assert result["sites_within_radius"] == 1
        assert len(result["high_risk_sites"]) == 1

    def test_multiple_sites_additive_risk(self, env_analyzer):
        """Test that multiple sites increase risk score."""
        mock_sites = [
            {
                "name": "RCRA Site 1",
                "site_type": "RCRA_Corrective_Action",
                "distance_km": 0.3,
                "active_remediation": False,
                "uncontrolled_release": False,
            },
            {
                "name": "RCRA Site 2",
                "site_type": "RCRA_Generator",
                "distance_km": 0.8,
                "active_remediation": False,
                "uncontrolled_release": False,
            },
        ]

        result = env_analyzer.assess_nearby_contaminated_sites(
            latitude=40.0, longitude=-105.0, search_radius_km=1.0, mock_sites=mock_sites
        )

        assert result["sites_within_radius"] == 2
        assert result["environmental_risk_score"] > 50

    def test_no_sites_nearby(self, env_analyzer):
        """Test low risk when no sites nearby."""
        mock_sites = []

        result = env_analyzer.assess_nearby_contaminated_sites(
            latitude=40.0, longitude=-105.0, search_radius_km=1.0, mock_sites=mock_sites
        )

        assert result["environmental_risk_score"] == 0
        assert result["sites_within_radius"] == 0
        assert result["high_risk_sites"] == []


class TestDischargePermits:
    """Test air and water discharge permit assessment."""

    def test_multiple_violations(self, env_analyzer):
        """Test high risk score for multiple significant violations."""
        mock_permits = [
            {
                "facility_name": "Industrial Facility",
                "permit_type": "NPDES",
                "distance_km": 1.5,
                "violations": [
                    {
                        "significant": True,
                        "type": "CWA",
                        "date": "2023-01-15",
                        "pollutants": ["heavy metals"],
                    },
                    {
                        "significant": True,
                        "type": "CWA",
                        "date": "2023-06-20",
                        "pollutants": ["organic compounds"],
                    },
                    {
                        "significant": True,
                        "type": "CWA",
                        "date": "2024-01-10",
                        "pollutants": ["suspended solids"],
                    },
                ],
            }
        ]

        result = env_analyzer.assess_discharge_permits(
            latitude=40.0,
            longitude=-105.0,
            search_radius_km=2.0,
            lookback_years=3,
            mock_permits=mock_permits,
        )

        assert result["violation_count"] == 3
        assert result["risk_flag"] == "moderate"
        assert result["pollution_proximity_risk_score"] >= 60

    def test_no_violations(self, env_analyzer):
        """Test low risk when no violations present."""
        mock_permits = [
            {
                "facility_name": "Clean Facility",
                "permit_type": "Air",
                "distance_km": 1.0,
                "violations": [],
            }
        ]

        result = env_analyzer.assess_discharge_permits(
            latitude=40.0,
            longitude=-105.0,
            search_radius_km=2.0,
            lookback_years=3,
            mock_permits=mock_permits,
        )

        assert result["violation_count"] == 0
        assert result["risk_flag"] == "minimal"
        assert result["pollution_proximity_risk_score"] == 10


class TestCompositeEnvironmentalRisk:
    """Test composite environmental risk calculation."""

    def test_high_composite_risk(self, env_analyzer):
        """Test high composite risk calculation."""
        components = {
            "environmental_risk_score": 85,
            "pollution_proximity_risk_score": 70,
        }

        result = env_analyzer.calculate_composite_environmental_risk(components)

        assert result["composite_environmental_score"] >= 70
        assert result["risk_level"] == "high"
        assert "Phase I" in result["recommendations"][0]

    def test_low_composite_risk(self, env_analyzer):
        """Test low composite risk calculation."""
        components = {
            "environmental_risk_score": 15,
            "pollution_proximity_risk_score": 20,
        }

        result = env_analyzer.calculate_composite_environmental_risk(components)

        assert result["composite_environmental_score"] < 50
        assert result["risk_level"] == "low"

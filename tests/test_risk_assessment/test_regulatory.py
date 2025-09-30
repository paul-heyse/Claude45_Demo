"""Tests for regulatory friction assessment."""

from __future__ import annotations

import pytest


class TestPermitTimeline:
    """Test permit timeline estimation."""

    def test_high_friction_long_timeline(self, regulatory_analyzer):
        """Test high-friction jurisdiction (>180 days)."""
        mock_permit = {"median_days_to_permit": 210, "p90_days": 300}

        result = regulatory_analyzer.estimate_permit_timeline(
            jurisdiction="Boulder, CO", mock_permit_data=mock_permit
        )

        assert result["friction_level"] == "high"
        assert result["friction_score"] >= 80

    def test_low_friction_short_timeline(self, regulatory_analyzer):
        """Test low-friction jurisdiction (<60 days)."""
        mock_permit = {"median_days_to_permit": 45, "p90_days": 60}

        result = regulatory_analyzer.estimate_permit_timeline(
            jurisdiction="Aurora, CO", mock_permit_data=mock_permit
        )

        assert result["friction_level"] == "low"
        assert result["friction_score"] <= 30


class TestZoningComplexity:
    """Test zoning complexity assessment."""

    def test_complex_zoning_multiple_overlays(self, regulatory_analyzer):
        """Test complex zoning with multiple overlay districts."""
        parcel_data = {"parcel_id": "12345"}
        mock_zoning = {
            "base_zone": "R-4",
            "overlay_districts": ["Historic", "Design Review", "View Protection"],
            "design_review_required": True,
            "height_limit_ft": 35,
            "far_limit": 1.5,
            "parking_minimum_per_unit": 1.8,
            "inclusionary_zoning": True,
        }

        result = regulatory_analyzer.assess_zoning_complexity(
            parcel_data=parcel_data, mock_zoning=mock_zoning
        )

        assert result["complexity_score"] >= 70
        assert len(result["constraints"]) > 0
        assert result["design_review_required"] is True

    def test_simple_zoning(self, regulatory_analyzer):
        """Test simple zoning with minimal restrictions."""
        parcel_data = {"parcel_id": "67890"}
        mock_zoning = {
            "base_zone": "MU-3",
            "overlay_districts": [],
            "design_review_required": False,
            "height_limit_ft": 75,
            "far_limit": 3.0,
            "parking_minimum_per_unit": 0.8,
            "inclusionary_zoning": False,
        }

        result = regulatory_analyzer.assess_zoning_complexity(
            parcel_data=parcel_data, mock_zoning=mock_zoning
        )

        assert result["complexity_score"] <= 40
        assert len(result["constraints"]) == 0


class TestPolicyRisk:
    """Test rent control and policy risk assessment."""

    def test_high_policy_risk_rent_control(self, regulatory_analyzer):
        """Test high policy risk with rent control."""
        mock_policy = {
            "rent_control": True,
            "just_cause_eviction": True,
            "rent_increase_limit_pct": 3.0,
            "political_climate": "tenant_favorable",
        }

        result = regulatory_analyzer.assess_policy_risk(
            jurisdiction="Boulder, CO", mock_policy=mock_policy
        )

        assert result["risk_level"] == "high"
        assert result["policy_risk_score"] >= 70
        assert result["rent_control"] is True

    def test_low_policy_risk(self, regulatory_analyzer):
        """Test low policy risk jurisdiction."""
        mock_policy = {
            "rent_control": False,
            "just_cause_eviction": False,
            "rent_increase_limit_pct": None,
            "political_climate": "neutral",
        }

        result = regulatory_analyzer.assess_policy_risk(
            jurisdiction="Aurora, CO", mock_policy=mock_policy
        )

        assert result["risk_level"] == "low"
        assert result["policy_risk_score"] <= 40


class TestCompositeRegulatoryRisk:
    """Test overall regulatory risk calculation."""

    def test_high_composite_risk(self, regulatory_analyzer):
        """Test high overall regulatory friction."""
        components = {
            "permit_friction_score": 85,
            "zoning_complexity_score": 75,
            "policy_risk_score": 80,
        }

        result = regulatory_analyzer.calculate_composite_regulatory_risk(components)

        assert result["composite_regulatory_score"] >= 70
        assert result["risk_level"] == "high"

    def test_low_composite_risk(self, regulatory_analyzer):
        """Test low overall regulatory friction."""
        components = {
            "permit_friction_score": 20,
            "zoning_complexity_score": 25,
            "policy_risk_score": 15,
        }

        result = regulatory_analyzer.calculate_composite_regulatory_risk(components)

        assert result["composite_regulatory_score"] <= 30
        assert result["risk_level"] == "low"


@pytest.fixture
def regulatory_analyzer():
    """Create RegulatoryFrictionAnalyzer instance for testing."""
    from Claude45_Demo.risk_assessment.regulatory import RegulatoryFrictionAnalyzer

    return RegulatoryFrictionAnalyzer()

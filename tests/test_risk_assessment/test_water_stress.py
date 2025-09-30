"""Tests for water stress assessment."""

from __future__ import annotations

import pytest


def test_colorado_decreed_rights(water_analyzer):
    """Test CO with decreed water rights (high availability)."""
    mock_rights = {
        "has_decreed_rights": True,
        "municipal_supply": False,
        "augmentation_required": False,
        "tap_fees_per_unit": 8000,
    }

    result = water_analyzer.assess_water_rights(
        state="CO", county_fips="08031", mock_rights=mock_rights
    )

    assert result["availability_score"] >= 85


def test_high_drought_stress(water_analyzer):
    """Test chronic drought conditions."""
    mock_drought = {
        "pct_years_in_moderate_plus_drought": 75,
        "groundwater_overdraft": True,
        "usgs_stress_index": 0.7,
    }

    result = water_analyzer.assess_drought_risk(
        county_fips="08031", mock_drought=mock_drought
    )

    assert result["chronic_drought"] is True
    assert result["drought_stress_score"] >= 85


@pytest.fixture
def water_analyzer():
    """Create WaterStressAnalyzer instance for testing."""
    from Claude45_Demo.risk_assessment.water_stress import WaterStressAnalyzer

    return WaterStressAnalyzer()

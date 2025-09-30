"""
Tests for Colorado state-specific analysis.

Tests scenarios from specs/state-rules/spec.md covering:
- Front Range hail risk premium calculation
- CDSS HydroBase water rights integration
- Mountain snow load adjustments
- Denver metro permit timeline patterns
"""

import pytest

from Claude45_Demo.state_rules.colorado import ColoradoStateAnalyzer


@pytest.fixture
def co_analyzer():
    """Colorado state analyzer with mocked data connectors."""
    return ColoradoStateAnalyzer()


class TestHailRiskPremium:
    """Test Colorado Front Range hail risk adjustment."""

    def test_front_range_hail_alley_premium(self, co_analyzer):
        """
        WHEN: Property in CO Front Range corridor (Denver to Pueblo)
        THEN: Elevated hail risk scoring, roof replacement reserve,
              insurance deductible impact, risk multiplier adjustment
        """
        # Denver coordinates (39.7392°N, 104.9903°W)
        result = co_analyzer.calculate_hail_risk_premium(39.7392, -104.9903)

        assert result["hail_events_per_decade"] >= 10
        assert result["risk_category"] in ["high", "extreme"]
        assert 15 <= result["roof_reserve_per_unit_per_year"] <= 20
        assert result["insurance_deductible_pct"] >= 5.0
        assert 0.03 <= result["risk_multiplier_adjustment"] <= 0.08

    def test_mountain_hail_moderate(self, co_analyzer):
        """
        WHEN: Property in CO mountains (lower hail frequency)
        THEN: Moderate hail risk, lower reserves
        """
        # Breckenridge coordinates (39.4817°N, 106.0384°W)
        result = co_analyzer.calculate_hail_risk_premium(39.4817, -106.0384)

        assert result["risk_category"] in ["low", "moderate"]
        assert result["roof_reserve_per_unit_per_year"] < 15


class TestCDSSWaterRights:
    """Test CDSS HydroBase water rights integration."""

    def test_cdss_water_rights_query(self, co_analyzer, monkeypatch):
        """
        WHEN: System analyzes CO property requiring water supply
        THEN: Query CDSS HydroBase, retrieve structures/rights,
              calculate tap fees, identify water court districts
        """
        # Mock CDSS API response
        mock_response = {
            "structures": [
                {
                    "wdid": "0500544",
                    "structure_name": "BOULDER MUNICIPAL SUPPLY",
                    "water_source": "Boulder Creek",
                }
            ],
            "water_rights": [
                {
                    "admin_no": "12345.12345",
                    "appropriation_date": "1880-01-15",
                    "decreed_amount": 100.0,
                    "unit": "CFS",
                }
            ],
            "water_court_district": 1,
        }

        def mock_query(*args, **kwargs):
            return mock_response

        monkeypatch.setattr(co_analyzer, "_query_cdss_hydrobase", mock_query)

        result = co_analyzer.assess_water_rights(
            county_fips="08013", parcel_id="123-456-789"
        )

        assert "availability_score" in result
        assert 0 <= result["availability_score"] <= 100
        assert "estimated_tap_fee" in result
        assert result["estimated_tap_fee"] >= 0
        assert result["water_court_district"] == 1
        assert "priority_date" in result
        assert len(result["structures"]) > 0

    def test_water_supply_constrained_area(self, co_analyzer, monkeypatch):
        """
        WHEN: Property in water-constrained CO area
        THEN: Low availability score, high tap fees, augmentation required
        """
        mock_response = {
            "structures": [],
            "water_rights": [],
            "water_court_district": 1,
            "augmentation_required": True,
        }

        monkeypatch.setattr(
            co_analyzer, "_query_cdss_hydrobase", lambda *a, **k: mock_response
        )

        result = co_analyzer.assess_water_rights(
            county_fips="08059", parcel_id="999"  # Jefferson County
        )

        assert result["availability_score"] < 50
        assert result["estimated_tap_fee"] > 20000
        assert result.get("augmentation_required") is True


class TestMountainSnowLoad:
    """Test mountain snow load adjustments."""

    def test_high_elevation_snow_load(self, co_analyzer):
        """
        WHEN: Property above 7,000 ft elevation in CO mountains
        THEN: ASCE 7 ground snow loads, structural cost premium,
              winter construction constraints
        """
        # Breckenridge at 9,600 ft elevation
        result = co_analyzer.calculate_snow_load_adjustment(
            latitude=39.4817, longitude=-106.0384, elevation_ft=9600
        )

        assert result["ground_snow_load_psf"] > 50
        assert 10 <= result["structural_cost_premium_pct"] <= 15
        assert result["winter_construction_months"] == [
            "November",
            "December",
            "January",
            "February",
            "March",
        ]
        assert result["winter_cost_premium_pct"] >= 15

    def test_low_elevation_minimal_snow(self, co_analyzer):
        """
        WHEN: Property at lower elevation (Front Range valleys)
        THEN: Lower snow loads, minimal cost premium
        """
        # Denver at 5,280 ft elevation
        result = co_analyzer.calculate_snow_load_adjustment(
            latitude=39.7392, longitude=-104.9903, elevation_ft=5280
        )

        assert result["ground_snow_load_psf"] < 40
        assert result["structural_cost_premium_pct"] < 5


class TestDenverMetroPermitTimelines:
    """Test Denver metro jurisdiction permit patterns."""

    def test_boulder_high_friction(self, co_analyzer):
        """
        WHEN: Property in Boulder, CO (known high friction)
        THEN: Long permit timeline (>180 days), design review,
              inclusionary zoning, high friction score
        """
        result = co_analyzer.assess_regulatory_environment("Boulder")

        assert result["median_permit_days"] > 180
        assert result["design_review_required"] is True
        assert result["inclusionary_zoning_pct"] >= 25
        assert result["friction_score"] >= 75

    def test_aurora_moderate_friction(self, co_analyzer):
        """
        WHEN: Property in Aurora, CO (moderate friction)
        THEN: Shorter permit timeline (~45 days), lower friction
        """
        result = co_analyzer.assess_regulatory_environment("Aurora")

        assert result["median_permit_days"] <= 60
        assert result["friction_score"] < 50

    def test_unknown_jurisdiction_state_default(self, co_analyzer):
        """
        WHEN: Jurisdiction not in pattern library
        THEN: Apply CO state-level default estimates
        """
        result = co_analyzer.assess_regulatory_environment("SmallTownCO")

        assert "median_permit_days" in result
        assert result["median_permit_days"] > 0
        assert result["data_source"] == "state_default"


class TestColoradoComposite:
    """Test composite CO state multiplier calculation."""

    def test_composite_state_multiplier(self, co_analyzer, monkeypatch):
        """
        WHEN: System calculates CO-specific adjustment for all factors
        THEN: Composite multiplier accounts for hail, water, snow, regulatory
        """
        # Mock individual components
        monkeypatch.setattr(
            co_analyzer,
            "calculate_hail_risk_premium",
            lambda *a, **k: {"risk_multiplier_adjustment": 0.05},
        )
        monkeypatch.setattr(
            co_analyzer,
            "assess_water_rights",
            lambda *a, **k: {"availability_score": 60},
        )
        monkeypatch.setattr(
            co_analyzer,
            "calculate_snow_load_adjustment",
            lambda *a, **k: {"structural_cost_premium_pct": 12},
        )
        monkeypatch.setattr(
            co_analyzer,
            "assess_regulatory_environment",
            lambda *a, **k: {"friction_score": 55},
        )

        result = co_analyzer.calculate_state_multiplier(
            latitude=39.7392,
            longitude=-104.9903,
            elevation_ft=5280,
            county_fips="08031",
            parcel_id="123",
            jurisdiction="Denver",
        )

        assert "co_multiplier" in result
        assert 0.9 <= result["co_multiplier"] <= 1.1
        assert "adjustments" in result
        assert len(result["adjustments"]) >= 3  # At least hail, water, regulatory
        assert "risk_premium_pct" in result


class TestColoradoWildfireWUI:
    """Test CO mountain wildfire WUI integration."""

    def test_mountain_county_wildfire_adjustment(self, co_analyzer):
        """
        WHEN: Property in CO mountain WUI area (Summit, Eagle, Routt counties)
        THEN: Elevated wildfire risk adjustment beyond base WHP score
        """
        # Summit County (high WUI risk)
        result = co_analyzer.apply_wildfire_wui_adjustment(
            county_fips="08117", base_wildfire_score=65
        )

        assert result["wui_multiplier"] > 1.0
        assert result["insurance_impact"] in ["limited_carriers", "high_deductible"]
        assert "firewise_community" in result["recommendations"]

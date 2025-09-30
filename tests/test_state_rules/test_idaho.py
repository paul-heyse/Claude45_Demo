"""
Tests for Idaho state-specific analysis.

Tests scenarios from specs/state-rules/spec.md covering:
- Treasure Valley in-migration tracking
- North Idaho wildland-urban interface fire risk
- Idaho DWR water rights and SRBA adjudication
- Property tax advantage
"""

import pytest

from Claude45_Demo.state_rules.idaho import IdahoStateAnalyzer


@pytest.fixture
def id_analyzer():
    """Idaho state analyzer with mocked data connectors."""
    return IdahoStateAnalyzer()


class TestTreasureValleyMigration:
    """Test Treasure Valley in-migration momentum analysis."""

    def test_high_inmigration_momentum(self, id_analyzer, monkeypatch):
        """
        WHEN: Analyze Boise/Meridian/Nampa markets
        THEN: Calculate net in-migration from IRS SOI, housing supply
              elasticity, remote-work patterns, momentum score
        """
        # Mock IRS SOI migration data
        mock_data = {
            "net_migration_annual": 8500,
            "top_origin_states": ["CA", "WA", "OR"],
            "remote_work_share_pct": 35,
            "permits_per_household_growth": 1.2,
        }

        monkeypatch.setattr(
            id_analyzer, "_query_migration_data", lambda *a, **k: mock_data
        )

        result = id_analyzer.analyze_treasure_valley_migration(
            county_fips="16001"  # Ada County (Boise)
        )

        assert result["migration_momentum_score"] >= 75
        assert result["supply_elasticity"] in ["moderate", "high"]
        assert "CA" in result["top_origin_states"]
        assert result["remote_work_factor"] >= 1.2

    def test_low_migration_rural_county(self, id_analyzer, monkeypatch):
        """
        WHEN: Rural Idaho county outside Treasure Valley
        THEN: Lower migration momentum
        """
        mock_data = {
            "net_migration_annual": 150,
            "top_origin_states": ["ID"],
            "remote_work_share_pct": 10,
            "permits_per_household_growth": 0.5,
        }

        monkeypatch.setattr(
            id_analyzer, "_query_migration_data", lambda *a, **k: mock_data
        )

        result = id_analyzer.analyze_treasure_valley_migration(
            county_fips="16023"  # Blaine County
        )

        assert result["migration_momentum_score"] < 50
        assert result["supply_elasticity"] in ["low", "moderate"]


class TestNorthIdahoWUI:
    """Test North Idaho wildland-urban interface fire risk."""

    def test_coeur_dalene_wui_high_risk(self, id_analyzer):
        """
        WHEN: Property in Coeur d'Alene or North Idaho WUI
        THEN: Elevated wildfire risk, limited insurance carriers,
              defensible space requirements
        """
        # Coeur d'Alene area
        result = id_analyzer.assess_wildfire_wui_risk(
            latitude=47.6777, longitude=-116.7805, county_fips="16055"  # Kootenai
        )

        assert result["wui_risk_category"] in ["high", "extreme"]
        assert result["insurance_availability"] == "limited"
        assert result["defensible_space_ft"] >= 100
        assert result["firewise_required"] is True

    def test_boise_area_lower_wui(self, id_analyzer):
        """
        WHEN: Property in Treasure Valley (lower WUI risk)
        THEN: Moderate wildfire risk
        """
        # Boise metro
        result = id_analyzer.assess_wildfire_wui_risk(
            latitude=43.6150, longitude=-116.2023, county_fips="16001"  # Ada
        )

        assert result["wui_risk_category"] in ["low", "moderate"]
        assert result["defensible_space_ft"] <= 50


class TestIdahoWaterRights:
    """Test Idaho DWR water rights and SRBA adjudication."""

    def test_srba_area_water_rights(self, id_analyzer, monkeypatch):
        """
        WHEN: Property in Snake River Basin Adjudication (SRBA) area
        THEN: Identify SRBA complexity, senior vs junior rights,
              curtailment risk
        """
        mock_response = {
            "water_right_claims": [
                {
                    "right_number": "36-12345",
                    "source": "Snake River",
                    "priority_date": "1905-03-20",
                    "status": "decreed",
                    "type": "surface",
                }
            ],
            "srba_area": True,
            "curtailment_risk": "moderate",
        }

        monkeypatch.setattr(id_analyzer, "_query_idwr", lambda *a, **k: mock_response)

        result = id_analyzer.assess_water_rights(
            county_fips="16001", parcel_id="ABC123"  # Ada County
        )

        assert result["srba_area"] is True
        assert "availability_score" in result
        assert result["curtailment_risk"] in ["low", "moderate", "high"]
        assert len(result["water_right_claims"]) > 0

    def test_municipal_hookup_availability(self, id_analyzer, monkeypatch):
        """
        WHEN: Property with municipal water availability
        THEN: High availability score, reasonable hook-up fees
        """
        mock_response = {
            "water_right_claims": [],
            "srba_area": False,
            "municipal_service_available": True,
            "curtailment_risk": "low",
        }

        monkeypatch.setattr(id_analyzer, "_query_idwr", lambda *a, **k: mock_response)

        result = id_analyzer.assess_water_rights(county_fips="16001", parcel_id="XYZ")

        assert result["availability_score"] >= 70
        assert result["estimated_hookup_fee"] <= 15000


class TestIdahoTaxRegulatory:
    """Test Idaho property tax and regulatory advantages."""

    def test_favorable_property_tax(self, id_analyzer):
        """
        WHEN: Evaluate Idaho tax environment
        THEN: Note favorable property tax rates (~1% effective),
              rent control prohibition
        """
        result = id_analyzer.assess_tax_and_regulatory_environment(jurisdiction="Boise")

        assert result["effective_property_tax_rate_pct"] <= 1.2
        assert result["rent_control_status"] == "prohibited"
        assert result["tax_advantage_score"] >= 70

    def test_streamlined_permitting(self, id_analyzer):
        """
        WHEN: Evaluate Idaho permitting environment
        THEN: Streamlined permitting, low friction
        """
        result = id_analyzer.assess_tax_and_regulatory_environment(
            jurisdiction="Meridian"
        )

        assert result["median_permit_days"] < 75
        assert result["regulatory_friction_score"] < 50


class TestIdahoComposite:
    """Test composite ID state multiplier calculation."""

    def test_composite_state_multiplier(self, id_analyzer, monkeypatch):
        """
        WHEN: Calculate ID-specific adjustment for all factors
        THEN: Composite multiplier for migration, wildfire, water,
              tax/regulatory advantage
        """
        # Mock components
        monkeypatch.setattr(
            id_analyzer,
            "analyze_treasure_valley_migration",
            lambda *a, **k: {
                "migration_momentum_score": 85,
                "remote_work_factor": 1.25,
            },
        )
        monkeypatch.setattr(
            id_analyzer,
            "assess_wildfire_wui_risk",
            lambda *a, **k: {
                "wui_risk_category": "moderate",
                "insurance_availability": "standard",
            },
        )
        monkeypatch.setattr(
            id_analyzer,
            "assess_water_rights",
            lambda *a, **k: {"availability_score": 75},
        )
        monkeypatch.setattr(
            id_analyzer,
            "assess_tax_and_regulatory_environment",
            lambda *a, **k: {
                "tax_advantage_score": 80,
                "regulatory_friction_score": 35,
            },
        )

        result = id_analyzer.calculate_state_multiplier(
            latitude=43.6150,
            longitude=-116.2023,
            county_fips="16001",
            parcel_id="123",
            jurisdiction="Boise",
        )

        assert "id_multiplier" in result
        assert 0.9 <= result["id_multiplier"] <= 1.1
        assert "adjustments" in result
        assert len(result["adjustments"]) >= 4

    def test_north_idaho_wui_penalty(self, id_analyzer, monkeypatch):
        """
        WHEN: North Idaho property with high WUI risk
        THEN: Wildfire penalty offsets other advantages
        """
        monkeypatch.setattr(
            id_analyzer,
            "analyze_treasure_valley_migration",
            lambda *a, **k: {"migration_momentum_score": 60, "remote_work_factor": 1.1},
        )
        monkeypatch.setattr(
            id_analyzer,
            "assess_wildfire_wui_risk",
            lambda *a, **k: {
                "wui_risk_category": "extreme",
                "insurance_availability": "limited",
            },
        )
        monkeypatch.setattr(
            id_analyzer,
            "assess_water_rights",
            lambda *a, **k: {"availability_score": 60},
        )
        monkeypatch.setattr(
            id_analyzer,
            "assess_tax_and_regulatory_environment",
            lambda *a, **k: {
                "tax_advantage_score": 75,
                "regulatory_friction_score": 40,
            },
        )

        result = id_analyzer.calculate_state_multiplier(
            latitude=47.6777,
            longitude=-116.7805,
            county_fips="16055",
            parcel_id="999",
            jurisdiction="Coeur d'Alene",
        )

        assert result["id_multiplier"] >= 1.0  # WUI risk increases multiplier
        assert any(
            adj["factor"] == "wildfire_wui" and adj["adjustment"] > 0
            for adj in result["adjustments"]
        )

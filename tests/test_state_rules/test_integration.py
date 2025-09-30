"""
State-specific integration tests.

Tests multi-factor state integration for realistic CO/UT/ID property scenarios.
Validates that state analyzers correctly integrate multiple risk factors.
"""

from Claude45_Demo.state_rules.colorado import ColoradoStateAnalyzer
from Claude45_Demo.state_rules.idaho import IdahoStateAnalyzer
from Claude45_Demo.state_rules.utah import UtahStateAnalyzer


class TestColoradoMountainProperty:
    """Test CO mountain property integration (Summit County)."""

    def test_summit_county_integration(self):
        """
        WHEN: Evaluate Summit County CO mountain property
        THEN: Integrate water rights, snow loads, wildfire WUI, hail exposure
        """
        co = ColoradoStateAnalyzer()

        # Summit County coordinates and parameters
        latitude = 39.6403  # Breckenridge
        longitude = -106.0384
        elevation_ft = 9600
        county_fips = "08117"  # Summit County
        parcel_id = "SUMMIT-123"
        jurisdiction = "Breckenridge"

        # Calculate individual factors
        hail = co.calculate_hail_risk_premium(latitude, longitude)
        _ = co.assess_water_rights(county_fips, parcel_id)  # Water rights checked
        snow = co.calculate_snow_load_adjustment(latitude, longitude, elevation_ft)
        wildfire = co.apply_wildfire_wui_adjustment(county_fips, 65)

        # Composite multiplier
        multiplier_result = co.calculate_state_multiplier(
            latitude, longitude, elevation_ft, county_fips, parcel_id, jurisdiction
        )

        # Assertions
        # Hail: Mountain areas have lower hail risk
        assert hail["risk_category"] in ["low", "moderate"]

        # Snow: High elevation = high snow loads
        assert snow["ground_snow_load_psf"] > 60
        assert snow["structural_cost_premium_pct"] >= 12

        # Wildfire: Summit County is mountain WUI
        assert wildfire["wui_multiplier"] >= 1.1

        # Composite: Multiple mountain risk factors
        assert multiplier_result["co_multiplier"] >= 1.0
        assert len(multiplier_result["adjustments"]) >= 3


class TestUtahWasatchFrontProperty:
    """Test UT Wasatch Front property integration (Salt Lake County)."""

    def test_salt_lake_county_integration(self):
        """
        WHEN: Evaluate Salt Lake County property
        THEN: Integrate seismic risk, topography, Silicon Slopes employment
        """
        ut = UtahStateAnalyzer()

        # Salt Lake City foothills parameters
        latitude = 40.7608
        longitude = -111.8910
        elevation_ft = 5200  # Bench development
        county_fips = "49035"  # Salt Lake County
        parcel_id = "SLC-456"
        jurisdiction = "Salt Lake City"

        # Calculate individual factors
        topo = ut.assess_topography_constraints(latitude, longitude, elevation_ft)
        employment = ut.analyze_silicon_slopes_employment(county_fips)
        _ = ut.assess_water_rights(county_fips, parcel_id)  # Water rights checked
        seismic = ut.assess_seismic_risk(latitude, longitude)

        # Composite multiplier
        multiplier_result = ut.calculate_state_multiplier(
            latitude, longitude, elevation_ft, county_fips, parcel_id, jurisdiction
        )

        # Assertions
        # Topography: Benches are steep
        assert topo["slope_pct"] > 15
        assert topo["geotechnical_investigation_required"] is True

        # Employment: Salt Lake is Silicon Slopes
        assert employment["tech_job_growth_score"] >= 55

        # Seismic: Near Wasatch Fault
        assert seismic["fault_proximity_miles"] < 10
        assert seismic["seismic_design_category"] in ["C", "D", "E"]

        # Composite: Topography and seismic increase cost, employment reduces risk
        assert 0.9 <= multiplier_result["ut_multiplier"] <= 1.1
        assert len(multiplier_result["adjustments"]) >= 4


class TestIdahoTreasureValleyProperty:
    """Test ID Treasure Valley property integration (Ada County)."""

    def test_boise_metro_integration(self, monkeypatch):
        """
        WHEN: Evaluate Boise metro property
        THEN: Integrate in-migration, water rights, tax/regulatory advantage
        """
        id_analyzer = IdahoStateAnalyzer()

        # Mock high in-migration
        mock_migration = {
            "net_migration_annual": 8000,
            "top_origin_states": ["CA", "WA", "OR"],
            "remote_work_share_pct": 32,
            "permits_per_household_growth": 1.1,
        }
        monkeypatch.setattr(
            id_analyzer, "_query_migration_data", lambda *a, **k: mock_migration
        )

        # Boise parameters
        latitude = 43.6150
        longitude = -116.2023
        county_fips = "16001"  # Ada County
        parcel_id = "BOISE-789"
        jurisdiction = "Boise"

        # Calculate individual factors
        migration = id_analyzer.analyze_treasure_valley_migration(county_fips)
        wildfire = id_analyzer.assess_wildfire_wui_risk(
            latitude, longitude, county_fips
        )
        _ = id_analyzer.assess_water_rights(
            county_fips, parcel_id
        )  # Water rights checked
        tax_reg = id_analyzer.assess_tax_and_regulatory_environment(jurisdiction)

        # Composite multiplier
        multiplier_result = id_analyzer.calculate_state_multiplier(
            latitude, longitude, county_fips, parcel_id, jurisdiction
        )

        # Assertions
        # Migration: High in-migration momentum
        assert migration["migration_momentum_score"] >= 75
        assert "CA" in migration["top_origin_states"]

        # Wildfire: Treasure Valley has low-moderate WUI risk
        assert wildfire["wui_risk_category"] in ["low", "moderate"]

        # Tax/Regulatory: ID advantages
        assert tax_reg["effective_property_tax_rate_pct"] <= 1.2
        assert tax_reg["rent_control_status"] == "prohibited"
        assert tax_reg["regulatory_friction_score"] < 50

        # Composite: Favorable environment reduces multiplier
        assert multiplier_result["id_multiplier"] <= 1.0
        assert any(
            adj["adjustment"] < 0 for adj in multiplier_result["adjustments"]
        )  # Has negative adj


class TestNorthIdahoWUIProperty:
    """Test North Idaho WUI property integration (Kootenai County)."""

    def test_coeur_dalene_integration(self):
        """
        WHEN: Evaluate Coeur d'Alene area property
        THEN: Wildfire WUI risk offsets other ID advantages
        """
        id_analyzer = IdahoStateAnalyzer()

        # Coeur d'Alene parameters
        latitude = 47.6777
        longitude = -116.7805
        county_fips = "16055"  # Kootenai County
        parcel_id = "CDA-999"
        jurisdiction = "Coeur d'Alene"

        # Calculate factors
        wildfire = id_analyzer.assess_wildfire_wui_risk(
            latitude, longitude, county_fips
        )
        tax_reg = id_analyzer.assess_tax_and_regulatory_environment(jurisdiction)

        # Composite multiplier
        multiplier_result = id_analyzer.calculate_state_multiplier(
            latitude, longitude, county_fips, parcel_id, jurisdiction
        )

        # Assertions
        # Wildfire: North ID WUI is high risk
        assert wildfire["wui_risk_category"] in ["high", "extreme"]
        assert wildfire["insurance_availability"] == "limited"
        assert wildfire["firewise_required"] is True

        # Tax/Regulatory: Still favorable
        assert tax_reg["tax_advantage_score"] >= 70

        # Composite: Wildfire risk increases multiplier despite tax advantages
        assert multiplier_result["id_multiplier"] >= 1.0
        assert any(
            adj["factor"] == "wildfire_wui" and adj["adjustment"] > 0
            for adj in multiplier_result["adjustments"]
        )

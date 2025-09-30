"""
Tests for state water rights connectors.

Tests stub implementations for CO/UT/ID water rights APIs.
"""

from Claude45_Demo.state_rules.water_rights import (
    ColoradoWaterRightsConnector,
    IdahoWaterRightsConnector,
    UtahWaterRightsConnector,
)


class TestColoradoWaterRightsConnector:
    """Test CO CDSS HydroBase connector."""

    def test_initialization(self):
        """
        WHEN: Initialize CO water rights connector
        THEN: Set base URL and cache TTL
        """
        connector = ColoradoWaterRightsConnector(api_key="test_key", cache_ttl_days=15)

        assert connector.api_key == "test_key"
        assert connector.cache_ttl == 15
        assert "dwr.state.co.us" in connector.base_url

    def test_query_structures_stub(self):
        """
        WHEN: Query CDSS for water structures (stub)
        THEN: Return stub data with expected structure
        """
        connector = ColoradoWaterRightsConnector()
        result = connector.query_structures(county_fips="08013", parcel_id="123")

        assert "structures" in result
        assert "water_rights" in result
        assert "water_court_district" in result
        assert isinstance(result["structures"], list)


class TestUtahWaterRightsConnector:
    """Test UT DWR Points of Diversion connector."""

    def test_initialization(self):
        """
        WHEN: Initialize UT water rights connector
        THEN: Set base URL and cache TTL
        """
        connector = UtahWaterRightsConnector(cache_ttl_days=20)

        assert connector.cache_ttl == 20
        assert "opendata.utah.gov" in connector.base_url

    def test_query_points_of_diversion_stub(self):
        """
        WHEN: Query UT DWR for Points of Diversion (stub)
        THEN: Return stub data with expected structure
        """
        connector = UtahWaterRightsConnector()
        result = connector.query_points_of_diversion(
            county_fips="49035", parcel_id="456"
        )

        assert "points_of_diversion" in result
        assert "critical_management_area" in result
        assert "drought_status" in result
        assert isinstance(result["points_of_diversion"], list)


class TestIdahoWaterRightsConnector:
    """Test ID IDWR water rights connector."""

    def test_initialization(self):
        """
        WHEN: Initialize ID water rights connector
        THEN: Set base URL and cache TTL
        """
        connector = IdahoWaterRightsConnector(cache_ttl_days=25)

        assert connector.cache_ttl == 25
        assert "idwr.idaho.gov" in connector.base_url

    def test_query_water_rights_stub(self):
        """
        WHEN: Query IDWR for water rights (stub)
        THEN: Return stub data with expected structure
        """
        connector = IdahoWaterRightsConnector()
        result = connector.query_water_rights(county_fips="16001", parcel_id="789")

        assert "water_right_claims" in result
        assert "srba_area" in result
        assert "municipal_service_available" in result
        assert isinstance(result["water_right_claims"], list)

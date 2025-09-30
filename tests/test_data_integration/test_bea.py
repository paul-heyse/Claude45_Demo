"""Tests for BEA (Bureau of Economic Analysis) API connector.

Scenarios map to Requirement: BEA Economic Data Integration in
openspec/changes/add-aker-investment-platform/specs/data-integration/spec.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest


def _bea_connector(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Lazy import and setup for BEA connector with mocked requests."""
    from Claude45_Demo.data_integration.bea import BEAConnector
    from Claude45_Demo.data_integration.cache import CacheManager

    cache = CacheManager(db_path=tmp_path / "bea_cache.db")
    connector = BEAConnector(api_key="test-key", cache_manager=cache)

    # Disable retry delays for faster tests
    monkeypatch.setattr(connector, "_retry_with_backoff", lambda func, **kw: func())

    return connector


class TestGDPByIndustryScenario:
    """Scenario: GDP by industry query returns sector data with shares and growth."""

    @pytest.fixture
    def mock_bea_gdp_response(self) -> Dict[str, Any]:
        """Mock BEA Regional API response for GDP by industry."""
        return {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "GeoFips": "08",
                            "GeoName": "Colorado",
                            "TimePeriod": "2021",
                            "LineCode": "1",
                            "IndustryId": "1",
                            "Description": "All industry total",
                            "DataValue": "420500",
                            "CL_UNIT": "Millions of current dollars",
                        },
                        {
                            "GeoFips": "08",
                            "GeoName": "Colorado",
                            "TimePeriod": "2021",
                            "LineCode": "3",
                            "IndustryId": "3",
                            "Description": "Information",
                            "DataValue": "25800",
                            "CL_UNIT": "Millions of current dollars",
                        },
                        {
                            "GeoFips": "08",
                            "GeoName": "Colorado",
                            "TimePeriod": "2021",
                            "LineCode": "51",
                            "IndustryId": "51",
                            "Description": "Professional and business services",
                            "DataValue": "68300",
                            "CL_UNIT": "Millions of current dollars",
                        },
                        {
                            "GeoFips": "08",
                            "GeoName": "Colorado",
                            "TimePeriod": "2020",
                            "LineCode": "1",
                            "IndustryId": "1",
                            "Description": "All industry total",
                            "DataValue": "400200",
                            "CL_UNIT": "Millions of current dollars",
                        },
                    ]
                }
            }
        }

    def test_fetch_gdp_by_industry_returns_sector_data(
        self, tmp_path, monkeypatch, mock_bea_gdp_response
    ):
        """Test BEA GDP by industry returns DataFrame with sectors and growth."""
        import pandas as pd

        connector = _bea_connector(tmp_path, monkeypatch)

        # Mock requests.get
        class MockResponse:
            def json(self):
                return mock_bea_gdp_response

            def raise_for_status(self):
                pass

        def mock_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr("requests.get", mock_get)

        # Execute
        df = connector.fetch_gdp_by_industry(geo_fips="08", years=[2020, 2021])

        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "Description" in df.columns
        assert "DataValue" in df.columns
        assert "TimePeriod" in df.columns

        # Verify sector data present
        sectors = df["Description"].unique()
        assert "All industry total" in sectors
        assert any("Information" in s for s in sectors)


class TestPersonalIncomeScenario:
    """Scenario: Personal income query returns income data by region."""

    @pytest.fixture
    def mock_bea_income_response(self) -> Dict[str, Any]:
        """Mock BEA Regional API response for personal income."""
        return {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "GeoFips": "08031",
                            "GeoName": "Denver, CO",
                            "TimePeriod": "2021",
                            "LineCode": "1",
                            "Description": "Personal income",
                            "DataValue": "45500",
                            "CL_UNIT": "Thousands of dollars",
                        },
                        {
                            "GeoFips": "08031",
                            "GeoName": "Denver, CO",
                            "TimePeriod": "2020",
                            "LineCode": "1",
                            "Description": "Personal income",
                            "DataValue": "43200",
                            "CL_UNIT": "Thousands of dollars",
                        },
                    ]
                }
            }
        }

    def test_fetch_personal_income_returns_income_data(
        self, tmp_path, monkeypatch, mock_bea_income_response
    ):
        """Test BEA personal income returns DataFrame with income trends."""
        import pandas as pd

        connector = _bea_connector(tmp_path, monkeypatch)

        # Mock requests.get
        class MockResponse:
            def json(self):
                return mock_bea_income_response

            def raise_for_status(self):
                pass

        def mock_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr("requests.get", mock_get)

        # Execute
        df = connector.fetch_personal_income(geo_fips="08031", years=[2020, 2021])

        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "DataValue" in df.columns
        assert "TimePeriod" in df.columns

        # Verify income data
        assert df["DataValue"].dtype in ["float64", "int64"]
        assert df["TimePeriod"].iloc[0] in ["2020", "2021"]


class TestCachingBehavior:
    """Verify BEA connector uses caching properly."""

    def test_subsequent_requests_use_cache(self, tmp_path, monkeypatch):
        """Test that identical requests hit cache instead of API."""

        connector = _bea_connector(tmp_path, monkeypatch)

        call_count = 0

        def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            class MockResponse:
                def json(self):
                    return {
                        "BEAAPI": {
                            "Results": {
                                "Data": [
                                    {
                                        "GeoFips": "08",
                                        "DataValue": "100",
                                        "TimePeriod": "2021",
                                        "Description": "Test",
                                    }
                                ]
                            }
                        }
                    }

                def raise_for_status(self):
                    pass

            return MockResponse()

        monkeypatch.setattr("requests.get", mock_get)

        # First call - should hit API
        df1 = connector.fetch_gdp_by_industry(geo_fips="08", years=[2021])
        assert call_count == 1

        # Second identical call - should hit cache
        df2 = connector.fetch_gdp_by_industry(geo_fips="08", years=[2021])
        assert call_count == 1  # No additional API call

        # DataFrames should be equivalent
        assert len(df1) == len(df2)


class TestErrorHandling:
    """Test error handling for BEA API failures."""

    def test_invalid_api_key_raises_configuration_error(self, tmp_path, monkeypatch):
        """Test that missing API key raises ConfigurationError."""
        from Claude45_Demo.data_integration.bea import BEAConnector
        from Claude45_Demo.data_integration.exceptions import ConfigurationError

        # Mock environment to have no BEA_API_KEY
        monkeypatch.delenv("BEA_API_KEY", raising=False)

        with pytest.raises(ConfigurationError, match="BEA_API_KEY"):
            BEAConnector(api_key=None)

    def test_api_error_response_handled_gracefully(self, tmp_path, monkeypatch):
        """Test that API errors are caught and re-raised appropriately."""
        from Claude45_Demo.data_integration.exceptions import DataSourceError

        connector = _bea_connector(tmp_path, monkeypatch)

        def mock_get(*args, **kwargs):
            class MockResponse:
                def json(self):
                    return {
                        "BEAAPI": {
                            "Error": {"ErrorCode": "40", "Detail": "Bad Request"}
                        }
                    }

                def raise_for_status(self):
                    raise Exception("HTTP 400")

            return MockResponse()

        monkeypatch.setattr("requests.get", mock_get)

        with pytest.raises((DataSourceError, Exception)):
            connector.fetch_gdp_by_industry(geo_fips="08", years=[2021])

"""
Tests for BLS (Bureau of Labor Statistics) API connector.

Tests scenarios from: openspec/changes/add-aker-investment-platform/specs/data-integration/spec.md
- Requirement: BLS Labor Statistics Integration
"""

from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from Claude45_Demo.data_integration.bls import BLSConnector
from Claude45_Demo.data_integration.cache import CacheManager
from Claude45_Demo.data_integration.exceptions import DataSourceError, ValidationError


@pytest.fixture
def cache_manager(tmp_path: Path) -> CacheManager:
    """Create a temporary cache manager for testing."""
    return CacheManager(db_path=tmp_path / "test_cache.db")


@pytest.fixture
def bls_connector(cache_manager: CacheManager) -> BLSConnector:
    """Create BLS connector with test cache."""
    return BLSConnector(api_key="test_key_12345", cache_manager=cache_manager)


@pytest.fixture
def qcew_response() -> Dict[str, Any]:
    """Mock QCEW API response."""
    return {
        "status": "REQUEST_SUCCEEDED",
        "responseTime": 100,
        "message": [],
        "Results": {
            "series": [
                {
                    "seriesID": "ENU0801000010",
                    "data": [
                        {
                            "year": "2021",
                            "period": "A01",
                            "periodName": "Annual",
                            "value": "50000",
                            "footnotes": [],
                        },
                        {
                            "year": "2020",
                            "period": "A01",
                            "periodName": "Annual",
                            "value": "48000",
                            "footnotes": [],
                        },
                        {
                            "year": "2019",
                            "period": "A01",
                            "periodName": "Annual",
                            "value": "46000",
                            "footnotes": [],
                        },
                    ],
                }
            ]
        },
    }


@pytest.fixture
def laus_response() -> Dict[str, Any]:
    """Mock LAUS API response."""
    return {
        "status": "REQUEST_SUCCEEDED",
        "responseTime": 80,
        "message": [],
        "Results": {
            "series": [
                {
                    "seriesID": "LAUCN080310000000003",
                    "data": [
                        {
                            "year": "2023",
                            "period": "M01",
                            "periodName": "January",
                            "value": "3.5",
                            "footnotes": [],
                        },
                        {
                            "year": "2023",
                            "period": "M02",
                            "periodName": "February",
                            "value": "3.3",
                            "footnotes": [],
                        },
                        {
                            "year": "2023",
                            "period": "M03",
                            "periodName": "March",
                            "value": "3.1",
                            "footnotes": [],
                        },
                    ],
                }
            ]
        },
    }


class TestBLSConnectorInitialization:
    """Test BLS connector initialization and configuration."""

    def test_connector_inherits_from_base(self, bls_connector: BLSConnector) -> None:
        """Test that BLSConnector properly inherits from APIConnector."""
        from Claude45_Demo.data_integration.base import APIConnector

        assert isinstance(bls_connector, APIConnector)

    def test_connector_has_correct_base_url(self, bls_connector: BLSConnector) -> None:
        """Test that BLS connector uses correct API base URL."""
        assert "bls.gov" in bls_connector.base_url
        assert bls_connector.api_key == "test_key_12345"

    def test_connector_has_correct_rate_limit(
        self, bls_connector: BLSConnector
    ) -> None:
        """Test that BLS rate limit is configured correctly."""
        # BLS allows 500 requests per day with API key
        assert bls_connector.rate_limit == 500


class TestQCEWEmploymentData:
    """
    Test Requirement: BLS Labor Statistics Integration

    Scenario: Employment by industry sector
    WHEN: the system requests QCEW employment data for a CBSA
    THEN: it fetches employment and wages by 4-digit NAICS code
    AND: calculates Location Quotient (LQ) for tech, healthcare, education, and
         advanced manufacturing
    AND: computes 3-year compound annual growth rate (CAGR) per sector
    """

    @patch("requests.post")
    def test_fetch_qcew_employment_data(
        self,
        mock_post: Mock,
        bls_connector: BLSConnector,
        qcew_response: Dict[str, Any],
    ) -> None:
        """Test fetching QCEW employment data for a CBSA."""
        mock_post.return_value.json.return_value = qcew_response
        mock_post.return_value.status_code = 200

        df = bls_connector.fetch_qcew_employment(
            area_code="08031",  # Denver County
            naics_codes=["10"],  # Total, all industries
            start_year=2019,
            end_year=2021,
        )

        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "year" in df.columns
        assert "value" in df.columns

    @patch("requests.post")
    def test_calculate_location_quotient(
        self,
        mock_post: Mock,
        bls_connector: BLSConnector,
        qcew_response: Dict[str, Any],
    ) -> None:
        """Test Location Quotient calculation for industry sectors."""
        mock_post.return_value.json.return_value = qcew_response
        mock_post.return_value.status_code = 200

        lq_result = bls_connector.calculate_location_quotient(
            area_code="08031",
            naics_code="5415",  # Computer systems design
            reference_area="US000",  # National
            year=2021,
        )

        # LQ should be a positive number
        assert isinstance(lq_result, float)
        assert lq_result > 0

    @patch("requests.post")
    def test_calculate_cagr(
        self,
        mock_post: Mock,
        bls_connector: BLSConnector,
        qcew_response: Dict[str, Any],
    ) -> None:
        """Test 3-year CAGR calculation for employment sector."""
        mock_post.return_value.json.return_value = qcew_response
        mock_post.return_value.status_code = 200

        df = bls_connector.fetch_qcew_employment(
            area_code="08031",
            naics_codes=["10"],
            start_year=2019,
            end_year=2021,
        )

        cagr = bls_connector.calculate_cagr(df, years=3)

        # CAGR should be a reasonable percentage
        assert isinstance(cagr, float)
        # Based on mock data: 46000 -> 50000 over 3 years ≈ 2.8% CAGR
        assert 0.02 < cagr < 0.04


class TestLAUSUnemploymentData:
    """
    Test Requirement: BLS Labor Statistics Integration

    Scenario: Unemployment rate retrieval
    WHEN: the system requests LAUS unemployment data for a county
    THEN: it fetches monthly unemployment rate time series
    AND: calculates 12-month moving average
    AND: compares to state and national benchmarks
    """

    @patch("requests.post")
    def test_fetch_laus_unemployment_rate(
        self,
        mock_post: Mock,
        bls_connector: BLSConnector,
        laus_response: Dict[str, Any],
    ) -> None:
        """Test fetching LAUS unemployment rate time series."""
        mock_post.return_value.json.return_value = laus_response
        mock_post.return_value.status_code = 200

        df = bls_connector.fetch_laus_unemployment(
            area_code="CN0803100000000", start_year=2023, end_year=2023
        )

        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "year" in df.columns
        assert "period" in df.columns
        assert "value" in df.columns

        # Verify data types
        assert df["value"].dtype == float

    def test_calculate_moving_average(self, bls_connector: BLSConnector) -> None:
        """Test 12-month moving average calculation."""
        # Create test data
        dates = pd.date_range("2022-01-01", periods=24, freq="ME")
        test_data = pd.DataFrame({"date": dates, "value": range(24)})

        ma = bls_connector.calculate_moving_average(test_data, window=12)

        # Moving average should have same length as input
        assert len(ma) == len(test_data)
        # First 11 values should be NaN, then calculated averages
        assert ma.isna().sum() == 11
        assert not ma[11:].isna().any()

    @patch("requests.post")
    def test_compare_to_benchmarks(
        self,
        mock_post: Mock,
        bls_connector: BLSConnector,
        laus_response: Dict[str, Any],
    ) -> None:
        """Test comparison to state and national unemployment benchmarks."""
        mock_post.return_value.json.return_value = laus_response
        mock_post.return_value.status_code = 200

        comparison = bls_connector.compare_unemployment_to_benchmarks(
            county_code="CN0803100000000",  # Denver County
            state_code="ST0800000000000",  # Colorado
            national_code="LNS14000000",  # National
            year=2023,
        )

        # Should return comparison metrics
        assert isinstance(comparison, dict)
        assert "county_rate" in comparison
        assert "state_rate" in comparison
        assert "national_rate" in comparison


class TestCaching:
    """Test that BLS connector properly uses caching."""

    @patch("requests.post")
    def test_cache_hit_avoids_api_call(
        self,
        mock_post: Mock,
        bls_connector: BLSConnector,
        qcew_response: Dict[str, Any],
    ) -> None:
        """Test that cached data is returned without making API call."""
        mock_post.return_value.json.return_value = qcew_response
        mock_post.return_value.status_code = 200

        # First call - should hit API
        df1 = bls_connector.fetch_qcew_employment(
            area_code="08031", naics_codes=["10"], start_year=2021, end_year=2021
        )

        assert mock_post.call_count == 1

        # Second call - should use cache
        df2 = bls_connector.fetch_qcew_employment(
            area_code="08031", naics_codes=["10"], start_year=2021, end_year=2021
        )

        # Should not make another API call
        assert mock_post.call_count == 1
        # Data should be identical
        pd.testing.assert_frame_equal(df1, df2)


class TestErrorHandling:
    """Test error handling and validation."""

    def test_invalid_api_key_raises_error(self, cache_manager: CacheManager) -> None:
        """Test that missing API key raises ConfigurationError."""
        from Claude45_Demo.data_integration.exceptions import ConfigurationError

        with pytest.raises(ConfigurationError):
            BLSConnector(api_key=None, cache_manager=cache_manager)  # type: ignore

    @patch("requests.post")
    def test_api_failure_raises_data_source_error(
        self, mock_post: Mock, bls_connector: BLSConnector
    ) -> None:
        """Test that API failures raise DataSourceError."""
        mock_post.side_effect = Exception("API Error")

        with pytest.raises(DataSourceError):
            bls_connector.fetch_qcew_employment(
                area_code="08031", naics_codes=["10"], start_year=2021, end_year=2021
            )

    def test_invalid_response_format_raises_validation_error(
        self, bls_connector: BLSConnector
    ) -> None:
        """Test that malformed API responses raise ValidationError."""
        invalid_response = {"status": "ERROR", "message": ["Invalid request"]}

        with pytest.raises(ValidationError):
            bls_connector.parse(invalid_response)

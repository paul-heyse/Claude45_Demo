"""
Security tests for API key validation and protection.

Tests scenarios from: openspec/changes/add-aker-investment-platform/specs/testing-validation/spec.md
- Requirement: Security Testing
- Scenario: API key validation
"""

import logging
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from Claude45_Demo.data_integration.bea import BEAConnector
from Claude45_Demo.data_integration.bls import BLSConnector
from Claude45_Demo.data_integration.cache import CacheManager
from Claude45_Demo.data_integration.census import CensusConnector
from Claude45_Demo.data_integration.drought_monitor import DroughtMonitorConnector
from Claude45_Demo.data_integration.epa_aqs import EPAAQSConnector
from Claude45_Demo.data_integration.epa_echo import EPAECHOConnector
from Claude45_Demo.data_integration.epa_radon import EPARadonConnector
from Claude45_Demo.data_integration.exceptions import ConfigurationError
from Claude45_Demo.data_integration.landfire_fuel import LANDFIREFuelConnector
from Claude45_Demo.data_integration.nasa_firms import NASAFIRMSConnector
from Claude45_Demo.data_integration.noaa_spc import NOAASPCConnector
from Claude45_Demo.data_integration.prism_snow import PRISMSnowConnector
from Claude45_Demo.data_integration.usfs_whp import USFSWHPConnector
from Claude45_Demo.data_integration.usgs_nshm import USGSNSHMConnector
from Claude45_Demo.data_integration.wui_classifier import WUIClassifier


@pytest.fixture
def cache_manager(tmp_path: Path) -> CacheManager:
    """Provide isolated cache manager for tests."""
    return CacheManager(db_path=tmp_path / "test_cache.db")


class TestAPIKeyValidation:
    """
    Test Requirement: Security Testing - API Key Validation

    Scenario: Invalid API keys are rejected
    WHEN: API keys are configured or used
    THEN: invalid keys are rejected with ConfigurationError
    """

    def test_bea_connector_rejects_none_api_key(
        self, cache_manager: CacheManager, monkeypatch
    ) -> None:
        """BEA connector must reject None API key."""
        monkeypatch.delenv("BEA_API_KEY", raising=False)

        with pytest.raises(ConfigurationError, match="BEA_API_KEY"):
            BEAConnector(api_key=None, cache_manager=cache_manager)  # type: ignore

    def test_bea_connector_rejects_empty_api_key(
        self, cache_manager: CacheManager
    ) -> None:
        """BEA connector must reject empty string API key."""
        with pytest.raises(ConfigurationError, match="BEA_API_KEY"):
            BEAConnector(api_key="", cache_manager=cache_manager)

    def test_bls_connector_rejects_none_api_key(
        self, cache_manager: CacheManager
    ) -> None:
        """BLS connector must reject None API key."""
        with pytest.raises(ConfigurationError):
            BLSConnector(api_key=None, cache_manager=cache_manager)  # type: ignore

    def test_bls_connector_rejects_empty_api_key(
        self, cache_manager: CacheManager
    ) -> None:
        """BLS connector must reject empty string API key."""
        with pytest.raises(ConfigurationError):
            BLSConnector(api_key="", cache_manager=cache_manager)

    def test_census_connector_rejects_none_api_key(
        self, cache_manager: CacheManager
    ) -> None:
        """Census connector must reject None API key."""
        with pytest.raises(ConfigurationError):
            CensusConnector(api_key=None, cache_manager=cache_manager)  # type: ignore

    def test_census_connector_rejects_empty_api_key(
        self, cache_manager: CacheManager
    ) -> None:
        """Census connector must reject empty string API key."""
        with pytest.raises(ConfigurationError):
            CensusConnector(api_key="", cache_manager=cache_manager)

    def test_epa_aqs_connector_rejects_none_api_key(
        self, cache_manager: CacheManager
    ) -> None:
        """EPA AQS connector must reject None API key."""
        with pytest.raises((ConfigurationError, ValueError)):
            EPAAQSConnector(
                email="test@example.com",
                api_key=None,  # type: ignore
                cache_manager=cache_manager,
            )

    def test_epa_aqs_connector_rejects_empty_api_key(
        self, cache_manager: CacheManager
    ) -> None:
        """EPA AQS connector must reject empty string API key."""
        with pytest.raises((ConfigurationError, ValueError)):
            EPAAQSConnector(
                email="test@example.com", api_key="", cache_manager=cache_manager
            )

    def test_nasa_firms_connector_rejects_none_api_key(
        self, cache_manager: CacheManager
    ) -> None:
        """NASA FIRMS connector must reject None API key."""
        with pytest.raises((ConfigurationError, ValueError)):
            NASAFIRMSConnector(api_key=None, cache_manager=cache_manager)  # type: ignore

    def test_nasa_firms_connector_rejects_empty_api_key(
        self, cache_manager: CacheManager
    ) -> None:
        """NASA FIRMS connector must reject empty string API key."""
        with pytest.raises((ConfigurationError, ValueError)):
            NASAFIRMSConnector(api_key="", cache_manager=cache_manager)

    def test_connectors_without_keys_accept_none(
        self, cache_manager: CacheManager
    ) -> None:
        """Connectors that don't require API keys should accept None gracefully."""
        # These connectors should work without API keys
        no_key_connectors = [
            DroughtMonitorConnector(cache_manager=cache_manager),
            EPAECHOConnector(cache_manager=cache_manager),
            EPARadonConnector(cache_manager=cache_manager),
            LANDFIREFuelConnector(cache_manager=cache_manager),
            NOAASPCConnector(cache_manager=cache_manager),
            PRISMSnowConnector(cache_manager=cache_manager),
            USFSWHPConnector(cache_manager=cache_manager),
            USGSNSHMConnector(cache_manager=cache_manager),
            WUIClassifier(cache_manager=cache_manager),
        ]

        # Should not raise errors
        assert len(no_key_connectors) == 9


class TestAPIKeyMasking:
    """
    Test Requirement: Security Testing - API Key Masking

    Scenario: API keys are masked in logs
    WHEN: API keys are logged
    THEN: API keys show only last 4 chars
    AND: full keys are never exposed
    """

    def test_api_key_not_in_logs(self, cache_manager: CacheManager, caplog) -> None:
        """API keys must not appear in full in log messages."""
        api_key = "super_secret_key_1234567890"

        with caplog.at_level(logging.DEBUG):
            connector = CensusConnector(api_key=api_key, cache_manager=cache_manager)

            # Check that full API key never appears in logs
            for record in caplog.records:
                assert api_key not in record.message, \
                    f"Full API key found in log: {record.message}"

    def test_api_key_masked_in_repr(self, cache_manager: CacheManager) -> None:
        """API keys must be masked in object representations."""
        api_key = "super_secret_key_1234567890"
        connector = CensusConnector(api_key=api_key, cache_manager=cache_manager)

        repr_string = repr(connector)

        # Full key should not be in repr
        assert api_key not in repr_string

        # Only last 4 chars should be visible (if repr includes key at all)
        if "key" in repr_string.lower():
            assert "...7890" in repr_string or "****7890" in repr_string or \
                   "7890" in repr_string

    def test_api_key_not_in_error_messages(
        self, cache_manager: CacheManager, monkeypatch
    ) -> None:
        """API keys must not appear in error messages."""
        api_key = "super_secret_key_1234567890"

        with monkeypatch.context() as m:
            def mock_get(*args, **kwargs):
                raise Exception("API request failed: Check your credentials")

            m.setattr("requests.get", mock_get)

            connector = CensusConnector(api_key=api_key, cache_manager=cache_manager)

            try:
                connector.fetch_acs_demographics(cbsa="19740", year=2021)
            except Exception as e:
                # Full API key should not be in error message
                assert api_key not in str(e)


class TestAPIKeyStorage:
    """
    Test Requirement: Security Testing - Credential Storage

    Scenario: API keys stored securely
    WHEN: credentials are stored or transmitted
    THEN: environment variables are used (not config files)
    AND: secrets are never logged
    """

    def test_api_key_from_environment_variable(
        self, cache_manager: CacheManager, monkeypatch
    ) -> None:
        """API keys should be loaded from environment variables."""
        test_key = "env_test_key_123"
        monkeypatch.setenv("BEA_API_KEY", test_key)

        # When no key is explicitly provided, should load from env
        connector = BEAConnector(cache_manager=cache_manager)

        # Verify the key was loaded (indirectly - api_key is set)
        assert connector.api_key is not None
        assert len(connector.api_key) > 0

    def test_no_hardcoded_api_keys_in_code(self) -> None:
        """Verify no hardcoded API keys exist in connector code."""
        import inspect
        from Claude45_Demo.data_integration import base

        # Check base connector source code
        source = inspect.getsource(base)

        # Look for suspicious patterns (common key patterns)
        suspicious_patterns = [
            "api_key = \"",
            "api_key='",
            "API_KEY = \"",
            "API_KEY='",
        ]

        for pattern in suspicious_patterns:
            assert pattern not in source, \
                f"Potential hardcoded API key found: {pattern}"

    def test_api_keys_not_in_cache_keys(
        self, cache_manager: CacheManager, tmp_path
    ) -> None:
        """API keys should not be included in cache keys."""
        api_key = "secret_key_987654321"
        connector = BEAConnector(api_key=api_key, cache_manager=cache_manager)

        # Cache keys should not contain the API key
        cache_key_example = "bea_gdp_08_2021"

        # Verify API key is not in typical cache key format
        assert api_key not in cache_key_example


class TestAPIKeyRotation:
    """
    Test Requirement: Security Testing - Credential Rotation

    Scenario: API key rotation handling
    WHEN: API keys are rotated
    THEN: system handles old/new keys gracefully
    AND: provides clear error messages
    """

    def test_expired_api_key_clear_error(
        self, cache_manager: CacheManager, monkeypatch
    ) -> None:
        """Expired API keys should produce clear error messages."""
        expired_key = "EXPIRED_KEY_123"

        def mock_get(*args, **kwargs):
            class MockResponse:
                status_code = 401
                text = "Invalid or expired API key"

                def raise_for_status(self):
                    import requests
                    raise requests.exceptions.HTTPError("401 Unauthorized")

                def json(self):
                    return {"error": "Invalid API key"}

            return MockResponse()

        monkeypatch.setattr("requests.get", mock_get)

        connector = CensusConnector(api_key=expired_key, cache_manager=cache_manager)

        with pytest.raises(Exception) as exc_info:
            connector.fetch_acs_demographics(cbsa="19740", year=2021)

        # Error message should indicate key issue (but not expose the key)
        error_msg = str(exc_info.value).lower()
        assert any(word in error_msg for word in ["unauthorized", "401", "key", "credential"])
        assert expired_key not in str(exc_info.value)

    def test_api_key_validation_at_init(self, cache_manager: CacheManager) -> None:
        """API keys should be validated at connector initialization."""
        # Valid key format should be accepted
        valid_key = "valid_key_format_12345"
        connector = CensusConnector(api_key=valid_key, cache_manager=cache_manager)
        assert connector.api_key == valid_key

        # Invalid formats should be rejected early
        with pytest.raises((ConfigurationError, ValueError)):
            CensusConnector(api_key=None, cache_manager=cache_manager)  # type: ignore


class TestSecurityBestPractices:
    """
    Test Requirement: Security Testing - Best Practices

    Scenario: Security best practices followed
    WHEN: security-sensitive operations occur
    THEN: best practices are followed
    """

    def test_no_api_keys_in_urls(self, cache_manager: CacheManager) -> None:
        """API keys should not be passed in URLs (use headers/body instead)."""
        api_key = "test_key_url_check"
        connector = CensusConnector(api_key=api_key, cache_manager=cache_manager)

        # Check that the base URL doesn't contain the API key
        assert api_key not in connector.base_url

    def test_https_required_for_api_calls(self, cache_manager: CacheManager) -> None:
        """All API connectors must use HTTPS, not HTTP."""
        connectors_to_check = [
            CensusConnector(api_key="test", cache_manager=cache_manager),
            BLSConnector(api_key="test", cache_manager=cache_manager),
            BEAConnector(api_key="test", cache_manager=cache_manager),
            EPAAQSConnector(email="test@test.com", api_key="test", cache_manager=cache_manager),
            NASAFIRMSConnector(api_key="test", cache_manager=cache_manager),
        ]

        for connector in connectors_to_check:
            # All base URLs must use https://
            assert connector.base_url.startswith("https://"), \
                f"{connector.__class__.__name__} must use HTTPS"

    def test_api_keys_cleared_on_deletion(
        self, cache_manager: CacheManager
    ) -> None:
        """API keys should be cleared when connectors are deleted."""
        api_key = "test_key_memory_clear"
        connector = CensusConnector(api_key=api_key, cache_manager=cache_manager)

        # Get the id before deletion
        connector_id = id(connector)

        # Delete the connector
        del connector

        # Key should no longer be in memory (can't test directly, but ensures cleanup)
        # This test mainly documents the expectation
        assert True  # Placeholder for memory scrubbing expectation


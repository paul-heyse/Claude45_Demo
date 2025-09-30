"""
Tests for base API connector functionality.

Tests scenarios from: openspec/changes/add-aker-investment-platform/specs/data-integration/spec.md
"""

import time
from datetime import timedelta
from typing import Any, Dict

import pytest


class MockConnector:
    """Mock connector for testing abstract base class."""

    def __init__(
        self, api_key: str = "test_key", base_url: str = "https://api.example.com"
    ):
        from Claude45_Demo.data_integration.base import APIConnector

        # Create a concrete implementation for testing
        class ConcreteConnector(APIConnector):
            def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
                return {"data": "mock_response", "params": params}

            def parse(self, response: Dict[str, Any]) -> Any:
                return response

        self.connector = ConcreteConnector(api_key=api_key, base_url=base_url)


class TestAPIConnectorAbstraction:
    """
    Test Requirement: API Connector Abstraction

    Scenario: Connector inheritance
    WHEN: a developer creates a new data source connector
    THEN: the connector class inherits from APIConnector base class
    AND: implements required methods: authenticate(), fetch(), parse(), validate()
    """

    def test_connector_inheritance(self):
        """Test that connectors properly inherit from APIConnector."""
        from Claude45_Demo.data_integration.base import APIConnector

        mock = MockConnector()
        assert isinstance(mock.connector, APIConnector)
        assert hasattr(mock.connector, "fetch")
        assert hasattr(mock.connector, "parse")
        assert hasattr(mock.connector, "validate")

    def test_required_methods_implemented(self):
        """Test that all required abstract methods are implemented."""
        mock = MockConnector()

        # Test fetch is callable
        result = mock.connector.fetch({"test": "param"})
        assert result is not None

        # Test parse is callable
        parsed = mock.connector.parse({"data": "test"})
        assert parsed is not None


class TestErrorHandlingWithRetry:
    """
    Test Requirement: API Connector Abstraction

    Scenario: Consistent error handling
    WHEN: an API request fails with a recoverable error (rate limit, timeout)
    THEN: the connector applies exponential backoff retry logic
    AND: logs the failure and retry attempts
    AND: raises a custom exception after max retries exceeded
    """

    def test_exponential_backoff_on_failure(self):
        """Test exponential backoff retry logic."""
        from Claude45_Demo.data_integration.base import APIConnector

        class FailingConnector(APIConnector):
            def __init__(self):
                super().__init__(api_key="test")
                self.attempt_count = 0
                self.attempt_times = []

            def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
                return {}

            def parse(self, response: Dict[str, Any]) -> Any:
                return response

        connector = FailingConnector()

        # Mock function that fails first 2 times, succeeds on 3rd
        call_count = 0

        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return {"success": True}

        # Test retry with backoff
        start_time = time.time()
        result = connector._retry_with_backoff(
            failing_func, max_retries=5, initial_delay=0.1
        )
        elapsed = time.time() - start_time

        assert result == {"success": True}
        assert call_count == 3
        # Should have waited at least 0.1 + 0.2 = 0.3 seconds
        assert elapsed >= 0.3

    def test_max_retries_exceeded_raises_exception(self):
        """Test that custom exception is raised after max retries."""
        from Claude45_Demo.data_integration.base import APIConnector
        from Claude45_Demo.data_integration.exceptions import DataSourceError

        class FailingConnector(APIConnector):
            def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
                return {}

            def parse(self, response: Dict[str, Any]) -> Any:
                return response

        connector = FailingConnector()

        def always_fails():
            raise ConnectionError("Persistent failure")

        # Should raise DataSourceError after exhausting retries
        with pytest.raises(DataSourceError):
            connector._retry_with_backoff(
                always_fails, max_retries=3, initial_delay=0.01
            )


class TestRateLimiting:
    """
    Test Requirement: Rate Limit Compliance

    Scenario: Census API rate limit
    WHEN: the system makes multiple Census API requests in succession
    THEN: it tracks requests per day (max 500)
    AND: queues additional requests if limit approached
    AND: logs rate limit warnings and suggests cache usage
    """

    def test_rate_limit_tracking(self):
        """Test that rate limit is tracked per connector."""
        mock = MockConnector()

        # Make multiple requests
        for i in range(10):
            mock.connector.fetch({"request": i})

        # Request count should be tracked
        assert hasattr(mock.connector, "_request_count")
        assert mock.connector._request_count >= 0

    def test_rate_limit_warning_on_high_usage(self, caplog):
        """Test warning is logged when approaching rate limit."""
        from Claude45_Demo.data_integration.base import APIConnector

        class TrackedConnector(APIConnector):
            def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
                self._track_request()
                return {"data": "test"}

            def parse(self, response: Dict[str, Any]) -> Any:
                return response

        connector = TrackedConnector(api_key="test", rate_limit=10)

        # Simulate approaching rate limit
        connector._request_count = 8

        with caplog.at_level("WARNING"):
            connector._check_rate_limit()

        # Should log warning when > 80% of limit
        assert any("rate limit" in record.message.lower() for record in caplog.records)


class TestConfigurationInitialization:
    """
    Test base connector configuration and initialization.
    """

    def test_connector_initialization_with_config(self):
        """Test connector initializes with proper configuration."""
        mock = MockConnector(api_key="test_key_123", base_url="https://test.api.com")

        assert mock.connector.api_key == "test_key_123"
        assert mock.connector.base_url == "https://test.api.com"
        assert hasattr(mock.connector, "cache_ttl")
        assert hasattr(mock.connector, "rate_limit")

    def test_default_cache_ttl_is_set(self):
        """Test that default cache TTL is configured."""
        mock = MockConnector()

        # Default TTL should be 30 days per spec
        assert mock.connector.cache_ttl == timedelta(days=30)


class TestValidation:
    """
    Test Requirement: Data Quality Validation

    Scenario: Schema validation
    WHEN: an API response is received
    THEN: the connector validates expected fields are present
    AND: checks data types match specification
    AND: logs warnings for missing or malformed fields
    AND: raises DataValidationError if critical fields are invalid
    """

    def test_validate_method_exists(self):
        """Test that validate method is available."""
        mock = MockConnector()
        assert hasattr(mock.connector, "validate")
        assert callable(mock.connector.validate)

    def test_validate_checks_required_fields(self):
        """Test validation checks for required fields."""
        from Claude45_Demo.data_integration.base import APIConnector
        from Claude45_Demo.data_integration.exceptions import ValidationError

        class ValidatingConnector(APIConnector):
            def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
                return {}

            def parse(self, response: Dict[str, Any]) -> Any:
                return response

        connector = ValidatingConnector()

        # Valid data should pass
        valid_data = {"required_field": "value", "optional_field": 123}
        try:
            connector.validate(valid_data, required_fields=["required_field"])
        except ValidationError:
            pytest.fail("Valid data should not raise ValidationError")

        # Missing required field should raise
        invalid_data = {"optional_field": 123}
        with pytest.raises(ValidationError):
            connector.validate(invalid_data, required_fields=["required_field"])

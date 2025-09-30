"""
Tests for configuration management system.

Tests scenarios from: openspec/changes/add-aker-investment-platform/specs/data-integration/spec.md
- Requirement: Configuration Management
"""

import os
from pathlib import Path
from typing import Dict

import pytest
import yaml

from Claude45_Demo.data_integration.config import ConfigManager
from Claude45_Demo.data_integration.exceptions import ConfigurationError


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Create a temporary config file for testing."""
    config_data = {
        "data_sources": {
            "census": {
                "api_key": "${CENSUS_API_KEY}",
                "base_url": "https://api.census.gov/data",
                "cache_ttl_days": 30,
                "rate_limit": 500,
            },
            "bls": {
                "api_key": "${BLS_API_KEY}",
                "base_url": "https://api.bls.gov/publicAPI/v2",
                "cache_ttl_days": 7,
                "rate_limit": 500,
            },
        },
        "scoring": {
            "weights": {
                "supply": 0.30,
                "jobs": 0.30,
                "urban": 0.20,
                "outdoor": 0.20,
            },
            "risk_multiplier_range": {"min": 0.85, "max": 1.10},
        },
    }

    config_path = tmp_path / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    return config_path


@pytest.fixture
def env_vars() -> Dict[str, str]:
    """Set up test environment variables."""
    test_env = {
        "CENSUS_API_KEY": "census_test_key_12345",
        "BLS_API_KEY": "bls_test_key_67890",
    }

    # Set environment variables
    for key, value in test_env.items():
        os.environ[key] = value

    yield test_env

    # Clean up
    for key in test_env.keys():
        os.environ.pop(key, None)


class TestConfigManagerInitialization:
    """Test ConfigManager initialization and loading."""

    def test_load_config_from_file(self, config_file: Path) -> None:
        """Test loading configuration from YAML file."""
        config = ConfigManager(config_path=config_file)

        assert config is not None
        assert "data_sources" in config.config
        assert "census" in config.config["data_sources"]
        assert "bls" in config.config["data_sources"]

    def test_load_config_with_defaults(self) -> None:
        """Test loading default configuration when no file specified."""
        config = ConfigManager()

        # Should load with default values
        assert config is not None
        assert hasattr(config, "config")

    def test_invalid_config_path_raises_error(self) -> None:
        """Test that invalid config path raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            ConfigManager(config_path=Path("/nonexistent/config.yaml"))


class TestAPIKeyLoading:
    """
    Test Requirement: Configuration Management

    Scenario: API key loading
    WHEN: the system initializes a data connector
    THEN: it reads API keys from environment variables or config file
    AND: validates keys are present for required services
    AND: logs masked key identifiers (last 4 chars) for debugging
    AND: raises ConfigurationError if required keys missing
    """

    def test_load_api_key_from_env(
        self, config_file: Path, env_vars: Dict[str, str]
    ) -> None:
        """Test loading API keys from environment variables."""
        config = ConfigManager(config_path=config_file)

        census_key = config.get_api_key("census")
        bls_key = config.get_api_key("bls")

        assert census_key == "census_test_key_12345"
        assert bls_key == "bls_test_key_67890"

    def test_validate_required_keys_present(
        self, config_file: Path, env_vars: Dict[str, str]
    ) -> None:
        """Test validation of required API keys."""
        config = ConfigManager(config_path=config_file)

        # Should not raise error when keys are present
        config.validate_required_keys(["census", "bls"])

    def test_validate_required_keys_missing_raises_error(
        self, config_file: Path
    ) -> None:
        """Test that missing required keys raise ConfigurationError."""
        config = ConfigManager(config_path=config_file)

        # Clear environment variables
        os.environ.pop("CENSUS_API_KEY", None)

        with pytest.raises(ConfigurationError, match="census"):
            config.validate_required_keys(["census"])

    def test_log_masked_key_identifiers(
        self,
        config_file: Path,
        env_vars: Dict[str, str],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that API keys are logged with masking (last 4 chars only)."""
        config = ConfigManager(config_path=config_file)

        masked_key = config.get_masked_key("census")

        # Should mask all but last 4 characters
        assert masked_key.endswith("2345")
        assert masked_key.startswith("...")
        assert len(masked_key) == 7  # ...2345


class TestCacheTTLConfiguration:
    """
    Test Requirement: Configuration Management

    Scenario: Cache TTL override
    WHEN: a user specifies custom cache TTL in config file
    THEN: the system uses the custom TTL for that data source
    AND: documents recommended TTLs per source in default config
    AND: warns if TTL is unusually short (<1 day) or long (>90 days)
    """

    def test_get_cache_ttl_from_config(self, config_file: Path) -> None:
        """Test retrieving cache TTL from config file."""
        config = ConfigManager(config_path=config_file)

        census_ttl = config.get_cache_ttl("census")
        bls_ttl = config.get_cache_ttl("bls")

        assert census_ttl == 30  # days
        assert bls_ttl == 7  # days

    def test_use_custom_cache_ttl(self, tmp_path: Path) -> None:
        """Test that custom TTL overrides default."""
        custom_config = {
            "data_sources": {
                "census": {
                    "api_key": "${CENSUS_API_KEY}",
                    "cache_ttl_days": 15,  # Custom value
                }
            }
        }

        config_path = tmp_path / "custom_config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(custom_config, f)

        config = ConfigManager(config_path=config_path)
        ttl = config.get_cache_ttl("census")

        assert ttl == 15

    def test_warn_on_unusually_short_ttl(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test warning is logged for TTL < 1 day."""
        short_ttl_config = {
            "data_sources": {
                "test_source": {
                    "api_key": "test",
                    "cache_ttl_days": 0.5,  # 12 hours - too short
                }
            }
        }

        config_path = tmp_path / "short_ttl.yaml"
        with open(config_path, "w") as f:
            yaml.dump(short_ttl_config, f)

        config = ConfigManager(config_path=config_path)

        with caplog.at_level("WARNING"):
            config.validate_cache_ttl("test_source")

        # Should warn about short TTL
        assert any("short" in record.message.lower() for record in caplog.records)

    def test_warn_on_unusually_long_ttl(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test warning is logged for TTL > 90 days."""
        long_ttl_config = {
            "data_sources": {
                "test_source": {
                    "api_key": "test",
                    "cache_ttl_days": 180,  # 6 months - too long
                }
            }
        }

        config_path = tmp_path / "long_ttl.yaml"
        with open(config_path, "w") as f:
            yaml.dump(long_ttl_config, f)

        config = ConfigManager(config_path=config_path)

        with caplog.at_level("WARNING"):
            config.validate_cache_ttl("test_source")

        # Should warn about long TTL
        assert any("long" in record.message.lower() for record in caplog.records)


class TestRateLimitConfiguration:
    """Test rate limit configuration from config file."""

    def test_get_rate_limit_from_config(self, config_file: Path) -> None:
        """Test retrieving rate limit from config file."""
        config = ConfigManager(config_path=config_file)

        census_limit = config.get_rate_limit("census")
        bls_limit = config.get_rate_limit("bls")

        assert census_limit == 500
        assert bls_limit == 500

    def test_get_base_url_from_config(self, config_file: Path) -> None:
        """Test retrieving base URL from config file."""
        config = ConfigManager(config_path=config_file)

        census_url = config.get_base_url("census")
        bls_url = config.get_base_url("bls")

        assert "census.gov" in census_url
        assert "bls.gov" in bls_url


class TestScoringConfiguration:
    """Test scoring weights and risk multiplier configuration."""

    def test_get_scoring_weights(self, config_file: Path) -> None:
        """Test retrieving scoring weights from config."""
        config = ConfigManager(config_path=config_file)

        weights = config.get_scoring_weights()

        assert weights["supply"] == 0.30
        assert weights["jobs"] == 0.30
        assert weights["urban"] == 0.20
        assert weights["outdoor"] == 0.20

        # Weights should sum to 1.0
        assert sum(weights.values()) == pytest.approx(1.0)

    def test_get_risk_multiplier_range(self, config_file: Path) -> None:
        """Test retrieving risk multiplier range from config."""
        config = ConfigManager(config_path=config_file)

        risk_range = config.get_risk_multiplier_range()

        assert risk_range["min"] == 0.85
        assert risk_range["max"] == 1.10


class TestEnvironmentVariableSubstitution:
    """Test environment variable substitution in config values."""

    def test_substitute_env_vars_in_config(
        self, config_file: Path, env_vars: Dict[str, str]
    ) -> None:
        """Test that ${VAR} syntax is replaced with environment values."""
        config = ConfigManager(config_path=config_file)

        # Should substitute ${CENSUS_API_KEY} with actual value
        census_key = config.get_api_key("census")
        assert census_key == env_vars["CENSUS_API_KEY"]
        assert "${" not in census_key

    def test_missing_env_var_raises_error(self, config_file: Path) -> None:
        """Test that missing environment variable raises error."""
        # Clear environment
        os.environ.pop("CENSUS_API_KEY", None)

        config = ConfigManager(config_path=config_file)

        with pytest.raises(ConfigurationError, match="CENSUS_API_KEY"):
            config.get_api_key("census")


class TestDefaultConfigGeneration:
    """Test default configuration file generation."""

    def test_generate_default_config(self, tmp_path: Path) -> None:
        """Test generating a default config file."""
        config_path = tmp_path / "generated_config.yaml"

        ConfigManager.generate_default_config(config_path)

        assert config_path.exists()

        # Load and verify structure
        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        assert "data_sources" in config_data
        assert "scoring" in config_data

    def test_generate_env_template(self, tmp_path: Path) -> None:
        """Test generating .env template file."""
        env_path = tmp_path / ".env.example"

        ConfigManager.generate_env_template(env_path)

        assert env_path.exists()

        # Should contain API key placeholders
        content = env_path.read_text()
        assert "CENSUS_API_KEY" in content
        assert "BLS_API_KEY" in content

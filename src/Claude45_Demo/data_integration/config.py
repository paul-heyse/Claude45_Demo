"""
Configuration management for the Aker Investment Platform.

Supports loading configuration from YAML files with environment variable
substitution. Manages API keys, base URLs, rate limits, cache TTLs, and
scoring weights.

Example config.yaml:
    data_sources:
      census:
        api_key: ${CENSUS_API_KEY}
        base_url: https://api.census.gov/data
        cache_ttl_days: 30
        rate_limit: 500
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manage configuration for data sources and scoring parameters.

    Loads configuration from YAML files with environment variable substitution.
    Validates required keys and provides accessors for common config values.
    """

    # Default configuration
    DEFAULT_CONFIG = {
        "data_sources": {
            "census": {
                "api_key": "${CENSUS_API_KEY}",
                "base_url": "https://api.census.gov/data",
                "cache_ttl_days": 30,
                "rate_limit": 500,
            },
            "bls": {
                "api_key": "${BLS_API_KEY}",
                "base_url": "https://api.bls.gov/publicAPI/v2/timeseries/data/",
                "cache_ttl_days": 7,
                "rate_limit": 500,
            },
            "bea": {
                "api_key": "${BEA_API_KEY}",
                "base_url": "https://apps.bea.gov/api/data",
                "cache_ttl_days": 30,
                "rate_limit": 100,
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

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to YAML config file. If None, uses default config.

        Raises:
            ConfigurationError: If config file is invalid or cannot be loaded
        """
        if config_path and not config_path.exists():
            raise ConfigurationError(f"Config file not found: {config_path}")

        if config_path:
            try:
                with open(config_path) as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_path}")
            except yaml.YAMLError as e:
                raise ConfigurationError(f"Invalid YAML in config file: {e}") from e
        else:
            self.config = self.DEFAULT_CONFIG.copy()
            logger.info("Using default configuration")

        # Substitute environment variables
        self._substitute_env_vars()

    def _substitute_env_vars(self) -> None:
        """
        Substitute ${VAR} patterns with environment variable values.

        This is done in-place on the config dictionary.
        """

        def substitute_value(value: Any) -> Any:
            """Recursively substitute environment variables in config values."""
            if isinstance(value, str):
                # Find all ${VAR} patterns
                pattern = r"\$\{([^}]+)\}"
                matches = re.findall(pattern, value)

                for var_name in matches:
                    env_value = os.environ.get(var_name)
                    if env_value is None:
                        # Don't raise here - we'll validate later when actually used
                        logger.debug(f"Environment variable {var_name} not set")
                        continue

                    value = value.replace(f"${{{var_name}}}", env_value)

                return value
            elif isinstance(value, dict):
                return {k: substitute_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [substitute_value(item) for item in value]
            else:
                return value

        self.config = substitute_value(self.config)

    def get_api_key(self, source: str) -> str:
        """
        Get API key for a data source.

        Args:
            source: Data source name (e.g., "census", "bls")

        Returns:
            API key string

        Raises:
            ConfigurationError: If API key is not configured or still contains ${VAR}
        """
        try:
            api_key: str = str(self.config["data_sources"][source]["api_key"])

            # Check if environment variable wasn't substituted
            if "${" in api_key:
                var_match = re.search(r"\$\{([^}]+)\}", api_key)
                var_name = var_match.group(1) if var_match else "unknown"
                raise ConfigurationError(
                    f"Environment variable {var_name} not set for {source} API key"
                )

            return api_key

        except KeyError as e:
            raise ConfigurationError(
                f"API key not configured for source: {source}"
            ) from e

    def get_masked_key(self, source: str) -> str:
        """
        Get masked API key for logging (shows only last 4 characters).

        Args:
            source: Data source name

        Returns:
            Masked key in format "...XXXX"
        """
        try:
            api_key = self.get_api_key(source)
            if len(api_key) <= 4:
                return "****"
            return f"...{api_key[-4:]}"
        except ConfigurationError:
            return "...NOT_SET"

    def validate_required_keys(self, sources: List[str]) -> None:
        """
        Validate that required API keys are configured.

        Args:
            sources: List of required data source names

        Raises:
            ConfigurationError: If any required keys are missing
        """
        missing = []
        for source in sources:
            try:
                self.get_api_key(source)
            except ConfigurationError:
                missing.append(source)

        if missing:
            raise ConfigurationError(
                f"Missing required API keys for: {', '.join(missing)}"
            )

        logger.info(f"Validated API keys for: {', '.join(sources)}")

    def get_cache_ttl(self, source: str) -> int:
        """
        Get cache TTL in days for a data source.

        Args:
            source: Data source name

        Returns:
            Cache TTL in days
        """
        try:
            return self.config["data_sources"][source]["cache_ttl_days"]
        except KeyError:
            logger.warning(
                f"No cache_ttl_days configured for {source}, using default 7"
            )
            return 7

    def validate_cache_ttl(self, source: str) -> None:
        """
        Validate and warn about unusual cache TTL values.

        Logs warnings if TTL is < 1 day (too short) or > 90 days (too long).

        Args:
            source: Data source name
        """
        ttl = self.get_cache_ttl(source)

        if ttl < 1:
            logger.warning(
                f"Cache TTL for {source} is unusually short ({ttl} days). "
                f"This may result in excessive API calls. Recommended minimum: 1 day."
            )
        elif ttl > 90:
            logger.warning(
                f"Cache TTL for {source} is unusually long ({ttl} days). "
                f"Data may become stale. Recommended maximum: 90 days."
            )

    def get_rate_limit(self, source: str) -> int:
        """
        Get rate limit for a data source.

        Args:
            source: Data source name

        Returns:
            Rate limit (requests per day)
        """
        try:
            return self.config["data_sources"][source]["rate_limit"]
        except KeyError:
            logger.warning(f"No rate_limit configured for {source}, using default 500")
            return 500

    def get_base_url(self, source: str) -> str:
        """
        Get base URL for a data source.

        Args:
            source: Data source name

        Returns:
            Base URL string

        Raises:
            ConfigurationError: If base URL is not configured
        """
        try:
            return self.config["data_sources"][source]["base_url"]
        except KeyError as e:
            raise ConfigurationError(
                f"Base URL not configured for source: {source}"
            ) from e

    def get_scoring_weights(self) -> Dict[str, float]:
        """
        Get scoring weights for the four pillars.

        Returns:
            Dictionary with keys: supply, jobs, urban, outdoor
        """
        try:
            return self.config["scoring"]["weights"]
        except KeyError:
            logger.warning("Scoring weights not configured, using defaults")
            return {"supply": 0.30, "jobs": 0.30, "urban": 0.20, "outdoor": 0.20}

    def get_risk_multiplier_range(self) -> Dict[str, float]:
        """
        Get risk multiplier range.

        Returns:
            Dictionary with keys: min, max
        """
        try:
            range_config = self.config["scoring"]["risk_multiplier_range"]
            return {k: float(v) for k, v in range_config.items()}
        except KeyError:
            logger.warning("Risk multiplier range not configured, using defaults")
            return {"min": 0.85, "max": 1.10}

    @staticmethod
    def generate_default_config(output_path: Path) -> None:
        """
        Generate a default configuration file.

        Args:
            output_path: Path where to write the config file
        """
        with open(output_path, "w") as f:
            yaml.dump(
                ConfigManager.DEFAULT_CONFIG,
                f,
                default_flow_style=False,
                sort_keys=False,
            )

        logger.info(f"Generated default config at {output_path}")

    @staticmethod
    def generate_env_template(output_path: Path) -> None:
        """
        Generate a .env template file with API key placeholders.

        Args:
            output_path: Path where to write the .env template
        """
        template = """# Aker Investment Platform - Environment Variables
# Copy this file to .env and fill in your API keys

# Census Bureau API Key
# Register at: https://api.census.gov/data/key_signup.html
CENSUS_API_KEY=your_census_api_key_here

# Bureau of Labor Statistics API Key
# Register at: https://www.bls.gov/developers/api_signature_v2.htm
BLS_API_KEY=your_bls_api_key_here

# Bureau of Economic Analysis API Key
# Register at: https://apps.bea.gov/API/signup/
BEA_API_KEY=your_bea_api_key_here

# Optional API keys (can be left empty)
EPA_API_KEY=
GOOGLE_PLACES_API_KEY=
"""

        with open(output_path, "w") as f:
            f.write(template)

        logger.info(f"Generated .env template at {output_path}")

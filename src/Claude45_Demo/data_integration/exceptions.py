"""
Custom exceptions for the Aker Investment Platform data integration layer.

All exceptions inherit from AkerPlatformError for easy catching.
"""


class AkerPlatformError(Exception):
    """Base exception for Aker Investment Platform."""

    pass


class DataSourceError(AkerPlatformError):
    """Error fetching or parsing data from external source."""

    pass


class ValidationError(AkerPlatformError):
    """Data validation failed."""

    pass


class DataValidationError(ValidationError):
    """Data validation failed (alias for compatibility)."""

    pass


class ScoringError(AkerPlatformError):
    """Error calculating scores."""

    pass


class RateLimitExceeded(DataSourceError):
    """API rate limit has been exceeded."""

    pass


class ConfigurationError(AkerPlatformError):
    """Configuration is missing or invalid."""

    pass


class CacheError(AkerPlatformError):
    """Error accessing or manipulating cache."""

    pass

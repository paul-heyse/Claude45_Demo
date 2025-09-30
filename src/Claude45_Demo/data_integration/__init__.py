"""
Data integration module for the Aker Investment Platform.

This module provides connectors for external data sources including:
- Census Bureau (ACS, Building Permits, Business Formation Statistics)
- Bureau of Labor Statistics (CES, LAUS, QCEW)
- Bureau of Economic Analysis (Regional GDP, Personal Income)
- OpenStreetMap (POI data via Overpass API)
- USGS (Elevation, terrain analysis)
- FEMA (Flood risk data)
- EPA (Air quality data)
- USFS (Wildfire risk data)

All connectors inherit from the abstract APIConnector base class.
"""

from .base import APIConnector
from .cache import CacheManager
from .exceptions import (
    AkerPlatformError,
    CacheError,
    ConfigurationError,
    DataSourceError,
    RateLimitExceeded,
    ScoringError,
    ValidationError,
)

__all__ = [
    "APIConnector",
    "AkerPlatformError",
    "DataSourceError",
    "ValidationError",
    "ScoringError",
    "RateLimitExceeded",
    "ConfigurationError",
    "CacheError",
    "CacheManager",
]

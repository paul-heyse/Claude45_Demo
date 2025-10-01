"""Tests for cache configuration system (Task 10.2)."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from Claude45_Demo.data_integration.cache_config import (
    CacheConfig,
    CompressionSettings,
    MemorySettings,
    MonitoringSettings,
    PrefetchSettings,
    SQLiteSettings,
)
from Claude45_Demo.data_integration.exceptions import ConfigurationError


@pytest.fixture()
def sample_config(tmp_path: Path) -> Path:
    """Create a temporary cache configuration file."""

    config_path = tmp_path / "cache.yaml"
    config_path.write_text(
        """
cache:
  memory:
    enable: true
    size_mb: 128
  sqlite:
    enable: true
    path: ${CACHE_DB_PATH}
  compression:
    enable: true
    threshold_kb: 8
    level: 5
  defaults:
    ttl: 14d
  ttl_policies:
    census_acs: 365d
    bls_ces: 7d
    epa_aqs: 1h
    custom_metric: PT30M
"""
    )
    return config_path


def test_cache_config_loads_ttls(
    sample_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CacheConfig should parse TTL policies into timedeltas."""

    monkeypatch.setenv("CACHE_DB_PATH", ".cache/test.db")
    config = CacheConfig(sample_config)

    assert config.get_ttl("census_acs") == timedelta(days=365)
    assert config.get_ttl("bls_ces") == timedelta(days=7)
    assert config.get_ttl("epa_aqs") == timedelta(hours=1)
    assert config.get_ttl("custom_metric") == timedelta(minutes=30)

    # TTL fallback to default (14 days)
    assert config.get_ttl("unknown_source") == timedelta(days=14)


def test_cache_config_returns_settings(
    sample_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify accessors return dataclasses with expected values."""

    monkeypatch.setenv("CACHE_DB_PATH", ".cache/custom.db")
    config = CacheConfig(sample_config)

    memory = config.memory
    sqlite = config.sqlite
    compression = config.compression

    assert isinstance(memory, MemorySettings)
    assert isinstance(sqlite, SQLiteSettings)
    assert isinstance(compression, CompressionSettings)
    assert memory.size_mb == 128
    assert sqlite.path == Path(".cache/custom.db")
    assert compression.threshold_kb == 8
    assert compression.level == 5

    prefetch = config.prefetch
    monitoring = config.monitoring
    assert isinstance(prefetch, PrefetchSettings)
    assert isinstance(monitoring, MonitoringSettings)


def test_cache_config_invalid_ttl_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Invalid TTL formats should raise configuration errors."""

    bad_config = tmp_path / "bad.yaml"
    bad_config.write_text(
        """
cache:
  memory:
    enable: true
    size_mb: 128
  sqlite:
    enable: true
    path: .cache/test.db
  ttl_policies:
    census_acs: invalid
"""
    )

    with pytest.raises(ConfigurationError):
        CacheConfig(bad_config)


def test_cache_config_rejects_negative_size(tmp_path: Path) -> None:
    """Negative memory sizes should be rejected."""

    bad_config = tmp_path / "bad_mem.yaml"
    bad_config.write_text(
        """
cache:
  memory:
    enable: true
    size_mb: -1
  sqlite:
    enable: true
    path: .cache/test.db
  ttl_policies:
    census_acs: 365d
"""
    )

    with pytest.raises(ConfigurationError):
        CacheConfig(bad_config)


def test_cache_config_from_defaults(tmp_path: Path) -> None:
    """When no file is provided the defaults should be used."""

    config = CacheConfig(config_path=None, config_data=None)
    assert isinstance(config.memory, MemorySettings)
    assert config.get_ttl("census_acs") == timedelta(days=365)
    assert config.sqlite.path == Path(".cache/aker_platform.db")


def test_cache_config_all_ttls(
    sample_config: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """all_ttls should return mapping for all configured policies."""

    monkeypatch.setenv("CACHE_DB_PATH", ".cache/test.db")
    config = CacheConfig(sample_config)

    ttls = config.all_ttls()
    assert "census_acs" in ttls
    assert ttls["census_acs"] == timedelta(days=365)
    assert len(ttls) >= 3

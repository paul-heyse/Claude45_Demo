"""Cache configuration loader for multi-tier caching system (Module 10 Task 10.2).

This module centralizes cache configuration, including per-source TTL policies,
cache layer settings, compression, and prefetch/monitoring controls. Settings
are loaded from a YAML configuration file with environment variable
substitution and schema validation.

Example usage:
    >>> from pathlib import Path
    >>> config = CacheConfig(Path("config/cache_config.yaml"))
    >>> ttl = config.get_ttl("census_acs")
    >>> memory_settings = config.memory
    >>> memory_settings.enabled
    True
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import yaml

from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


_TTL_PATTERN = re.compile(r"^(?P<value>\d+(?:\.\d+)?)(?P<unit>[smhdw])$", re.IGNORECASE)


@dataclass(frozen=True)
class MemorySettings:
    """Configuration for the in-memory cache layer."""

    enabled: bool
    size_mb: int


@dataclass(frozen=True)
class SQLiteSettings:
    """Configuration for the SQLite cache layer."""

    enabled: bool
    path: Path


@dataclass(frozen=True)
class CompressionSettings:
    """Compression configuration for cached payloads."""

    enabled: bool
    threshold_kb: int
    level: int


@dataclass(frozen=True)
class PrefetchSettings:
    """Prefetch and cache warming settings."""

    enabled: bool
    nearby_radius_miles: int
    max_parallel_requests: int


@dataclass(frozen=True)
class MonitoringSettings:
    """Monitoring and alerting thresholds for cache behaviour."""

    log_cache_hits: bool
    alert_on_low_hit_rate: float
    alert_on_high_latency_ms: int


class CacheConfig:
    """Load and validate cache configuration from YAML or defaults."""

    DEFAULT_CONFIG: Dict[str, Any] = {
        "cache": {
            "memory": {
                "enable": True,
                "size_mb": 256,
            },
            "sqlite": {
                "enable": True,
                "path": ".cache/aker_platform.db",
            },
            "compression": {
                "enable": True,
                "threshold_kb": 10,
                "level": 6,
            },
            "prefetch": {
                "enabled": True,
                "nearby_radius_miles": 50,
                "max_parallel_requests": 5,
            },
            "monitoring": {
                "log_cache_hits": True,
                "alert_on_low_hit_rate": 0.5,
                "alert_on_high_latency_ms": 20,
            },
            "defaults": {
                "ttl": "30d",
            },
            "ttl_policies": {
                "census_acs": "365d",
                "census_permits": "30d",
                "bls_ces": "7d",
                "irs_migration": "30d",
                "epa_aqs": "1h",
            },
        }
    }

    def __init__(
        self,
        config_path: Optional[Path] = None,
        *,
        config_data: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Load cache configuration.

        Args:
            config_path: Optional path to YAML configuration file. If not provided,
                defaults to ``config/cache_config.yaml`` when present.
            config_data: Optional dictionary to use instead of reading from disk.

        Raises:
            ConfigurationError: If configuration is invalid or file cannot be read.
        """

        if config_data is not None and config_path is not None:
            raise ConfigurationError(
                "Provide either config_data or config_path, not both"
            )

        if config_data is not None:
            raw_config = dict(config_data)
        else:
            resolved_path = self._resolve_config_path(config_path)
            if resolved_path and resolved_path.exists():
                try:
                    with resolved_path.open("r", encoding="utf-8") as fh:
                        raw_config = yaml.safe_load(fh) or {}
                    logger.info("Loaded cache config from %s", resolved_path)
                except yaml.YAMLError as exc:
                    raise ConfigurationError(
                        f"Invalid YAML in cache config file: {exc}"
                    ) from exc
            else:
                raw_config = {}
                if resolved_path:
                    logger.warning(
                        "Cache config path %s not found. Falling back to defaults.",
                        resolved_path,
                    )
                else:
                    logger.info("Using default cache configuration")

        self._config = self._merge_with_defaults(raw_config)
        self._substitute_env_vars()
        self._validate_schema()
        self._ttl_cache: Dict[str, timedelta] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def memory(self) -> MemorySettings:
        """Return memory cache settings."""

        memory_cfg = self._config["cache"]["memory"]
        return MemorySettings(
            enabled=bool(memory_cfg.get("enable", True)),
            size_mb=int(memory_cfg.get("size_mb", 256)),
        )

    @property
    def sqlite(self) -> SQLiteSettings:
        """Return SQLite cache settings."""

        sqlite_cfg = self._config["cache"]["sqlite"]
        return SQLiteSettings(
            enabled=bool(sqlite_cfg.get("enable", True)),
            path=Path(sqlite_cfg.get("path", ".cache/aker_platform.db")),
        )

    @property
    def compression(self) -> CompressionSettings:
        """Return compression settings."""

        compression_cfg = self._config["cache"].get("compression", {})
        enabled = bool(compression_cfg.get("enable", False))
        threshold = int(compression_cfg.get("threshold_kb", 10))
        level = int(compression_cfg.get("level", 6))
        return CompressionSettings(enabled=enabled, threshold_kb=threshold, level=level)

    @property
    def prefetch(self) -> PrefetchSettings:
        """Return cache prefetch settings."""

        cfg = self._config["cache"].get("prefetch", {})
        return PrefetchSettings(
            enabled=bool(cfg.get("enabled", True)),
            nearby_radius_miles=int(cfg.get("nearby_radius_miles", 50)),
            max_parallel_requests=int(cfg.get("max_parallel_requests", 5)),
        )

    @property
    def monitoring(self) -> MonitoringSettings:
        """Return monitoring thresholds for cache metrics."""

        cfg = self._config["cache"].get("monitoring", {})
        return MonitoringSettings(
            log_cache_hits=bool(cfg.get("log_cache_hits", True)),
            alert_on_low_hit_rate=float(cfg.get("alert_on_low_hit_rate", 0.5)),
            alert_on_high_latency_ms=int(cfg.get("alert_on_high_latency_ms", 20)),
        )

    def get_ttl(self, source: str) -> timedelta:
        """Return TTL for a data source, falling back to default.

        Args:
            source: Data source name (case-insensitive)

        Returns:
            TTL as :class:`datetime.timedelta`

        Raises:
            ConfigurationError: If TTL value cannot be parsed
        """

        key = source.lower()
        if key in self._ttl_cache:
            return self._ttl_cache[key]

        ttl_policies: Mapping[str, Any] = self._config["cache"].get("ttl_policies", {})
        value = ttl_policies.get(key)
        if value is None:
            default = self._config["cache"].get("defaults", {}).get("ttl", "30d")
            ttl = self._parse_ttl(default, label=f"default TTL for {key}")
        else:
            ttl = self._parse_ttl(value, label=f"ttl for {key}")

        self._ttl_cache[key] = ttl
        return ttl

    def all_ttls(self) -> Dict[str, timedelta]:
        """Return mapping of all configured TTL policies."""

        ttls: Dict[str, timedelta] = {}
        policies = self._config["cache"].get("ttl_policies", {})
        for source in policies.keys():
            ttls[source] = self.get_ttl(source)
        return ttls

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_config_path(self, provided: Optional[Path]) -> Optional[Path]:
        if provided is not None:
            return provided
        default_path = Path("config/cache_config.yaml")
        return default_path if default_path.exists() else None

    def _merge_with_defaults(self, config: Mapping[str, Any]) -> Dict[str, Any]:
        """Merge provided config with defaults recursively."""

        def deep_merge(
            base: Mapping[str, Any], override: Mapping[str, Any]
        ) -> Dict[str, Any]:
            merged: Dict[str, Any] = dict(base)
            for key, value in override.items():
                if isinstance(value, Mapping) and isinstance(base.get(key), Mapping):
                    merged[key] = deep_merge(base[key], value)
                else:
                    merged[key] = value
            return merged

        return deep_merge(self.DEFAULT_CONFIG, config or {})

    def _substitute_env_vars(self) -> None:
        """Recursively substitute ${VAR} with environment values."""

        pattern = re.compile(r"\$\{([^}]+)\}")

        def substitute(value: Any) -> Any:
            if isinstance(value, str):
                matches = pattern.findall(value)
                for var_name in matches:
                    env_value = os.environ.get(var_name)
                    if env_value is None:
                        logger.debug("Environment variable %s not set", var_name)
                        continue
                    value = value.replace(f"${{{var_name}}}", env_value)
                return value
            if isinstance(value, Mapping):
                return {k: substitute(v) for k, v in value.items()}
            if isinstance(value, list):
                return [substitute(item) for item in value]
            return value

        self._config = substitute(self._config)

    def _validate_schema(self) -> None:
        """Validate expected configuration structure."""

        if "cache" not in self._config:
            raise ConfigurationError("Cache configuration missing 'cache' section")

        cache_cfg = self._config["cache"]
        for section in ("memory", "sqlite", "ttl_policies"):
            if section not in cache_cfg:
                raise ConfigurationError(
                    f"Cache configuration missing '{section}' section"
                )

        memory_cfg = cache_cfg["memory"]
        if memory_cfg.get("size_mb", 0) <= 0:
            raise ConfigurationError("cache.memory.size_mb must be > 0")

        sqlite_cfg = cache_cfg["sqlite"]
        if not sqlite_cfg.get("path"):
            raise ConfigurationError("cache.sqlite.path must be provided")

        compression_cfg = cache_cfg.get("compression", {})
        if compression_cfg:
            level = compression_cfg.get("level", 6)
            if not (0 <= int(level) <= 9):
                raise ConfigurationError(
                    "cache.compression.level must be between 0 and 9"
                )
            threshold = compression_cfg.get("threshold_kb", 10)
            if int(threshold) < 0:
                raise ConfigurationError("cache.compression.threshold_kb must be >= 0")

        ttl_policies = cache_cfg.get("ttl_policies", {})
        if not isinstance(ttl_policies, Mapping):
            raise ConfigurationError("cache.ttl_policies must be a mapping")
        for source, value in ttl_policies.items():
            try:
                self._parse_ttl(value, label=f"ttl for {source}")
            except ConfigurationError as exc:
                raise ConfigurationError(
                    f"Invalid TTL for cache source '{source}': {exc}"
                ) from exc

    def _parse_ttl(self, value: Any, *, label: str) -> timedelta:
        """Parse TTL value into timedelta."""

        if isinstance(value, timedelta):
            return value

        if isinstance(value, (int, float)):
            if value < 0:
                raise ConfigurationError(f"{label} must be non-negative")
            return timedelta(days=float(value))

        if isinstance(value, str):
            normalized = value.strip()
            if not normalized:
                raise ConfigurationError(f"{label} cannot be empty")

            match = _TTL_PATTERN.match(normalized)
            if match:
                amount = float(match.group("value"))
                unit = match.group("unit").lower()
                if unit == "s":
                    return timedelta(seconds=amount)
                if unit == "m":
                    return timedelta(minutes=amount)
                if unit == "h":
                    return timedelta(hours=amount)
                if unit == "d":
                    return timedelta(days=amount)
                if unit == "w":
                    return timedelta(weeks=amount)

            # Support ISO 8601-like values (e.g., PT1H) if provided
            try:
                return self._parse_iso_duration(normalized)
            except ConfigurationError:
                pass

        raise ConfigurationError(f"Invalid TTL value '{value}' for {label}")

    def _parse_iso_duration(self, value: str) -> timedelta:
        """Parse minimal subset of ISO 8601 durations (PnDTnHnMnS)."""

        iso_pattern = re.compile(
            r"P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?",
            re.IGNORECASE,
        )
        match = iso_pattern.fullmatch(value)
        if not match:
            raise ConfigurationError(f"Unsupported TTL format '{value}'")

        days = int(match.group("days") or 0)
        hours = int(match.group("hours") or 0)
        minutes = int(match.group("minutes") or 0)
        seconds = int(match.group("seconds") or 0)
        if days == hours == minutes == seconds == 0:
            raise ConfigurationError(f"TTL duration '{value}' cannot be zero")
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


__all__ = [
    "CacheConfig",
    "MemorySettings",
    "SQLiteSettings",
    "CompressionSettings",
    "PrefetchSettings",
    "MonitoringSettings",
]

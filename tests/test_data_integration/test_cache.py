"""Tests for the SQLite-backed caching layer.

Scenarios map to Requirement: Response Caching with TTL in
openspec/changes/add-aker-investment-platform/specs/data-integration/spec.md.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict


def _cache_manager(tmp_path: Path):
    """Lazy import to align with TDD (fails before implementation exists)."""
    from Claude45_Demo.data_integration.cache import CacheManager

    return CacheManager(db_path=tmp_path / "cache.db")


class TestCacheHitScenario:
    """Scenario: Cache hit returns cached response within TTL."""

    def test_cache_hit_returns_cached_value(self, tmp_path, caplog):
        cache = _cache_manager(tmp_path)
        payload: Dict[str, Any] = {"result": "cached", "count": 42}
        cache.set("demo-key", payload, ttl=timedelta(minutes=5))

        with caplog.at_level("INFO"):
            cached = cache.get("demo-key")

        assert cached == payload
        assert any("cache hit" in record.message.lower() for record in caplog.records)


class TestCacheMissScenario:
    """Scenario: Cache miss fetches fresh data when TTL expired."""

    def test_cache_miss_after_ttl_expiry_returns_none(self, tmp_path, monkeypatch):
        cache = _cache_manager(tmp_path)

        base_time = datetime(2025, 1, 1, 12, 0, 0)
        monkeypatch.setattr(cache, "_current_time", lambda: base_time)
        cache.set("expiring-key", {"value": 1}, ttl=timedelta(minutes=1))

        future_time = base_time + timedelta(minutes=2)
        monkeypatch.setattr(cache, "_current_time", lambda: future_time)

        assert cache.get("expiring-key") is None

        cache.clear_expired()
        with cache._connect() as conn:  # type: ignore[attr-defined]
            cursor = conn.execute(
                "SELECT COUNT(*) FROM cache WHERE key = ?",
                ("expiring-key",),
            )
            assert cursor.fetchone()[0] == 0


class TestCacheBypassScenario:
    """Scenario: Cache invalidation when user requests fresh data."""

    def test_cache_bypass_returns_none_but_preserves_entry(self, tmp_path):
        cache = _cache_manager(tmp_path)
        cache.set("bypass-key", {"value": "original"}, ttl=timedelta(hours=1))

        bypassed = cache.get("bypass-key", bypass_cache=True)
        assert bypassed is None

        assert cache.get("bypass-key") == {"value": "original"}

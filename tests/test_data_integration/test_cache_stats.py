"""Tests for cache statistics and monitoring (Task 10.4)."""

from __future__ import annotations

import time
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest

from Claude45_Demo.data_integration.cache_stats import (
    CacheStatistics,
    LatencyMetrics,
    TierStatistics,
)
from Claude45_Demo.data_integration.exceptions import CacheError


@pytest.fixture
def cache_stats() -> CacheStatistics:
    """Provide a CacheStatistics instance."""
    return CacheStatistics()


class TestCacheStatistics:
    """Test suite for CacheStatistics."""

    def test_record_cache_hit(self, cache_stats: CacheStatistics) -> None:
        """Test recording cache hits."""
        cache_stats.record_hit(source="census", tier="memory", latency_ms=0.5)

        stats = cache_stats.get_summary()
        assert stats["total_hits"] == 1
        assert stats["total_misses"] == 0
        assert stats["hit_rate"] == 1.0

    def test_record_cache_miss(self, cache_stats: CacheStatistics) -> None:
        """Test recording cache misses."""
        cache_stats.record_miss(source="census", tier="memory")

        stats = cache_stats.get_summary()
        assert stats["total_hits"] == 0
        assert stats["total_misses"] == 1
        assert stats["hit_rate"] == 0.0

    def test_hit_rate_calculation(self, cache_stats: CacheStatistics) -> None:
        """Test hit rate calculation with mixed results."""
        # Record 7 hits and 3 misses
        for _ in range(7):
            cache_stats.record_hit(source="census", tier="memory", latency_ms=0.5)
        for _ in range(3):
            cache_stats.record_miss(source="census", tier="memory")

        stats = cache_stats.get_summary()
        assert stats["total_hits"] == 7
        assert stats["total_misses"] == 3
        assert stats["hit_rate"] == pytest.approx(0.7, abs=0.01)

    def test_tier_specific_stats(self, cache_stats: CacheStatistics) -> None:
        """Test statistics by cache tier."""
        cache_stats.record_hit(source="census", tier="memory", latency_ms=0.3)
        cache_stats.record_hit(source="census", tier="sqlite", latency_ms=5.0)
        cache_stats.record_miss(source="census", tier="memory")

        stats = cache_stats.get_tier_stats()
        assert "memory" in stats
        assert "sqlite" in stats
        assert stats["memory"]["hits"] == 1
        assert stats["memory"]["misses"] == 1
        assert stats["sqlite"]["hits"] == 1
        assert stats["sqlite"]["misses"] == 0

    def test_source_specific_stats(self, cache_stats: CacheStatistics) -> None:
        """Test statistics by data source."""
        cache_stats.record_hit(source="census", tier="memory", latency_ms=0.5)
        cache_stats.record_hit(source="bls", tier="memory", latency_ms=0.4)
        cache_stats.record_miss(source="census", tier="memory")

        stats = cache_stats.get_source_stats()
        assert "census" in stats
        assert "bls" in stats
        assert stats["census"]["hits"] == 1
        assert stats["census"]["misses"] == 1
        assert stats["census"]["hit_rate"] == pytest.approx(0.5, abs=0.01)
        assert stats["bls"]["hit_rate"] == 1.0

    def test_latency_metrics(self, cache_stats: CacheStatistics) -> None:
        """Test latency percentile calculations."""
        # Record various latencies
        latencies = [0.5, 1.0, 2.0, 5.0, 10.0, 15.0, 20.0, 50.0, 100.0, 200.0]
        for latency in latencies:
            cache_stats.record_hit(source="census", tier="memory", latency_ms=latency)

        metrics = cache_stats.get_latency_metrics()
        assert metrics["p50"] > 0
        assert metrics["p95"] > metrics["p50"]
        assert metrics["p99"] > metrics["p95"]
        assert metrics["avg"] > 0

    def test_storage_utilization_tracking(self, cache_stats: CacheStatistics) -> None:
        """Test storage size tracking."""
        cache_stats.update_storage_size(tier="memory", size_mb=128.5)
        cache_stats.update_storage_size(tier="sqlite", size_mb=512.3)

        stats = cache_stats.get_storage_stats()
        assert stats["memory"]["size_mb"] == pytest.approx(128.5, abs=0.1)
        assert stats["sqlite"]["size_mb"] == pytest.approx(512.3, abs=0.1)
        assert stats["total_size_mb"] == pytest.approx(640.8, abs=0.1)

    def test_reset_statistics(self, cache_stats: CacheStatistics) -> None:
        """Test resetting statistics."""
        # Record some activity
        cache_stats.record_hit(source="census", tier="memory", latency_ms=0.5)
        cache_stats.record_miss(source="census", tier="memory")

        # Reset
        cache_stats.reset()

        stats = cache_stats.get_summary()
        assert stats["total_hits"] == 0
        assert stats["total_misses"] == 0

    def test_export_to_json(self, cache_stats: CacheStatistics, tmp_path: Path) -> None:
        """Test exporting statistics to JSON."""
        # Record some activity
        cache_stats.record_hit(source="census", tier="memory", latency_ms=0.5)
        cache_stats.record_miss(source="bls", tier="sqlite")

        output_path = tmp_path / "cache_stats.json"
        cache_stats.export_json(output_path)

        assert output_path.exists()
        # Verify JSON structure
        import json

        with open(output_path) as f:
            data = json.load(f)
        assert "summary" in data
        assert "by_tier" in data
        assert "by_source" in data


class TestLatencyMetrics:
    """Test latency metric calculations."""

    def test_empty_latency_metrics(self) -> None:
        """Test metrics with no data."""
        metrics = LatencyMetrics([])
        stats = metrics.calculate()

        assert stats["p50"] == 0.0
        assert stats["p95"] == 0.0
        assert stats["p99"] == 0.0
        assert stats["avg"] == 0.0

    def test_single_value_latency(self) -> None:
        """Test metrics with single value."""
        metrics = LatencyMetrics([5.0])
        stats = metrics.calculate()

        assert stats["p50"] == 5.0
        assert stats["p95"] == 5.0
        assert stats["p99"] == 5.0
        assert stats["avg"] == 5.0

    def test_percentile_calculation(self) -> None:
        """Test percentile calculations."""
        # Create dataset with known percentiles
        values = list(range(1, 101))  # 1 to 100
        metrics = LatencyMetrics([float(v) for v in values])
        stats = metrics.calculate()

        # For 1-100, p50 should be ~50, p95 should be ~95, p99 should be ~99
        assert 45 <= stats["p50"] <= 55
        assert 90 <= stats["p95"] <= 100
        assert 95 <= stats["p99"] <= 100
        assert stats["avg"] == pytest.approx(50.5, abs=1.0)


class TestTierStatistics:
    """Test tier-specific statistics."""

    def test_tier_hit_rate(self) -> None:
        """Test tier-specific hit rate."""
        tier = TierStatistics(tier="memory")
        tier.record_hit(latency_ms=0.5)
        tier.record_hit(latency_ms=0.6)
        tier.record_miss()

        stats = tier.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == pytest.approx(0.667, abs=0.01)

    def test_tier_latency_tracking(self) -> None:
        """Test latency tracking per tier."""
        tier = TierStatistics(tier="memory")
        tier.record_hit(latency_ms=0.5)
        tier.record_hit(latency_ms=1.0)
        tier.record_hit(latency_ms=1.5)

        stats = tier.get_stats()
        assert stats["avg_latency_ms"] == pytest.approx(1.0, abs=0.1)


class TestStatisticsIntegration:
    """Integration tests with cache components."""

    def test_statistics_with_memory_cache(self, tmp_path: Path) -> None:
        """Test statistics integration with MemoryCache."""
        from Claude45_Demo.data_integration import MemoryCache

        cache = MemoryCache(max_size_mb=10)
        stats = CacheStatistics()

        # Simulate cache operations
        cache.set("key1", {"data": "value1"}, ttl=timedelta(hours=1))

        # Record stats
        result = cache.get("key1")
        if result is not None:
            stats.record_hit(source="test", tier="memory", latency_ms=0.5)
        else:
            stats.record_miss(source="test", tier="memory")

        result2 = cache.get("key_missing")
        if result2 is None:
            stats.record_miss(source="test", tier="memory")

        summary = stats.get_summary()
        assert summary["total_hits"] >= 1
        assert summary["total_misses"] >= 1

    def test_statistics_monitoring_alerts(self, cache_stats: CacheStatistics) -> None:
        """Test alerting on low hit rate."""
        # Record low hit rate scenario
        for _ in range(2):
            cache_stats.record_hit(source="census", tier="memory", latency_ms=0.5)
        for _ in range(8):
            cache_stats.record_miss(source="census", tier="memory")

        # Check if hit rate is below threshold
        stats = cache_stats.get_summary()
        assert stats["hit_rate"] < 0.5  # Alert threshold

        # Verify alert would be triggered
        alerts = cache_stats.check_alerts(min_hit_rate=0.5, max_latency_ms=10.0)
        assert "low_hit_rate" in alerts

    def test_statistics_high_latency_alert(self, cache_stats: CacheStatistics) -> None:
        """Test alerting on high latency."""
        # Record high latency
        for _ in range(5):
            cache_stats.record_hit(source="census", tier="sqlite", latency_ms=50.0)

        alerts = cache_stats.check_alerts(min_hit_rate=0.5, max_latency_ms=20.0)
        assert "high_latency" in alerts


class TestStatisticsPerformance:
    """Test that statistics tracking doesn't impact performance."""

    def test_statistics_overhead(self, cache_stats: CacheStatistics) -> None:
        """Test that recording statistics is fast."""
        # Record 10,000 operations
        start = time.time()
        for i in range(10000):
            cache_stats.record_hit(source="test", tier="memory", latency_ms=0.5)
        duration = time.time() - start

        # Should complete in under 1 second
        assert duration < 1.0

    def test_concurrent_statistics_recording(
        self, cache_stats: CacheStatistics
    ) -> None:
        """Test thread-safe statistics recording."""
        from concurrent.futures import ThreadPoolExecutor

        def record_stats() -> None:
            for _ in range(100):
                cache_stats.record_hit(source="test", tier="memory", latency_ms=0.5)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(record_stats) for _ in range(5)]
            for future in futures:
                future.result()

        stats = cache_stats.get_summary()
        assert stats["total_hits"] == 500  # 5 threads * 100 operations

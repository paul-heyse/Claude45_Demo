"""Cache statistics and monitoring (Module 10 Task 10.4).

This module provides comprehensive cache performance tracking including hit/miss
rates, latency metrics, storage utilization, and alerting capabilities.

Example usage:
    >>> from Claude45_Demo.data_integration import CacheStatistics
    >>> stats = CacheStatistics()
    >>> stats.record_hit(source="census", tier="memory", latency_ms=0.5)
    >>> summary = stats.get_summary()
    >>> print(f"Hit rate: {summary['hit_rate']:.2%}")
"""

from __future__ import annotations

import json
import logging
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TierStatistics:
    """Statistics for a single cache tier."""

    tier: str
    hits: int = 0
    misses: int = 0
    latencies: list[float] = field(default_factory=list)
    size_mb: float = 0.0

    def record_hit(self, latency_ms: float) -> None:
        """Record a cache hit with latency."""
        self.hits += 1
        self.latencies.append(latency_ms)

    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1

    def get_stats(self) -> dict[str, Any]:
        """Return tier statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0

        avg_latency = statistics.mean(self.latencies) if self.latencies else 0.0

        return {
            "tier": self.tier,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "avg_latency_ms": avg_latency,
            "size_mb": self.size_mb,
        }


@dataclass
class SourceStatistics:
    """Statistics for a single data source."""

    source: str
    hits: int = 0
    misses: int = 0

    def get_stats(self) -> dict[str, Any]:
        """Return source statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0

        return {
            "source": self.source,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }


class LatencyMetrics:
    """Calculate latency percentiles."""

    def __init__(self, latencies: list[float]) -> None:
        """Initialize with latency measurements."""
        self.latencies = sorted(latencies)

    def calculate(self) -> dict[str, float]:
        """Calculate latency metrics."""
        if not self.latencies:
            return {
                "p50": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "avg": 0.0,
                "min": 0.0,
                "max": 0.0,
            }

        return {
            "p50": self._percentile(50),
            "p95": self._percentile(95),
            "p99": self._percentile(99),
            "avg": statistics.mean(self.latencies),
            "min": min(self.latencies),
            "max": max(self.latencies),
        }

    def _percentile(self, p: float) -> float:
        """Calculate percentile."""
        if not self.latencies:
            return 0.0

        k = (len(self.latencies) - 1) * (p / 100)
        f = int(k)
        c = f + 1

        if c >= len(self.latencies):
            return self.latencies[-1]

        d0 = self.latencies[f]
        d1 = self.latencies[c]
        return d0 + (d1 - d0) * (k - f)


class CacheStatistics:
    """Comprehensive cache statistics tracking and monitoring."""

    def __init__(self) -> None:
        """Initialize statistics tracker."""
        self._lock = RLock()
        self._tier_stats: dict[str, TierStatistics] = {}
        self._source_stats: dict[str, SourceStatistics] = {}
        self._all_latencies: list[float] = []
        self._start_time = time.time()

    def record_hit(self, source: str, tier: str, latency_ms: float) -> None:
        """Record a cache hit.

        Args:
            source: Data source name (e.g., "census")
            tier: Cache tier (e.g., "memory", "sqlite")
            latency_ms: Latency in milliseconds
        """
        with self._lock:
            # Update tier stats
            if tier not in self._tier_stats:
                self._tier_stats[tier] = TierStatistics(tier=tier)
            self._tier_stats[tier].record_hit(latency_ms)

            # Update source stats
            if source not in self._source_stats:
                self._source_stats[source] = SourceStatistics(source=source)
            self._source_stats[source].hits += 1

            # Track global latencies
            self._all_latencies.append(latency_ms)

    def record_miss(self, source: str, tier: str) -> None:
        """Record a cache miss.

        Args:
            source: Data source name
            tier: Cache tier
        """
        with self._lock:
            # Update tier stats
            if tier not in self._tier_stats:
                self._tier_stats[tier] = TierStatistics(tier=tier)
            self._tier_stats[tier].record_miss()

            # Update source stats
            if source not in self._source_stats:
                self._source_stats[source] = SourceStatistics(source=source)
            self._source_stats[source].misses += 1

    def update_storage_size(self, tier: str, size_mb: float) -> None:
        """Update storage size for a tier.

        Args:
            tier: Cache tier
            size_mb: Storage size in megabytes
        """
        with self._lock:
            if tier not in self._tier_stats:
                self._tier_stats[tier] = TierStatistics(tier=tier)
            self._tier_stats[tier].size_mb = size_mb

    def get_summary(self) -> dict[str, Any]:
        """Get overall cache statistics summary."""
        with self._lock:
            total_hits = sum(t.hits for t in self._tier_stats.values())
            total_misses = sum(t.misses for t in self._tier_stats.values())
            total_requests = total_hits + total_misses
            hit_rate = total_hits / total_requests if total_requests > 0 else 0.0

            uptime_seconds = time.time() - self._start_time

            return {
                "total_hits": total_hits,
                "total_misses": total_misses,
                "total_requests": total_requests,
                "hit_rate": hit_rate,
                "uptime_seconds": uptime_seconds,
            }

    def get_tier_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics by cache tier."""
        with self._lock:
            return {tier: stats.get_stats() for tier, stats in self._tier_stats.items()}

    def get_source_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics by data source."""
        with self._lock:
            return {
                source: stats.get_stats()
                for source, stats in self._source_stats.items()
            }

    def get_latency_metrics(self) -> dict[str, float]:
        """Get latency percentiles and averages."""
        with self._lock:
            metrics = LatencyMetrics(self._all_latencies)
            return metrics.calculate()

    def get_storage_stats(self) -> dict[str, Any]:
        """Get storage utilization by tier."""
        with self._lock:
            tier_sizes = {
                tier: {"size_mb": stats.size_mb}
                for tier, stats in self._tier_stats.items()
            }
            total_size = sum(s["size_mb"] for s in tier_sizes.values())

            return {
                **tier_sizes,
                "total_size_mb": total_size,
            }

    def check_alerts(
        self, min_hit_rate: float = 0.5, max_latency_ms: float = 20.0
    ) -> list[str]:
        """Check for alert conditions.

        Args:
            min_hit_rate: Minimum acceptable hit rate
            max_latency_ms: Maximum acceptable p95 latency

        Returns:
            List of alert condition names
        """
        alerts = []

        # Check hit rate
        summary = self.get_summary()
        if summary["hit_rate"] < min_hit_rate:
            alerts.append("low_hit_rate")
            logger.warning(
                f"Cache hit rate {summary['hit_rate']:.2%} below threshold {min_hit_rate:.2%}"
            )

        # Check latency
        latency = self.get_latency_metrics()
        if latency["p95"] > max_latency_ms:
            alerts.append("high_latency")
            logger.warning(
                f"Cache p95 latency {latency['p95']:.1f}ms above threshold {max_latency_ms}ms"
            )

        return alerts

    def reset(self) -> None:
        """Reset all statistics."""
        with self._lock:
            self._tier_stats.clear()
            self._source_stats.clear()
            self._all_latencies.clear()
            self._start_time = time.time()
            logger.info("Cache statistics reset")

    def export_json(self, output_path: Path) -> None:
        """Export statistics to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        with self._lock:
            data = {
                "timestamp": time.time(),
                "summary": self.get_summary(),
                "by_tier": self.get_tier_stats(),
                "by_source": self.get_source_stats(),
                "latency": self.get_latency_metrics(),
                "storage": self.get_storage_stats(),
            }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Cache statistics exported to {output_path}")

    def get_full_report(self) -> dict[str, Any]:
        """Get complete statistics report."""
        with self._lock:
            return {
                "summary": self.get_summary(),
                "by_tier": self.get_tier_stats(),
                "by_source": self.get_source_stats(),
                "latency": self.get_latency_metrics(),
                "storage": self.get_storage_stats(),
            }


__all__ = ["CacheStatistics", "TierStatistics", "SourceStatistics", "LatencyMetrics"]

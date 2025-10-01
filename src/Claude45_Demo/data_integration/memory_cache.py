"""In-memory LRU cache layer for hot data access.

Implements Task 10.1: In-Memory LRU Cache Layer

Provides a fast in-memory cache tier that sits in front of SQLite, offering
sub-millisecond access times for frequently accessed data. Uses LRU eviction
policy with configurable size limits and TTL support.
"""

from __future__ import annotations

import logging
import sys
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cached value with metadata."""

    value: Any
    created_at: datetime
    expires_at: datetime
    size_bytes: int
    access_count: int = 0
    last_accessed: datetime | None = None

    def is_expired(self, now: datetime | None = None) -> bool:
        """Check if entry has expired."""
        if now is None:
            now = datetime.now(timezone.utc)
        return now >= self.expires_at

    def record_access(self) -> None:
        """Record access for statistics."""
        self.access_count += 1
        self.last_accessed = datetime.now(timezone.utc)


class MemoryCache:
    """Thread-safe in-memory LRU cache with size-based eviction.

    Provides sub-millisecond access to cached data with automatic LRU eviction
    when memory limits are reached. Thread-safe for concurrent read/write access.

    Args:
        max_size_mb: Maximum cache size in megabytes (default 256MB)
        enable_stats: Track hit/miss statistics (default True)

    Example:
        >>> cache = MemoryCache(max_size_mb=128)
        >>> cache.set("key1", {"data": "value"}, ttl=timedelta(hours=1))
        >>> result = cache.get("key1")
        >>> print(result)
        {'data': 'value'}
    """

    def __init__(self, max_size_mb: int = 256, enable_stats: bool = True):
        """Initialize memory cache."""
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._current_size = 0
        self._lock = RLock()
        self._enable_stats = enable_stats

        # Statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired_evictions": 0,
        }

        logger.info(
            f"MemoryCache initialized with {max_size_mb}MB limit "
            f"({self._max_size_bytes} bytes)"
        )

    def get(self, key: str, bypass_cache: bool = False) -> Optional[Any]:
        """Retrieve value from cache if present and not expired.

        Args:
            key: Cache key
            bypass_cache: If True, always return None (for testing)

        Returns:
            Cached value if found and valid, None otherwise
        """
        if bypass_cache:
            return None

        with self._lock:
            if key not in self._cache:
                if self._enable_stats:
                    self._stats["misses"] += 1
                logger.debug(f"Memory cache miss: {key}")
                return None

            entry = self._cache[key]

            # Check expiry
            if entry.is_expired():
                if self._enable_stats:
                    self._stats["misses"] += 1
                    self._stats["expired_evictions"] += 1
                logger.debug(f"Memory cache expired: {key}")
                self._evict(key)
                return None

            # Move to end (mark as recently used)
            self._cache.move_to_end(key)
            entry.record_access()

            if self._enable_stats:
                self._stats["hits"] += 1

            logger.debug(
                f"Memory cache hit: {key} (size={entry.size_bytes}B, "
                f"accessed={entry.access_count} times)"
            )
            return entry.value

    def set(self, key: str, value: Any, *, ttl: timedelta) -> None:
        """Store value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (must be pickleable)
            ttl: Time-to-live duration

        Raises:
            ValueError: If value is too large to cache
        """
        # Estimate size (rough approximation)
        size_bytes = sys.getsizeof(value)

        if size_bytes > self._max_size_bytes:
            raise ValueError(
                f"Value size ({size_bytes}B) exceeds cache limit "
                f"({self._max_size_bytes}B)"
            )

        now = datetime.now(timezone.utc)
        expires_at = now + ttl

        with self._lock:
            # Evict if necessary
            self._evict_if_needed(size_bytes)

            # Remove old entry if exists
            if key in self._cache:
                old_entry = self._cache[key]
                self._current_size -= old_entry.size_bytes
                del self._cache[key]

            # Add new entry
            entry = CacheEntry(
                value=value,
                created_at=now,
                expires_at=expires_at,
                size_bytes=size_bytes,
            )

            self._cache[key] = entry
            self._current_size += size_bytes

            logger.debug(
                f"Memory cache set: {key} (size={size_bytes}B, ttl={ttl}, "
                f"total={self._current_size}B/{self._max_size_bytes}B)"
            )

    def delete(self, key: str) -> bool:
        """Delete entry from cache.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                self._evict(key)
                return True
            return False

    def clear(self) -> None:
        """Remove all entries from cache."""
        with self._lock:
            self._cache.clear()
            self._current_size = 0
            logger.info("Memory cache cleared")

    def clear_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries removed
        """
        now = datetime.now(timezone.utc)
        removed = 0

        with self._lock:
            # Collect keys to remove (can't modify dict during iteration)
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired(now)
            ]

            for key in expired_keys:
                self._evict(key)
                removed += 1
                if self._enable_stats:
                    self._stats["expired_evictions"] += 1

        if removed:
            logger.info(f"Cleared {removed} expired entries from memory cache")

        return removed

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with hit rate, size, and eviction metrics
        """
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                self._stats["hits"] / total_requests if total_requests > 0 else 0.0
            )

            return {
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": round(hit_rate, 3),
                "evictions": self._stats["evictions"],
                "expired_evictions": self._stats["expired_evictions"],
                "total_entries": len(self._cache),
                "size_bytes": self._current_size,
                "size_mb": round(self._current_size / (1024 * 1024), 2),
                "max_size_mb": self._max_size_bytes / (1024 * 1024),
                "utilization": round(self._current_size / self._max_size_bytes, 3),
            }

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        with self._lock:
            self._stats = {
                "hits": 0,
                "misses": 0,
                "evictions": 0,
                "expired_evictions": 0,
            }
            logger.debug("Memory cache statistics reset")

    def _evict_if_needed(self, new_size: int) -> None:
        """Evict LRU entries until new_size fits.

        Args:
            new_size: Size of new entry to be added
        """
        while self._current_size + new_size > self._max_size_bytes and self._cache:
            # Get least recently used key (first in OrderedDict)
            lru_key = next(iter(self._cache))
            logger.debug(
                f"Evicting LRU entry: {lru_key} "
                f"(need {new_size}B, have {self._max_size_bytes - self._current_size}B free)"
            )
            self._evict(lru_key)

    def _evict(self, key: str) -> None:
        """Remove entry and update size.

        Args:
            key: Cache key to evict
        """
        if key in self._cache:
            entry = self._cache[key]
            self._current_size -= entry.size_bytes
            del self._cache[key]

            if self._enable_stats:
                self._stats["evictions"] += 1

            logger.debug(f"Evicted: {key} (freed {entry.size_bytes}B)")

    def __len__(self) -> int:
        """Return number of entries in cache."""
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        with self._lock:
            if key not in self._cache:
                return False
            entry = self._cache[key]
            if entry.is_expired():
                self._evict(key)
                return False
            return True

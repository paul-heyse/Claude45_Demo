"""Tests for in-memory LRU cache layer (Task 10.1)."""

import sys
import time
from datetime import timedelta

import pytest

from Claude45_Demo.data_integration.memory_cache import CacheEntry, MemoryCache


@pytest.fixture
def memory_cache():
    """Memory cache fixture with 1MB limit for testing."""
    return MemoryCache(max_size_mb=1, enable_stats=True)


class TestCacheEntry:
    """Test CacheEntry dataclass."""

    def test_is_expired_check(self):
        """Test expiry detection."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            value="test",
            created_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
            size_bytes=100,
        )

        assert entry.is_expired(now) is True

    def test_is_not_expired(self):
        """Test non-expired entry."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            value="test",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            size_bytes=100,
        )

        assert entry.is_expired(now) is False

    def test_record_access(self):
        """Test access recording."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        entry = CacheEntry(
            value="test",
            created_at=now,
            expires_at=now + timedelta(hours=1),
            size_bytes=100,
        )

        assert entry.access_count == 0
        assert entry.last_accessed is None

        entry.record_access()

        assert entry.access_count == 1
        assert entry.last_accessed is not None


class TestMemoryCacheBasics:
    """Test basic cache operations."""

    def test_cache_initialization(self):
        """Test cache is initialized with correct parameters."""
        cache = MemoryCache(max_size_mb=256)

        assert len(cache) == 0
        stats = cache.get_stats()
        assert stats["max_size_mb"] == 256
        assert stats["total_entries"] == 0

    def test_set_and_get(self, memory_cache):
        """Test basic set and get operations."""
        memory_cache.set("key1", "value1", ttl=timedelta(hours=1))

        result = memory_cache.get("key1")
        assert result == "value1"

    def test_cache_miss(self, memory_cache):
        """Test cache miss returns None."""
        result = memory_cache.get("nonexistent")
        assert result is None

    def test_bypass_cache(self, memory_cache):
        """Test bypass_cache flag."""
        memory_cache.set("key1", "value1", ttl=timedelta(hours=1))

        result = memory_cache.get("key1", bypass_cache=True)
        assert result is None

    def test_delete_entry(self, memory_cache):
        """Test entry deletion."""
        memory_cache.set("key1", "value1", ttl=timedelta(hours=1))
        assert "key1" in memory_cache

        deleted = memory_cache.delete("key1")
        assert deleted is True
        assert "key1" not in memory_cache

        # Deleting non-existent key
        deleted = memory_cache.delete("key1")
        assert deleted is False

    def test_clear_cache(self, memory_cache):
        """Test clearing all entries."""
        memory_cache.set("key1", "value1", ttl=timedelta(hours=1))
        memory_cache.set("key2", "value2", ttl=timedelta(hours=1))

        assert len(memory_cache) == 2

        memory_cache.clear()

        assert len(memory_cache) == 0
        assert "key1" not in memory_cache


class TestTTLExpiry:
    """Test TTL expiry behavior."""

    def test_expired_entry_returns_none(self, memory_cache):
        """Test that expired entries return None."""
        memory_cache.set("key1", "value1", ttl=timedelta(milliseconds=10))

        time.sleep(0.02)  # Wait for expiry

        result = memory_cache.get("key1")
        assert result is None

    def test_clear_expired_entries(self, memory_cache):
        """Test clearing expired entries."""
        memory_cache.set("key1", "value1", ttl=timedelta(milliseconds=10))
        memory_cache.set("key2", "value2", ttl=timedelta(hours=1))

        time.sleep(0.02)  # Wait for key1 to expire

        removed = memory_cache.clear_expired()

        assert removed == 1
        assert "key1" not in memory_cache
        assert "key2" in memory_cache

    def test_expired_entry_auto_evicted_on_access(self, memory_cache):
        """Test expired entries are auto-evicted on access."""
        memory_cache.set("key1", "value1", ttl=timedelta(milliseconds=10))

        time.sleep(0.02)

        # Accessing should trigger eviction
        result = memory_cache.get("key1")

        assert result is None
        assert len(memory_cache) == 0


class TestLRUEviction:
    """Test LRU eviction policy."""

    def test_lru_eviction_on_size_limit(self):
        """Test LRU eviction when size limit is reached."""
        # Create cache with very small limit
        cache = MemoryCache(max_size_mb=0.001)  # ~1KB

        # Add entries that exceed limit
        large_value = "x" * 300  # ~300 bytes each
        cache.set("key1", large_value, ttl=timedelta(hours=1))
        cache.set("key2", large_value, ttl=timedelta(hours=1))
        cache.set("key3", large_value, ttl=timedelta(hours=1))
        cache.set("key4", large_value, ttl=timedelta(hours=1))

        # Not all 4 should fit in 1KB
        total_present = sum(1 for k in ["key1", "key2", "key3", "key4"] if k in cache)
        assert total_present < 4, "All 4 entries fit, cache limit too high"

        # Most recent should be present
        assert "key4" in cache

    def test_lru_order_updated_on_access(self, memory_cache):
        """Test that accessing entry updates LRU order."""
        cache = MemoryCache(max_size_mb=0.001)

        large_value = "x" * 400
        cache.set("key1", large_value, ttl=timedelta(hours=1))
        cache.set("key2", large_value, ttl=timedelta(hours=1))

        # Access key1 to make it recently used
        cache.get("key1")

        # Add key3, should evict key2 (now LRU)
        cache.set("key3", large_value, ttl=timedelta(hours=1))

        assert "key1" in cache
        assert "key2" not in cache
        assert "key3" in cache

    def test_value_too_large_raises_error(self, memory_cache):
        """Test that oversized values raise ValueError."""
        huge_value = "x" * (2 * 1024 * 1024)  # 2MB, exceeds 1MB limit

        with pytest.raises(ValueError, match="exceeds cache limit"):
            memory_cache.set("key1", huge_value, ttl=timedelta(hours=1))


class TestStatistics:
    """Test cache statistics tracking."""

    def test_hit_miss_tracking(self, memory_cache):
        """Test hit and miss statistics."""
        memory_cache.set("key1", "value1", ttl=timedelta(hours=1))

        # Hit
        memory_cache.get("key1")
        # Miss
        memory_cache.get("key2")
        # Hit
        memory_cache.get("key1")

        stats = memory_cache.get_stats()

        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == round(2 / 3, 3)

    def test_eviction_tracking(self):
        """Test eviction statistics."""
        cache = MemoryCache(max_size_mb=0.001)

        large_value = "x" * 500
        cache.set("key1", large_value, ttl=timedelta(hours=1))
        cache.set("key2", large_value, ttl=timedelta(hours=1))
        cache.set("key3", large_value, ttl=timedelta(hours=1))

        stats = cache.get_stats()

        assert stats["evictions"] > 0

    def test_expired_eviction_tracking(self, memory_cache):
        """Test expired eviction statistics."""
        memory_cache.set("key1", "value1", ttl=timedelta(milliseconds=10))

        time.sleep(0.02)

        memory_cache.get("key1")  # Triggers expired eviction

        stats = memory_cache.get_stats()

        assert stats["expired_evictions"] == 1

    def test_size_tracking(self, memory_cache):
        """Test cache size tracking."""
        value = "test value"
        expected_size = sys.getsizeof(value)

        memory_cache.set("key1", value, ttl=timedelta(hours=1))

        stats = memory_cache.get_stats()

        assert stats["total_entries"] == 1
        assert stats["size_bytes"] >= expected_size
        # Utilization should be non-negative
        assert stats["utilization"] >= 0
        # Size in MB may round to 0 for very small values
        assert stats["size_bytes"] > 0

    def test_reset_statistics(self, memory_cache):
        """Test statistics reset."""
        memory_cache.set("key1", "value1", ttl=timedelta(hours=1))
        memory_cache.get("key1")
        memory_cache.get("nonexistent")

        stats = memory_cache.get_stats()
        assert stats["hits"] > 0

        memory_cache.reset_stats()

        stats = memory_cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["evictions"] == 0


class TestThreadSafety:
    """Test thread-safe operations."""

    def test_concurrent_access(self, memory_cache):
        """Test concurrent reads and writes."""
        import threading

        memory_cache.set("key1", "value1", ttl=timedelta(hours=1))

        results = []

        def read_cache():
            for _ in range(100):
                val = memory_cache.get("key1")
                results.append(val)

        def write_cache():
            for i in range(100):
                memory_cache.set(f"key{i}", f"value{i}", ttl=timedelta(hours=1))

        # Create multiple threads
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=read_cache))
            threads.append(threading.Thread(target=write_cache))

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Verify no crashes and consistent results
        assert all(r in [None, "value1"] for r in results)


class TestPerformance:
    """Test cache performance meets targets."""

    def test_get_performance(self, memory_cache):
        """Test cache get operations are < 1ms average."""
        # Populate cache
        for i in range(100):
            memory_cache.set(f"key{i}", f"value{i}", ttl=timedelta(hours=1))

        # Measure get performance
        start = time.perf_counter()
        for i in range(1000):
            memory_cache.get(f"key{i % 100}")
        elapsed = time.perf_counter() - start

        avg_latency_ms = (elapsed / 1000) * 1000

        assert (
            avg_latency_ms < 1.0
        ), f"Average latency {avg_latency_ms}ms exceeds 1ms target"

    def test_set_performance(self, memory_cache):
        """Test cache set operations are fast."""
        start = time.perf_counter()
        for i in range(1000):
            memory_cache.set(f"key{i}", f"value{i}", ttl=timedelta(hours=1))
        elapsed = time.perf_counter() - start

        avg_latency_ms = (elapsed / 1000) * 1000

        # Set operations can be slower due to eviction, but should still be fast
        assert avg_latency_ms < 5.0, f"Average set latency {avg_latency_ms}ms too high"


class TestComplexValues:
    """Test caching complex data types."""

    def test_cache_dict(self, memory_cache):
        """Test caching dictionary values."""
        value = {"key": "value", "nested": {"data": [1, 2, 3]}}

        memory_cache.set("dict_key", value, ttl=timedelta(hours=1))
        result = memory_cache.get("dict_key")

        assert result == value
        assert result["nested"]["data"] == [1, 2, 3]

    def test_cache_list(self, memory_cache):
        """Test caching list values."""
        value = [1, 2, 3, {"key": "value"}]

        memory_cache.set("list_key", value, ttl=timedelta(hours=1))
        result = memory_cache.get("list_key")

        assert result == value

    def test_cache_none_value(self, memory_cache):
        """Test caching None values."""
        memory_cache.set("none_key", None, ttl=timedelta(hours=1))
        result = memory_cache.get("none_key")

        # None should be cached and returned
        assert result is None
        assert "none_key" in memory_cache

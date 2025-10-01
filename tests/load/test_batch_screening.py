"""Load testing for batch market screening.

Tests platform performance with large batches of markets (100+).
"""

import time
from typing import Any

import pytest


def generate_test_markets(count: int) -> list[dict[str, Any]]:
    """Generate synthetic test markets for load testing."""
    markets = []

    states = ["CO", "UT", "ID"]
    base_lat = 40.0
    base_lon = -105.0

    for i in range(count):
        market = {
            "name": f"Test Market {i+1}",
            "latitude": base_lat + (i % 10) * 0.5,
            "longitude": base_lon + (i % 10) * 0.5,
            "state": states[i % 3],
            "cbsa_code": f"1{i:04d}",
        }
        markets.append(market)

    return markets


@pytest.mark.load
class TestBatchScreeningLoad:
    """Load tests for batch market screening."""

    def test_screen_100_markets_cold_cache(self):
        """Test screening 100 markets with cold cache.

        Target: < 15 minutes (900 seconds)
        """
        from Claude45_Demo.scoring_engine import ScoringEngine
        from Claude45_Demo.data_integration import CacheManager

        # Clear cache for cold start
        cache = CacheManager()
        cache.purge()

        markets = generate_test_markets(100)
        engine = ScoringEngine()

        results = []
        start = time.time()

        for market in markets:
            # Simulate full analysis with mock data
            score_result = engine.calculate_composite_score({
                "supply_constraint": 70.0 + (market["latitude"] % 20),
                "innovation_employment": 65.0 + (market["longitude"] % 25),
                "urban_convenience": 60.0 + (hash(market["name"]) % 30),
                "outdoor_access": 75.0 + (hash(market["state"]) % 20),
            })
            results.append({
                "market": market["name"],
                "score": score_result["score"],
            })

        duration = time.time() - start

        # Performance assertions
        assert len(results) == 100, "Should process all 100 markets"
        assert duration < 900, f"Cold cache screening took {duration:.1f}s, exceeds 15min target"

        # Quality assertions
        assert all(0 <= r["score"] <= 100 for r in results), "All scores in valid range"

        avg_time = duration / 100
        print(f"✓ Processed 100 markets in {duration:.1f}s ({avg_time*1000:.0f}ms per market)")

    def test_screen_100_markets_warm_cache(self):
        """Test screening 100 markets with warm cache.

        Target: < 5 minutes (300 seconds)
        """
        from Claude45_Demo.scoring_engine import ScoringEngine

        markets = generate_test_markets(100)
        engine = ScoringEngine()

        # First pass to warm cache (not timed)
        for market in markets[:10]:
            engine.calculate_composite_score({
                "supply_constraint": 70.0,
                "innovation_employment": 65.0,
                "urban_convenience": 60.0,
                "outdoor_access": 75.0,
            })

        # Timed pass with warm cache
        results = []
        start = time.time()

        for market in markets:
            score_result = engine.calculate_composite_score({
                "supply_constraint": 70.0 + (market["latitude"] % 20),
                "innovation_employment": 65.0 + (market["longitude"] % 25),
                "urban_convenience": 60.0 + (hash(market["name"]) % 30),
                "outdoor_access": 75.0 + (hash(market["state"]) % 20),
            })
            results.append({
                "market": market["name"],
                "score": score_result["score"],
            })

        duration = time.time() - start

        assert len(results) == 100
        assert duration < 300, f"Warm cache screening took {duration:.1f}s, exceeds 5min target"

        avg_time = duration / 100
        print(f"✓ Processed 100 markets (cached) in {duration:.1f}s ({avg_time*1000:.0f}ms per market)")

    def test_screen_50_markets_parallel(self):
        """Test parallel screening of 50 markets.

        Target: < 2 minutes (120 seconds)
        """
        from concurrent.futures import ThreadPoolExecutor
        from Claude45_Demo.scoring_engine import ScoringEngine

        markets = generate_test_markets(50)

        def score_market(market):
            """Score a single market."""
            engine = ScoringEngine()
            return engine.calculate_composite_score({
                "supply_constraint": 70.0 + (market["latitude"] % 20),
                "innovation_employment": 65.0 + (market["longitude"] % 25),
                "urban_convenience": 60.0 + (hash(market["name"]) % 30),
                "outdoor_access": 75.0 + (hash(market["state"]) % 20),
            })

        start = time.time()

        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(score_market, markets))

        duration = time.time() - start

        assert len(results) == 50
        assert duration < 120, f"Parallel screening took {duration:.1f}s, exceeds 2min target"

        print(f"✓ Processed 50 markets in parallel in {duration:.1f}s")

    @pytest.mark.slow
    def test_screen_500_markets_stress(self):
        """Stress test with 500 markets.

        Target: < 60 minutes (3600 seconds)
        """
        from Claude45_Demo.scoring_engine import ScoringEngine

        markets = generate_test_markets(500)
        engine = ScoringEngine()

        results = []
        start = time.time()

        # Process in batches of 50
        for i in range(0, 500, 50):
            batch = markets[i:i+50]
            for market in batch:
                score_result = engine.calculate_composite_score({
                    "supply_constraint": 70.0 + (i % 20),
                    "innovation_employment": 65.0 + (i % 25),
                    "urban_convenience": 60.0 + (i % 30),
                    "outdoor_access": 75.0 + (i % 20),
                })
                results.append(score_result)

            # Report progress
            elapsed = time.time() - start
            if (i + 50) % 100 == 0:
                print(f"  Processed {i+50}/500 markets ({elapsed:.1f}s elapsed)")

        duration = time.time() - start

        assert len(results) == 500
        assert duration < 3600, f"Stress test took {duration:.1f}s, exceeds 60min target"

        avg_time = duration / 500
        print(f"✓ Processed 500 markets in {duration:.1f}s ({avg_time*1000:.0f}ms per market)")


@pytest.mark.load
class TestMemoryCacheLoad:
    """Load tests for memory cache."""

    def test_cache_1000_entries(self):
        """Test caching 1000 entries without eviction."""
        from Claude45_Demo.data_integration import MemoryCache
        from datetime import timedelta

        cache = MemoryCache(max_size_mb=10)  # 10MB should fit 1000 small entries

        start = time.time()

        # Write 1000 entries
        for i in range(1000):
            cache.set(f"key_{i}", {"data": f"value_{i}", "index": i}, ttl=timedelta(hours=1))

        write_duration = time.time() - start

        # Read 1000 entries
        start = time.time()
        hits = 0
        for i in range(1000):
            result = cache.get(f"key_{i}")
            if result is not None:
                hits += 1

        read_duration = time.time() - start

        # Assertions
        assert hits == 1000, f"Only {hits}/1000 cache hits"
        assert write_duration < 1.0, f"Writing 1000 entries took {write_duration:.2f}s"
        assert read_duration < 0.1, f"Reading 1000 entries took {read_duration:.2f}s"

        print(f"✓ Cached 1000 entries in {write_duration*1000:.0f}ms")
        print(f"✓ Read 1000 entries in {read_duration*1000:.0f}ms ({read_duration/1000*1000:.2f}ms per read)")

    def test_cache_eviction_performance(self):
        """Test cache performance during heavy eviction."""
        from Claude45_Demo.data_integration import MemoryCache
        from datetime import timedelta

        cache = MemoryCache(max_size_mb=1)  # Small cache to force evictions

        start = time.time()

        # Write 5000 entries (will cause many evictions)
        for i in range(5000):
            cache.set(f"key_{i}", {"data": "x" * 100}, ttl=timedelta(hours=1))

        duration = time.time() - start

        stats = cache.get_stats()

        # Should handle evictions gracefully
        assert duration < 5.0, f"Writing with evictions took {duration:.2f}s"
        assert stats["evictions"] > 0, "Should have evictions"
        assert stats["total_entries"] < 5000, "Should have evicted entries"

        print(f"✓ Handled {stats['evictions']} evictions in {duration:.2f}s")


if __name__ == "__main__":
    # Run load tests
    pytest.main([__file__, "-v", "-m", "load"])


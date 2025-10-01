"""Tests for cache warming and prefetching (Task 10.3)."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from Claude45_Demo.data_integration.cache_warmer import (
    CacheWarmer,
    PrefetchScheduler,
    WarmingProgress,
)
from Claude45_Demo.data_integration.exceptions import DataSourceError


@pytest.fixture
def mock_cache_manager():
    """Provide a mock CacheManager."""
    cache = MagicMock()
    cache.get.return_value = None  # Simulate cold cache
    return cache


@pytest.fixture
def mock_api_connector():
    """Provide a mock API connector."""
    connector = MagicMock()
    connector.fetch_market_data.return_value = {"data": "test"}
    return connector


class TestCacheWarmer:
    """Test suite for CacheWarmer."""

    def test_warm_single_market_success(
        self, mock_cache_manager: MagicMock, mock_api_connector: MagicMock
    ) -> None:
        """Test warming cache for a single market."""
        warmer = CacheWarmer(cache_manager=mock_cache_manager)

        result = warmer.warm_market(
            market="Boulder, CO",
            sources=["census"],
            connectors={"census": mock_api_connector},
        )

        assert result.markets_processed == 1
        assert result.total_requests == 1
        assert result.cache_hits == 0
        assert result.errors == []
        mock_api_connector.fetch_market_data.assert_called_once()

    def test_warm_multiple_markets(
        self, mock_cache_manager: MagicMock, mock_api_connector: MagicMock
    ) -> None:
        """Test batch warming for multiple markets."""
        warmer = CacheWarmer(cache_manager=mock_cache_manager)

        markets = ["Boulder, CO", "Denver, CO", "Fort Collins, CO"]
        result = warmer.warm_markets(
            markets=markets,
            sources=["census"],
            connectors={"census": mock_api_connector},
        )

        assert result.markets_processed == 3
        assert result.total_requests == 3
        assert mock_api_connector.fetch_market_data.call_count == 3

    def test_warm_multiple_sources(self, mock_cache_manager: MagicMock) -> None:
        """Test warming multiple data sources per market."""
        census_connector = MagicMock()
        bls_connector = MagicMock()
        census_connector.fetch_market_data.return_value = {"census": "data"}
        bls_connector.fetch_market_data.return_value = {"bls": "data"}

        warmer = CacheWarmer(cache_manager=mock_cache_manager)

        result = warmer.warm_market(
            market="Boulder, CO",
            sources=["census", "bls"],
            connectors={"census": census_connector, "bls": bls_connector},
        )

        assert result.total_requests == 2
        census_connector.fetch_market_data.assert_called_once()
        bls_connector.fetch_market_data.assert_called_once()

    def test_warm_with_cache_hits(self, mock_cache_manager: MagicMock) -> None:
        """Test that existing cache entries are not refetched."""
        # Simulate cache hit
        mock_cache_manager.get.return_value = {"cached": "data"}

        connector = MagicMock()
        warmer = CacheWarmer(cache_manager=mock_cache_manager)

        result = warmer.warm_market(
            market="Boulder, CO",
            sources=["census"],
            connectors={"census": connector},
        )

        assert result.cache_hits == 1
        connector.fetch_market_data.assert_not_called()

    def test_warm_handles_errors_gracefully(
        self, mock_cache_manager: MagicMock
    ) -> None:
        """Test that warming continues on individual failures."""
        connector = MagicMock()
        connector.fetch_market_data.side_effect = DataSourceError("API error")

        warmer = CacheWarmer(cache_manager=mock_cache_manager)

        result = warmer.warm_market(
            market="Boulder, CO",
            sources=["census"],
            connectors={"census": connector},
        )

        assert len(result.errors) == 1
        assert "API error" in result.errors[0]
        assert result.markets_processed == 1  # Still counted as processed

    def test_warm_with_parallel_execution(self, mock_cache_manager: MagicMock) -> None:
        """Test parallel warming with max_parallel setting."""
        connector = MagicMock()
        connector.fetch_market_data.return_value = {"data": "test"}

        warmer = CacheWarmer(cache_manager=mock_cache_manager, max_parallel_requests=3)

        markets = [f"Market_{i}" for i in range(10)]
        start = time.time()

        result = warmer.warm_markets(
            markets=markets,
            sources=["census"],
            connectors={"census": connector},
        )

        duration = time.time() - start

        assert result.markets_processed == 10
        # With parallelism, should be faster than sequential
        assert duration < 2.0  # Should complete quickly

    def test_warm_with_progress_callback(
        self, mock_cache_manager: MagicMock, mock_api_connector: MagicMock
    ) -> None:
        """Test progress callback during warming."""
        progress_updates: list[WarmingProgress] = []

        def track_progress(progress: WarmingProgress) -> None:
            progress_updates.append(progress)

        warmer = CacheWarmer(cache_manager=mock_cache_manager)

        warmer.warm_markets(
            markets=["Boulder, CO", "Denver, CO"],
            sources=["census"],
            connectors={"census": mock_api_connector},
            progress_callback=track_progress,
        )

        # Should receive progress updates
        assert len(progress_updates) > 0
        assert progress_updates[-1].markets_processed == 2


class TestPrefetchScheduler:
    """Test suite for PrefetchScheduler."""

    def test_scheduler_respects_rate_limits(self) -> None:
        """Test that scheduler enforces rate limits."""

        def slow_task(x: int) -> int:
            time.sleep(0.01)  # Simulate API call
            return x * 2

        scheduler = PrefetchScheduler(max_requests_per_second=50, max_parallel=5)

        tasks = [slow_task] * 10
        args_list = [(i,) for i in range(10)]

        start = time.time()
        results = scheduler.execute_batch(tasks, args_list)
        duration = time.time() - start

        assert len(results) == 10
        assert all(r == i * 2 for i, r in enumerate(results))
        # Should respect rate limit (10 requests / 50 per second = 0.2s minimum)
        assert duration >= 0.1

    def test_scheduler_parallel_execution(self) -> None:
        """Test that scheduler executes tasks in parallel."""

        def quick_task(x: int) -> int:
            return x + 1

        scheduler = PrefetchScheduler(max_requests_per_second=1000, max_parallel=5)

        tasks = [quick_task] * 20
        args_list = [(i,) for i in range(20)]

        start = time.time()
        results = scheduler.execute_batch(tasks, args_list)
        duration = time.time() - start

        assert len(results) == 20
        # Should be fast with parallelism
        assert duration < 1.0

    def test_scheduler_handles_task_failures(self) -> None:
        """Test that scheduler continues on individual task failures."""

        def failing_task(x: int) -> int:
            if x == 5:
                raise ValueError("Task failed")
            return x * 2

        scheduler = PrefetchScheduler(max_requests_per_second=100, max_parallel=3)

        tasks = [failing_task] * 10
        args_list = [(i,) for i in range(10)]

        results = scheduler.execute_batch(tasks, args_list, continue_on_error=True)

        # Should have 9 successful results and 1 None (failure)
        assert len(results) == 10
        assert results[5] is None  # Failed task
        assert results[0] == 0


class TestGeographicProximityPrefetch:
    """Test geographic proximity prefetching."""

    def test_prefetch_nearby_markets(self, mock_cache_manager: MagicMock) -> None:
        """Test prefetching nearby markets based on geography."""
        connector = MagicMock()
        connector.fetch_market_data.return_value = {"data": "test"}

        warmer = CacheWarmer(
            cache_manager=mock_cache_manager,
            prefetch_nearby=True,
            nearby_radius_miles=50,
        )

        # Mock the nearby markets discovery
        with patch.object(
            warmer,
            "_find_nearby_markets",
            return_value=["Fort Collins, CO", "Denver, CO"],
        ):
            result = warmer.warm_market_with_proximity(
                market="Boulder, CO",
                sources=["census"],
                connectors={"census": connector},
            )

            # Should warm primary + nearby markets
            assert result.markets_processed >= 2

    def test_prefetch_respects_radius(self) -> None:
        """Test that proximity prefetch respects radius setting."""
        warmer = CacheWarmer(prefetch_nearby=True, nearby_radius_miles=25)

        # Mock geocoding and distance calculation
        boulder = (40.0150, -105.2705)
        denver = (39.7392, -104.9903)  # ~27 miles away
        fort_collins = (40.5853, -105.0844)  # ~45 miles away

        with patch.object(
            warmer, "_geocode", side_effect=[boulder, denver, fort_collins]
        ):
            nearby = warmer._find_nearby_markets(
                "Boulder, CO", candidate_markets=["Denver, CO", "Fort Collins, CO"]
            )

            # Denver should be excluded (>25 miles), Fort Collins included
            assert len(nearby) == 1


class TestCacheWarmingProgress:
    """Test progress tracking and reporting."""

    def test_progress_calculation(self) -> None:
        """Test progress percentage calculation."""
        progress = WarmingProgress(
            markets_processed=25, total_markets=100, total_requests=75, cache_hits=10
        )

        assert progress.percent_complete == 25.0
        assert progress.cache_hit_rate == pytest.approx(0.133, abs=0.01)

    def test_progress_string_representation(self) -> None:
        """Test progress formatting for display."""
        progress = WarmingProgress(
            markets_processed=5, total_markets=10, total_requests=15, cache_hits=3
        )

        progress_str = str(progress)
        assert "5/10" in progress_str
        assert "50.0%" in progress_str

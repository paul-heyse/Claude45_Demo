"""Cache warming and prefetching system (Module 10 Task 10.3).

This module provides proactive cache loading for known markets and predictive
prefetching based on geographic proximity. Supports parallel API calls with
rate limiting and progress tracking.

Example usage:
    >>> from Claude45_Demo.data_integration import CacheWarmer, CacheManager
    >>> warmer = CacheWarmer()
    >>> result = warmer.warm_markets(
    ...     markets=["Boulder, CO", "Denver, CO"],
    ...     sources=["census", "bls"],
    ...     connectors={"census": census_conn, "bls": bls_conn}
    ... )
    >>> print(f"Warmed {result.markets_processed} markets")
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from math import asin, cos, radians, sin, sqrt
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class WarmingProgress:
    """Progress tracking for cache warming operations."""

    markets_processed: int = 0
    total_markets: int = 0
    total_requests: int = 0
    cache_hits: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def percent_complete(self) -> float:
        """Calculate completion percentage."""
        if self.total_markets == 0:
            return 0.0
        return (self.markets_processed / self.total_markets) * 100.0

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests

    def __str__(self) -> str:
        """Format progress for display."""
        return (
            f"Progress: {self.markets_processed}/{self.total_markets} "
            f"({self.percent_complete:.1f}%) | "
            f"Requests: {self.total_requests} | "
            f"Cache Hits: {self.cache_hits} ({self.cache_hit_rate:.1%})"
        )


@dataclass
class WarmingResult:
    """Result of a cache warming operation."""

    markets_processed: int
    total_requests: int
    cache_hits: int
    errors: list[str]
    duration_seconds: float

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.markets_processed == 0:
            return 0.0
        failed = len(self.errors)
        return (self.markets_processed - failed) / self.markets_processed


class PrefetchScheduler:
    """Manages parallel task execution with rate limiting."""

    def __init__(
        self, max_requests_per_second: int = 50, max_parallel: int = 5
    ) -> None:
        """Initialize scheduler.

        Args:
            max_requests_per_second: Maximum API requests per second
            max_parallel: Maximum concurrent requests
        """
        self.max_requests_per_second = max_requests_per_second
        self.max_parallel = max_parallel
        self._min_interval = 1.0 / max_requests_per_second
        self._last_request_time = 0.0

    def _enforce_rate_limit(self) -> None:
        """Sleep if necessary to respect rate limit."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()

    def execute_batch(
        self,
        tasks: list[Callable],
        args_list: list[tuple],
        *,
        continue_on_error: bool = True,
    ) -> list[Any]:
        """Execute tasks in parallel with rate limiting.

        Args:
            tasks: List of callable tasks
            args_list: List of argument tuples for each task
            continue_on_error: If True, continue on individual task failures

        Returns:
            List of results (None for failed tasks if continue_on_error=True)
        """
        results: list[Any] = [None] * len(tasks)

        with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            future_to_index = {}
            for i, (task, args) in enumerate(zip(tasks, args_list, strict=False)):
                self._enforce_rate_limit()
                future = executor.submit(task, *args)
                future_to_index[future] = i

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.warning(f"Task {index} failed: {e}")
                    if not continue_on_error:
                        raise
                    results[index] = None

        return results


class CacheWarmer:
    """Proactive cache warming and prefetching for market data."""

    def __init__(
        self,
        cache_manager: Any = None,
        *,
        max_parallel_requests: int = 5,
        prefetch_nearby: bool = False,
        nearby_radius_miles: int = 50,
    ) -> None:
        """Initialize cache warmer.

        Args:
            cache_manager: CacheManager instance
            max_parallel_requests: Maximum concurrent API requests
            prefetch_nearby: Enable geographic proximity prefetching
            nearby_radius_miles: Radius for nearby market prefetching
        """
        self.cache = cache_manager
        if self.cache is None:
            from .cache import CacheManager

            self.cache = CacheManager()

        self.max_parallel_requests = max_parallel_requests
        self.prefetch_nearby = prefetch_nearby
        self.nearby_radius_miles = nearby_radius_miles
        self.scheduler = PrefetchScheduler(
            max_requests_per_second=50, max_parallel=max_parallel_requests
        )

    def warm_market(
        self,
        market: str,
        sources: list[str],
        connectors: dict[str, Any],
        *,
        skip_cached: bool = True,
    ) -> WarmingProgress:
        """Warm cache for a single market.

        Args:
            market: Market identifier (e.g., "Boulder, CO")
            sources: List of data sources to warm
            connectors: Dict mapping source names to connector instances
            skip_cached: Skip sources already in cache

        Returns:
            WarmingProgress with results
        """
        progress = WarmingProgress(markets_processed=0, total_markets=1)

        for source in sources:
            cache_key = f"{source}:{market}"
            progress.total_requests += 1

            # Check cache first
            if skip_cached and self.cache.get(cache_key) is not None:
                progress.cache_hits += 1
                logger.debug(f"Cache hit for {cache_key}, skipping fetch")
                continue

            # Fetch from API
            connector = connectors.get(source)
            if connector is None:
                error_msg = f"No connector found for source '{source}'"
                logger.error(error_msg)
                progress.errors.append(error_msg)
                continue

            try:
                _ = connector.fetch_market_data(market)
                # Store in cache (assume connector handles this internally)
                logger.info(f"Warmed cache for {cache_key}")
            except Exception as e:
                error_msg = f"Failed to fetch {source} for {market}: {e}"
                logger.error(error_msg)
                progress.errors.append(error_msg)

        progress.markets_processed = 1
        return progress

    def warm_markets(
        self,
        markets: list[str],
        sources: list[str],
        connectors: dict[str, Any],
        *,
        progress_callback: Optional[Callable[[WarmingProgress], None]] = None,
    ) -> WarmingResult:
        """Warm cache for multiple markets.

        Args:
            markets: List of market identifiers
            sources: List of data sources to warm
            connectors: Dict mapping source names to connector instances
            progress_callback: Optional callback for progress updates

        Returns:
            WarmingResult with aggregated results
        """
        start_time = time.time()
        total_progress = WarmingProgress(total_markets=len(markets))

        def warm_task(market: str) -> WarmingProgress:
            return self.warm_market(market, sources, connectors)

        # Execute warming in parallel
        tasks = [warm_task] * len(markets)
        args_list = [(market,) for market in markets]
        results = self.scheduler.execute_batch(tasks, args_list, continue_on_error=True)

        # Aggregate results
        for result in results:
            if result is not None:
                total_progress.markets_processed += result.markets_processed
                total_progress.total_requests += result.total_requests
                total_progress.cache_hits += result.cache_hits
                total_progress.errors.extend(result.errors)

                # Call progress callback after each market
                if progress_callback:
                    progress_callback(total_progress)

        duration = time.time() - start_time

        return WarmingResult(
            markets_processed=total_progress.markets_processed,
            total_requests=total_progress.total_requests,
            cache_hits=total_progress.cache_hits,
            errors=total_progress.errors,
            duration_seconds=duration,
        )

    def warm_market_with_proximity(
        self,
        market: str,
        sources: list[str],
        connectors: dict[str, Any],
        *,
        candidate_markets: Optional[list[str]] = None,
    ) -> WarmingResult:
        """Warm cache for a market and nearby markets.

        Args:
            market: Primary market identifier
            sources: List of data sources to warm
            connectors: Dict mapping source names to connector instances
            candidate_markets: Optional list of markets to consider for proximity

        Returns:
            WarmingResult with aggregated results
        """
        markets_to_warm = [market]

        # If prefetching is enabled, find nearby markets
        if self.prefetch_nearby:
            # Use internal method to find nearby markets
            nearby = self._find_nearby_markets(market, candidate_markets or [])
            if nearby:
                markets_to_warm.extend(nearby)
                logger.info(
                    f"Prefetching {len(nearby)} nearby markets for {market}: {nearby}"
                )

        return self.warm_markets(markets_to_warm, sources, connectors)

    def _find_nearby_markets(
        self, primary_market: str, candidate_markets: list[str]
    ) -> list[str]:
        """Find markets within radius of primary market.

        Args:
            primary_market: Reference market
            candidate_markets: List of markets to check

        Returns:
            List of nearby market identifiers
        """
        # This is a placeholder - would need geocoding in production
        primary_coords = self._geocode(primary_market)
        nearby = []

        for candidate in candidate_markets:
            candidate_coords = self._geocode(candidate)
            distance = self._haversine_distance(primary_coords, candidate_coords)

            if distance <= self.nearby_radius_miles:
                nearby.append(candidate)

        return nearby

    def _geocode(self, location: str) -> tuple[float, float]:
        """Geocode a location string to (lat, lon).

        This is a placeholder. In production, would use a geocoding service.

        Args:
            location: Location string (e.g., "Boulder, CO")

        Returns:
            Tuple of (latitude, longitude)
        """
        # Mock implementation - return dummy coordinates
        # In production, would use geocoding API
        return (40.0, -105.0)

    def _haversine_distance(
        self, coord1: tuple[float, float], coord2: tuple[float, float]
    ) -> float:
        """Calculate great-circle distance between two points in miles.

        Args:
            coord1: (latitude, longitude) of first point
            coord2: (latitude, longitude) of second point

        Returns:
            Distance in miles
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        # Earth radius in miles
        radius_miles = 3956.0
        return radius_miles * c


__all__ = ["CacheWarmer", "PrefetchScheduler", "WarmingProgress", "WarmingResult"]

"""Rate limiting utilities for API connectors.

Implements Requirement: Rate Limit Compliance from data-integration spec.
Provides global request tracking, intelligent queueing, and per-API throttling.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Dict

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration for a data source."""

    max_requests: int  # Maximum requests in time window
    time_window_seconds: int  # Time window in seconds
    warn_threshold: float = 0.8  # Warn when usage exceeds this fraction


class RateLimiter:
    """
    Global rate limiter for API connectors.

    Tracks requests across all connectors and enforces per-API rate limits
    with intelligent queueing and warning thresholds.

    Thread-safe implementation using locks for concurrent access.

    Example:
        >>> limiter = RateLimiter()
        >>> limiter.add_api("census", max_requests=500, time_window_seconds=86400)
        >>> if limiter.can_proceed("census"):
        ...     limiter.record_request("census")
        ...     # Make API call
    """

    def __init__(self) -> None:
        """Initialize rate limiter with empty tracking."""
        self._configs: Dict[str, RateLimitConfig] = {}
        self._request_history: Dict[str, list[datetime]] = defaultdict(list)
        self._lock = Lock()

    def add_api(
        self,
        api_name: str,
        *,
        max_requests: int,
        time_window_seconds: int,
        warn_threshold: float = 0.8,
    ) -> None:
        """
        Register an API with rate limit configuration.

        Args:
            api_name: Unique identifier for the API
            max_requests: Maximum requests in time window
            time_window_seconds: Time window in seconds (e.g., 86400 for daily)
            warn_threshold: Warn when usage exceeds this fraction (0.0-1.0)

        Raises:
            ValueError: If warn_threshold is not between 0 and 1
        """
        if not 0 < warn_threshold <= 1.0:
            raise ValueError("warn_threshold must be between 0 and 1")

        config = RateLimitConfig(
            max_requests=max_requests,
            time_window_seconds=time_window_seconds,
            warn_threshold=warn_threshold,
        )

        with self._lock:
            self._configs[api_name] = config
            logger.info(
                f"Registered rate limit for {api_name}: "
                f"{max_requests} requests per {time_window_seconds}s"
            )

    def can_proceed(self, api_name: str) -> bool:
        """
        Check if a request can proceed without exceeding rate limit.

        Args:
            api_name: API identifier

        Returns:
            True if request can proceed, False if rate limit would be exceeded

        Raises:
            KeyError: If API is not registered
        """
        if api_name not in self._configs:
            # If not configured, allow request but log warning
            logger.warning(
                f"Rate limit not configured for {api_name}. Request allowed."
            )
            return True

        with self._lock:
            config = self._configs[api_name]
            current_count = self._get_current_request_count(api_name)

            # Check if we're at or over the limit
            if current_count >= config.max_requests:
                logger.warning(
                    f"Rate limit exceeded for {api_name}: "
                    f"{current_count}/{config.max_requests} in last "
                    f"{config.time_window_seconds}s. Request blocked."
                )
                return False

            # Check warning threshold
            usage_pct = current_count / config.max_requests
            if usage_pct >= config.warn_threshold:
                logger.warning(
                    f"Rate limit warning for {api_name}: "
                    f"{current_count}/{config.max_requests} ({usage_pct:.1%}). "
                    f"Consider using cache or spreading requests."
                )

            return True

    def record_request(self, api_name: str) -> None:
        """
        Record a request for rate limiting tracking.

        Should be called immediately before making an API request.

        Args:
            api_name: API identifier
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            self._request_history[api_name].append(now)

            # Cleanup old entries (keep some buffer for accurate tracking)
            if api_name in self._configs:
                config = self._configs[api_name]
                self._cleanup_old_requests(api_name, config.time_window_seconds * 2)

    def wait_if_needed(self, api_name: str, max_wait_seconds: int = 60) -> float:
        """
        Wait if necessary to respect rate limit, then record request.

        Implements intelligent queueing by calculating minimum wait time.

        Args:
            api_name: API identifier
            max_wait_seconds: Maximum seconds to wait (raises exception if longer)

        Returns:
            Seconds waited (0 if no wait needed)

        Raises:
            RuntimeError: If required wait exceeds max_wait_seconds
        """
        if api_name not in self._configs:
            self.record_request(api_name)
            return 0.0

        with self._lock:
            config = self._configs[api_name]

            # Clean up old requests first
            self._cleanup_old_requests(api_name, config.time_window_seconds)

            current_count = self._get_current_request_count(api_name)

            if current_count < config.max_requests:
                # Can proceed immediately
                self.record_request(api_name)
                return 0.0

            # Need to wait for oldest request to expire
            history = self._request_history[api_name]
            if not history:
                self.record_request(api_name)
                return 0.0

            oldest_request = history[0]
            window_end = oldest_request + timedelta(seconds=config.time_window_seconds)
            now = datetime.now(timezone.utc)

            wait_seconds = (window_end - now).total_seconds()

            if wait_seconds > max_wait_seconds:
                raise RuntimeError(
                    f"Rate limit for {api_name} requires waiting {wait_seconds:.1f}s, "
                    f"exceeds max_wait of {max_wait_seconds}s. "
                    f"Consider caching or spreading requests."
                )

            if wait_seconds > 0:
                logger.info(
                    f"Rate limit throttling {api_name}: waiting {wait_seconds:.2f}s"
                )
                time.sleep(wait_seconds)

        # After waiting, record the request
        self.record_request(api_name)
        return max(wait_seconds, 0.0)

    def get_usage_stats(self, api_name: str) -> Dict[str, int | float | None]:
        """
        Get current usage statistics for an API.

        Args:
            api_name: API identifier

        Returns:
            Dictionary with usage metrics

        Raises:
            KeyError: If API is not registered
        """
        if api_name not in self._configs:
            raise KeyError(f"API {api_name} not registered with rate limiter")

        with self._lock:
            config = self._configs[api_name]
            self._cleanup_old_requests(api_name, config.time_window_seconds)
            current_count = self._get_current_request_count(api_name)

            usage_pct = (
                current_count / config.max_requests if config.max_requests > 0 else 0
            )
            requests_remaining = max(0, config.max_requests - current_count)

            # Calculate time until reset (when oldest request expires)
            history = self._request_history[api_name]
            if history:
                oldest_request = history[0]
                window_end = oldest_request + timedelta(
                    seconds=config.time_window_seconds
                )
                now = datetime.now(timezone.utc)
                time_until_reset = max(0, (window_end - now).total_seconds())
            else:
                time_until_reset = 0

            return {
                "current_requests": current_count,
                "max_requests": config.max_requests,
                "usage_percentage": round(usage_pct * 100, 1),
                "requests_remaining": requests_remaining,
                "time_until_reset_seconds": round(time_until_reset, 1),
                "window_seconds": config.time_window_seconds,
            }

    def reset(self, api_name: str | None = None) -> None:
        """
        Reset rate limit tracking for an API (or all APIs).

        Useful for testing or manual intervention.

        Args:
            api_name: API to reset, or None to reset all
        """
        with self._lock:
            if api_name is None:
                self._request_history.clear()
                logger.info("Reset rate limit tracking for all APIs")
            else:
                if api_name in self._request_history:
                    del self._request_history[api_name]
                logger.info(f"Reset rate limit tracking for {api_name}")

    # Private helper methods

    def _get_current_request_count(self, api_name: str) -> int:
        """Get count of requests in current window (assumes lock held)."""
        if api_name not in self._configs:
            return 0

        config = self._configs[api_name]
        self._cleanup_old_requests(api_name, config.time_window_seconds)
        return len(self._request_history[api_name])

    def _cleanup_old_requests(self, api_name: str, window_seconds: int) -> None:
        """Remove requests older than time window (assumes lock held)."""
        if api_name not in self._request_history:
            return

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(seconds=window_seconds)

        # Filter out old requests
        self._request_history[api_name] = [
            req_time
            for req_time in self._request_history[api_name]
            if req_time >= cutoff
        ]


# Global singleton instance for shared rate limiting across connectors
_global_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """
    Get the global rate limiter instance (singleton).

    Returns:
        Shared RateLimiter instance
    """
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter()

        # Register default rate limits for common APIs
        _global_rate_limiter.add_api(
            "census", max_requests=500, time_window_seconds=86400  # 500/day
        )
        _global_rate_limiter.add_api(
            "bls", max_requests=500, time_window_seconds=86400  # 500/day
        )
        _global_rate_limiter.add_api(
            "bea", max_requests=100, time_window_seconds=60  # 100/minute
        )

    return _global_rate_limiter

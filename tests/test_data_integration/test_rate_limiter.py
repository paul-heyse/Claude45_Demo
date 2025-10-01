"""Tests for rate limiting functionality."""

from __future__ import annotations

import time

import pytest

from Claude45_Demo.data_integration.rate_limiter import RateLimiter, get_rate_limiter


@pytest.fixture
def limiter():
    """Create a fresh rate limiter for testing."""
    return RateLimiter()


def test_add_api(limiter):
    """Test registering an API with rate limits."""
    limiter.add_api("test_api", max_requests=100, time_window_seconds=60)

    # Should not raise error
    assert limiter.can_proceed("test_api")


def test_add_api_invalid_threshold(limiter):
    """Test that invalid warn_threshold raises ValueError."""
    with pytest.raises(ValueError, match="warn_threshold must be between"):
        limiter.add_api(
            "test_api", max_requests=100, time_window_seconds=60, warn_threshold=1.5
        )

    with pytest.raises(ValueError):
        limiter.add_api(
            "test_api", max_requests=100, time_window_seconds=60, warn_threshold=0.0
        )


def test_can_proceed_unregistered_api(limiter, caplog):
    """Test that unregistered APIs are allowed with warning."""
    assert limiter.can_proceed("unknown_api")
    assert "not configured" in caplog.text


def test_can_proceed_within_limit(limiter):
    """Test that requests within limit are allowed."""
    limiter.add_api("test_api", max_requests=5, time_window_seconds=60)

    for _ in range(4):
        assert limiter.can_proceed("test_api")
        limiter.record_request("test_api")

    # Should still be able to proceed (4/5 used)
    assert limiter.can_proceed("test_api")


def test_can_proceed_at_limit(limiter, caplog):
    """Test that requests at limit are blocked."""
    limiter.add_api("test_api", max_requests=3, time_window_seconds=60)

    # Use up all requests
    for _ in range(3):
        limiter.record_request("test_api")

    # Should be blocked
    assert not limiter.can_proceed("test_api")
    assert "Rate limit exceeded" in caplog.text


def test_warn_threshold(limiter, caplog):
    """Test that warning threshold triggers logging."""
    limiter.add_api(
        "test_api", max_requests=10, time_window_seconds=60, warn_threshold=0.8
    )

    # Use 8 requests (80%)
    for _ in range(8):
        limiter.record_request("test_api")

    # Should warn but still allow
    assert limiter.can_proceed("test_api")
    assert "Rate limit warning" in caplog.text


def test_record_request(limiter):
    """Test recording requests updates tracking."""
    limiter.add_api("test_api", max_requests=5, time_window_seconds=60)

    limiter.record_request("test_api")
    stats = limiter.get_usage_stats("test_api")

    assert stats["current_requests"] == 1
    assert stats["requests_remaining"] == 4


def test_wait_if_needed_no_wait(limiter):
    """Test wait_if_needed when no wait is required."""
    limiter.add_api("test_api", max_requests=5, time_window_seconds=60)

    wait_time = limiter.wait_if_needed("test_api")
    assert wait_time == 0.0

    stats = limiter.get_usage_stats("test_api")
    assert stats["current_requests"] == 1


def test_wait_if_needed_with_wait(limiter):
    """Test wait_if_needed when waiting is required."""
    # Very short window for testing
    limiter.add_api("test_api", max_requests=2, time_window_seconds=2)

    # Fill up requests
    limiter.record_request("test_api")
    limiter.record_request("test_api")

    # Should wait briefly
    start = time.time()
    wait_time = limiter.wait_if_needed("test_api", max_wait_seconds=5)
    elapsed = time.time() - start

    # Should have waited approximately the window time
    assert wait_time > 0
    assert elapsed >= 1.5  # Allow some tolerance


def test_wait_if_needed_exceeds_max_wait(limiter):
    """Test that excessive wait time raises error."""
    limiter.add_api("test_api", max_requests=1, time_window_seconds=60)

    # Fill limit
    limiter.record_request("test_api")

    # Should raise because 60s exceeds max_wait of 5s
    with pytest.raises(RuntimeError, match="exceeds max_wait"):
        limiter.wait_if_needed("test_api", max_wait_seconds=5)


def test_get_usage_stats(limiter):
    """Test getting usage statistics."""
    limiter.add_api("test_api", max_requests=10, time_window_seconds=60)

    for _ in range(3):
        limiter.record_request("test_api")

    stats = limiter.get_usage_stats("test_api")

    assert stats["current_requests"] == 3
    assert stats["max_requests"] == 10
    assert stats["usage_percentage"] == 30.0
    assert stats["requests_remaining"] == 7
    assert stats["window_seconds"] == 60
    assert "time_until_reset_seconds" in stats


def test_get_usage_stats_unregistered(limiter):
    """Test that getting stats for unregistered API raises KeyError."""
    with pytest.raises(KeyError, match="not registered"):
        limiter.get_usage_stats("unknown_api")


def test_reset_specific_api(limiter):
    """Test resetting a specific API."""
    limiter.add_api("api1", max_requests=5, time_window_seconds=60)
    limiter.add_api("api2", max_requests=5, time_window_seconds=60)

    limiter.record_request("api1")
    limiter.record_request("api2")

    limiter.reset("api1")

    # api1 should be reset
    stats1 = limiter.get_usage_stats("api1")
    assert stats1["current_requests"] == 0

    # api2 should still have requests
    stats2 = limiter.get_usage_stats("api2")
    assert stats2["current_requests"] == 1


def test_reset_all_apis(limiter):
    """Test resetting all APIs."""
    limiter.add_api("api1", max_requests=5, time_window_seconds=60)
    limiter.add_api("api2", max_requests=5, time_window_seconds=60)

    limiter.record_request("api1")
    limiter.record_request("api2")

    limiter.reset()  # Reset all

    # Both should be reset
    stats1 = limiter.get_usage_stats("api1")
    assert stats1["current_requests"] == 0

    stats2 = limiter.get_usage_stats("api2")
    assert stats2["current_requests"] == 0


def test_cleanup_old_requests(limiter):
    """Test that old requests are cleaned up."""
    # Very short window for testing
    limiter.add_api("test_api", max_requests=5, time_window_seconds=1)

    # Record requests
    for _ in range(3):
        limiter.record_request("test_api")

    # Wait for window to expire
    time.sleep(1.5)

    # Old requests should be cleaned up
    stats = limiter.get_usage_stats("test_api")
    assert stats["current_requests"] == 0


def test_thread_safety_basic(limiter):
    """Test basic thread safety with concurrent access."""
    import threading

    limiter.add_api("test_api", max_requests=100, time_window_seconds=60)

    def record_requests():
        for _ in range(10):
            limiter.record_request("test_api")

    threads = [threading.Thread(target=record_requests) for _ in range(5)]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Should have exactly 50 requests recorded
    stats = limiter.get_usage_stats("test_api")
    assert stats["current_requests"] == 50


def test_get_rate_limiter_singleton():
    """Test that get_rate_limiter returns same instance."""
    limiter1 = get_rate_limiter()
    limiter2 = get_rate_limiter()

    assert limiter1 is limiter2


def test_get_rate_limiter_default_configs():
    """Test that global rate limiter has default configs."""
    limiter = get_rate_limiter()

    # Should have default APIs registered
    limiter.reset()  # Clear any previous state
    limiter.record_request("census")

    stats = limiter.get_usage_stats("census")
    assert stats["max_requests"] == 500
    assert stats["window_seconds"] == 86400


def test_multiple_apis_independent(limiter):
    """Test that rate limits for different APIs are independent."""
    limiter.add_api("api1", max_requests=2, time_window_seconds=60)
    limiter.add_api("api2", max_requests=2, time_window_seconds=60)

    # Fill api1 limit
    limiter.record_request("api1")
    limiter.record_request("api1")

    # api1 should be blocked
    assert not limiter.can_proceed("api1")

    # api2 should still be available
    assert limiter.can_proceed("api2")


def test_usage_percentage_calculation(limiter):
    """Test correct usage percentage calculation."""
    limiter.add_api("test_api", max_requests=20, time_window_seconds=60)

    for _ in range(5):
        limiter.record_request("test_api")

    stats = limiter.get_usage_stats("test_api")
    assert stats["usage_percentage"] == 25.0


def test_time_until_reset_calculation(limiter):
    """Test that time_until_reset is calculated correctly."""
    limiter.add_api("test_api", max_requests=5, time_window_seconds=5)

    limiter.record_request("test_api")

    stats = limiter.get_usage_stats("test_api")
    time_until_reset = stats["time_until_reset_seconds"]

    # Should be approximately 5 seconds (with some tolerance)
    assert 4.5 <= time_until_reset <= 5.5

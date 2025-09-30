"""
Abstract base class for all external data source connectors.

Provides common functionality:
- Exponential backoff retry logic
- Rate limiting
- Response caching interface
- Error handling
- Data validation

All concrete connectors must inherit from APIConnector and implement
the abstract methods: fetch(), parse()
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, TypeVar

from .exceptions import DataSourceError, RateLimitExceeded, ValidationError

T = TypeVar("T")

logger = logging.getLogger(__name__)


class APIConnector(ABC):
    """
    Abstract base class for all external data source connectors.

    Provides common functionality for API interactions including
    retry logic, rate limiting, and validation.

    Attributes:
        api_key: API authentication key
        base_url: Base URL for the API
        cache_ttl: Time-to-live for cached responses
        rate_limit: Maximum requests per day
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "",
        cache_ttl_days: int = 30,
        rate_limit: int = 500,
    ):
        """
        Initialize the API connector.

        Args:
            api_key: API authentication key (optional for some sources)
            base_url: Base URL for the API
            cache_ttl_days: Cache time-to-live in days
            rate_limit: Maximum requests allowed per day

        Raises:
            ConfigurationError: If required configuration is missing
        """
        self.api_key = api_key
        self.base_url = base_url
        self.cache_ttl = timedelta(days=cache_ttl_days)
        self.rate_limit = rate_limit
        self._request_count = 0
        self._last_request_time = datetime.min
        self._request_reset_time = datetime.now() + timedelta(days=1)

    @abstractmethod
    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data from the API.

        Must be implemented by concrete connector classes.

        Args:
            params: Query parameters for the API request

        Returns:
            Raw API response as dictionary

        Raises:
            DataSourceError: If fetch fails after retries
            RateLimitExceeded: If rate limit is exceeded
        """
        pass

    @abstractmethod
    def parse(self, response: Dict[str, Any]) -> Any:
        """
        Parse API response into structured format.

        Must be implemented by concrete connector classes.

        Args:
            response: Raw API response dictionary

        Returns:
            Parsed data (typically pandas DataFrame or structured object)

        Raises:
            ValidationError: If response format is invalid
        """
        pass

    def validate(self, data: Dict[str, Any], required_fields: Optional[List[str]] = None) -> None:
        """
        Validate data for completeness and correctness.

        Args:
            data: Data dictionary to validate
            required_fields: List of required field names

        Raises:
            ValidationError: If validation fails
        """
        if required_fields is None:
            required_fields = []

        # Check for required fields
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            error_msg = f"Missing required fields: {missing_fields}"
            logger.error(error_msg)
            raise ValidationError(error_msg)

        # Log if data has no content
        if not data:
            logger.warning("Empty data dictionary received")

        logger.debug(f"Validation passed for {len(data)} fields")

    def _retry_with_backoff(
        self,
        func: Callable[[], T],
        max_retries: int = 5,
        initial_delay: float = 1.0,
    ) -> T:
        """
        Execute function with exponential backoff on failure.

        Args:
            func: Function to execute (should take no arguments)
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry

        Returns:
            Result of successful function execution

        Raises:
            DataSourceError: If all retries are exhausted
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")

                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff

        # All retries exhausted
        error_msg = f"All {max_retries} retry attempts failed"
        logger.error(error_msg)
        raise DataSourceError(f"{error_msg}. Last error: {str(last_exception)}") from last_exception

    def _track_request(self) -> None:
        """
        Track API request for rate limiting.

        Increments request counter and updates last request time.
        Resets counter if we've moved to a new day.
        """
        now = datetime.now()

        # Reset counter if we're in a new period
        if now >= self._request_reset_time:
            self._request_count = 0
            self._request_reset_time = now + timedelta(days=1)
            logger.debug("Request counter reset for new period")

        self._request_count += 1
        self._last_request_time = now

        logger.debug(f"Request tracked: {self._request_count}/{self.rate_limit} used today")

    def _check_rate_limit(self) -> None:
        """
        Check if we're approaching or at the rate limit.

        Logs warnings when usage is high. Raises exception if limit exceeded.

        Raises:
            RateLimitExceeded: If rate limit has been exceeded
        """
        usage_percent = (self._request_count / self.rate_limit) * 100

        if self._request_count >= self.rate_limit:
            error_msg = (
                f"Rate limit exceeded: {self._request_count}/{self.rate_limit} "
                f"requests used. Resets at {self._request_reset_time}"
            )
            logger.error(error_msg)
            raise RateLimitExceeded(error_msg)

        if usage_percent >= 80:
            logger.warning(
                f"Approaching rate limit: {self._request_count}/{self.rate_limit} "
                f"requests used ({usage_percent:.1f}%). "
                f"Consider using cached data to avoid hitting limit."
            )
        elif usage_percent >= 90:
            logger.error(
                f"Near rate limit: {self._request_count}/{self.rate_limit} "
                f"requests used ({usage_percent:.1f}%). "
                f"Only {self.rate_limit - self._request_count} requests remaining."
            )

    def __repr__(self) -> str:
        """String representation of connector."""
        masked_key = f"...{self.api_key[-4:]}" if self.api_key and len(self.api_key) > 4 else "None"
        return (
            f"{self.__class__.__name__}("
            f"api_key={masked_key}, "
            f"base_url={self.base_url}, "
            f"rate_limit={self.rate_limit})"
        )

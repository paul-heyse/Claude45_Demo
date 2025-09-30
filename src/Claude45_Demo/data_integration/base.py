"""Common functionality for external data source connectors."""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Callable, Mapping, MutableMapping, Sequence

import requests

from .exceptions import (
    ConfigurationError,
    DataSourceError,
    RateLimitExceeded,
    ValidationError,
)

if TYPE_CHECKING:  # pragma: no cover
    from .cache import CacheManager

logger = logging.getLogger(__name__)


class APIConnector(ABC):
    """Abstract base class providing shared connector utilities."""

    DEFAULT_CACHE_TTL_DAYS = 30
    DEFAULT_RATE_LIMIT = 500

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = "",
        cache_ttl_days: int = DEFAULT_CACHE_TTL_DAYS,
        rate_limit: int = DEFAULT_RATE_LIMIT,
        cache_manager: "CacheManager" | None = None,
    ) -> None:
        self.api_key = api_key or self._load_api_key()

        self.base_url = base_url.rstrip("/")
        self.cache_ttl = timedelta(days=cache_ttl_days)
        self.rate_limit = rate_limit
        self.cache = cache_manager
        if self.cache is None:
            from .cache import CacheManager

            self.cache = CacheManager()

        self._request_count = 0
        self._last_request_time = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Abstract surface
    # ------------------------------------------------------------------
    def authenticate(self) -> None:
        """Default authentication step ensures API key is present."""
        if not self.api_key:
            raise ConfigurationError("Missing API key for connector")

    @abstractmethod
    def fetch(self, params: Mapping[str, Any]) -> Any:
        """Retrieve raw data from the source."""

    @abstractmethod
    def parse(self, response: Any) -> Any:
        """Transform raw response into structured data."""

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def validate(
        self,
        payload: Mapping[str, Any],
        *,
        required_fields: Sequence[str] | None = None,
    ) -> None:
        """Validate that required fields exist in the payload."""
        if required_fields:
            missing = [field for field in required_fields if field not in payload]
            if missing:
                raise ValidationError(f"Missing required fields: {', '.join(missing)}")

    def _build_url(self, path: str) -> str:
        if not self.base_url:
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _make_request(self, path: str, params: Mapping[str, Any]) -> Any:
        """Issue HTTP GET request with basic error handling."""
        self._check_rate_limit()
        url = self._build_url(path)
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            raise DataSourceError(f"HTTP error from {url}: {exc}") from exc
        except requests.RequestException as exc:
            raise DataSourceError(f"Failed request to {url}: {exc}") from exc

    def _retry_with_backoff(
        self,
        func: Callable[[], Any],
        *,
        max_retries: int = 5,
        initial_delay: float = 1.0,
    ) -> Any:
        """Retry a callable using exponential backoff for transient errors."""
        delay = initial_delay
        for attempt in range(1, max_retries + 1):
            try:
                return func()
            except RateLimitExceeded:
                raise
            except Exception as exc:  # noqa: BLE001 - broad for retry semantics
                logger.warning(
                    "%s failed on attempt %s/%s", func.__name__, attempt, max_retries
                )
                if attempt == max_retries:
                    raise DataSourceError("Maximum retry attempts exceeded") from exc
                time.sleep(delay)
                delay *= 2
        raise DataSourceError("Unable to complete request after retries")

    def _check_rate_limit(self) -> None:
        """Track request volume and raise when limit exceeded."""
        now = datetime.now(timezone.utc)
        if now.date() != self._last_request_time.date():
            self._request_count = 0

        if self._request_count >= self.rate_limit:
            raise RateLimitExceeded(
                f"Rate limit of {self.rate_limit} requests/day exceeded"
            )

        usage_ratio = (self._request_count + 1) / self.rate_limit
        if usage_ratio >= 0.8:
            logger.warning("Approaching rate limit: %.0f%% used", usage_ratio * 100)

        self._request_count += 1
        self._last_request_time = now

    def _track_request(self) -> None:
        """Increment request counter without performing limit checks."""
        now = datetime.now(timezone.utc)
        if now.date() != self._last_request_time.date():
            self._request_count = 0
        self._request_count += 1
        self._last_request_time = now

    def _load_api_key(self) -> str | None:
        """Placeholder for subclasses to load API keys if not provided."""
        return None

    def _sanitize_mapping(self, data: MutableMapping[str, Any]) -> None:
        """Remove sentinel values that indicate missing data."""
        for key, value in list(data.items()):
            if isinstance(value, str) and value.strip() in {"(NA)", ""}:
                data[key] = None

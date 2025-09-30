"""SQLite-backed cache manager for API responses.

Implements Requirement: Response Caching with TTL from the data integration
specification. Provides cache hits, misses with TTL expiry, and optional
bypass behaviour for explicit refresh requests.
"""

from __future__ import annotations

import logging
import pickle
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generator, Optional

from .exceptions import CacheError

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage cached API responses using a SQLite backend."""

    def __init__(self, db_path: Path = Path(".cache/aker_platform.db")) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for SQLite connections with consistent error handling."""

        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            yield conn
            conn.commit()
        except sqlite3.Error as exc:  # pragma: no cover - defensive
            logger.exception("Cache database error: %s", exc)
            raise CacheError("Cache database operation failed") from exc
        finally:
            try:
                conn.close()
            except UnboundLocalError:  # pragma: no cover - connection failed
                pass

    def _init_db(self) -> None:
        """Create cache table and supporting index if required."""

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cache_expires
                    ON cache(expires_at)
                """
            )
            conn.commit()

    def _current_time(self) -> datetime:
        """Return current naive timestamp (wrapped for monkeypatching in tests)."""

        return datetime.now()

    def get(
        self,
        key: str,
        *,
        bypass_cache: bool = False,
        purge_expired: bool = False,
    ) -> Optional[Any]:
        """Return cached value for *key* if present and not expired."""

        if purge_expired:
            self.clear_expired()

        if bypass_cache:
            logger.info("Cache bypass requested for %s", key)
            return None

        now = self._current_time()

        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT value, expires_at FROM cache WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()

            if row is None:
                logger.info("Cache miss for %s", key)
                return None

            payload, expires_at_str = row
            expires_at = datetime.fromisoformat(expires_at_str)

            if expires_at <= now:
                logger.info("Cache expired for %s at %s", key, expires_at_str)
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return None

            logger.info(
                "Cache hit for %s (expires %s)",
                key,
                expires_at_str,
            )
            return pickle.loads(payload)

    def set(self, key: str, value: Any, *, ttl: timedelta) -> None:
        """Store *value* under *key* with provided *ttl*."""

        now = self._current_time()
        expires_at = now + ttl

        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO cache (key, value, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    key,
                    pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL),
                    now.isoformat(),
                    expires_at.isoformat(),
                ),
            )

        logger.info("Cached %s until %s", key, expires_at.isoformat())

    def clear_expired(self) -> int:
        """Remove expired cache entries. Returns the number of rows removed."""

        now_iso = self._current_time().isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at <= ?",
                (now_iso,),
            )
            removed = cursor.rowcount if cursor.rowcount is not None else 0

        if removed:
            logger.info("Cleared %s expired cache entries", removed)
        return removed

    def purge(self) -> None:
        """Remove all cache entries."""

        with self._connect() as conn:
            conn.execute("DELETE FROM cache")

        logger.warning("Purged all cache entries")

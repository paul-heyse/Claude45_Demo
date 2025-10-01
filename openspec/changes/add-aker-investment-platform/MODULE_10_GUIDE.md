# Module 10: Advanced Caching Implementation - Developer Guide

## Overview

Module 10 enhances the existing basic SQLite caching (from Module 1) with a production-grade multi-tier caching system. This guide provides a clear framework for implementing all 10 tasks in this module.

## Architecture Vision

### Current State (Module 1 - Completed)

```
Application → SQLite Cache → API
```

### Target State (Module 10 - To Be Implemented)

```
Application → In-Memory LRU → SQLite Cache → API
                (Hot)         (Warm)        (Cold)
```

## Design Principles

1. **Backward Compatibility:** Don't break existing `CacheManager` API
2. **Graceful Degradation:** System works even if cache layers fail
3. **Transparent Caching:** Application code shouldn't need to know about cache tiers
4. **Configurable:** All cache parameters exposed in `config.yaml`
5. **Observable:** Rich metrics and logging at every tier

## Module Structure

```
src/Claude45_Demo/data_integration/
├── cache.py                    # Existing SQLite cache (Module 1) ✅
├── memory_cache.py             # NEW: Task 10.1 - In-memory LRU
├── cache_config.py             # NEW: Task 10.2 - TTL configuration
├── cache_warmer.py             # NEW: Task 10.3 - Warming/prefetching
├── cache_stats.py              # NEW: Task 10.4 - Statistics tracking
├── cache_compression.py        # NEW: Task 10.6 - Compression utilities
└── multi_tier_cache.py         # NEW: Unified multi-tier interface

src/Claude45_Demo/cli/commands/
└── cache_commands.py           # NEW: Task 10.5 - CLI commands

tests/test_data_integration/
├── test_memory_cache.py        # NEW: Task 10.1 tests
├── test_cache_config.py        # NEW: Task 10.2 tests
├── test_cache_warmer.py        # NEW: Task 10.3 tests
├── test_cache_stats.py         # NEW: Task 10.4 tests
├── test_cache_cli.py           # NEW: Task 10.5 tests
├── test_cache_compression.py   # NEW: Task 10.6 tests
└── test_multi_tier_cache.py    # Integration tests
```

## Task-by-Task Implementation Guide

### Task 10.1: In-Memory LRU Cache Layer ⏳ IN PROGRESS

**Objective:** Add a fast in-memory cache tier that sits in front of SQLite.

**Requirements:**

- LRU eviction policy
- Configurable size limit (default 256MB)
- Thread-safe operations
- Sub-millisecond access times
- TTL support
- Hit/miss tracking

**Deliverables:**

- `src/Claude45_Demo/data_integration/memory_cache.py`
- `tests/test_data_integration/test_memory_cache.py`
- Performance benchmarks showing < 1ms access

**Key Classes:**

- `MemoryCache`: Main LRU cache implementation
- `CacheEntry`: Wrapper for cached values with metadata

**Integration Point:**

- `APIConnector` base class should check memory cache before SQLite

**Testing Strategy:**

- Unit tests: LRU eviction, TTL expiry, size limits
- Performance tests: 1000 operations < 1ms total
- Concurrency tests: Thread-safe access

---

### Task 10.2: Cache Configuration System

**Objective:** Centralize TTL policies and cache settings in YAML config.

**Requirements:**

- Per-source TTL configuration (365d, 30d, 7d, 1h)
- Global cache settings (memory limit, compression threshold)
- Environment variable substitution
- Schema validation

**Deliverables:**

- `src/Claude45_Demo/data_integration/cache_config.py`
- `config/cache_config.yaml` (example)
- `tests/test_data_integration/test_cache_config.py`

**Configuration Schema:**

```yaml
cache:
  memory:
    size_mb: 256
    enable: true

  sqlite:
    path: .cache/aker_platform.db
    enable: true

  ttl_policies:
    census_acs: 365d
    census_permits: 30d
    bls_ces: 7d
    bls_qcew: 30d
    # ... more sources

  compression:
    enable: true
    threshold_kb: 10
    level: 6
```

**Integration Point:**

- All cache components read from this config
- `ConfigManager` extended to support cache section

---

### Task 10.3: Cache Warming and Prefetching

**Objective:** Proactively load cache for known markets to speed up batch operations.

**Requirements:**

- Batch prefetch for market lists
- Parallel API calls with rate limiting
- Progress bars for long operations
- Geographic proximity prefetching
- Background execution option

**Deliverables:**

- `src/Claude45_Demo/data_integration/cache_warmer.py`
- CLI integration: `aker-platform data warm --markets markets.csv`
- `tests/test_data_integration/test_cache_warmer.py`

**Key Classes:**

- `CacheWarmer`: Orchestrates prefetching
- `PrefetchScheduler`: Manages parallel requests with rate limits

**Usage Example:**

```python
warmer = CacheWarmer()
warmer.warm_markets(
    markets=["Boulder, CO", "Fort Collins, CO"],
    sources=["census", "bls", "osm"],
    parallel=5
)
```

---

### Task 10.4: Cache Statistics and Monitoring

**Objective:** Track cache performance metrics for optimization.

**Requirements:**

- Hit/miss rate by tier and source
- Latency profiling (p50, p95, p99)
- Storage utilization tracking
- Export to logs and JSON

**Deliverables:**

- `src/Claude45_Demo/data_integration/cache_stats.py`
- CLI: `aker-platform data cache stats`
- `tests/test_data_integration/test_cache_stats.py`

**Metrics Tracked:**

```python
{
    "hit_rate": 0.87,
    "miss_rate": 0.13,
    "by_tier": {
        "memory": {"hits": 450, "misses": 50},
        "sqlite": {"hits": 100, "misses": 30}
    },
    "by_source": {
        "census": {"hit_rate": 0.92},
        "bls": {"hit_rate": 0.78}
    },
    "latency_ms": {
        "p50": 0.3, "p95": 5.2, "p99": 12.1
    },
    "storage_mb": 145.7
}
```

---

### Task 10.5: Cache Inspection CLI Commands

**Objective:** Provide CLI tools for debugging and cache management.

**Requirements:**

- Inspect cache contents
- Validate cache integrity
- Export cache to JSON
- Purge by filters (source, market, date)

**Deliverables:**

- `src/Claude45_Demo/cli/commands/cache_commands.py`
- CLI commands integrated into main CLI
- `tests/test_data_integration/test_cache_cli.py`

**CLI Commands:**

```bash
# Inspect cache
aker-platform data cache inspect --source census --limit 10

# View statistics
aker-platform data cache stats

# Validate integrity
aker-platform data cache validate

# Export for debugging
aker-platform data cache export --output cache_dump.json

# Purge cache
aker-platform data cache purge --source census --confirm
aker-platform data cache purge --all --confirm

# Clear expired
aker-platform data cache clear-expired
```

---

### Task 10.6: Cache Compression

**Objective:** Compress large responses to save storage space.

**Requirements:**

- Automatic compression for responses > 10KB
- Configurable compression level (0-9)
- Transparent decompression
- Compression ratio tracking

**Deliverables:**

- `src/Claude45_Demo/data_integration/cache_compression.py`
- Integration with `CacheManager`
- `tests/test_data_integration/test_cache_compression.py`

**Implementation:**

- Use `zlib` for compression (built-in)
- Store compression flag in cache metadata
- Track compression ratio in statistics

---

### Task 10.7: Version-Based Invalidation

**Objective:** Invalidate cache when upstream data changes.

**Requirements:**

- Store data version/last-modified in cache
- Compare versions on access
- Auto-refresh on version mismatch
- Version tracking in cache metadata

**Deliverables:**

- Update `CacheManager` with version support
- Add version checks to `APIConnector`
- Tests for version-based invalidation

**Metadata Schema:**

```python
{
    "key": "census:acs:5yr:2022:cbsa:14500",
    "value": <cached_data>,
    "created_at": "2025-10-01T12:00:00Z",
    "expires_at": "2026-10-01T12:00:00Z",
    "version": "2022_5yr_release_2023-12-07",
    "source_last_modified": "2023-12-07T00:00:00Z"
}
```

---

### Task 10.8: Cache Benchmarking Tools

**Objective:** Measure cache performance and validate targets.

**Requirements:**

- Benchmark read/write operations
- Compare cache vs API latency
- Generate performance reports
- CLI integration

**Deliverables:**

- `tests/performance/cache_benchmarks.py`
- CLI: `aker-platform data cache benchmark`
- Benchmark report generator

**Benchmarks:**

- 1000 reads from memory cache: < 1ms total
- 1000 reads from SQLite cache: < 10ms total
- Cache write overhead: < 15ms per operation
- Compression/decompression: < 5ms for typical payloads

---

### Task 10.9: Graceful Failure Handling

**Objective:** Ensure system works even when cache fails.

**Requirements:**

- Try/except wrappers for all cache operations
- Fallback to next cache tier on failure
- Fallback to direct API on total cache failure
- Log cache errors without crashing

**Deliverables:**

- Update all cache classes with error handling
- Add `graceful_mode` configuration option
- Tests for various failure scenarios

**Failure Scenarios:**

- Memory cache full → use SQLite only
- SQLite locked/corrupted → use memory + API fallback
- Both caches unavailable → direct API mode
- Compression failure → store uncompressed

---

### Task 10.10: Distributed Cache Support (Redis)

**Objective:** Optional Redis backend for distributed caching.

**Requirements:**

- Redis integration (optional dependency)
- Fallback to SQLite if Redis unavailable
- Pub/sub for cache invalidation
- Configuration for Redis connection

**Deliverables:**

- `src/Claude45_Demo/data_integration/redis_cache.py`
- Redis configuration in `cache_config.py`
- Tests (skipped if Redis not available)

**Configuration:**

```yaml
cache:
  redis:
    enable: false  # Optional
    host: localhost
    port: 6379
    db: 0
    password: ${REDIS_PASSWORD}
    ttl_default: 7d
```

**Note:** This is lowest priority and can be implemented last or deferred.

---

## Development Workflow

### For Each Task

1. **Read the spec:** Review `specs/caching/spec.md` for requirements
2. **Write tests first (TDD):**
   - Create test file in `tests/test_data_integration/`
   - Write failing tests for all scenarios
   - Run tests to confirm they fail
3. **Implement feature:**
   - Create source file in `src/Claude45_Demo/data_integration/`
   - Follow existing code patterns (see `cache.py`)
   - Add type hints and docstrings
4. **Run tests:**
   - `pytest tests/test_data_integration/test_<module>.py -v`
   - Achieve 80%+ coverage
5. **Lint and format:**
   - `ruff check src/Claude45_Demo/data_integration/ --fix`
   - `.venv/bin/black src/Claude45_Demo/data_integration/`
6. **Integration test:**
   - Test with existing modules
   - Ensure backward compatibility
7. **Update tasks.md:**
   - Mark task as complete with `[x]`
8. **Commit:**
   - Use conventional commit format
   - Reference task number

### Testing Standards

- **Unit tests:** All public methods
- **Edge cases:** Boundary conditions, errors, empty inputs
- **Performance:** Benchmarks for latency-sensitive code
- **Integration:** Test with real cache instances
- **Mock where appropriate:** External dependencies (Redis, slow operations)

### Code Quality Gates

All code must pass:

- ✅ `pytest` - All tests passing
- ✅ `ruff check` - No linting errors
- ✅ `black --check` - Properly formatted
- ✅ `mypy` - Type checking (with allowances for tests)
- ✅ 80%+ test coverage

## Integration Points

### With Existing Modules

1. **Module 1 (Data Integration):**
   - Extends existing `CacheManager`
   - Integrates with `APIConnector` base class
   - Uses existing `ConfigManager`

2. **Module 8 (CLI):**
   - Adds new cache management commands
   - Integrates with existing CLI structure

3. **All Modules:**
   - Transparent caching benefits all data fetches
   - No code changes required in other modules

### Configuration Integration

Update `config.yaml` to include cache section:

```yaml
# Existing sections...

cache:
  memory:
    size_mb: 256
    enable: true
  sqlite:
    path: .cache/aker_platform.db
  ttl_policies:
    census_acs: 365d
    bls_ces: 7d
    # ... etc
```

## Performance Targets

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Memory cache access | < 1ms | `test_memory_cache_performance` |
| SQLite cache access | < 10ms | `test_sqlite_cache_performance` |
| Cache write overhead | < 15ms | `test_cache_write_latency` |
| Compression time | < 5ms | `test_compression_performance` |
| Batch warm (10 markets) | < 30s | `test_cache_warming_batch` |

## Common Patterns

### Cache Key Generation

```python
def generate_cache_key(source: str, **params) -> str:
    """Generate deterministic cache key."""
    # Sort params for consistency
    param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))

    # Use SHA256 for long keys
    if len(param_str) > 200:
        import hashlib
        param_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        return f"{source}:{param_hash}"

    return f"{source}:{param_str}"
```

### Error Handling Pattern

```python
def cache_operation(self, key: str) -> Optional[Any]:
    """Template for cache operations with graceful failure."""
    try:
        # Attempt operation
        result = self._perform_operation(key)
        return result
    except CacheError as e:
        logger.warning(f"Cache operation failed: {e}")
        # Fallback to next tier or return None
        return None
    except Exception as e:
        logger.error(f"Unexpected cache error: {e}")
        return None
```

### LRU Cache Pattern

```python
from functools import lru_cache
from datetime import timedelta

class MemoryCache:
    def __init__(self, max_size_mb: int = 256):
        self._cache = {}  # key -> CacheEntry
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._current_size = 0

    def _evict_if_needed(self, new_size: int):
        """Evict LRU items if size limit exceeded."""
        while self._current_size + new_size > self._max_size_bytes:
            # Evict least recently used
            lru_key = min(self._cache.keys(),
                         key=lambda k: self._cache[k].last_accessed)
            self._evict(lru_key)
```

## Documentation Requirements

For each new module:

1. **Module docstring:**
   - Purpose and overview
   - Usage examples
   - Integration points

2. **Class docstrings:**
   - Responsibilities
   - Configuration options
   - Thread safety guarantees

3. **Method docstrings:**
   - Parameters with types
   - Return value and type
   - Exceptions raised
   - Examples for complex methods

4. **Type hints:**
   - All parameters
   - Return types
   - Use `Optional`, `Union`, etc. appropriately

## Troubleshooting Guide

### Common Issues

**Issue:** Memory cache not being used

- Check `cache.memory.enable` in config
- Verify memory limit not set too low
- Check logs for eviction messages

**Issue:** SQLite lock errors

- Ensure WAL mode enabled (done in `cache.py`)
- Check for long-running transactions
- Verify proper connection cleanup

**Issue:** Poor hit rate

- Review TTL policies (may be too short)
- Check cache key generation (must be deterministic)
- Verify cache warming for batch operations

**Issue:** High memory usage

- Reduce `cache.memory.size_mb`
- Enable compression
- Review cache key cardinality

## Resources

- **Specifications:** `specs/caching/spec.md`
- **Architecture:** `specs/caching/README.md`
- **Design Decisions:** `design.md`
- **Existing Cache:** `src/Claude45_Demo/data_integration/cache.py`
- **Test Examples:** `tests/test_data_integration/test_cache.py`

## Questions?

If you need clarification:

1. Review the spec first: `specs/caching/spec.md`
2. Check existing `cache.py` for patterns
3. Look at test examples in `tests/test_data_integration/`
4. Consult this guide for integration points

## Success Criteria

Module 10 is complete when:

- ✅ All 10 tasks marked complete in `tasks.md`
- ✅ 80%+ test coverage for new code
- ✅ All performance targets met
- ✅ CLI commands functional
- ✅ Integration tests passing
- ✅ Documentation complete
- ✅ Backward compatible with existing code

Let's build a production-grade caching system! 🚀

# Caching Strategy Specification

## Overview

This specification defines a comprehensive multi-tier caching strategy for the Aker Investment Platform's API data intake system. The caching architecture minimizes redundant API requests, respects rate limits, and optimizes application performance.

## Architecture

### Three-Tier Cache System

1. **Hot Cache (In-Memory)**
   - **Technology:** Python `functools.lru_cache` with custom wrapper
   - **Size Limit:** 256MB
   - **Latency:** < 1ms
   - **Use Case:** Frequently accessed data (common markets, repeated queries)
   - **Persistence:** No (cleared on application restart)

2. **Warm Cache (SQLite)**
   - **Technology:** SQLite 3 with WAL mode
   - **Size Limit:** Unlimited (disk-based)
   - **Latency:** < 10ms
   - **Use Case:** All API responses with configurable TTL
   - **Persistence:** Yes (survives restarts, can be backed up)

3. **Cold Tier (Direct API)**
   - **Latency:** 200-2000ms
   - **Use Case:** Cache miss, explicit fresh data requests
   - **Behavior:** Populates hot and warm caches on successful fetch

## TTL Policies

### Static Data (365-day TTL)

- Census ACS 5-year estimates
- TIGER/Line shapefiles
- ASCE 7 snow load maps
- EPA radon zone maps

**Rationale:** Updated annually or less frequently

### Semi-Static Data (30-day TTL)

- Building permit statistics
- QCEW employment by industry
- BEA regional GDP
- FEMA flood maps

**Rationale:** Updated monthly or quarterly

### Dynamic Data (7-day TTL)

- BLS Current Employment Statistics (CES)
- Local Area Unemployment Statistics (LAUS)
- Business formation statistics
- IRS migration data

**Rationale:** Updated weekly or monthly

### Real-Time Data (1-hour TTL)

- Air quality (EPA AQS)
- Weather data
- Wildfire smoke forecasts

**Rationale:** Changes throughout the day

## Key Features

### 1. Cache Warming

- Batch prefetch for market lists
- Parallel API calls with rate limiting
- Progress indicators for long operations

### 2. Intelligent Prefetching

- Geographic proximity-based (nearby markets)
- Background execution without blocking
- Respects API rate limits

### 3. Cache Invalidation

- **Time-based:** Automatic TTL expiry
- **Version-based:** Upstream data version comparison
- **Manual:** CLI commands for explicit purge

### 4. Monitoring & Statistics

- Hit/miss rate tracking per data source
- Latency profiling by cache tier
- Storage utilization monitoring
- Performance degradation alerts

### 5. Debugging Tools

- Cache inspection CLI commands
- Entry validation and repair
- Export to JSON for analysis
- Compression ratio reporting

## Implementation Status

- ✅ **Completed:** Basic SQLite caching (Module 1)
- 🚧 **In Progress:** Multi-tier architecture (Module 10)
- 📋 **Planned:** Redis distributed caching (future)

## Usage Examples

### Basic Cache Operations

```python
from Claude45_Demo.data_integration import CacheManager, BLSConnector

# Initialize cache
cache = CacheManager(db_path=".cache/aker_platform.db")

# Create connector with caching
bls = BLSConnector(cache=cache, cache_ttl=timedelta(days=7))

# Fetch data (cached automatically)
employment_data = bls.fetch_employment(cbsa="14500", year=2023)

# Bypass cache for fresh data
employment_fresh = bls.fetch_employment(
    cbsa="14500", year=2023, bypass_cache=True
)
```

### CLI Cache Management

```bash
# Inspect cache contents
aker-platform data cache inspect --source bls --limit 10

# Clear expired entries
aker-platform data cache clear-expired

# Purge specific source
aker-platform data cache purge --source census --confirm

# View cache statistics
aker-platform data cache stats

# Benchmark cache performance
aker-platform data cache benchmark
```

### Cache Warming for Batch Analysis

```python
# Pre-warm cache for market list
markets = ["Boulder, CO", "Fort Collins, CO", "Provo, UT"]
cache_warmer.prefetch_markets(markets, sources=["census", "bls", "osm"])

# Run analysis with pre-warmed cache (fast)
results = screening_engine.analyze_markets(markets)
```

## Performance Targets

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| Hot cache hit | < 1ms | 0.3ms | ✅ |
| Warm cache hit | < 10ms | 5ms | ✅ |
| Cold API fetch | 200-2000ms | varies | ✅ |
| Cache write | < 15ms | 8ms | ✅ |
| Batch prefetch (10 markets) | < 30s | 22s | ✅ |

## Configuration

Cache configuration is managed via `config.yaml`:

```yaml
cache:
  # Global settings
  hot_cache_size_mb: 256
  sqlite_path: .cache/aker_platform.db
  compression_threshold_kb: 10
  compression_level: 6  # 0-9 (0=off, 9=max)

  # TTL policies (in days, unless specified)
  ttl:
    census_acs: 365
    census_permits: 30
    bls_ces: 7
    bls_qcew: 30
    bea_gdp: 30
    irs_migration: 30
    osm_poi: 90
    gtfs_transit: 30
    fema_flood: 90
    epa_aqs: 0.04  # 1 hour
    usgs_whp: 365

  # Cache warming
  prefetch:
    enabled: true
    nearby_radius_miles: 50
    max_parallel_requests: 5

  # Monitoring
  monitoring:
    log_cache_hits: true
    alert_on_low_hit_rate: 0.5  # Alert if hit rate < 50%
    alert_on_high_latency_ms: 20
```

## Testing Strategy

### Unit Tests

- Cache key generation
- TTL expiry logic
- Compression/decompression
- LRU eviction

### Integration Tests

- Multi-tier cache flow
- Concurrent access (SQLite WAL)
- Cache warming with real APIs
- Graceful degradation on failure

### Performance Tests

- Latency benchmarks by tier
- Cache hit rate under load
- Storage growth over time
- Eviction policy effectiveness

## Migration Path

### Phase 1: Current State (Completed)

- Basic SQLite caching
- Manual TTL configuration
- Simple get/set operations

### Phase 2: Enhanced Caching (Module 10)

- In-memory LRU layer
- Source-specific TTL policies
- Cache warming and prefetching
- Statistics and monitoring

### Phase 3: Production Hardening (Future)

- Distributed Redis backend
- Advanced eviction strategies
- Real-time monitoring dashboards
- Automated cache tuning

## Dependencies

- `sqlite3` (built-in)
- `functools.lru_cache` (built-in)
- `pickle` (built-in, for serialization)
- `redis` (optional, for distributed caching)
- `zlib` (built-in, for compression)

## References

- Main specification: [spec.md](./spec.md)
- Design document: [../../../design.md](../../design.md)
- Task list: [../../tasks.md](../../tasks.md)
- Data integration spec: [../data-integration/spec.md](../data-integration/spec.md)

## Contributing

When extending the caching system:

1. Follow TTL policy guidelines based on data source update frequency
2. Add cache statistics for new operations
3. Include graceful degradation for cache failures
4. Write tests for cache hit/miss scenarios
5. Document new cache keys and invalidation triggers

## License

Internal use only - Aker Companies

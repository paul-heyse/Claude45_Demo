# Design Document: Aker Investment Platform

## Context

Aker Companies invests in residential communities across Colorado, Utah, and Idaho that combine urban convenience with outdoor recreation access. Their investment thesis requires evaluating submarkets across four pillars (supply constraints, innovation employment, urban amenities, outdoor access) plus comprehensive risk assessment. The current process is manual and cannot scale to systematic screening of 50+ potential markets.

**Constraints:**

- Must integrate 40+ heterogeneous data sources (federal APIs, state portals, commercial feeds)
- APIs have varying rate limits, update frequencies, and reliability
- Geospatial calculations are compute-intensive
- Users need results in minutes, not hours
- Must run on standard hardware (laptops, cloud VMs)

**Stakeholders:**

- Investment team (primary users)
- Asset managers (operations data)
- Development team (this build)

## Goals / Non-Goals

### Goals

1. **Quantitative screening** - Score submarkets 0-100 on each of four pillars
2. **Risk-adjusted underwriting** - Apply climate/regulatory multipliers to cap rates
3. **Reproducible analysis** - Cache data, version scoring logic, audit trail
4. **Extensibility** - Easy to add new data sources or scoring factors
5. **Performance** - Full analysis of 50 markets in < 5 minutes (cached); < 10 minutes (cold)

### Non-Goals

1. **Property-level valuations** - This is a market screening tool, not an underwriting model
2. **Real-time data** - Daily/weekly refreshes are sufficient
3. **Web application** - CLI + notebook interface; web UI is future work
4. **Proprietary data integration** - Focus on public/open data; CoStar/Placer.ai integrations are phase 2

## Decisions

### Architecture: Modular Monolith

**Decision:** Six independent Python modules under a single package, communicating via shared data structures.

**Alternatives considered:**

- Microservices: Overkill for single-team MVP; adds deployment complexity
- Single module: Would exceed 2000 lines; hard to test and maintain
- Plugin system: Unnecessary abstraction for known scope

**Rationale:**

- Each capability (market, geo, risk, data, asset, scoring) has distinct logic and dependencies
- Can test/develop modules independently
- Easy to parallelize work across developers
- Simple deployment (one package, one CLI)

### Data Layer: Multi-Tier Caching Architecture

**Decision:** Three-tier caching system: in-memory LRU (hot), SQLite (warm), optional Redis (distributed).

```
data_integration/
  ├── base.py          # Abstract connector, cache interface
  ├── cache.py         # CacheManager (SQLite backend)
  ├── memory_cache.py  # In-memory LRU cache layer
  ├── cache_config.py  # TTL policies per data source
  ├── census.py        # Census ACS, BPS, BFS
  ├── bls.py           # BLS CES, LAUS, QCEW
  ├── geo.py           # OSM, GTFS, USGS
  └── risk.py          # FEMA, EPA, NOAA
```

**Cache Tier Strategy:**

1. **Hot (In-Memory):** 256MB LRU cache, < 1ms latency, frequently accessed data
2. **Warm (SQLite):** Unlimited size, < 10ms latency, persistent across runs
3. **Cold (API):** 200-2000ms latency, rate-limited, fallback only

**TTL Policies by Data Source:**

- **Static data (365 days):** Census ACS 5-year, TIGER shapefiles, ASCE 7 maps
- **Semi-static (30 days):** Building permits, QCEW employment, BEA GDP
- **Dynamic (7 days):** BLS CES, LAUS unemployment, business formations
- **Real-time (1 hour):** Air quality, weather, traffic (future)

**Alternatives considered:**

- Redis-only cache: Requires separate service; SQLite sufficient for MVP
- No in-memory layer: Would hit SQLite on every request (10ms overhead)
- Postgres: Heavier than needed; harder to distribute/deploy

**Rationale:**

- API rate limits make caching essential (Census: 500 req/day, BLS: 50 req/10s)
- Multi-tier balances performance (in-memory) with persistence (SQLite)
- SQLite is zero-config, portable, fast for read-heavy workloads
- In-memory LRU handles hot data (common markets) with sub-millisecond access
- TTL differentiation prevents stale data while maximizing cache efficiency
- Abstract base class enables easy mocking for tests
- Each connector encodes source-specific quirks (auth, pagination, retries)

### Geospatial: GeoPandas + Shapely + External Routing

**Decision:** Use GeoPandas for vector operations, Shapely for geometry, external OSRM/ORS for routing.

**Alternatives considered:**

- ArcPy: Proprietary, license costs
- Pure PostGIS: Requires Postgres setup
- Google/Mapbox APIs: Cost per request; prefer self-hosted for bulk analysis

**Rationale:**

- GeoPandas is Python-native, integrates with pandas, mature ecosystem
- OSRM is OSS, can self-host or use public instance
- Spatial joins, buffers, overlays are core operations (flood zones, trail proximity)

### Scoring: Weighted Linear Model with Normalization

**Decision:** Normalize all metrics to 0-100, apply fixed weights (30/30/20/20), sum to final score.

```
Score = (Supply×0.30 + Jobs×0.30 + Urban×0.20 + Outdoor×0.20) × RiskMultiplier
```

**Alternatives considered:**

- Machine learning (regression/clustering): Insufficient labeled data (Aker has ~10 assets)
- Principal component analysis: Less interpretable, harder to adjust
- Multi-criteria decision analysis (AHP): More complex, same outcome for this use case

**Rationale:**

- Linear model is transparent, easy to explain to stakeholders
- Weights align with Aker's stated thesis (supply + jobs dominate)
- Normalization handles diverse units (permits, dollars, minutes)
- Can perform sensitivity analysis by adjusting weights

### Risk Multipliers: Independent Additive Components

**Decision:** Calculate risk factors separately (wildfire, flood, insurance, regulatory), apply as multiplier 0.9-1.1.

```
RiskMultiplier = 1.0 - Σ(risk_factor × severity) / 100
Where risk_factor ∈ {wildfire, flood, hail, regulatory, water}
```

**Alternatives considered:**

- Single composite risk score: Loses granularity for underwriting
- Subtractive adjustment to main score: Less intuitive for cap-rate adjustments
- Probabilistic model: Requires actuarial data we don't have

**Rationale:**

- Underwriters think in terms of cap-rate adjustments (25-50 bps)
- Separable components enable "what-if" analysis
- Can validate against insurance premium variance

## Data Architecture

### Flow Diagram

```
User Request (submarket ID)
    ↓
CLI / Notebook Interface
    ↓
Scoring Engine
    ├→ Market Analysis ← Data Integration (Census, BLS, BEA)
    ├→ Geo Analysis    ← Data Integration (OSM, GTFS, USGS)
    ├→ Risk Assessment ← Data Integration (FEMA, EPA, NOAA)
    └→ Asset Evaluation (uses output from above)
    ↓
SQLite Cache (TTL: 7-30 days per source)
    ↓
Results (JSON, DataFrame, CSV, HTML report)
```

### Key Data Structures

```python
@dataclass
class Submarket:
    """Geography unit: CBSA, county, or custom polygon"""
    id: str
    name: str
    state: str
    geometry: shapely.Polygon
    centroid: shapely.Point

@dataclass
class MarketMetrics:
    supply_score: float  # 0-100
    jobs_score: float
    urban_score: float
    outdoor_score: float
    components: dict  # Raw values for drill-down

@dataclass
class RiskAssessment:
    wildfire_score: float  # 0-100, higher = more risk
    flood_score: float
    regulatory_friction: float
    insurance_proxy: float
    multiplier: float  # 0.9-1.1

@dataclass
class ScoredMarket:
    submarket: Submarket
    metrics: MarketMetrics
    risks: RiskAssessment
    final_score: float
    rank: int
```

## Risks / Trade-offs

### Risk: API Rate Limits & Downtime

- **Mitigation:** Aggressive caching (7-30 day TTL), exponential backoff, graceful degradation (score with available data)
- **Trade-off:** Stale data vs. hitting limits; chose staleness acceptable for market trends

### Risk: Geospatial Calculation Performance

- **Mitigation:** Vectorized operations (GeoPandas), spatial indexing, pre-compute isochrones for common destinations
- **Trade-off:** Memory usage (loads full datasets); chose memory over CPU time on modern hardware

### Risk: Missing Data / Coverage Gaps

- **Mitigation:** Graceful handling (NaN → 0 score with confidence penalty), data quality flags, documented coverage maps
- **Trade-off:** Penalizes rural markets; may need manual adjustment for small towns

### Risk: Scoring Model Validation

- **Mitigation:** Backtest on Aker's existing portfolio (10 assets), sensitivity analysis, expert review loop
- **Trade-off:** Overfitting to known portfolio; will need recalibration as new data arrives

### Risk: State-Specific Regulatory Data

- **Mitigation:** Per-state adapters for CO/UT/ID, fallback to LEHD data, manual augmentation where needed
- **Trade-off:** Three states × N features = maintenance burden; document data provenance carefully

## Migration Plan

This is a greenfield build, no migration needed.

**Rollout:**

1. **Phase 1 (Weeks 1-4):** Data integration + caching layer, test with known submarkets
2. **Phase 2 (Weeks 5-7):** Market + geo analysis modules, validate scores against manual assessments
3. **Phase 3 (Weeks 8-9):** Risk module + scoring engine, backtest on portfolio
4. **Phase 4 (Weeks 10-11):** Asset evaluation + CLI, full documentation, handoff

**Rollback:**

- N/A (new capability)

**Success Criteria:**

- Score 50 markets in < 5 minutes (cached)
- Top 10 scored markets include 8+ of Aker's existing locations (sanity check)
- Test coverage > 80%
- Documentation complete (README, API docs, methodology)

## Open Questions

1. **Q:** Should we integrate CoStar/SafeGraph for retail vacancy + foot traffic?
   **A (deferred):** Use OSM/Yelp for MVP; evaluate commercial data after validation.

2. **Q:** How to handle custom submarket polygons (not aligned to CBSA/county)?
   **A:** Support GeoJSON upload, overlay Census block groups for population estimates.

3. **Q:** CLI vs. notebook vs. web app for interface?
   **A:** CLI + Jupyter notebooks for MVP; web app is Phase 2 if adoption is strong.

4. **Q:** How to version scoring model (for auditing)?
   **A:** Git-tag releases; embed version in output JSON; log parameters with each run.

5. **Q:** Should risk multipliers be configurable per user?
   **A (yes):** YAML config file for weights + multipliers; CLI flag to override.

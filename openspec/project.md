# Project Context

## Purpose

Aker Investment Platform is a data-driven residential real estate investment screening tool for identifying and evaluating multifamily opportunities across Colorado, Utah, and Idaho. The platform systematically scores submarkets against Aker Companies' investment thesis: **supply-constrained markets with innovation-driven employment, urban convenience, and outdoor recreation access**.

**Core Goals:**

- Quantitative screening of 50+ submarkets in < 5 minutes
- Risk-adjusted underwriting with climate and regulatory multipliers
- Reproducible analysis with audit trails and versioned scoring logic
- Support for Aker's "Invest → Create → Operate" business model

## Tech Stack

**Core Framework:**

- Python 3.11+ (managed via micromamba in `.venv`)
- Package manager: micromamba with conda-forge channel (prefer over pip)

**Data & Analytics:**

- pandas - Data manipulation and analysis
- geopandas - Geospatial vector operations
- numpy - Numerical computations
- scikit-learn - Normalization and statistical analysis
- shapely - Geometric operations

**Infrastructure:**

- SQLite - Local caching layer for API responses (7-30 day TTL)
- requests - HTTP client for API integrations
- click/argparse - CLI interface

**Visualization & Reporting:**

- matplotlib - Charts and visualizations
- seaborn - Statistical graphics
- Jupyter - Interactive notebooks for analysis

**Testing & Quality:**

- pytest - Unit and integration testing (target: 80%+ coverage)
- ruff - Linting
- black - Code formatting

## Project Conventions

### Code Style

- Follow PEP 8 with black formatting (line length: 88)
- Type hints required for public functions
- Docstrings: Google style for all public modules/classes/functions
- Use dataclasses for structured data (see design doc for key types)
- Prefer functional patterns; avoid mutable global state
- Maximum function length: ~50 lines

**Naming Conventions:**

- Modules: `snake_case` (e.g., `data_integration`, `market_analysis`)
- Classes: `PascalCase` (e.g., `APIConnector`, `ScoredMarket`)
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: prefix with single underscore `_method_name`

### Architecture Patterns

**Modular Monolith (6 capabilities):**

```
src/Claude45_Demo/
├── data_integration/   # API connectors + SQLite cache
├── market_analysis/    # Supply, jobs, demographics scoring
├── geo_analysis/       # Spatial analysis, POI proximity
├── risk_assessment/    # Climate, regulatory, insurance risks
├── asset_evaluation/   # Deal archetypes, product fit
└── scoring_engine/     # Weighted scoring + risk multipliers
```

**Design Principles:**

- Each module is independently testable
- Communicate via shared dataclasses (Submarket, MarketMetrics, RiskAssessment, ScoredMarket)
- Abstract base class `APIConnector` for all data sources
- Aggressive caching to respect API rate limits
- Graceful degradation for missing data (score with available data, flag confidence)

**Key Patterns:**

- Factory pattern for API connectors
- Strategy pattern for state-specific logic (CO/UT/ID)
- Repository pattern for cache access
- Normalization pipeline: raw data → 0-100 scale → weighted sum

### Testing Strategy

**Coverage Requirements:**

- Minimum 80% test coverage for core calculation logic
- 100% coverage for scoring algorithms and risk multipliers

**Test Types:**

1. **Unit tests** - Pure functions, calculations, normalization
2. **Integration tests** - API connectors with mock responses (default)
3. **Integration tests (real APIs)** - CI-only, limited runs to respect rate limits
4. **Validation tests** - Backtest on Aker's known good markets (10 assets)
5. **Performance benchmarks** - 50 markets in < 5 minutes

**Test Organization:**

```
tests/
├── test_data_integration.py
├── test_market_analysis.py
├── test_geo_analysis.py
├── test_risk_assessment.py
├── test_asset_evaluation.py
├── test_scoring_engine.py
├── fixtures/              # Mock API responses
└── validation/            # Known good markets dataset
```

**Quality Gates:**

- All tests pass: `pytest -q`
- Linting clean: `ruff check src tests`
- Formatting clean: `black .`
- Coverage report: `pytest --cov=src --cov-report=html`

### Git Workflow

**Branch Naming:**

- Feature branches: `cx/<short-task>` (e.g., `cx/add-census-api`)
- Hotfix branches: `hotfix/<issue>`

**Commit Conventions:**

- Use conventional commits: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`
- Examples:
  - `feat: add Census ACS API connector`
  - `fix: handle missing CBSA codes in BLS data`
  - `test: add validation for wildfire risk scores`
  - `docs: document scoring methodology`

**PR Guidelines:**

- Keep changes focused and reviewable
- Include tests for new functionality
- Update documentation for public APIs
- Stage partial diffs for logical commits
- Run `lint` and `pytest` tasks before opening PR

## Domain Context

**Investment Thesis (Four Pillars):**

1. **Supply Constraints (30% weight)** - Topographically constrained markets with housing scarcity
   - Building permits per 1,000 households (lower = better)
   - Regulatory friction (permit timelines, zoning)
   - Physical constraints (terrain, protected lands)

2. **Innovation Employment (30% weight)** - Knowledge economy job growth
   - Tech, healthcare, education employment mix
   - Location Quotient (LQ) for innovation sectors
   - Job growth momentum (3-year CAGR)
   - Human capital indicators (education attainment, startup density)

3. **Urban Convenience (20% weight)** - 15-minute city accessibility
   - Walkability scores (POI density, intersection density)
   - Transit access (GTFS-based isochrones)
   - Retail/amenity health (OSM POI coverage)

4. **Outdoor Recreation (20% weight)** - Proximity to nature assets
   - Trail access (USGS, NPS, RIDB APIs)
   - Parks and open space
   - Water recreation (lakes, rivers)
   - Mountain/elevation access

**Risk Adjustments:**

- Wildfire risk (USFS Wildfire Hazard Potential, LANDFIRE)
- Flood zones (FEMA NFHL)
- Climate hazards (hail, air quality, water stress)
- Regulatory friction (permit delays, impact fees)
- Insurance cost proxies

**Deal Archetypes:**

- **Value-add** - Stabilized properties needing light renovation ($90-$180/unit rent lift)
- **Heavy lift** - Major repositioning (2+ years)
- **Ground-up** - New construction on entitled land

**Product Types (Preferred):**

- Garden-style (3-4 story wood-frame)
- Low-rise (4-6 story podium)
- Mid-rise (6-10 story Type-I concrete)
- Mixed-use infill

**Geographic Scope:**

- Colorado (Front Range priority: Denver, Boulder, Fort Collins, Colorado Springs)
- Utah (Wasatch Front: Salt Lake, Provo, Ogden + Silicon Slopes)
- Idaho (Boise metro, Sun Valley, Coeur d'Alene)

## Important Constraints

**Technical Constraints:**

- API rate limits (Census: 500 req/day; BLS: 500 req/day; others vary)
- Must run on standard hardware (16GB RAM laptops, cloud VMs)
- Performance target: 50 markets in < 5 minutes (cached), < 10 minutes (cold)
- SQLite cache size limits (~1GB expected)

**Data Constraints:**

- Federal data: 1-5 year lags (Census ACS is T-1 year)
- API reliability varies (USGS stable; state portals flaky)
- Missing data for rural submarkets (graceful degradation required)
- No proprietary data in MVP (CoStar, Placer.ai deferred to Phase 2)

**Business Constraints:**

- Must align with Aker's thesis (not generic investment tool)
- Transparent scoring (no black-box ML; stakeholder explainability required)
- Validation against existing portfolio (sanity check: 8 of 10 assets in top scores)

**Regulatory Constraints:**

- State-specific zoning/permitting data (CO/UT/ID each different)
- Water rights vary by state (CO prior appropriation; UT/ID hybrid systems)
- Environmental regulations (EPA, state EPAs)

## External Dependencies

**Federal Data Sources (20+ APIs):**

*Economic & Demographic:*

- Census Bureau (ACS, Building Permits, Business Formation Stats)
- BLS (Current Employment Statistics, Local Area Unemployment, QCEW)
- BEA (Regional GDP, Personal Income)
- IRS SOI (Migration data - CSV ingestion)
- LEHD LODES (Workplace/daytime population)

*Geospatial:*

- OpenStreetMap / Overpass API (POI data, amenities)
- GTFS / Transitland (Public transit analysis)
- OSRM / OpenRouteService (Routing, isochrones)
- USGS 3DEP (Elevation, slope, terrain)
- NPS / RIDB (Parks, trails, recreation)

*Climate & Risk:*

- FEMA NFHL (Flood zones - WMS/WFS)
- USFS Wildfire Hazard Potential (Wildfire risk)
- LANDFIRE (Fuel models, fire behavior)
- EPA AQS (Air quality)
- NOAA (Climate normals, smoke days)
- USGS (Seismic hazard)

*State-Specific:*

- Colorado: CDSS (Water rights), DOLA (Local planning)
- Utah: DWR (Water data), GOED (Economic data)
- Idaho: DWR (Water rights), Commerce (Economic development)

**Data Update Frequencies:**

- Census ACS: Annual (September release)
- BLS CES: Monthly (lag: 1-2 months)
- Building Permits: Monthly
- OSM: Continuous (weekly snapshots)
- FEMA flood maps: 18-24 month cycles
- Wildfire data: Annual updates

**Rate Limits & Caching:**

- Cache TTL: 7 days (economic), 30 days (demographic), 90 days (geospatial)
- Exponential backoff for retries (max 3 attempts)
- Fallback to cached data on API failures
- Manual cache refresh command for critical updates

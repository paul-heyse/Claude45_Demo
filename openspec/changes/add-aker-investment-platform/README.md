# Aker Investment Platform - OpenSpec Change Proposal

## Overview

This change proposal defines a comprehensive Python-based investment analysis platform for Aker Companies. The platform will systematically screen, evaluate, and underwrite residential real estate opportunities in Colorado, Utah, and Idaho based on Aker's four-pillar investment thesis.

## What's Been Created

This proposal includes **9 documentation files** totaling ~3,000 lines of detailed specifications:

### Core Documents

1. **`proposal.md`** - Executive summary, rationale, and impact analysis
2. **`tasks.md`** - 100 implementation tasks organized into 10 phases
3. **`design.md`** - Architecture decisions, data flows, and technical patterns

### Capability Specifications (6 modules)

Each spec defines requirements with concrete scenarios (WHEN/THEN format):

4. **`specs/data-integration/spec.md`** - API connectors for 40+ data sources
   - Census (ACS, Building Permits, BFS)
   - BLS (employment, wages, industry mix)
   - BEA (GDP, income)
   - EPA (air quality, environmental compliance)
   - FEMA (flood zones)
   - USGS (elevation, wildfire, seismic)
   - OpenStreetMap, GTFS, and more
   - SQLite caching layer with TTL
   - Rate limit compliance and error recovery

5. **`specs/market-analysis/spec.md`** - Investment screening logic
   - Supply constraint scoring (permits, vacancy, regulatory friction)
   - Innovation employment analysis (tech, healthcare, education, manufacturing)
   - Urban convenience scoring (15-minute accessibility, retail health, transit)
   - Demographic and economic trends
   - Rent affordability and cost burden
   - Market report generation

6. **`specs/geo-analysis/spec.md`** - Geospatial computation
   - Outdoor recreation access (trails, ski, water, public lands)
   - Isochrone travel time analysis (walk, drive, transit)
   - Elevation and slope constraints
   - Intersection density and bikeway connectivity
   - Flood zone and water body buffers
   - Airport noise and view shed protections
   - POI counting and density metrics
   - Air quality and smoke day analysis

7. **`specs/risk-assessment/spec.md`** - Risk modeling
   - Wildfire risk (WHP, fuel models, WUI classification)
   - Flood risk (FEMA zones, BFE, historical events)
   - Seismic hazard (PGA, fault proximity)
   - Hail and wind exposure
   - Snow load and avalanche terrain
   - Water rights and drought stress (CO/UT/ID specific)
   - Radon potential
   - Environmental compliance (EPA ECHO)
   - Regulatory friction (permit timelines, rent control)
   - Insurance cost proxies
   - Risk multipliers (0.9-1.1 for cap rate adjustments)

8. **`specs/scoring-engine/spec.md`** - Ranking and prioritization
   - Weighted composite scoring (Supply 30%, Jobs 30%, Urban 20%, Outdoor 20%)
   - Risk-adjusted scoring
   - Normalization functions (linear, percentile, logarithmic, threshold)
   - Submarket ranking and peer grouping
   - Sensitivity analysis and Monte Carlo simulation
   - Benchmark comparisons (portfolio, regional, national)
   - Visualizations (radar charts, heatmaps, scatter plots, choropleth maps)
   - Confidence scoring (data completeness, freshness, method uncertainty)
   - Non-fit filtering (negative screening rules)
   - Score versioning and audit trail
   - Batch processing with parallel execution

9. **`specs/asset-evaluation/spec.md`** - Property filtering
   - Product type classification (garden, low-rise, mid-rise, mixed-use)
   - Deal archetype identification (value-add, heavy lift, ground-up)
   - Unit mix optimization (studio/1BR for job cores, 2BR/3BR for families)
   - Amenity scoring (bike/ski storage, dog wash, EV charging, remote work spaces)
   - Parking ratio optimization (0.5-0.8 infill, 1.1-1.4 suburban)
   - CapEx scope and ROI estimation (interior upgrades, systems, sustainability)
   - Operating model support (NPS tracking, programming budgets, lease-up velocity)
   - Construction cost adjustments (winter premiums, mountain logistics, labor)
   - Diligence checklist generation
   - Portfolio fit analysis
   - Exit strategy and hold period modeling

## Validation

✅ **The proposal has been validated with `openspec validate --strict`** - all requirements have proper scenario formatting.

## Data Sources Catalog

The platform integrates 40+ data sources organized by domain:

### Demographics & Economics

- U.S. Census ACS API (population, income, education, commute)
- IRS SOI Migration (county-to-county flows)
- LEHD LODES (daytime population, workplace analytics)
- BLS (employment, wages, unemployment by NAICS)
- BEA Regional API (GDP, personal income)
- Census BFS (business formation statistics)

### Housing & Permits

- Census Building Permits Survey (monthly permits by county/CBSA)

### Urban Amenities & Transit

- OpenStreetMap Overpass API (POIs, bikeways)
- Transitland / GTFS (transit stops, schedules, frequencies)
- Google Places / Yelp / Foursquare (optional licensed data)

### Geospatial & Terrain

- USGS 3DEP (elevation, slope)
- OSRM / OpenRouteService (isochrones, routing)
- USFWS National Wetlands Inventory
- USGS NHDPlus (hydrography)

### Hazards & Risk

- FEMA NFHL (flood zones, BFE)
- EPA AQS / AirNow (air quality)
- NOAA HMS (smoke polygons)
- USFS Wildfire Hazard Potential & Risk to Communities
- LANDFIRE (vegetation, fuels)
- USGS PAD-US (public lands)
- NPS API / RIDB (trailheads, facilities)
- USGS National Seismic Hazard Model
- NOAA NCEI Storm Events / SPC (hail, wind, tornado)
- PRISM / NOAA CDO (snowfall normals)

### Regulatory & Compliance

- Socrata / ArcGIS Feature Services (city/county permits)
- Accela / Tyler EnerGov (permit systems where exposed)
- EPA ECHO (environmental violations)
- HUD FMR & Income Limits (affordability)
- EIA (electricity prices)

### State-Specific (CO/UT/ID)

- Colorado DWR / CDSS HydroBase (water rights)
- Utah Division of Water Rights (points of diversion)
- Idaho Department of Water Resources (water rights)

## Technology Stack

### Core Dependencies

- **pandas** - Data manipulation and analysis
- **geopandas** - Geospatial data operations
- **numpy** - Numerical computations
- **scikit-learn** - Machine learning utilities (clustering, normalization)
- **requests** - HTTP API calls
- **shapely** - Geometric operations
- **matplotlib** - Static visualizations
- **seaborn** - Statistical visualizations
- **folium** - Interactive maps (optional)

### Environment

- Python 3.9+ managed via micromamba (`.venv`)
- SQLite for local caching (no external database required)
- Install via `micromamba install -c conda-forge <package>`

## Implementation Roadmap

The implementation is organized into 10 phases with 100 tasks:

### Phase 1: Foundation & Data Integration (Tasks 1.1-1.10)

Build API connector framework, caching layer, and integrate Census, BLS, BEA, IRS, LEHD data sources.

### Phase 2: Geographic Analysis Module (Tasks 2.1-2.10)

Implement OSM POI extraction, GTFS transit analysis, isochrone calculation, elevation/slope analysis, trail proximity.

### Phase 3: Market Analysis Module (Tasks 3.1-3.10)

Build supply constraint calculator, job mix analyzer, demographic trends, urban convenience scoring, market reports.

### Phase 4: Risk Assessment Module (Tasks 4.1-4.10)

Implement flood zone analysis, wildfire risk calculator, air quality analyzer, hazard overlays, regulatory friction estimator.

### Phase 5: Scoring Engine (Tasks 5.1-5.10)

Build weighted scoring algorithm, normalization functions, risk multipliers, ranking system, visualizations.

### Phase 6: Asset Evaluation Module (Tasks 6.1-6.10)

Create product type taxonomy, deal archetype classifier, unit mix optimizer, amenity checker, ROI estimator.

### Phase 7: State-Specific Rules (Tasks 7.1-7.7)

Implement CO/UT/ID specific logic for water rights, regulatory patterns, climate peculiarities.

### Phase 8: CLI & Reporting (Tasks 8.1-8.10)

Build command-line interface, report generation, data refresh commands, user documentation.

### Phase 9: Testing & Validation (Tasks 9.1-9.10)

Achieve 80%+ test coverage, validate against Aker's known markets, performance benchmarks.

### Phase 10: Documentation & Deployment (Tasks 10.1-10.10)

Write comprehensive README, API docs, data source catalog, deployment guide, example notebooks.

**Estimated Timeline: 8-11 weeks for MVP**

## Success Criteria

- ✅ Score 50+ submarkets across CO/UT/ID in < 5 minutes (cached runs)
- ✅ API caching reduces subsequent runs to < 30 seconds
- ✅ Risk scores correlate with actual insurance premium variance
- ✅ Top-scoring submarkets include Aker's existing portfolio locations (sanity check)
- ✅ Test coverage > 80% for core calculation logic
- ✅ Professional-grade documentation and deployment guide

## Next Steps

### 1. Review and Approval

**ACTION REQUIRED:** Review this proposal and provide approval to proceed with implementation.

Questions to consider:

- Does this capture Aker's investment thesis accurately?
- Are there additional data sources or features needed?
- Are the success metrics appropriate?
- Is the timeline realistic for your needs?

### 2. API Key Acquisition

Obtain API keys for data sources that require registration:

- Census API: <https://api.census.gov/data/key_signup.html> (free)
- BLS API: <https://www.bls.gov/developers/api_signature_v2.shtml> (free, higher limits with key)
- EPA APIs: Most are open, no key required
- Optional: Google Places, Foursquare, Mapbox (paid)

### 3. Implementation Start

Once approved, we can begin with Phase 1 (Foundation & Data Integration):

- Set up project structure
- Install dependencies
- Build abstract API connector class
- Implement caching layer
- Test with Census API integration

### 4. Iterative Development

- Complete tasks sequentially per the roadmap
- Mark tasks complete in `tasks.md` as we progress
- Run tests continuously to maintain quality
- Generate sample reports after each phase for validation

## Questions or Clarifications?

Before implementation begins, please review and confirm:

1. **Scope Alignment** - Does this proposal match your vision for the platform?
2. **Data Access** - Do you have or can you obtain necessary API keys?
3. **Timeline** - Is the 8-11 week MVP timeline acceptable?
4. **Priorities** - Should any capabilities be built first or deferred?
5. **Portfolio Data** - Can you provide existing Aker portfolio locations for validation?
6. **Custom Requirements** - Any Aker-specific logic or data sources not captured here?

## Viewing This Proposal

You can explore the proposal structure using OpenSpec CLI:

```bash
# Show full proposal
openspec show add-aker-investment-platform

# View specific capability spec
openspec show add-aker-investment-platform --type change

# Show differences (since this is new, shows all as additions)
openspec diff add-aker-investment-platform

# Re-validate
openspec validate add-aker-investment-platform --strict

# List all tasks
cat openspec/changes/add-aker-investment-platform/tasks.md

# View specific spec
cat openspec/changes/add-aker-investment-platform/specs/market-analysis/spec.md
```

## Contact

Ready to proceed? Let's start building this platform for Aker Companies!

---

**Status:** ✅ Proposal Complete, Awaiting Approval
**Created:** 2025-09-30
**Validation:** Passed `openspec validate --strict`
**Change ID:** `add-aker-investment-platform`

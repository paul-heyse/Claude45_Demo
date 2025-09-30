# Aker Investment Platform - Proposal

## Why

Aker Companies requires a data-driven platform to systematically identify, evaluate, and underwrite residential real estate investment opportunities in Colorado, Utah, and Idaho. The current manual process lacks the ability to efficiently screen markets against Aker's thesis: supply-constrained markets with innovation-driven employment, urban convenience, and outdoor recreation access. This platform will enable quantitative scoring, risk assessment, and deal prioritization aligned with Aker's "Invest → Create → Operate" model.

## What Changes

- **NEW CAPABILITY: Market Analysis** - Quantitative screening of submarkets across four pillars: supply constraints, innovation employment, urban convenience, and outdoor access
- **NEW CAPABILITY: Geographic Analysis** - Spatial analysis for terrain constraints, proximity to amenities, transit accessibility, and outdoor recreation
- **NEW CAPABILITY: Risk Assessment** - Climate risk modeling including wildfire, flood, hail, insurance cost factors, and regulatory friction
- **NEW CAPABILITY: Data Integration** - API connector framework for 40+ federal, state, and commercial data sources with intelligent caching
- **NEW CAPABILITY: Asset Evaluation** - Property filtering by deal archetype (value-add, heavy lift, ground-up) and Aker product fit criteria
- **NEW CAPABILITY: Scoring Engine** - Weighted scoring system (Supply 30%, Jobs 30%, Urban 20%, Outdoor 20%) with risk multipliers

## Impact

### Affected Specs

- **market-analysis** (new) - Core investment screening logic
- **geo-analysis** (new) - Geospatial computation layer
- **risk-assessment** (new) - Risk modeling and underwriting adjustments
- **data-integration** (new) - Data pipeline foundation
- **asset-evaluation** (new) - Deal filtering and product fit
- **scoring-engine** (new) - Ranking and prioritization

### Affected Code

- `src/Claude45_Demo/` (new modules for each capability)
- `tests/` (comprehensive test suite per capability)
- Python dependencies: pandas, geopandas, numpy, scikit-learn, requests, shapely, matplotlib, seaborn
- Environment: micromamba-managed `.venv` with conda-forge packages

### Key Deliverables

1. **Professional-grade Python package** with modular architecture
2. **API integration layer** for Census, BLS, BEA, EPA, FEMA, USGS, and 30+ other sources
3. **Scoring algorithms** implementing Aker's investment thesis
4. **Risk modeling** for climate, regulatory, and operational factors
5. **Comprehensive documentation** and test coverage
6. **CLI tools** for market screening and report generation

### Timeline Estimate

- Phase 1 (Data Integration): 3-4 weeks
- Phase 2 (Market & Geo Analysis): 2-3 weeks
- Phase 3 (Risk & Scoring): 2 weeks
- Phase 4 (Asset Evaluation & Polish): 1-2 weeks
- **Total: 8-11 weeks for MVP**

## Success Metrics

- Ability to score 50+ submarkets across CO/UT/ID in < 5 minutes
- API response caching reduces subsequent runs to < 30 seconds
- Risk scores correlate with insurance premium variance (validation)
- Top-scoring submarkets match Aker's existing portfolio locations (sanity check)
- Test coverage > 80% for core calculation logic

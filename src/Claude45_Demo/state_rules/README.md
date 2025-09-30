# Module 7: State-Specific Rules (CO/UT/ID)

## Overview

This module implements state-specific business logic, data connectors, and regulatory patterns for Colorado, Utah, and Idaho - the three primary markets for Aker Companies' investment platform.

## Purpose

While the core risk assessment, market analysis, and geographic modules provide general-purpose functionality, many factors require state-specific knowledge:

- **Water Rights**: Each state has unique water law (CO prior appropriation, UT beneficial use, ID SRBA adjudication)
- **Natural Hazards**: Regional patterns (CO Front Range hail alley, UT Wasatch Fault seismic, ID wildland-urban interface)
- **Regulatory Environment**: State-level policies (ID rent control prohibition, CO inclusionary zoning patterns, UT pro-development stance)
- **Economic Drivers**: Region-specific growth patterns (Silicon Slopes tech, CO outdoor recreation, ID in-migration from CA/WA)

## Module Structure

```
src/Claude45_Demo/state_rules/
├── __init__.py
├── README.md (this file)
├── colorado.py          # CO-specific logic
├── utah.py              # UT-specific logic
├── idaho.py             # ID-specific logic
├── data_connectors/     # State API connectors
│   ├── __init__.py
│   ├── co_cdss.py       # CO Division of Water Resources CDSS
│   ├── ut_dwr.py        # UT Division of Water Rights
│   └── id_dwr.py        # ID Department of Water Resources
└── patterns/            # Regulatory pattern library
    ├── __init__.py
    ├── jurisdictions.py # Permit timelines by jurisdiction
    └── zoning.py        # State zoning nomenclature

tests/test_state_rules/
├── test_colorado.py
├── test_utah.py
├── test_idaho.py
├── test_data_connectors/
│   ├── test_co_cdss.py
│   ├── test_ut_dwr.py
│   └── test_id_dwr.py
└── test_integration/    # Multi-factor state integration tests
    └── test_state_integration.py
```

## Tasks Breakdown

### Task 7.1: Colorado-Specific Logic ✅ (In Progress)

**Module**: `colorado.py`
**Key Features**:

- Front Range hail risk premium calculation
- CDSS HydroBase water rights integration
- Mountain snow load adjustments (ASCE 7 + elevation)
- Denver metro permit timeline patterns
- Wildfire WUI risk for mountain counties

**Data Sources**:

- CO Division of Water Resources CDSS REST API
- NOAA SPC hail climatology (CO-specific)
- ASCE 7 snow load maps (CO mountain zones)
- Municipal permit databases (Denver, Boulder, Aurora, etc.)

**Tests**: `tests/test_state_rules/test_colorado.py`

### Task 7.2: Utah-Specific Logic

**Module**: `utah.py`
**Key Features**:

- Wasatch Front topography constraints
- Silicon Slopes employment data integration
- Utah DWR Points of Diversion water rights
- Seismic risk (Wasatch Fault)
- Pro-development regulatory advantage

**Data Sources**:

- Utah Division of Water Rights open data
- EDCUtah economic development data
- USGS Wasatch Fault seismic data
- Municipal zoning databases

**Tests**: `tests/test_state_rules/test_utah.py`

### Task 7.3: Idaho-Specific Logic

**Module**: `idaho.py`
**Key Features**:

- Treasure Valley in-migration tracking (IRS SOI + local data)
- North Idaho wildland-urban interface fire risk
- IDWR water rights and SRBA adjudication
- Property tax advantage (1% effective rate)
- Remote-work migration patterns

**Data Sources**:

- Idaho Department of Water Resources (IDWR)
- IRS SOI migration data (ID-specific analysis)
- Idaho Department of Lands fire data
- Municipal permit/tax databases

**Tests**: `tests/test_state_rules/test_idaho.py`

### Task 7.4: State Data Connectors

**Module**: `data_connectors/`
**Implementation**:

- `co_cdss.py`: Colorado CDSS HydroBase REST API connector
- `ut_dwr.py`: Utah DWR Points of Diversion connector
- `id_dwr.py`: Idaho IDWR GIS services connector

**Pattern**: All connectors inherit from `data_integration.APIConnector` base class for:

- Caching (SQLite backend, 30-day TTL for water rights)
- Rate limiting
- Error handling
- Retry logic

**Tests**: `tests/test_state_rules/test_data_connectors/`

### Task 7.5: State Regulatory Pattern Library

**Module**: `patterns/`
**Implementation**:

- `jurisdictions.py`: Permit timeline lookup by jurisdiction
- `zoning.py`: State zoning nomenclature parser

**Data Format**: JSON pattern files with:

- Jurisdiction metadata (name, state, type)
- Historical permit timelines (median, P90, by project type)
- Zoning code mappings (zone → density, height, FAR)
- Known regulatory quirks (design review boards, inclusionary zoning)

**Tests**: Unit tests for pattern matching logic

### Task 7.6: State Integration Tests

**Module**: `tests/test_state_rules/test_integration/`
**Scenarios**:

1. **CO Mountain Property**: Summit County property with water rights, snow loads, wildfire, hail
2. **UT Wasatch Front**: Salt Lake County property with seismic, topography, Silicon Slopes employment
3. **ID Treasure Valley**: Boise metro property with in-migration, water rights, favorable tax environment

**Purpose**: Validate that state-specific logic integrates correctly with core modules (risk assessment, market analysis, geo analysis)

### Task 7.7: Data Source Documentation

**Deliverable**: Comprehensive markdown documentation
**Contents**:

- API endpoint catalog
- Authentication methods
- Rate limits and quotas
- Data update frequencies
- Known data quality issues
- Example queries
- Troubleshooting guide

**Location**: `docs/state_data_sources.md`

## Development Patterns

### State Analyzer Classes

Each state analyzer follows this pattern:

```python
class ColoradoStateAnalyzer:
    """CO-specific analysis and adjustments."""

    def __init__(self, cdss_connector=None):
        self.cdss = cdss_connector or COCDSSConnector()

    def calculate_hail_risk_premium(self, latitude, longitude):
        """Front Range hail alley adjustment."""
        # Implementation
        return {"hail_premium_pct": 0.15, "roof_reserve": 18}

    def assess_water_rights(self, county_fips, parcel_id):
        """Query CDSS HydroBase for water availability."""
        # Implementation
        return {"availability_score": 75, "tap_fee": 12000}

    def calculate_state_multiplier(self, base_scores):
        """Apply CO-specific adjustments to base scores."""
        # Combines hail, water, snow, regulatory adjustments
        return {"co_multiplier": 1.03, "adjustments": [...]}
```

### Integration with Core Modules

State analyzers **augment** (not replace) core modules:

```python
# Core wildfire module provides general WUI risk
wildfire_score = wildfire_analyzer.calculate_composite_risk(...)

# Colorado module adds state-specific context
co_adjustments = colorado_analyzer.apply_wildfire_adjustments(
    wildfire_score,
    county="Summit"
)

# Final score includes both general + state-specific
final_score = wildfire_score + co_adjustments["state_premium"]
```

### Testing Strategy

1. **Unit Tests**: Each state method tested independently with mocks
2. **Integration Tests**: Multi-module scenarios (water + hazards + regulatory)
3. **Fixtures**: Realistic property data for each state
4. **Mocks**: State API responses cached as test fixtures

## Data Source Reference

### Colorado

| Source | Endpoint | Update Frequency | Coverage |
|--------|----------|------------------|----------|
| CDSS HydroBase | <https://dwr.state.co.us/rest/> | Real-time | Statewide water structures |
| NOAA SPC Hail | SPC climatology database | Annual | Event history 1955-present |
| Municipal Permits | Varies by jurisdiction | Weekly/monthly | Denver metro primarily |

### Utah

| Source | Endpoint | Update Frequency | Coverage |
|--------|----------|------------------|----------|
| UT DWR | Utah Open Data portal | Monthly | Statewide water rights |
| EDCUtah | Business relocation data | Quarterly | Silicon Slopes focus |
| USGS Seismic | Wasatch Fault database | Continuous | Northern Utah |

### Idaho

| Source | Endpoint | Update Frequency | Coverage |
|--------|----------|------------------|----------|
| IDWR | GIS services + public DB | Weekly | Statewide, SRBA areas |
| IRS SOI | Annual migration CSV | Annual (lag 2 years) | County-to-county flows |
| ID Dept of Lands | Fire history | Annual | Statewide |

## Contributing

When adding state-specific logic:

1. **Check Spec First**: Read `specs/state-rules/spec.md` for requirements
2. **Follow TDD**: Write tests before implementation
3. **Use Base Classes**: Inherit from `APIConnector` for data connectors
4. **Document Data**: Update data source catalog with new APIs
5. **Add Integration Test**: Create end-to-end scenario for state
6. **Update README**: Add patterns and examples

## Common Pitfalls

1. **Don't Duplicate Core Logic**: State modules should augment, not replace core risk/market/geo analysis
2. **Cache Aggressively**: Water rights and regulatory data change infrequently (30-day TTL appropriate)
3. **Handle Missing Data**: Not all parcels have water rights records; provide defaults
4. **State Nomenclature**: CO "water district" ≠ UT "water conservancy district" ≠ ID "water district"
5. **Jurisdiction Boundaries**: Don't assume county == water management area

## Examples

### Example 1: Colorado Property Evaluation

```python
from Claude45_Demo.state_rules import ColoradoStateAnalyzer

co = ColoradoStateAnalyzer()

# Get hail risk premium for Denver property
hail_risk = co.calculate_hail_risk_premium(39.7392, -104.9903)
# Returns: {"hail_premium_pct": 0.18, "roof_reserve": 20}

# Check water rights for Boulder County parcel
water = co.assess_water_rights(county_fips="08013", parcel_id="123-456-789")
# Returns: {"availability_score": 45, "tap_fee": 25000, "augmentation_required": True}
```

### Example 2: Multi-State Comparison

```python
from Claude45_Demo.state_rules import ColoradoStateAnalyzer, UtahStateAnalyzer

co = ColoradoStateAnalyzer()
ut = UtahStateAnalyzer()

# Compare regulatory environments
co_reg = co.assess_regulatory_environment("Denver")
ut_reg = ut.assess_regulatory_environment("Salt Lake City")

# UT typically has faster permits, lower friction
assert ut_reg["friction_score"] < co_reg["friction_score"]
```

## Status

- ✅ Task 7.1: Colorado-specific logic (IN PROGRESS)
- ⏳ Task 7.2-7.7: Pending

**Current Progress**: Module framework complete, Task 7.1 implementation in progress.

## Questions / Support

For questions about state-specific logic, consult:

- **Spec**: `specs/state-rules/spec.md`
- **Core Modules**: `risk_assessment/`, `market_analysis/`, `geo_analysis/`
- **Data Integration Patterns**: `data_integration/base.py`

This module is designed for team collaboration - each state (CO/UT/ID) can be developed independently!

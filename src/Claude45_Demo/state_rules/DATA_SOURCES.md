# State-Specific Data Sources

Comprehensive guide to CO/UT/ID data sources, APIs, and integration patterns for Module 7.

## Colorado Data Sources

### CO Division of Water Resources (CDSS HydroBase)

**API Endpoint**: `https://dwr.state.co.us/rest/get/api/v2/`

**Purpose**: Water structures, decreed water rights, administrative calls, augmentation plans

**Authentication**: No API key required (public API)

**Update Frequency**: Real-time for admin calls, monthly for structures/rights

**Coverage**: Statewide (all 7 water districts)

**Rate Limits**: None documented, but recommend 1 req/sec for courtesy

**Example Query**:

```bash
GET /structures/byCounty/08013  # Boulder County structures
GET /waterrights/byCounty/08013
GET /administrativecalls/active
```

**Data Quality**:

- ✅ Comprehensive structure database
- ✅ Historical decrees back to 1800s
- ⚠️ Augmentation plan data requires manual parsing
- ⚠️ Parcel-level linkage not always available

**Recommended Cache TTL**: 30 days (water rights change infrequently)

### NOAA Storm Prediction Center (SPC) Hail Climatology

**Endpoint**: `https://www.spc.noaa.gov/climo/reports/`

**Purpose**: Historical hail event data for Front Range "hail alley"

**Authentication**: None required

**Update Frequency**: Annual (after storm season)

**Coverage**: 1955-present, point-level events

**Rate Limits**: None, but data is bulk CSV download

**Data Quality**:

- ✅ Long historical record
- ✅ Georeferenced events
- ⚠️ Under-reporting in rural areas (pre-2000)
- ⚠️ Size estimates may be subjective

**Recommended Cache TTL**: 90 days (annual updates)

### CO Municipal Permit Systems

**Sources**: Varies by jurisdiction (Accela, Socrata, custom portals)

**Coverage**: Denver, Aurora, Boulder, Fort Collins, Colorado Springs

**Authentication**: Varies (some require API keys)

**Update Frequency**: Weekly to monthly

**Data Quality**:

- ✅ Denver/Aurora: Accela Civic Platform (good API)
- ✅ Boulder: Custom portal (CSV exports)
- ⚠️ Smaller jurisdictions: Limited/no API access
- ⚠️ Data formats inconsistent across jurisdictions

**Recommended Approach**: Use pattern library (Task 7.5) for most jurisdictions, supplement with API data for major cities

**Recommended Cache TTL**: 7 days

---

## Utah Data Sources

### UT Division of Water Rights

**Endpoint**: `https://opendata.utah.gov/`

**Purpose**: Points of Diversion, water right numbers, beneficial use

**Authentication**: No API key required

**Update Frequency**: Monthly

**Coverage**: Statewide water rights database

**Rate Limits**: None documented

**Example Query**:

```bash
GET /resource/i3an-tk73.json?county=Salt+Lake
```

**Data Quality**:

- ✅ Well-maintained open data portal
- ✅ GeoJSON/CSV formats available
- ⚠️ Great Salt Lake critical management area data requires separate queries
- ⚠️ Drought status not in API (use USDM integration)

**Recommended Cache TTL**: 30 days

### EDCUtah (Economic Development Corporation of Utah)

**Endpoint**: Custom reports and CSV downloads

**Purpose**: Tech company expansions, Silicon Slopes employment data

**Authentication**: None (public reports)

**Update Frequency**: Quarterly

**Coverage**: Focus on Silicon Slopes corridor (Salt Lake, Utah, Davis counties)

**Data Quality**:

- ✅ High-quality company expansion announcements
- ⚠️ No programmatic API (scraping/CSV parsing required)
- ⚠️ Lag time on job creation data (announced vs. actual)

**Recommended Approach**: Manual CSV ingestion, cached for 90 days

### USGS Wasatch Fault Data

**Endpoint**: <https://earthquake.usgs.gov/hazards/>

**Purpose**: Seismic hazard, fault trace, ground motion estimates

**Authentication**: None

**Update Frequency**: Irregular (model updates every 5-10 years)

**Coverage**: Wasatch Front (Brigham City to Nephi)

**Data Quality**:

- ✅ USGS National Seismic Hazard Model (NSHM) is authoritative
- ✅ Fault trace shapefiles available
- ⚠️ Site-specific analysis requires geotechnical study

**Recommended Cache TTL**: 365 days (infrequent updates)

---

## Idaho Data Sources

### Idaho Department of Water Resources (IDWR)

**Endpoint**: `https://research.idwr.idaho.gov/`

**Purpose**: Water right claims, SRBA adjudication status, priority dates

**Authentication**: None (public database)

**Update Frequency**: Weekly

**Coverage**: Statewide, with detailed SRBA coverage

**Rate Limits**: None documented

**Example Query**:

```bash
GET /s/wris-public/   # Web interface
# GIS services: https://gis.idwr.idaho.gov/arcgis/rest/services/
```

**Data Quality**:

- ✅ Comprehensive SRBA database
- ✅ Priority date tracking
- ⚠️ Senior vs. junior rights require manual interpretation
- ⚠️ Municipal service boundaries not in water rights DB

**Recommended Cache TTL**: 30 days

### IRS SOI Migration Data

**Endpoint**: `https://www.irs.gov/statistics/soi-tax-stats-migration-data`

**Purpose**: County-to-county migration flows (Treasure Valley in-migration tracking)

**Authentication**: None (public CSV downloads)

**Update Frequency**: Annual (2-year lag)

**Coverage**: All US counties, inflows/outflows

**Data Quality**:

- ✅ Authoritative migration source (based on tax returns)
- ✅ State-level detail on origin/destination
- ⚠️ 2-year data lag
- ⚠️ Does not capture non-filers (students, low-income)

**Recommended Cache TTL**: 365 days

### Idaho Department of Lands (IDL) Fire Data

**Endpoint**: `https://www.idl.idaho.gov/fire/`

**Purpose**: Historical fire perimeters, WUI classifications, Firewise communities

**Authentication**: None

**Update Frequency**: Annual (after fire season)

**Coverage**: Statewide, focus on North Idaho panhandle

**Data Quality**:

- ✅ Good WUI mapping
- ⚠️ Fire perimeters vary in quality (older fires less accurate)
- ⚠️ Insurance carrier availability not in public data

**Recommended Cache TTL**: 90 days

---

## Common Integration Patterns

### Pattern 1: Water Rights Query

```python
from Claude45_Demo.state_rules.water_rights import ColoradoWaterRightsConnector

co_water = ColoradoWaterRightsConnector(cache_ttl_days=30)
result = co_water.query_structures(county_fips="08013", parcel_id="123")
# Returns: structures, water_rights, water_court_district
```

### Pattern 2: Regulatory Pattern Lookup

```python
from Claude45_Demo.state_rules.patterns import get_jurisdiction_pattern

pattern = get_jurisdiction_pattern("colorado", "Boulder")
median_days = pattern["median_permit_days"]  # 210
```

### Pattern 3: State Analyzer Integration

```python
from Claude45_Demo.state_rules import ColoradoStateAnalyzer

co = ColoradoStateAnalyzer()
multiplier = co.calculate_state_multiplier(
    latitude=39.7392,
    longitude=-104.9903,
    elevation_ft=5280,
    county_fips="08031",
    parcel_id="DEN-001",
    jurisdiction="Denver"
)
# Returns: co_multiplier (0.9-1.1), adjustments, risk_premium_pct
```

---

## Troubleshooting

### Issue: Water rights data not found for parcel

**Cause**: Parcel may not have direct water rights; relies on municipal supply

**Solution**: Check for municipal service availability; use default availability score

### Issue: Permit timeline data missing for jurisdiction

**Cause**: Small jurisdictions not in pattern library

**Solution**: Use state-level default (CO: 90 days, UT: 70 days, ID: 50 days)

### Issue: API rate limiting

**Cause**: Exceeding undocumented rate limits

**Solution**: Implement exponential backoff; use caching aggressively (30-day TTL for water rights)

### Issue: Stale data

**Cause**: Cached data past TTL

**Solution**: Check `CacheManager` TTL settings; purge expired entries

---

## Future Enhancements

### Planned for Future Releases

1. **Full API Integration (Task 7.4 extension)**:
   - Live CDSS REST API queries (CO)
   - UT Open Data portal integration
   - IDWR GIS service queries

2. **Advanced Pattern Matching**:
   - Machine learning for permit timeline prediction
   - Zoning code parsing (NLP)

3. **Real-Time Data Feeds**:
   - CDSS administrative calls (drought curtailment tracking)
   - USDM drought monitor integration
   - USGS earthquake alerts

4. **Additional States**:
   - Expand to MT, WY, NM, AZ (Mountain West corridor)

---

## Data Source Summary Table

| Source | State | Update Freq | Cache TTL | API Available | Auth Required |
|--------|-------|-------------|-----------|---------------|---------------|
| CDSS HydroBase | CO | Real-time | 30 days | ✅ REST | ❌ |
| NOAA SPC Hail | CO | Annual | 90 days | ⚠️ CSV | ❌ |
| UT DWR | UT | Monthly | 30 days | ✅ REST | ❌ |
| EDCUtah | UT | Quarterly | 90 days | ❌ CSV | ❌ |
| USGS Seismic | UT | 5-10 years | 365 days | ✅ REST | ❌ |
| IDWR | ID | Weekly | 30 days | ⚠️ GIS | ❌ |
| IRS SOI | ID | Annual | 365 days | ❌ CSV | ❌ |
| ID Dept of Lands | ID | Annual | 90 days | ⚠️ Shapefiles | ❌ |

---

## Contact & Support

For data source issues or API changes:

- **Colorado**: CDSS Help Desk - <cdss_help@state.co.us>
- **Utah**: UT DWR - <waterrights@utah.gov>
- **Idaho**: IDWR Public Info - <idwr@idwr.idaho.gov>

For Module 7 code issues:

- See `src/Claude45_Demo/state_rules/README.md`
- Check `tests/test_state_rules/` for examples

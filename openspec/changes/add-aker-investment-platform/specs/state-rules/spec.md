# State-Specific Rules Capability - Delta Spec

## ADDED Requirements

### Requirement: Colorado State-Specific Logic

The system SHALL implement Colorado-specific analysis including Front Range hail climatology, CDSS HydroBase water rights integration, mountain snow loads, and Denver metro permit patterns.

#### Scenario: Colorado hail risk premium

- **WHEN** the system evaluates a property in the Colorado Front Range corridor
- **THEN** it applies elevated hail risk scoring (CO hail alley: 10+ events/decade)
- **AND** calculates roof replacement reserve premium ($15-20/unit/year)
- **AND** estimates insurance deductible impact (5% wind/hail deductible common)
- **AND** returns CO-specific hail adjustment to risk multiplier

#### Scenario: CDSS HydroBase water rights query

- **WHEN** the system analyzes a Colorado property requiring water supply
- **THEN** it queries CO Division of Water Resources CDSS HydroBase REST API
- **AND** retrieves water structures, decreed rights, and augmentation plan requirements
- **AND** calculates water tap fee estimates by municipality
- **AND** identifies water court districts and priority date constraints
- **AND** returns water availability score with CO-specific regulatory context

#### Scenario: Mountain snow load requirements

- **WHEN** the system evaluates properties above 7,000 ft elevation in CO
- **THEN** it applies ASCE 7 ground snow loads specific to CO mountain zones
- **AND** estimates structural cost premium (10-15% for >50 psf loads)
- **AND** checks winter construction timeline constraints (Nov-Mar premium)
- **AND** returns snow load cost adjustment

#### Scenario: Denver metro permit timeline patterns

- **WHEN** the system evaluates regulatory friction in Denver metro submarkets
- **THEN** it applies known permit timelines by jurisdiction (Boulder >180 days, Aurora ~45 days)
- **AND** identifies design review board requirements (historic districts)
- **AND** flags inclusionary zoning mandates (Denver IZ, Boulder 25% affordable)
- **AND** returns jurisdiction-specific regulatory friction score

### Requirement: Utah State-Specific Logic

The system SHALL implement Utah-specific analysis including Wasatch Front topography constraints, Silicon Slopes employment data, Utah Division of Water Rights integration, and seismic considerations.

#### Scenario: Wasatch Front topography constraints

- **WHEN** the system evaluates Utah properties along the Wasatch Front
- **THEN** it analyzes steep-slope parcels (>15% grade) and bench development feasibility
- **AND** identifies fault-adjacent parcels (Wasatch Fault active)
- **AND** calculates geotechnical investigation requirements
- **AND** returns topography-adjusted development feasibility score

#### Scenario: Silicon Slopes employment growth

- **WHEN** the system analyzes Utah County or Salt Lake County employment
- **THEN** it applies Silicon Slopes tech cluster job growth multipliers
- **AND** retrieves EDCUtah data on company expansions and relocations
- **AND** calculates innovation employment momentum (Lehi/Draper/Provo tech corridor)
- **AND** returns UT-specific employment growth score

#### Scenario: Utah water rights and drought

- **WHEN** the system evaluates water availability for a Utah property
- **THEN** it queries Utah Division of Water Rights Points of Diversion database
- **AND** identifies critical management areas (Great Salt Lake watershed)
- **AND** checks for municipal water availability and connection fees
- **AND** assesses multi-year drought impact on supply reliability
- **AND** returns UT-specific water constraint level

#### Scenario: Utah regulatory environment

- **WHEN** the system evaluates Utah jurisdictions for regulatory friction
- **THEN** it applies state-level pro-development policy context
- **AND** identifies local zoning complexity (Salt Lake City design review)
- **AND** notes Utah's generally favorable permit timelines (<90 days typical)
- **AND** returns UT regulatory advantage vs. baseline

### Requirement: Idaho State-Specific Logic

The system SHALL implement Idaho-specific analysis including Treasure Valley migration metrics, wildland-urban interface fire risk, North Idaho recreation access, and water rights from Idaho Department of Water Resources.

#### Scenario: Treasure Valley in-migration momentum

- **WHEN** the system evaluates Boise/Meridian/Nampa markets
- **THEN** it calculates net in-migration rates from IRS SOI data (CA/WA/OR flows)
- **AND** analyzes housing supply elasticity (permits/household growth ratio)
- **AND** tracks remote-work migration patterns (2020-2024 surge)
- **AND** returns ID-specific population momentum score

#### Scenario: Wildland-urban interface in North Idaho

- **WHEN** the system evaluates Coeur d'Alene or surrounding forest-interface properties
- **THEN** it applies elevated wildfire risk for ID panhandle WUI areas
- **AND** checks Idaho Department of Lands fire history and fuel management
- **AND** estimates wildfire insurance availability (limited carrier market)
- **AND** calculates defensible space and Firewise community requirements
- **AND** returns ID WUI-specific wildfire adjustment

#### Scenario: Idaho water rights adjudication

- **WHEN** the system evaluates water supply for an Idaho property
- **THEN** it queries Idaho Department of Water Resources (IDWR) water rights database
- **AND** identifies if property is in Snake River Basin Adjudication (SRBA) area
- **AND** checks for senior water rights vs. junior rights during drought curtailment
- **AND** calculates municipal hook-up availability and impact fees
- **AND** returns ID-specific water rights complexity score

#### Scenario: Idaho property tax and regulatory simplicity

- **WHEN** the system evaluates Idaho tax and regulatory environment
- **THEN** it applies Idaho's favorable property tax rates (1% effective)
- **AND** notes state-level prohibition on rent control
- **AND** identifies streamlined permitting in most jurisdictions
- **AND** returns ID regulatory advantage score

### Requirement: State Data Connector Integration

The system SHALL provide state-specific API connectors for CO CDSS HydroBase, Utah Division of Water Rights, Idaho Department of Water Resources, and state employment/migration databases.

#### Scenario: Colorado CDSS HydroBase connector

- **WHEN** the system queries Colorado water data
- **THEN** it connects to CDSS REST API (<https://dwr.state.co.us/rest/>)
- **AND** retrieves water structures, administrative calls, and court decree data
- **AND** caches responses with appropriate TTL (water rights change infrequently)
- **AND** handles CDSS API rate limits and error responses gracefully
- **AND** returns structured water rights data

#### Scenario: Utah DWR Points of Diversion connector

- **WHEN** the system queries Utah water rights
- **THEN** it connects to Utah Open Data portal water rights datasets
- **AND** retrieves point of diversion locations, rights, and permit status
- **AND** parses UT-specific water right nomenclature
- **AND** returns structured UT water data

#### Scenario: Idaho IDWR connector

- **WHEN** the system queries Idaho water rights
- **THEN** it connects to IDWR GIS services and public water rights database
- **AND** retrieves water right claims, permits, and SRBA adjudication status
- **AND** handles ID-specific water right types (surface, groundwater, storage)
- **AND** returns structured ID water data

### Requirement: State Regulatory Pattern Library

The system SHALL maintain a pattern library of state and local regulatory environments, permit timelines, zoning patterns, and policy quirks for CO/UT/ID jurisdictions.

#### Scenario: Jurisdiction permit timeline lookup

- **WHEN** the system needs regulatory friction estimates for a jurisdiction
- **THEN** it queries the state regulatory pattern library
- **AND** retrieves historical median permit timelines (if available)
- **AND** identifies known high-friction jurisdictions (Boulder CO, Park City UT)
- **AND** applies default state-level estimates where local data unavailable
- **AND** returns jurisdiction-specific or state-default friction score

#### Scenario: Zoning pattern recognition

- **WHEN** the system evaluates zoning for a property
- **THEN** it applies state-specific zoning nomenclature (CO PUD, UT RMF, ID R-3)
- **AND** recognizes common overlay districts by state (CO historic, UT hillside)
- **AND** identifies state-level zoning preemption rules
- **AND** returns interpreted zoning complexity with state context

### Requirement: State-Specific Integration Testing

The system SHALL provide integration tests that validate state-specific logic across multiple data sources and risk factors for realistic CO/UT/ID property scenarios.

#### Scenario: Colorado mountain property integration test

- **WHEN** the system evaluates a Summit County CO mountain property
- **THEN** it integrates: CDSS water rights, high snow loads, wildfire WUI risk, hail exposure, resort area dynamics
- **AND** produces composite CO mountain market score
- **AND** validates all CO-specific adjustments applied correctly
- **AND** returns integration test results

#### Scenario: Utah Wasatch Front property integration test

- **WHEN** the system evaluates a Salt Lake County property
- **THEN** it integrates: UT water rights, seismic risk (Wasatch Fault), Silicon Slopes employment, topography constraints
- **AND** produces composite UT urban market score
- **AND** validates all UT-specific adjustments applied correctly
- **AND** returns integration test results

#### Scenario: Idaho Treasure Valley property integration test

- **WHEN** the system evaluates a Boise metro property
- **THEN** it integrates: IDWR water rights, in-migration momentum, wildfire interface risk, favorable tax/regulatory environment
- **AND** produces composite ID growth market score
- **AND** validates all ID-specific adjustments applied correctly
- **AND** returns integration test results

### Requirement: State Data Source Documentation

The system SHALL maintain comprehensive documentation of state-specific data sources, API peculiarities, data quality issues, update frequencies, and usage patterns.

#### Scenario: Data source catalog export

- **WHEN** a developer needs to understand state data sources
- **THEN** the system provides documentation including:
  - API endpoints and authentication methods
  - Data update frequencies and historical availability
  - Known data quality issues (missing counties, stale data)
  - Rate limits and usage quotas
  - Example queries and response formats
  - Troubleshooting guidance
- **AND** exports catalog to markdown/HTML for team reference

#### Scenario: Data freshness monitoring

- **WHEN** the system uses state-specific data
- **THEN** it logs data vintage and freshness warnings
- **AND** alerts if cached state data exceeds recommended TTL
- **AND** documents known seasonal data gaps (e.g., winter construction data)
- **AND** returns data quality metadata with results

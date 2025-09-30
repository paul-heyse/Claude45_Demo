# Risk Assessment Capability - Delta Spec

## ADDED Requirements

### Requirement: Wildfire Risk Scoring

The system SHALL calculate wildfire risk scores (0-100, higher = more risk) using USFS Wildfire Hazard Potential, LANDFIRE fuel models, and historical fire perimeters to assess exposure in the wildland-urban interface.

#### Scenario: Wildfire Hazard Potential lookup

- **WHEN** the system evaluates wildfire risk for a point location
- **THEN** it queries USFS WHP raster for hazard score (1-5 scale)
- **AND** buffers point by 1km and calculates mean and max WHP
- **AND** normalizes to 0-100 score (5 = 100, 1 = 20)
- **AND** returns wildfire hazard component score

#### Scenario: Fuel model analysis

- **WHEN** the system assesses fire behavior potential
- **THEN** it queries LANDFIRE for fuel models in surrounding area
- **AND** identifies high-risk fuel types (timber, brush)
- **AND** calculates percentage of 1km buffer in high-risk fuels
- **AND** returns fuel load component score 0-100

#### Scenario: Historical fire proximity

- **WHEN** the system evaluates burn history
- **THEN** it retrieves USGS/NIFC fire perimeter history (20-year lookback)
- **AND** calculates distance to nearest large fire (>1000 acres)
- **AND** counts fires within 10km in last 20 years
- **AND** returns fire history component score 0-100

#### Scenario: Wildland-urban interface classification

- **WHEN** the system determines WUI status
- **THEN** it classifies location as Interface, Intermix, or Non-WUI using USFS Wildfire Risk to Communities data
- **AND** applies higher risk score for Intermix zones (vegetation + structures)
- **AND** documents evacuation route constraints (single access)
- **AND** returns WUI risk flag and score adjustment

### Requirement: Flood Risk Assessment

The system SHALL assess flood risk using FEMA NFHL flood zones, base flood elevations, historical flood events, and climate projection adjustments.

#### Scenario: FEMA flood zone classification

- **WHEN** the system evaluates flood exposure for a parcel
- **THEN** it queries FEMA NFHL for intersecting flood zones
- **AND** maps zones to risk categories (A/AE/VE = high, X shaded = moderate, X unshaded = minimal)
- **AND** calculates percentage of parcel in each zone
- **AND** returns flood zone risk score 0-100

#### Scenario: Base flood elevation analysis

- **WHEN** building elevation data is available
- **THEN** the system retrieves BFE from FEMA NFHL
- **AND** compares structure elevation to BFE (positive freeboard = lower risk)
- **AND** calculates flood insurance cost proxy (SFHA + low freeboard = high premium)
- **AND** returns elevation risk score and insurance multiplier

#### Scenario: Historical flood event proximity

- **WHEN** the system assesses past flooding
- **THEN** it queries NOAA NCEI or FEMA disaster declarations for flood events in county (20-year lookback)
- **AND** counts presidentially declared disasters
- **AND** identifies chronic flooding (>3 events in 20 years)
- **AND** returns historical flood component score 0-100

#### Scenario: Dam and levee influence

- **WHEN** the system evaluates flood infrastructure
- **THEN** it identifies upstream dams or adjacent levees from National Inventory of Dams
- **AND** checks dam hazard classification and condition rating
- **AND** applies risk adjustment for high-hazard dams with fair/poor condition
- **AND** returns infrastructure risk flag

### Requirement: Seismic Hazard Assessment

The system SHALL evaluate earthquake risk using USGS National Seismic Hazard Model, fault proximity, and historical seismicity for building code and insurance considerations.

#### Scenario: Peak ground acceleration lookup

- **WHEN** the system evaluates seismic design requirements
- **THEN** it queries USGS NSHM for 2% in 50-year PGA (0.2s spectral acceleration)
- **AND** maps PGA to seismic design category per ASCE 7
- **AND** estimates construction cost premium for seismic bracing
- **AND** returns seismic risk score 0-100

#### Scenario: Fault proximity check

- **WHEN** the system is in California, Nevada, Utah, or other high-seismicity states
- **THEN** it retrieves Quaternary faults from USGS database
- **AND** calculates distance to nearest active fault
- **AND** flags sites within fault rupture zone (<100m)
- **AND** returns fault proximity risk component

### Requirement: Hail and Wind Hazard Assessment

The system SHALL analyze historical severe weather events (hail, wind, tornadoes) using NOAA SPC and NCEI data to assess property damage risk and insurance costs.

#### Scenario: Hail climatology analysis

- **WHEN** the system evaluates hail risk for a county (especially Colorado Front Range)
- **THEN** it queries NOAA SPC hail climatology or NCEI storm events for hail >1 inch
- **AND** counts events per decade and calculates frequency
- **AND** identifies hail alley regions with annual >2% probability
- **AND** returns hail risk score 0-100

#### Scenario: Wind and tornado exposure

- **WHEN** the system assesses severe wind risk
- **THEN** it retrieves historical tornado tracks and wind reports from SPC
- **AND** calculates density of EF1+ tornadoes within 50km (normalized)
- **AND** estimates straight-line wind risk from downburst climatology
- **AND** returns wind risk score 0-100

### Requirement: Snow Load and Winter Hazard Assessment

The system SHALL calculate snow load requirements and winter weather impact using PRISM snowfall normals, elevation, and ASCE 7 design values.

#### Scenario: Design snow load calculation

- **WHEN** the system evaluates construction requirements in mountain areas
- **THEN** it retrieves ground snow load from ASCE 7 maps or PRISM data
- **AND** applies elevation adjustments for site-specific topography
- **AND** estimates structural cost premium for heavy snow loads (>50 psf)
- **AND** returns snow load value and cost multiplier

#### Scenario: Avalanche terrain identification

- **WHEN** the system evaluates high-elevation sites
- **THEN** it queries USFS or state avalanche path inventories
- **AND** checks if parcel intersects known avalanche runout zones
- **AND** flags sites with avalanche risk as unbuildable or requiring mitigation
- **AND** returns avalanche risk flag

### Requirement: Water Availability and Rights Assessment

The system SHALL evaluate water supply constraints, drought risk, and water rights availability using state databases and USGS water stress indices.

#### Scenario: Colorado water rights lookup

- **WHEN** the system analyzes a site in Colorado
- **THEN** it queries CDSS HydroBase REST API for water structures and rights
- **AND** identifies if parcel has decreed water rights or relies on municipal supply
- **AND** checks for augmentation plan requirements
- **AND** returns water availability score 0-100 (lower = more constrained)

#### Scenario: Utah water rights query

- **WHEN** the system analyzes a site in Utah
- **THEN** it queries Utah Division of Water Rights Points of Diversion
- **AND** identifies available water sources and permitted uses
- **AND** checks for critical management areas or moratoria
- **AND** returns water constraint level

#### Scenario: Drought and water stress analysis

- **WHEN** the system evaluates long-term water supply
- **THEN** it retrieves USGS water stress index or NOAA drought monitor history
- **AND** calculates percentage of last 10 years in moderate+ drought
- **AND** identifies groundwater overdraft basins
- **AND** returns water stress component score 0-100

### Requirement: Radon Potential Assessment

The system SHALL evaluate radon exposure potential using EPA/USGS county-level radon zone classifications to inform construction mitigation requirements.

#### Scenario: Radon zone lookup

- **WHEN** the system evaluates indoor air quality risk
- **THEN** it retrieves EPA Map of Radon Zones classification for county (Zone 1/2/3)
- **AND** applies radon mitigation cost estimate for Zone 1 (high potential)
- **AND** documents mitigation requirement in risk report
- **AND** returns radon risk level (high/moderate/low)

### Requirement: Environmental Compliance and Contamination Risk

The system SHALL identify nearby regulated sites, violations, and environmental compliance issues using EPA ECHO and Facility Registry Services.

#### Scenario: Nearby contaminated sites

- **WHEN** the system performs environmental due diligence
- **THEN** it queries EPA FRS for Superfund, brownfield, or RCRA sites within 1km
- **AND** retrieves EPA ECHO for violation history and enforcement actions
- **AND** flags sites with ongoing remediation or uncontrolled releases
- **AND** returns environmental risk score 0-100

#### Scenario: Air and water discharge proximity

- **WHEN** the system evaluates pollution sources
- **THEN** it identifies NPDES water discharge permits and air permits within 2km
- **AND** checks for significant violations (CAA, CWA) in last 3 years
- **AND** documents pollutant types and quantities
- **AND** returns pollution proximity risk flag

### Requirement: Regulatory Friction and Entitlement Risk

The system SHALL estimate permitting timelines, zoning complexity, and political risk for development projects using permit data and policy analysis.

#### Scenario: Permit timeline estimation

- **WHEN** the system evaluates a submarket's regulatory environment
- **THEN** it queries city/county permit databases (Accela, Socrata) for historical timelines
- **AND** calculates median days from application to permit issuance for MF projects
- **AND** identifies submarkets with >180-day timelines as high-friction
- **AND** returns regulatory friction score 0-100

#### Scenario: Zoning overlay complexity

- **WHEN** parcel-level zoning data is available
- **THEN** the system retrieves zoning code and overlay districts
- **AND** identifies design review requirements, height limits, parking minimums
- **AND** flags inclusionary zoning or affordable housing mandates
- **AND** documents density restrictions (FAR, units/acre)
- **AND** returns zoning complexity score 0-100

#### Scenario: Rent control and eviction policy risk

- **WHEN** the system evaluates regulatory risk for value-add strategies
- **THEN** it checks for local rent control or rent stabilization ordinances
- **AND** identifies just-cause eviction requirements
- **AND** flags jurisdictions with tenant-favorable political climates
- **AND** returns policy risk flag (low/moderate/high)

### Requirement: Insurance Cost Proxy Calculation

The system SHALL estimate relative property insurance costs using hazard scores, loss history, and state insurance market dynamics as a cap rate adjustment factor.

#### Scenario: Composite hazard to premium mapping

- **WHEN** the system calculates insurance cost proxy
- **THEN** it combines wildfire, flood, hail, wind scores into composite hazard index
- **AND** applies state-specific multipliers (CO hail, CA wildfire)
- **AND** estimates premium as percentage above baseline (0-3% of replacement cost)
- **AND** returns insurance cost multiplier for underwriting

#### Scenario: FEMA NFIP premium estimation

- **WHEN** a property is in SFHA and requires flood insurance
- **THEN** the system estimates annual flood premium based on zone and elevation
- **AND** applies NFIP rate table approximations
- **AND** documents if property is in Risk Rating 2.0 high-cost zone
- **AND** returns flood insurance annual cost estimate

### Requirement: Risk Multiplier Application

The system SHALL calculate a composite risk multiplier (0.9-1.1) that adjusts market scores or cap rates to reflect hazard exposure and regulatory friction.

#### Scenario: Risk multiplier calculation

- **WHEN** the system produces final scores for a submarket
- **THEN** it sums weighted risk components: wildfire 25%, flood 25%, regulatory 30%, insurance 20%
- **AND** normalizes to a multiplier range (0.9 = low risk, 1.0 = baseline, 1.1 = high risk)
- **AND** applies multiplier to market score OR suggests cap rate adjustment (+50 bps per 0.05 multiplier)
- **AND** returns multiplier with component breakdown

#### Scenario: Risk de-rating vs. exclusion

- **WHEN** a submarket has extreme risk (wildfire >90, flood >90)
- **THEN** the system flags market as "non-fit" rather than just applying multiplier
- **AND** documents rationale for exclusion
- **AND** allows override with user confirmation

### Requirement: Climate Projection Adjustments

The system SHALL incorporate forward-looking climate risk adjustments using available climate projection data (NOAA, USGS) for wildfire, drought, and extreme heat.

#### Scenario: Future wildfire risk trend

- **WHEN** climate projection data is available for a region
- **THEN** the system notes projected increase in fire season length and intensity
- **AND** applies forward-looking adjustment to current wildfire score (+10-20% for high-projection scenarios)
- **AND** documents projection source and scenario (e.g., RCP 4.5, SSP2)
- **AND** returns climate-adjusted wildfire score

#### Scenario: Drought frequency projection

- **WHEN** evaluating long-term water supply
- **THEN** the system retrieves USGS water stress projections (2050)
- **AND** flags markets with projected supply-demand imbalance
- **AND** applies water risk adjustment to long-hold (10+ year) underwriting
- **AND** returns climate-adjusted water score

### Requirement: Risk Report Generation

The system SHALL generate comprehensive risk assessment reports with hazard maps, scores, cost implications, and mitigation recommendations.

#### Scenario: Risk scorecard export

- **WHEN** a user requests a risk report for a submarket
- **THEN** the system generates PDF/HTML report including:
  - Risk multiplier summary and component scores
  - Hazard maps (wildfire, flood, seismic)
  - Insurance cost estimates and deductible structures
  - Regulatory friction documentation
  - Mitigation recommendations (e.g., defensible space, elevation certificates)
- **AND** exports raw risk data to CSV

#### Scenario: Diligence checklist generation

- **WHEN** a submarket proceeds to acquisition
- **THEN** the system generates risk-specific due diligence checklist
- **AND** flags required studies (Phase I ESA, geotech, flood cert)
- **AND** documents contractor requirements (wildfire-resistant materials)
- **AND** lists insurance carrier contacts for high-risk areas

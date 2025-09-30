# Market Analysis Capability - Delta Spec

## ADDED Requirements

### Requirement: Supply Constraint Scoring

The system SHALL calculate a supply constraint score (0-100) for submarkets based on topography, protected lands, regulatory friction, and building permit elasticity, where higher scores indicate more constrained (favorable) markets.

#### Scenario: Permit elasticity calculation

- **WHEN** the system analyzes a submarket for supply constraints
- **THEN** it calculates 3-year average building permits per 1,000 households
- **AND** normalizes the metric inversely (lower permits per HH = higher constraint score)
- **AND** weighs residential vacancy rates and median time-on-market
- **AND** returns elasticity component score 0-100

#### Scenario: Topographic constraint analysis

- **WHEN** the system evaluates terrain constraints
- **THEN** it calculates percentage of land with >15% slope
- **AND** identifies protected lands (national forests, parks, water bodies)
- **AND** applies buffers for floodplains, wetlands, airports
- **AND** returns topography component score 0-100

#### Scenario: Regulatory friction estimation

- **WHEN** the system assesses regulatory environment
- **THEN** it estimates median days from permit application to certificate of occupancy
- **AND** identifies presence of inclusionary zoning, design review boards, parking minimums
- **AND** checks for water/sewer hook-up moratoria
- **AND** returns regulatory component score 0-100

### Requirement: Innovation Employment Scoring

The system SHALL calculate an innovation employment score (0-100) based on job growth, location quotient, and human capital indicators in technology, healthcare, education, and advanced manufacturing sectors.

#### Scenario: Sector job growth analysis

- **WHEN** the system evaluates employment trends for a CBSA
- **THEN** it calculates 3-year CAGR for tech, healthcare, education, and manufacturing (NAICS codes)
- **AND** computes location quotient (LQ) for each sector relative to national average
- **AND** weights sectors by Aker relevance (tech 40%, healthcare 30%, education 20%, manufacturing 10%)
- **AND** returns job growth component score 0-100

#### Scenario: Human capital assessment

- **WHEN** the system evaluates workforce quality
- **THEN** it calculates bachelor's degree attainment percentage
- **AND** retrieves graduate enrollment counts from major universities
- **AND** estimates startup density (business formations per 10k population)
- **AND** analyzes net in-migration of 25-44 age cohort
- **AND** returns human capital component score 0-100

#### Scenario: Announced expansions tracking

- **WHEN** the system has access to announced employer expansions (optional data)
- **THEN** it boosts employment score based on major projects (universities, health systems, tech campuses)
- **AND** applies bonus points for federal research funding (NIH, NSF, DoD)
- **AND** documents expansion sources in score metadata

### Requirement: Urban Convenience Scoring

The system SHALL calculate an urban convenience score (0-100) based on 15-minute accessibility to daily needs, intersection density, transit availability, and neighborhood retail health.

#### Scenario: 15-minute accessibility analysis

- **WHEN** the system evaluates walkability for a submarket
- **THEN** it identifies grocery stores, pharmacies, K-8 schools, transit stops, urgent care within 15-minute walk/bike
- **AND** counts amenities reachable via isochrone analysis
- **AND** calculates intersection density per square kilometer
- **AND** measures bikeway network connectivity (ratio of protected/separated lanes)
- **AND** returns accessibility component score 0-100

#### Scenario: Retail health assessment

- **WHEN** the system evaluates neighborhood retail viability
- **THEN** it calculates daytime population within 1-mile radius (LEHD LODES)
- **AND** estimates local retail vacancy rate (OSM + commercial data where available)
- **AND** checks last-mile delivery coverage (proxy via population density)
- **AND** returns retail health component score 0-100

#### Scenario: Transit service quality

- **WHEN** the system evaluates public transit access
- **THEN** it identifies stops within 800m of submarket centroid
- **AND** calculates average weekday headway (wait time) for high-frequency routes
- **AND** assesses hours of operation and weekend service availability
- **AND** returns transit component score 0-100

### Requirement: Market Elasticity Metrics

The system SHALL calculate market elasticity indicators including rental vacancy rates, time-on-market for new multi-family lease-ups, and absorption rates to identify supply-demand imbalances.

#### Scenario: Vacancy rate analysis

- **WHEN** the system analyzes rental market tightness
- **THEN** it retrieves rental vacancy rate from ACS 5-year estimates
- **AND** normalizes vacancy inversely (lower vacancy = higher demand = better score)
- **AND** compares to state and national benchmarks
- **AND** returns vacancy component 0-100

#### Scenario: Lease-up velocity proxy

- **WHEN** commercial data is unavailable for time-on-market
- **THEN** the system uses building permits and occupancy lag as proxy
- **AND** estimates absorption rate from population growth vs. new units delivered
- **AND** applies conservative scoring for data uncertainty
- **AND** flags estimate in metadata

### Requirement: Demographic and Economic Trends

The system SHALL analyze population growth, household income trends, age distribution, and economic indicators to assess long-term market fundamentals.

#### Scenario: Population growth analysis

- **WHEN** the system evaluates demographic momentum
- **THEN** it calculates 5-year and 10-year population CAGR
- **AND** compares growth to state and regional averages
- **AND** analyzes age distribution with focus on 25-44 cohort (primary renter demographic)
- **AND** returns population trend score 0-100

#### Scenario: Income trend analysis

- **WHEN** the system evaluates economic health
- **THEN** it retrieves median household income time series
- **AND** calculates real income growth (inflation-adjusted)
- **AND** assesses income distribution (Gini coefficient or quintile ratios)
- **AND** compares to cost of living indices
- **AND** returns income trend score 0-100

#### Scenario: Net migration patterns

- **WHEN** the system analyzes migration flows using IRS SOI data
- **THEN** it calculates net in-migration (inflows - outflows) over 3 years
- **AND** computes adjusted gross income (AGI) per migrant household
- **AND** identifies top origin markets (talent/wealth sources)
- **AND** returns migration component score 0-100

### Requirement: Composite Market Scoring

The system SHALL combine supply constraint, innovation employment, and urban convenience sub-scores into a composite market score using configurable weights.

#### Scenario: Weighted market score calculation

- **WHEN** the system produces a final market score for a submarket
- **THEN** it normalizes all sub-scores to 0-100 range
- **AND** applies configured weights (default: Supply 30%, Jobs 30%, Urban 20%, Outdoor 20% from geo module)
- **AND** calculates weighted average
- **AND** includes confidence interval based on data completeness
- **AND** returns composite score with component breakdown

#### Scenario: Data completeness handling

- **WHEN** some metrics are unavailable for a submarket
- **THEN** the system calculates score using available components
- **AND** adjusts weights proportionally (e.g., if Urban data missing, redistribute 20% to Supply/Jobs)
- **AND** flags score as "partial" in metadata
- **AND** documents missing data sources

### Requirement: Benchmark Comparisons

The system SHALL compare submarket metrics to state, regional, and national benchmarks to provide context for absolute values.

#### Scenario: Percentile ranking

- **WHEN** the system calculates a metric for a submarket
- **THEN** it compares the value to all submarkets in the analysis set
- **AND** calculates percentile rank (0-100)
- **AND** identifies peer markets (similar scores)
- **AND** returns benchmark context in output

#### Scenario: State and national comparison

- **WHEN** the system presents employment or demographic data
- **THEN** it includes state average and national average for context
- **AND** calculates difference in percentage points or standard deviations
- **AND** highlights metrics significantly above/below benchmarks

### Requirement: Time Series Trend Detection

The system SHALL analyze time series data to identify acceleration, deceleration, or inflection points in key metrics that signal changing market conditions.

#### Scenario: Growth acceleration detection

- **WHEN** the system analyzes job growth time series
- **THEN** it fits a regression to identify trend slope
- **AND** detects acceleration (positive second derivative) or deceleration
- **AND** flags markets with recent inflection points (last 12-18 months)
- **AND** highlights anomalies (e.g., pandemic distortions)

#### Scenario: Seasonal adjustment

- **WHEN** monthly or quarterly data exhibits seasonality
- **THEN** the system applies seasonal adjustment (moving average or decomposition)
- **AND** reports both raw and adjusted values
- **AND** uses adjusted values for trend calculations

### Requirement: Market Momentum Indicators

The system SHALL calculate forward-looking momentum indicators such as building permit pipelines, business formation rates, and announced projects to complement historical trend analysis.

#### Scenario: Pipeline-to-completion lag

- **WHEN** the system evaluates future supply risk
- **THEN** it calculates building permits issued (not yet completed) relative to current stock
- **AND** estimates time-to-completion based on historical construction durations
- **AND** projects supply increase as percentage of current inventory
- **AND** flags markets with >5% near-term supply surge

#### Scenario: Business formation velocity

- **WHEN** the system analyzes entrepreneurial momentum
- **THEN** it retrieves Census BFS high-propensity business applications (HBA)
- **AND** calculates 4-quarter moving average and YoY growth
- **AND** compares to pre-pandemic baseline
- **AND** returns business formation momentum score 0-100

### Requirement: Sector-Specific Employment Analysis

The system SHALL provide detailed drill-down into specific employment sectors (tech, healthcare, education, manufacturing) with NAICS-level granularity and firm-size distributions.

#### Scenario: Tech sector deep-dive

- **WHEN** a user requests detailed tech employment analysis
- **THEN** the system retrieves QCEW data for NAICS 51 (Information), 5415 (Computer Systems Design), 5417 (R&D)
- **AND** calculates employment by firm size category
- **AND** identifies major employers (if data available)
- **AND** computes average wage and wage growth trends
- **AND** returns sector report with LQ and CAGR

### Requirement: Rent and Affordability Context

The system SHALL integrate HUD Fair Market Rent (FMR) data and income limits to assess affordability dynamics and regulatory risk from rent control or inclusionary zoning.

#### Scenario: Rent-to-income ratio

- **WHEN** the system evaluates affordability
- **THEN** it retrieves HUD FMR for 2BR units
- **AND** calculates FMR as percentage of area median income (AMI)
- **AND** identifies submarkets with >30% rent burden at 80% AMI
- **AND** flags high affordability pressure (risk of future rent control)

#### Scenario: Cost-burdened renter prevalence

- **WHEN** the system uses CHAS data for housing cost burden
- **THEN** it calculates percentage of renter households paying >30% of income on housing
- **AND** breaks down by income category (extremely low, very low, low, moderate)
- **AND** compares to state and national averages
- **AND** returns affordability stress indicator 0-100

### Requirement: Market Report Generation

The system SHALL generate human-readable market analysis reports with visualizations, data tables, and narrative summaries for investment committee review.

#### Scenario: Market scorecard export

- **WHEN** a user requests a market report for a submarket
- **THEN** the system generates a PDF/HTML report including:
  - Summary scorecard (4-pillar scores + composite)
  - Component metric tables with benchmarks
  - Time series charts for key trends
  - Peer market comparisons
  - Data source citations and freshness timestamps
- **AND** exports raw data to CSV for further analysis

#### Scenario: Batch market comparison

- **WHEN** a user analyzes multiple submarkets simultaneously
- **THEN** the system generates comparative visualizations (heatmap, radar chart, scatter plots)
- **AND** ranks markets by composite score
- **AND** highlights outliers and top performers
- **AND** exports batch results to Excel with multiple tabs

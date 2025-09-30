# Scoring Engine Capability - Delta Spec

## ADDED Requirements

### Requirement: Weighted Composite Scoring

The system SHALL calculate composite market scores by combining supply constraint, innovation employment, urban convenience, and outdoor access scores using configurable weights (default: 30%/30%/20%/20%).

#### Scenario: Default weighted score calculation

- **WHEN** the system calculates final score for a submarket
- **THEN** it retrieves component scores from market-analysis and geo-analysis modules
- **AND** normalizes all scores to 0-100 range
- **AND** applies weights: Supply 30%, Jobs 30%, Urban 20%, Outdoor 20%
- **AND** calculates weighted average: Score = Σ(component × weight)
- **AND** returns composite score 0-100 with component breakdown

#### Scenario: Custom weight configuration

- **WHEN** a user specifies custom weights in configuration file
- **THEN** the system validates weights sum to 100%
- **AND** applies custom weights to component scores
- **AND** documents weight configuration in output metadata
- **AND** allows comparison between default and custom scoring

#### Scenario: Missing component handling

- **WHEN** one or more component scores are unavailable
- **THEN** the system redistributes missing component's weight proportionally to available components
- **AND** flags score as "partial" in metadata
- **AND** documents which components are missing
- **AND** applies confidence penalty (reduces score by 5-10% per missing component)

### Requirement: Risk-Adjusted Scoring

The system SHALL apply risk multipliers (0.9-1.1) from the risk-assessment module to composite market scores to produce final investment attractiveness scores.

#### Scenario: Risk multiplier application

- **WHEN** the system applies risk adjustments to market score
- **THEN** it retrieves composite risk multiplier from risk-assessment module
- **AND** calculates risk-adjusted score = market_score × risk_multiplier
- **AND** documents risk adjustment magnitude (points gained/lost)
- **AND** returns final score with risk components documented

#### Scenario: Extreme risk exclusion

- **WHEN** a submarket has risk multiplier <0.85 (very high risk)
- **THEN** the system flags market as "non-fit" regardless of market score
- **AND** documents exclusion rationale (specific hazards)
- **AND** allows override with explicit user approval and documentation
- **AND** logs override decision for audit trail

### Requirement: Normalization Functions

The system SHALL provide normalization functions to convert diverse raw metrics (dollars, percentages, counts, minutes) to consistent 0-100 scale for scoring.

#### Scenario: Linear normalization

- **WHEN** a metric has known min/max bounds (e.g., unemployment rate 0-20%)
- **THEN** the system applies linear scaling: score = 100 × (value - min) / (max - min)
- **AND** handles inverse metrics (lower is better) by reversing: score = 100 - scaled_value
- **AND** returns normalized score 0-100

#### Scenario: Percentile-based normalization

- **WHEN** a metric lacks natural bounds but has distribution across submarkets
- **THEN** the system calculates percentile rank (0-100) across all submarkets
- **AND** uses percentile as normalized score
- **AND** updates percentiles when new submarkets are added to comparison set
- **AND** returns percentile score and rank

#### Scenario: Logarithmic normalization

- **WHEN** a metric has exponential distribution (e.g., job counts, population)
- **THEN** the system applies log transformation before linear scaling
- **AND** prevents extreme outliers from dominating score
- **AND** returns log-normalized score 0-100

#### Scenario: Threshold-based scoring

- **WHEN** a metric has meaningful threshold values (e.g., permits per 1k HH <5 = constrained)
- **THEN** the system applies step function or sigmoid curve around threshold
- **AND** assigns higher scores for values meeting Aker criteria
- **AND** returns threshold-based score with rationale

### Requirement: Submarket Ranking

The system SHALL rank submarkets by final score, providing percentile ranks, quartile assignments, and peer groupings for comparative analysis.

#### Scenario: Rank calculation

- **WHEN** the system scores multiple submarkets
- **THEN** it sorts submarkets by final risk-adjusted score (descending)
- **AND** assigns rank 1, 2, 3, ... N
- **AND** calculates percentile: 100 × (N - rank + 1) / N
- **AND** assigns quartile (Q1 = top 25%, Q2 = 25-50%, Q3 = 50-75%, Q4 = bottom 25%)
- **AND** returns rank, percentile, quartile for each submarket

#### Scenario: Peer group identification

- **WHEN** the system presents ranked results
- **THEN** it identifies peer markets within ±5 points of each submarket
- **AND** groups submarkets by similar score profiles (clustering on component scores)
- **AND** highlights markets with similar strengths/weaknesses
- **AND** returns peer group IDs and members

#### Scenario: Tie-breaking

- **WHEN** two submarkets have identical composite scores
- **THEN** the system applies tie-breaking rules: (1) higher supply score, (2) higher jobs score, (3) lower risk
- **AND** documents tie-breaker used
- **AND** assigns distinct ranks

### Requirement: Sensitivity Analysis

The system SHALL perform sensitivity analysis to show how score changes with weight adjustments, component variations, and data uncertainty.

#### Scenario: Weight sensitivity sweep

- **WHEN** a user requests sensitivity analysis
- **THEN** the system varies each weight ±10% while adjusting others proportionally
- **AND** recalculates scores for all submarkets
- **AND** identifies submarkets with high rank volatility (large rank swings)
- **AND** returns sensitivity matrix and visualization (tornado diagram)

#### Scenario: Component score perturbation

- **WHEN** the system evaluates scoring robustness
- **THEN** it perturbs each component score by ±10% (Monte Carlo simulation)
- **AND** recalculates final scores 1000 times
- **AND** calculates 90% confidence interval for each submarket's rank
- **AND** flags submarkets with wide confidence intervals (high uncertainty)

#### Scenario: What-if scenario modeling

- **WHEN** a user wants to test hypothetical changes
- **THEN** the system allows manual override of specific metrics (e.g., "what if job growth doubles?")
- **AND** recalculates affected component and final scores
- **AND** shows before/after rank comparison
- **AND** returns scenario analysis report

### Requirement: Benchmark Comparisons

The system SHALL compare submarket scores to Aker's existing portfolio, regional averages, and national benchmarks to provide investment context.

#### Scenario: Portfolio comparison

- **WHEN** Aker's current holdings are provided as reference dataset
- **THEN** the system calculates average scores for existing portfolio
- **AND** compares candidate submarkets to portfolio average
- **AND** identifies candidates that exceed portfolio quality (superior markets)
- **AND** flags candidates below portfolio average as off-strategy

#### Scenario: Regional peer benchmarking

- **WHEN** the system presents scores for Colorado markets
- **THEN** it calculates Colorado state average and median scores
- **AND** compares each submarket to state benchmarks
- **AND** identifies best-in-state and below-average markets
- **AND** repeats for Utah and Idaho

#### Scenario: National context

- **WHEN** the system has nationwide data (optional)
- **THEN** it compares CO/UT/ID submarkets to national percentiles
- **AND** positions regional markets in national context
- **AND** highlights submarkets in top national quartile

### Requirement: Score Visualization

The system SHALL generate visualizations (charts, maps, dashboards) to communicate scores, rankings, and component breakdowns to investment committee.

#### Scenario: Radar chart generation

- **WHEN** the system presents component scores for a submarket
- **THEN** it generates radar/spider chart with four axes (Supply, Jobs, Urban, Outdoor)
- **AND** plots submarket score, portfolio average, and benchmark on same chart
- **AND** enables quick visual identification of strengths/weaknesses
- **AND** exports chart as PNG/SVG/PDF

#### Scenario: Heatmap comparison

- **WHEN** the system presents scores for multiple submarkets
- **THEN** it generates heatmap table with submarkets as rows, components as columns
- **AND** color-codes cells (green = high, yellow = moderate, red = low)
- **AND** sorts rows by final score (descending)
- **AND** exports heatmap as image or interactive HTML

#### Scenario: Scatter plot analysis

- **WHEN** the system explores score relationships
- **THEN** it generates scatter plots (e.g., Supply vs. Jobs, Score vs. Risk)
- **AND** labels submarkets with names
- **AND** highlights top-scoring markets and portfolio holdings
- **AND** fits regression line to identify correlations
- **AND** exports scatter plot as image or interactive

#### Scenario: Choropleth map

- **WHEN** the system presents geographic distribution of scores
- **THEN** it generates choropleth map with submarkets color-coded by final score
- **AND** includes tooltip with scores on hover
- **AND** adds markers for Aker portfolio properties
- **AND** exports map as HTML or static image

### Requirement: Confidence Scoring

The system SHALL calculate confidence scores (0-100) for each submarket based on data completeness, data freshness, and method uncertainty.

#### Scenario: Data completeness factor

- **WHEN** the system calculates confidence for a submarket
- **THEN** it counts percentage of required metrics successfully retrieved
- **AND** applies completeness factor = min(100, pct_complete × 1.2)
- **AND** documents missing data sources
- **AND** penalizes confidence for critical missing data (e.g., no employment data)

#### Scenario: Data freshness factor

- **WHEN** the system evaluates data recency
- **THEN** it checks timestamp of cached data vs. current date
- **AND** applies freshness penalty for data >12 months old (linear decay)
- **AND** flags stale data sources in metadata
- **AND** calculates freshness factor 0-100

#### Scenario: Method uncertainty factor

- **WHEN** the system uses estimated or proxy metrics (vs. direct measurements)
- **THEN** it applies method uncertainty penalty (10-30% depending on proxy quality)
- **AND** documents which metrics are estimated
- **AND** calculates method factor 0-100

#### Scenario: Composite confidence score

- **WHEN** the system reports final score
- **THEN** it calculates confidence = 0.5×completeness + 0.3×freshness + 0.2×method
- **AND** returns confidence score 0-100 alongside final score
- **AND** flags submarkets with confidence <70% as "uncertain"
- **AND** suggests data refresh for low-confidence scores

### Requirement: Non-Fit Filtering

The system SHALL apply negative screening rules to exclude submarkets that violate Aker's investment criteria regardless of positive scores.

#### Scenario: Commodity sprawl exclusion

- **WHEN** a submarket has low supply constraint (<40) AND low urban convenience (<40)
- **THEN** the system flags market as "commodity greenfield sprawl"
- **AND** excludes from investment consideration
- **AND** documents non-fit rationale

#### Scenario: Auto-only desert exclusion

- **WHEN** a submarket has transit score <20 AND walkability score <30 AND outdoor access <40
- **THEN** the system flags market as "auto-only, weak outdoor signal"
- **AND** excludes from consideration
- **AND** documents non-fit rationale

#### Scenario: Hard rent control exclusion

- **WHEN** risk-assessment flags hard rent control with vacancy control
- **THEN** the system excludes market unless basis is 2+ standard deviations below FMR
- **AND** requires manual override with documented rationale
- **AND** logs exclusion decision

#### Scenario: Chronic hazard exclusion

- **WHEN** a submarket has wildfire score >90 AND flood score >80
- **THEN** the system flags market as "uninsurable or unaffordable insurance"
- **AND** excludes from consideration
- **AND** allows override only with insurance commitment letter

### Requirement: Score Versioning and Audit Trail

The system SHALL version scoring models, log all score calculations, and maintain audit trail for regulatory and investment committee review.

#### Scenario: Model version embedding

- **WHEN** the system calculates scores
- **THEN** it embeds model version (git tag or semantic version) in output
- **AND** documents weights, normalization functions, risk multiplier formula
- **AND** enables reproducibility (same inputs + same version = same outputs)
- **AND** returns version metadata with scores

#### Scenario: Calculation logging

- **WHEN** the system produces a final score
- **THEN** it logs: timestamp, submarket ID, component scores, weights, multiplier, final score, confidence, rank
- **AND** stores log in SQLite or CSV for audit trail
- **AND** enables filtering/querying of historical calculations
- **AND** supports "why this score?" queries with drill-down

#### Scenario: Score comparison across versions

- **WHEN** the system upgrades scoring model (new version)
- **THEN** it reruns scores for reference submarkets with old and new versions
- **AND** generates migration report showing score deltas
- **AND** documents changes in methodology
- **AND** flags submarkets with large rank changes (>10 positions)

### Requirement: Batch Processing

The system SHALL support batch scoring of 50+ submarkets in a single run with progress indicators, parallel processing, and failure recovery.

#### Scenario: Parallel submarket scoring

- **WHEN** the system scores multiple submarkets
- **THEN** it processes submarkets in parallel (up to 4-8 threads depending on API limits)
- **AND** respects API rate limits globally across threads
- **AND** displays progress bar (X of N complete)
- **AND** estimates time remaining

#### Scenario: Graceful failure handling

- **WHEN** scoring fails for one submarket (e.g., API timeout)
- **THEN** the system logs error and continues with remaining submarkets
- **AND** includes partial result with error message for failed submarket
- **AND** retries failed submarkets at end of batch
- **AND** returns batch report with success/failure counts

#### Scenario: Resume interrupted batch

- **WHEN** a batch run is interrupted (e.g., user abort, system crash)
- **THEN** the system detects partial results in cache
- **AND** offers to resume from last completed submarket
- **AND** skips already-scored submarkets
- **AND** completes batch efficiently

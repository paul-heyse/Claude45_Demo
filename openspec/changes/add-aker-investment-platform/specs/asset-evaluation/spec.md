# Asset Evaluation Capability - Delta Spec

## ADDED Requirements

### Requirement: Product Type Classification

The system SHALL classify potential assets by product type (garden, low-rise, mid-rise, mixed-use) and assess fit with Aker's target investment profile.

#### Scenario: Product type identification

- **WHEN** the system evaluates a multifamily property
- **THEN** it classifies as: Garden (1-2 stories, surface parking), Low-Rise (3-4 stories), Mid-Rise (5-8 stories), or High-Rise (9+ stories)
- **AND** assigns Aker fit score: Garden 100%, Low-Rise 100%, Mid-Rise 70% (select only), High-Rise 20% (rare)
- **AND** documents product type in property metadata

#### Scenario: Mixed-use assessment

- **WHEN** a property has ground-floor commercial and residential above
- **THEN** the system flags as mixed-use
- **AND** checks if location is in walkable node or town center
- **AND** assesses retail tenant mix (prefer coffee/gear/bodega per Aker thesis)
- **AND** scores mixed-use fit 0-100 based on location + retail profile

#### Scenario: Adaptive reuse evaluation

- **WHEN** a property is listed as office, retail, or industrial with conversion potential
- **THEN** the system flags for adaptive reuse consideration
- **AND** checks ceiling height (>9ft ideal), floor plates, natural light
- **AND** estimates conversion feasibility (low/medium/high complexity)
- **AND** returns reuse potential score 0-100

### Requirement: Deal Archetype Classification

The system SHALL classify investment opportunities by deal archetype (value-add light, value-add medium, heavy lift/reposition, ground-up) and estimate return profiles.

#### Scenario: Value-add light identification

- **WHEN** a property is 1985-2015 vintage with occupancy >85%
- **THEN** the system classifies as value-add light candidate
- **AND** estimates scope: interiors (LVP, counters, lighting), common area refresh, smart tech
- **AND** projects rent lift: $90-$180/mo avg, 4-year payback
- **AND** returns value-add score and ROI estimate

#### Scenario: Value-add medium identification

- **WHEN** a property has deferred maintenance, dated systems, but solid bones
- **THEN** the system classifies as value-add medium
- **AND** estimates scope: above + HVAC, plumbing, exterior paint, amenity upgrades
- **AND** projects rent lift: $150-$250/mo, 5-6 year payback, retention +200 bps
- **AND** returns value-add score and ROI estimate

#### Scenario: Heavy lift/reposition identification

- **WHEN** a property has significant systems issues or reputation problems
- **THEN** the system classifies as heavy lift
- **AND** estimates scope: envelope, major systems, unit splits/rebalance, full rebrand
- **AND** projects longer downtime buffer (6-12 months), higher capex
- **AND** flags as higher risk/return profile
- **AND** returns reposition score with risk notes

#### Scenario: Ground-up infill identification

- **WHEN** opportunity is vacant land or tear-down in town center/transit area
- **THEN** the system classifies as ground-up development
- **AND** evaluates yield-on-cost vs. stabilized cap spread (require >150 bps)
- **AND** checks entitlement complexity and timeline
- **AND** assesses if retail component is viable (placemaking, not profit center)
- **AND** returns development feasibility score 0-100

### Requirement: Unit Mix Optimization

The system SHALL recommend optimal unit mix (studio, 1BR, 2BR, 3BR ratios) based on submarket characteristics, employment profile, and remote work trends.

#### Scenario: Job-core unit mix

- **WHEN** submarket is near major employment center with high daytime population
- **THEN** the system recommends studio/1BR bias (60-70% of units)
- **AND** targets young professionals, singles, couples without children
- **AND** prioritizes compact, efficient layouts
- **AND** returns unit mix recommendation with rationale

#### Scenario: Family/remote-work node mix

- **WHEN** submarket has high 35-44 age cohort, good schools, outdoor access
- **THEN** the system recommends more 2BR/3BR (50-60% of units)
- **AND** targets families, remote workers needing home office
- **AND** prioritizes in-unit W/D, extra storage, balconies
- **AND** returns unit mix recommendation with rationale

#### Scenario: Affordability-driven mix

- **WHEN** submarket has high rent burden and workforce housing need
- **THEN** the system suggests smaller average unit size to hit affordability targets
- **AND** includes some workforce-affordable 1BR units
- **AND** evaluates if inclusionary zoning requires affordable set-aside
- **AND** returns unit mix with affordability compliance

### Requirement: Amenity and Physical Feature Scoring

The system SHALL assess properties against Aker's "outdoors brand" amenities: balconies, mudroom/gear nooks, bike/ski storage, dog wash, EV charging.

#### Scenario: Outdoor-enabling features check

- **WHEN** the system evaluates a property for Aker fit
- **THEN** it checks for: balconies/patios (50+ units), mudroom/gear storage, secure bike/ski/board storage, dog wash station
- **AND** scores each feature present (20 points each, 100 max)
- **AND** applies bonus for unique features (e.g., bike tune bench, boot dryers)
- **AND** returns amenity score 0-100

#### Scenario: EV readiness assessment

- **WHEN** the system evaluates parking infrastructure
- **THEN** it checks for existing EV chargers or "EV-ready" conduit
- **AND** calculates percentage of stalls that are EV-capable
- **AND** estimates retrofit cost if not EV-ready
- **AND** returns EV readiness score 0-100

#### Scenario: Remote work amenity check

- **WHEN** the system evaluates work-from-home support
- **THEN** it checks for: quiet rooms, reservable micro-offices, robust Wi-Fi (mesh, not single router)
- **AND** evaluates if amenities can be monetized via memberships
- **AND** estimates incremental rent capture ($20-$50/mo)
- **AND** returns remote work amenity score 0-100

#### Scenario: Pet-forward features

- **WHEN** the system evaluates pet amenities
- **THEN** it checks for: dog run, dog wash, pet policy (size/breed limits)
- **AND** estimates retention and premium impact (100-300 bps retention, $15-$30/mo pet rent)
- **AND** returns pet-friendliness score 0-100

### Requirement: Parking Ratio Optimization

The system SHALL recommend parking ratios (stalls per unit) based on location type, transit access, and observed car ownership to avoid over-parking or under-parking.

#### Scenario: Infill parking ratio

- **WHEN** property is in walkable, transit-rich urban core
- **THEN** the system recommends 0.5-0.8 stalls/unit
- **AND** validates using Census ACS vehicle availability data for tract
- **AND** checks for unbundled parking (separate rent from parking fee)
- **AND** returns parking ratio recommendation

#### Scenario: Suburban parking ratio

- **WHEN** property is in auto-oriented suburban area
- **THEN** the system recommends 1.1-1.4 stalls/unit
- **AND** checks local zoning parking minimums
- **AND** estimates land cost of excess parking (opportunity cost)
- **AND** returns parking ratio recommendation

#### Scenario: Transit-adjacent adjustment

- **WHEN** property is within 800m of high-frequency transit (headway <15 min)
- **THEN** the system reduces parking ratio by 0.1-0.2 stalls/unit
- **AND** documents transit access as justification
- **AND** validates against local parking reduction ordinances
- **AND** returns adjusted parking ratio

### Requirement: CapEx Scope and ROI Estimation

The system SHALL estimate capital expenditure requirements and return on investment for value-add improvements based on Aker's playbook.

#### Scenario: Interior unit upgrade ROI

- **WHEN** the system evaluates value-add interior scope
- **THEN** it estimates cost: LVP $4-6/sf, countertops $50/LF, lighting $300/unit
- **AND** calculates total per-unit cost: $6,000-$12,000
- **AND** estimates rent lift: $90-$180/mo
- **AND** calculates simple payback: (total cost) / (annual rent lift) = 3-5 years
- **AND** returns ROI metrics and payback period

#### Scenario: Common area and amenity ROI

- **WHEN** the system evaluates common area refresh
- **THEN** it estimates cost: lobby $50k, fitness $30k, package lockers $15k, signage $20k
- **AND** estimates impact: retention +150 bps, lease-up velocity +10%, rent premium $20-40/mo
- **AND** calculates blended ROI with retention savings + rent lift
- **AND** returns ROI and break-even timeline

#### Scenario: Systems upgrade ROI

- **WHEN** the system evaluates HVAC, plumbing, or roof replacement
- **THEN** it estimates cost and remaining useful life of existing systems
- **AND** calculates utility savings (LED, smart thermostats, low-flow fixtures)
- **AND** estimates avoided emergency repair costs (deferred maintenance)
- **AND** returns ROI including savings + avoided costs + rent impact

#### Scenario: Sustainability ROI

- **WHEN** the system evaluates green improvements (LED, controls, envelope sealing, submetering)
- **THEN** it estimates utility cost reduction per unit per month
- **AND** calculates payback from resident savings (if bill-back)
- **AND** estimates reputation/marketing value ("green certified")
- **AND** returns ROI with environmental and financial benefits

### Requirement: Operating Model Support

The system SHALL provide data and metrics to support Aker's "Invest → Create → Operate" model including NPS tracking, programming budgets, and community engagement ROI.

#### Scenario: NPS and reputation tracking

- **WHEN** the system evaluates operations performance
- **THEN** it integrates review data (Google, Yelp, ApartmentRatings) for NPS calculation
- **AND** tracks reputation lift from brand improvements (before/after ratings)
- **AND** models concession reduction from higher NPS (25 bps per 10-point NPS gain)
- **AND** returns reputation score and pricing impact

#### Scenario: Programming budget estimation

- **WHEN** the system estimates Aker Collective programming costs
- **THEN** it recommends budget: $50-$100/door/year for events, partnerships, amenities
- **AND** tracks KPIs: renewal %, review volume/rating, referral share, event attendance
- **AND** estimates CAC reduction from community engagement (20-40% lower)
- **AND** returns programming ROI with resident retention impact

#### Scenario: Lease-up velocity impact

- **WHEN** the system models lease-up for new acquisition or heavy lift
- **THEN** it estimates baseline days-to-lease (market average)
- **AND** applies Aker brand/reputation lift (10-20% faster lease-up)
- **AND** calculates carrying cost savings (NOI gain from faster stabilization)
- **AND** returns lease-up forecast and financial impact

### Requirement: Construction and Logistics Cost Adjustments

The system SHALL apply state-specific and seasonal cost adjustments for construction, logistics, and labor availability in CO/UT/ID mountain markets.

#### Scenario: Winter construction premium

- **WHEN** construction timeline spans Nov-Mar in mountain markets
- **THEN** the system applies 10-20% schedule premium for cold weather
- **AND** estimates heating costs, snow removal, shorter workdays
- **AND** adjusts project timeline for seasonal delays
- **AND** returns winter-adjusted cost and schedule

#### Scenario: Mountain logistics premium

- **WHEN** property is in remote or mountain location
- **THEN** the system applies logistics premium: material delivery, equipment mobilization
- **AND** estimates 5-15% cost premium depending on accessibility
- **AND** flags limited contractor pool (fewer bids, higher prices)
- **AND** returns logistics-adjusted cost estimate

#### Scenario: Labor availability check

- **WHEN** the system evaluates construction feasibility
- **THEN** it checks local unemployment rate and construction employment trends
- **AND** flags tight labor markets (unemployment <3%) as high-risk for delays
- **AND** estimates wage premium for skilled trades (10-25% above baseline)
- **AND** returns labor market risk score 0-100

### Requirement: Deal Diligence Checklist Generation

The system SHALL generate customized due diligence checklists based on property type, deal archetype, and identified risks.

#### Scenario: Value-add diligence checklist

- **WHEN** a property is classified as value-add
- **THEN** the system generates checklist:
  - Physical: roof age, HVAC age, plumbing leaks, envelope condition
  - Financial: T-12 P&L, rent roll, lease terms, concession history
  - Operations: lead sources, conversion rates, renewal reasons, turnover cost
  - Reputation: online reviews, resident surveys, BBB complaints
- **AND** includes Aker-specific items: bike storage feasibility, dog run potential, EV retrofit cost

#### Scenario: Ground-up diligence checklist

- **WHEN** opportunity is development/ground-up
- **THEN** the system generates checklist:
  - Entitlement: zoning, variances, design review, inclusionary requirements
  - Site: geotech, Phase I ESA, flood cert, wetlands, slope analysis
  - Utilities: water/sewer capacity, tap fees, electric service, fiber
  - Risk: wildfire defensible space, snow load, construction access
- **AND** includes cost estimate reviews and contractor references

#### Scenario: High-risk diligence checklist

- **WHEN** risk-assessment flags high wildfire, flood, or seismic risk
- **THEN** the system adds to checklist:
  - Insurance: quotes from 3+ carriers, deductible structures, coverage limits
  - Mitigation: defensible space cost, flood elevation options, seismic retrofit
  - Operations: evacuation plans, emergency preparedness, resident communication
- **AND** flags if insurability is in question

### Requirement: Portfolio Fit Analysis

The system SHALL compare candidate properties to Aker's existing portfolio to assess strategic fit, diversification, and operational synergies.

#### Scenario: Geographic diversification

- **WHEN** the system evaluates a new market entry
- **THEN** it compares to existing portfolio locations
- **AND** calculates geographic concentration risk (% NOI in single metro)
- **AND** assesses if new market adds diversification or increases concentration
- **AND** returns diversification score 0-100

#### Scenario: Product type mix

- **WHEN** the system evaluates portfolio product type distribution
- **THEN** it calculates current mix (% garden, % low-rise, % mixed-use)
- **AND** assesses if candidate balances or concentrates product risk
- **AND** recommends target mix for diversification
- **AND** returns product mix score

#### Scenario: Operational scale synergies

- **WHEN** candidate property is in existing market with Aker assets
- **THEN** the system estimates operational synergies: shared vendors, bulk purchasing, brand recognition
- **AND** calculates estimated opex savings (2-5% of opex)
- **AND** models faster lease-up from local reputation
- **AND** returns synergy value estimate

### Requirement: Exit Strategy and Hold Period Analysis

The system SHALL model exit cap rates, appreciation scenarios, and optimal hold periods to support investment committee decision-making.

#### Scenario: Value-add exit modeling

- **WHEN** deal is value-add with 3-5 year business plan
- **THEN** the system estimates stabilized NOI post-improvements
- **AND** projects exit cap rate (entry +/- 25-50 bps depending on market trajectory)
- **AND** calculates IRR and equity multiple at various hold periods (3, 5, 7 years)
- **AND** returns hold period sensitivity analysis

#### Scenario: Market appreciation scenarios

- **WHEN** the system models long-term returns
- **THEN** it projects rent growth scenarios: base case (inflation + 1%), bull (inflation + 2.5%), bear (inflation)
- **AND** applies cap rate expansion/compression (±50 bps)
- **AND** calculates IRR under each scenario
- **AND** returns distribution of outcomes (P10, P50, P90)

#### Scenario: Refinance vs. sale decision

- **WHEN** the system evaluates hold/sell decision at year 3-5
- **THEN** it compares refinance (extract equity, hold for cash flow) vs. sale (realize gains)
- **AND** models tax implications (depreciation recapture, capital gains)
- **AND** estimates net proceeds under each strategy
- **AND** returns recommendation with sensitivity to interest rates

### Requirement: Asset Fit Report Generation

The system SHALL generate comprehensive asset evaluation reports combining property analysis, deal archetype fit, CapEx scopes, and portfolio context.

#### Scenario: Asset summary report

- **WHEN** a user requests property evaluation report
- **THEN** the system generates PDF/HTML including:
  - Property summary (type, vintage, units, location)
  - Deal archetype classification and fit score
  - Recommended CapEx scope and ROI estimates
  - Amenity checklist and Aker brand alignment
  - Unit mix and parking recommendations
  - Diligence checklist
  - Portfolio fit analysis
  - Return projections (IRR, equity multiple)
- **AND** exports underlying data to Excel for underwriting model

#### Scenario: Batch property screening

- **WHEN** the system evaluates multiple properties in a market
- **THEN** it ranks properties by Aker fit score
- **AND** generates comparison table with key metrics
- **AND** highlights top candidates for further diligence
- **AND** exports batch results to CSV/Excel

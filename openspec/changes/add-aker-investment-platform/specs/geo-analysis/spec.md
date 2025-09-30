# Geographic Analysis Capability - Delta Spec

## ADDED Requirements

### Requirement: Outdoor Recreation Access Scoring

The system SHALL calculate an outdoor recreation access score (0-100) based on proximity to trailheads, ski areas, water bodies, regional parks, trail density, and public land access.

#### Scenario: Trail proximity calculation

- **WHEN** the system evaluates outdoor access for a submarket
- **THEN** it calculates drive time to nearest trailhead using road network routing
- **AND** identifies trails within 30-minute drive radius
- **AND** retrieves trail miles per capita from local/NPS/USFS data
- **AND** returns trail access component score 0-100 (shorter distance = higher score)

#### Scenario: Ski and resort access

- **WHEN** the system analyzes winter recreation access
- **THEN** it calculates distance to nearest ski resort or ski bus stop
- **AND** identifies lift-serviced areas within 60-minute drive
- **AND** weights score by resort size (skiable acres, vertical drop)
- **AND** returns winter recreation component score 0-100

#### Scenario: Water recreation proximity

- **WHEN** the system evaluates water access
- **THEN** it identifies reservoirs, rivers, lakes within 30-minute drive
- **AND** calculates shoreline miles or river access points
- **AND** checks for boat ramps, fishing access, swimming areas
- **AND** returns water recreation component score 0-100

#### Scenario: Public land percentage

- **WHEN** the system analyzes public land access using PAD-US data
- **THEN** it calculates percentage of land within 30-minute drive that is public (BLM, USFS, NPS, state parks)
- **AND** weights by access type (unrestricted > day-use only)
- **AND** returns public land component score 0-100

### Requirement: Isochrone Travel Time Analysis

The system SHALL calculate drive-time and walk-time isochrones from submarket centroids to amenities, employment centers, and recreation using road network routing.

#### Scenario: 15-minute walk isochrone

- **WHEN** the system evaluates walkability from a point
- **THEN** it queries OSRM or OpenRouteService for 15-minute walk isochrone polygon
- **AND** counts POIs within the isochrone (grocery, pharmacy, school, transit)
- **AND** calculates population within isochrone using Census block data
- **AND** returns isochrone geometry and amenity counts

#### Scenario: 30-minute drive isochrone

- **WHEN** the system evaluates outdoor access or employment reach
- **THEN** it calculates 30-minute drive isochrone using current traffic model
- **AND** overlays with trailheads, parks, job centers
- **AND** returns reachable destinations and population coverage

#### Scenario: Multi-modal routing

- **WHEN** the system evaluates transit-accessible amenities
- **THEN** it calculates isochrones combining walk + transit + walk segments
- **AND** uses GTFS schedule data for realistic transit times
- **AND** identifies destinations reachable within 30 minutes total

### Requirement: Elevation and Slope Analysis

The system SHALL retrieve digital elevation models and calculate slope, aspect, and terrain ruggedness for parcels and submarkets to assess development constraints.

#### Scenario: Parcel slope calculation

- **WHEN** the system analyzes a parcel polygon for development feasibility
- **THEN** it queries USGS 3DEP for elevation raster covering the parcel
- **AND** calculates mean slope, max slope, and slope distribution
- **AND** classifies terrain as flat (<5%), moderate (5-15%), steep (>15%)
- **AND** returns percentage of parcel in each category

#### Scenario: Aspect and solar exposure

- **WHEN** the system evaluates site orientation
- **THEN** it calculates dominant aspect (N, S, E, W) from DEM
- **AND** estimates solar exposure hours (useful for energy modeling)
- **AND** returns aspect distribution and solar potential score

#### Scenario: Terrain ruggedness index

- **WHEN** the system assesses overall terrain difficulty
- **THEN** it calculates TRI (terrain ruggedness index) for submarket
- **AND** normalizes to 0-100 (higher = more rugged = more constrained)
- **AND** returns ruggedness score for supply constraint analysis

### Requirement: Intersection Density and Network Connectivity

The system SHALL calculate street intersection density, block size, and bikeway connectivity as proxies for walkability and urban form quality.

#### Scenario: Intersection density calculation

- **WHEN** the system evaluates walkability infrastructure
- **THEN** it retrieves OSM road network for submarket
- **AND** counts 3-way and 4-way intersections per square kilometer
- **AND** excludes highway interchanges and cul-de-sacs
- **AND** returns intersection density score 0-100 (higher = more walkable)

#### Scenario: Bikeway network analysis

- **WHEN** the system evaluates bicycle infrastructure
- **THEN** it retrieves OSM bikeways tagged as cycleway, lane, or path
- **AND** calculates total bikeway miles and miles per capita
- **AND** assesses connectivity (ratio of protected lanes to total network)
- **AND** returns bikeway score 0-100

#### Scenario: Block size distribution

- **WHEN** the system analyzes urban form
- **THEN** it calculates average block perimeter from road network polygons
- **AND** compares to walkability benchmarks (ideal: 300-600m perimeter)
- **AND** returns block size score 0-100

### Requirement: Flood Zone and Water Body Buffers

The system SHALL identify flood hazard zones, wetlands, and water body buffers to flag development constraints and environmental risks.

#### Scenario: FEMA flood zone overlay

- **WHEN** the system analyzes flood risk for a parcel
- **THEN** it queries FEMA NFHL WMS for intersecting flood zones
- **AND** returns flood zone types (A, AE, VE, X) and base flood elevation (BFE)
- **AND** calculates percentage of parcel in high-risk zones (A/AE/VE)
- **AND** flags parcels >25% in SFHA as high-risk

#### Scenario: Wetland buffer application

- **WHEN** the system evaluates environmental constraints
- **THEN** it queries USFWS National Wetlands Inventory for nearby wetlands
- **AND** applies regulatory buffers (typically 50-100ft depending on state)
- **AND** calculates buildable area after buffer subtraction
- **AND** returns wetland constraint flag and affected acreage

#### Scenario: River and lake setbacks

- **WHEN** the system analyzes waterfront parcels
- **THEN** it retrieves NHDPlus High Resolution hydrography features
- **AND** applies appropriate setbacks (varies by waterbody type)
- **AND** overlays with 100-year floodplain for cumulative constraints
- **AND** returns water setback geometry and impact

### Requirement: Airport and Noise Constraint Mapping

The system SHALL identify airport noise contours, flight path restrictions, and height limitations to assess airspace constraints on development.

#### Scenario: Airport proximity check

- **WHEN** the system evaluates a submarket near an airport
- **THEN** it retrieves USDOT National Transportation Noise Map data
- **AND** overlays noise contours (DNL 65+, 70+, 75+ dB)
- **AND** checks for FAA height restriction zones (Part 77 surfaces)
- **AND** returns noise exposure level and height limit

#### Scenario: Highway noise analysis

- **WHEN** the system evaluates parcels near major highways
- **THEN** it calculates distance to highway centerline
- **AND** estimates noise exposure using traffic volume (if available) or distance proxy
- **AND** applies attenuation for natural/built barriers
- **AND** returns highway noise score (higher = quieter = better)

### Requirement: View Shed and Scenic Resource Protection

The system SHALL identify view corridors, ridgelines, and scenic resource overlays that may limit development height or design to assess regulatory constraints.

#### Scenario: Ridgeline overlay check

- **WHEN** the system evaluates a parcel in mountainous terrain
- **THEN** it identifies if parcel intersects local ridgeline protection zones (GIS layers)
- **AND** retrieves maximum height restrictions from zoning
- **AND** flags view corridor protections
- **AND** returns view shed constraint level (none, moderate, severe)

### Requirement: Protected Lands and Conservation Easements

The system SHALL identify national forests, parks, wilderness areas, BLM lands, and conservation easements that constrain adjacent development and create supply scarcity.

#### Scenario: Public land proximity

- **WHEN** the system analyzes land availability for development
- **THEN** it queries PAD-US for protected lands within 5km
- **AND** classifies by protection level (GAP 1-4)
- **AND** calculates percentage of surrounding area that is undevelopable
- **AND** returns supply constraint boost for scarcity

#### Scenario: Conservation easement check

- **WHEN** property-level data includes conservation easements
- **THEN** the system flags parcel as constrained or unbuildable
- **AND** documents easement holder and restrictions
- **AND** excludes from developable land inventory

### Requirement: POI Category Counting and Density

The system SHALL count and categorize points of interest (grocery, pharmacy, schools, cafes, parks) within defined radii to quantify amenity access.

#### Scenario: Grocery store accessibility

- **WHEN** the system evaluates food access
- **THEN** it queries OSM Overpass for shop=supermarket, shop=grocery within 1km
- **AND** counts stores and calculates stores per 10k population
- **AND** identifies food deserts (>1km to nearest grocery)
- **AND** returns grocery access score 0-100

#### Scenario: School proximity

- **WHEN** the system evaluates family-friendliness
- **THEN** it identifies K-8 schools within 1.5km walk distance
- **AND** retrieves school ratings (if available from state data)
- **AND** counts schools and normalizes by child population
- **AND** returns school access score 0-100

#### Scenario: Third-place density

- **WHEN** the system evaluates neighborhood vibrancy
- **THEN** it counts cafes, restaurants, pubs, libraries, community centers within 1km
- **AND** calculates third-place density per square kilometer
- **AND** compares to urban walkability benchmarks
- **AND** returns vibrancy score 0-100

### Requirement: Air Quality and Smoke Day Analysis

The system SHALL analyze historical air quality data to identify PM2.5 seasonal variation, wildfire smoke days, and chronic pollution exposure.

#### Scenario: Seasonal PM2.5 variance

- **WHEN** the system evaluates air quality for a county
- **THEN** it retrieves EPA AQS daily PM2.5 readings for 3 years
- **AND** calculates seasonal averages (summer wildfire season vs. winter)
- **AND** counts days exceeding unhealthy thresholds (>55 µg/m³)
- **AND** returns air quality score 0-100 (lower PM2.5 = higher score)

#### Scenario: Smoke day identification

- **WHEN** the system analyzes wildfire smoke impact
- **THEN** it retrieves NOAA HMS smoke polygons overlapping the submarket
- **AND** counts days with light, medium, heavy smoke density
- **AND** identifies multi-day smoke events (>3 consecutive days)
- **AND** returns smoke day count and severity score

### Requirement: Transit Stop and Service Frequency Analysis

The system SHALL analyze GTFS data to calculate transit stop density, route coverage, service frequency (headways), and hours of operation for public transit accessibility.

#### Scenario: Transit stop density

- **WHEN** the system evaluates transit access for a submarket
- **THEN** it queries Transitland for stops within bounding box
- **AND** calculates stops per square kilometer and per 10k population
- **AND** identifies high-frequency stops (headway <15 min peak hours)
- **AND** returns transit stop density score 0-100

#### Scenario: Service frequency analysis

- **WHEN** the system evaluates transit quality
- **THEN** it parses GTFS stop_times.txt for weekday schedules
- **AND** calculates average headway (wait time) during peak and off-peak
- **AND** identifies all-day service (>16 hours) vs. commuter-only routes
- **AND** returns transit frequency score 0-100

#### Scenario: Weekend and evening service

- **WHEN** the system evaluates lifestyle-oriented transit (not just commuting)
- **THEN** it checks GTFS for Saturday/Sunday service availability
- **AND** identifies routes with evening service past 10 PM
- **AND** calculates service hour coverage as percentage of week
- **AND** returns transit coverage score 0-100

### Requirement: Geospatial Data Export

The system SHALL export geospatial analysis results as GeoJSON, Shapefiles, or GeoPackage for use in GIS software and map visualizations.

#### Scenario: GeoJSON export

- **WHEN** a user requests map export of analyzed submarkets
- **THEN** the system generates GeoJSON FeatureCollection
- **AND** includes all scores and metrics as feature properties
- **AND** preserves coordinate reference system (WGS84)
- **AND** validates geometry using Shapely

#### Scenario: Interactive map generation

- **WHEN** a user requests visual output
- **THEN** the system generates an HTML map using folium or similar
- **AND** color-codes submarkets by score (choropleth)
- **AND** adds popup tooltips with key metrics
- **AND** includes basemap (OSM or satellite imagery)
- **AND** exports to standalone HTML file

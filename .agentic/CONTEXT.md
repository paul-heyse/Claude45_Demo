# Agentic Development Context

This file provides structured context for AI coding assistants working on the Aker Investment Platform.

## Project Overview

**Name:** Aker Investment Platform
**Purpose:** Data-driven screening and evaluation of residential real estate investments in CO/UT/ID
**Architecture:** Modular Python package with 6 core capabilities
**Development Stage:** Pre-implementation (OpenSpec proposal approved)

## Current State

- **Active Change:** `add-aker-investment-platform` (not yet implemented)
- **Existing Code:** Minimal (starter package only)
- **Test Coverage:** 0% (greenfield build)
- **Dependencies:** To be installed per OpenSpec proposal

## Core Capabilities (To Be Built)

1. **data-integration** - API connectors, caching (SQLite), 40+ data sources
2. **market-analysis** - Supply constraints, employment, demographics scoring
3. **geo-analysis** - Geospatial operations, outdoor recreation, terrain
4. **risk-assessment** - Wildfire, flood, seismic, regulatory risk modeling
5. **scoring-engine** - Weighted scoring (30/30/20/20), ranking, visualization
6. **asset-evaluation** - Property filtering, ROI estimation, portfolio fit

## Module Structure Pattern

Each capability follows this structure:

```
src/Claude45_Demo/
├── data_integration/
│   ├── __init__.py
│   ├── base.py           # Abstract base classes
│   ├── cache.py          # SQLite caching layer
│   ├── census.py         # Census API connector
│   ├── bls.py            # BLS API connector
│   └── ...
├── market_analysis/
│   ├── __init__.py
│   ├── supply.py         # Supply constraint scoring
│   ├── employment.py     # Innovation employment analysis
│   └── ...
tests/
├── test_data_integration/
│   ├── test_census.py
│   ├── fixtures/         # Mock API responses
│   └── ...
```

## Coding Patterns

### 1. Data Classes for Structured Data

```python
from dataclasses import dataclass
from shapely.geometry import Point, Polygon

@dataclass
class Submarket:
    """Represents a geographic investment target."""
    id: str
    name: str
    state: str  # CO, UT, or ID
    geometry: Polygon
    centroid: Point
```

### 2. Abstract Base Connectors

```python
from abc import ABC, abstractmethod

class APIConnector(ABC):
    """Base class for all data source connectors."""

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate with the API."""

    @abstractmethod
    def fetch(self, params: dict) -> dict:
        """Fetch data from the API."""

    def _retry_with_backoff(self, func, max_retries=5):
        """Common retry logic with exponential backoff."""
```

### 3. Score Calculation Pattern

```python
def calculate_score(
    raw_value: float,
    min_val: float,
    max_val: float,
    inverse: bool = False
) -> float:
    """
    Normalize raw metric to 0-100 score.

    Args:
        raw_value: The metric value to normalize
        min_val: Minimum expected value
        max_val: Maximum expected value
        inverse: If True, lower raw_value = higher score

    Returns:
        Normalized score 0-100
    """
    normalized = (raw_value - min_val) / (max_val - min_val)
    score = (1 - normalized) * 100 if inverse else normalized * 100
    return max(0, min(100, score))
```

## Test Patterns

### 1. Mock API Responses

```python
# tests/test_data_integration/fixtures/census_response.json
{
    "data": [
        ["B01001_001E", "41403", "geo_id"],
        ["243455", "08031", "05000US08031"]
    ],
    "columns": ["population", "income", "geoid"]
}
```

### 2. Fixture-Based Tests

```python
import pytest
from pathlib import Path

@pytest.fixture
def census_response():
    """Load mock Census API response."""
    fixture_path = Path(__file__).parent / "fixtures" / "census_response.json"
    return json.loads(fixture_path.read_text())

def test_census_parser(census_response):
    """Test Census data parsing with mock response."""
    connector = CensusConnector(api_key="test")
    df = connector.parse(census_response)
    assert len(df) == 1
    assert df["population"].iloc[0] == 243455
```

## Documentation Standards

### Docstring Format (Google Style)

```python
def calculate_wildfire_risk(
    location: Point,
    whp_score: float,
    fuel_model: str,
    wui_class: str
) -> float:
    """
    Calculate wildfire risk score for a location.

    Combines USFS Wildfire Hazard Potential, LANDFIRE fuel models,
    and WUI classification into 0-100 risk score.

    Args:
        location: Geographic point (lat, lon)
        whp_score: USFS WHP score (1-5 scale)
        fuel_model: LANDFIRE fuel model code
        wui_class: WUI classification (Interface, Intermix, Non-WUI)

    Returns:
        Risk score 0-100 where 100 is highest risk

    Raises:
        ValueError: If whp_score is outside 1-5 range

    Example:
        >>> from shapely.geometry import Point
        >>> loc = Point(-105.27, 40.01)  # Boulder, CO
        >>> risk = calculate_wildfire_risk(loc, 4, "TL5", "Interface")
        >>> assert 60 <= risk <= 90  # High risk area
    """
```

## Configuration Management

### Config File Pattern (config.yaml)

```yaml
data_sources:
  census:
    api_key: ${CENSUS_API_KEY}
    base_url: https://api.census.gov/data
    cache_ttl_days: 30
    rate_limit: 500  # requests per day

  bls:
    api_key: ${BLS_API_KEY}
    base_url: https://api.bls.gov/publicAPI/v2
    cache_ttl_days: 7
    rate_limit: 500  # requests per day

scoring:
  weights:
    supply: 0.30
    jobs: 0.30
    urban: 0.20
    outdoor: 0.20

  risk_multiplier_range:
    min: 0.85
    max: 1.10
```

## Error Handling Pattern

```python
class AkerPlatformError(Exception):
    """Base exception for Aker platform."""

class DataSourceError(AkerPlatformError):
    """Error fetching or parsing data from external source."""

class ValidationError(AkerPlatformError):
    """Data validation failed."""

class ScoringError(AkerPlatformError):
    """Error calculating scores."""

# Usage
try:
    data = census_connector.fetch(params)
except RateLimitExceeded:
    logger.warning("Rate limit hit, using cached data")
    data = cache.get(cache_key)
except DataSourceError as e:
    logger.error(f"Census API failed: {e}")
    raise
```

## Common Commands

```bash
# Activate environment
micromamba activate ./.venv

# Install new package
micromamba install -p ./.venv -c conda-forge <package>

# Run tests
pytest -q                           # Quick run
pytest -v --cov=src --cov-report=html  # With coverage

# Lint and format
ruff check src tests                # Lint
black src tests                     # Format

# Type checking (if we add mypy)
mypy src/

# Run specific test
pytest tests/test_market_analysis/test_supply.py -v -k test_permit_calculation

# OpenSpec workflow
openspec show add-aker-investment-platform  # View proposal
openspec validate --strict                   # Validate all
```

## API Key Management

```bash
# .env file (DO NOT COMMIT)
CENSUS_API_KEY=your_key_here
BLS_API_KEY=your_key_here
EPA_API_KEY=optional
GOOGLE_PLACES_API_KEY=optional

# Load with python-dotenv
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("CENSUS_API_KEY")
if not api_key:
    raise ConfigurationError("CENSUS_API_KEY not set")
```

## Incremental Development Strategy

When building a new capability:

1. **Read the spec** - `cat openspec/changes/add-aker-investment-platform/specs/<capability>/spec.md`
2. **Create module structure** - directories, `__init__.py`, stub files
3. **Write tests first** (TDD) - Based on scenarios in spec
4. **Implement minimum viable** - Get one scenario passing
5. **Iterate** - Add scenarios one at a time
6. **Mark task complete** - Update `tasks.md` with `[x]`
7. **Integration test** - Ensure capability works with others
8. **Document** - Add examples, update README

## Key Principles

- **Spec is truth** - OpenSpec requirements define behavior
- **Test scenarios map to spec scenarios** - Each `#### Scenario:` becomes a test
- **Fail fast** - Validate inputs, raise clear exceptions
- **Cache aggressively** - Respect API rate limits
- **Type everything** - Use type hints for agent clarity
- **Small functions** - <50 lines, single responsibility
- **Normalize to 0-100** - All scores use same scale
- **Document assumptions** - Especially for proxies and estimates

## Performance Targets

- Score 50 submarkets in <5 minutes (cached)
- Individual API calls <2 seconds
- Batch processing with progress bars
- Graceful degradation on missing data

## State-Specific Notes

### Colorado

- Heavy hail risk (Front Range)
- Complex water rights (CDSS HydroBase)
- Strong town centers (Boulder, Fort Collins, etc.)

### Utah

- Topographic constraints (Wasatch Front)
- Tech employment concentration (Silicon Slopes)
- Strong university presence (BYU, U of U)

### Idaho

- In-migration momentum (Treasure Valley)
- Forest-interface wildfire risk
- Property tax dynamics different from CO/UT

## Agent Workflow Checklist

When implementing a new feature:

- [ ] Read relevant spec section
- [ ] Check existing similar code for patterns
- [ ] Create test fixtures (if API integration)
- [ ] Write failing tests (TDD)
- [ ] Implement minimum viable version
- [ ] Pass tests
- [ ] Check type hints with mypy (if configured)
- [ ] Run linter (ruff)
- [ ] Format code (black)
- [ ] Update task in tasks.md
- [ ] Test integration with other modules
- [ ] Update documentation

## Questions? Check These First

1. **Spec requirements** - `openspec/changes/add-aker-investment-platform/specs/`
2. **Design decisions** - `openspec/changes/add-aker-investment-platform/design.md`
3. **Task list** - `openspec/changes/add-aker-investment-platform/tasks.md`
4. **This context file** - `.agentic/CONTEXT.md`

# Data Schemas and Type Definitions

JSON Schema and Python type definitions for structured data exchange.
These schemas enable AI agents to understand and generate valid data structures.

## Core Data Models

### Submarket

```python
from dataclasses import dataclass
from shapely.geometry import Point, Polygon
from typing import Optional

@dataclass
class Submarket:
    """
    Geographic unit for investment analysis.

    Can represent CBSA, county, city, or custom polygon.
    """
    id: str  # Unique identifier (kebab-case)
    name: str  # Human-readable name
    state: str  # Two-letter state code: CO, UT, or ID
    geometry: Polygon  # Boundary polygon (WGS84)
    centroid: Point  # Geographic center (WGS84)
    cbsa_code: Optional[str] = None  # Census CBSA code if applicable
    county_fips: Optional[str] = None  # 5-digit FIPS code if county
```

**JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "name", "state", "geometry", "centroid"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "description": "Kebab-case identifier"
    },
    "name": {"type": "string"},
    "state": {
      "type": "string",
      "enum": ["CO", "UT", "ID"]
    },
    "geometry": {
      "type": "object",
      "description": "GeoJSON Polygon"
    },
    "centroid": {
      "type": "object",
      "properties": {
        "lon": {"type": "number", "minimum": -180, "maximum": 180},
        "lat": {"type": "number", "minimum": -90, "maximum": 90}
      }
    },
    "cbsa_code": {"type": ["string", "null"]},
    "county_fips": {
      "type": ["string", "null"],
      "pattern": "^[0-9]{5}$"
    }
  }
}
```

---

### MarketMetrics

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MarketMetrics:
    """Component scores for market analysis."""
    supply_score: float  # 0-100, higher = more constrained (better)
    jobs_score: float  # 0-100, higher = more innovation employment
    urban_score: float  # 0-100, higher = more convenient
    outdoor_score: float  # 0-100, higher = better outdoor access
    components: Dict[str, Any]  # Raw values for drill-down

    def composite_score(self, weights: Dict[str, float]) -> float:
        """Calculate weighted composite score."""
        return (
            self.supply_score * weights.get('supply', 0.30) +
            self.jobs_score * weights.get('jobs', 0.30) +
            self.urban_score * weights.get('urban', 0.20) +
            self.outdoor_score * weights.get('outdoor', 0.20)
        )
```

**JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["supply_score", "jobs_score", "urban_score", "outdoor_score"],
  "properties": {
    "supply_score": {"type": "number", "minimum": 0, "maximum": 100},
    "jobs_score": {"type": "number", "minimum": 0, "maximum": 100},
    "urban_score": {"type": "number", "minimum": 0, "maximum": 100},
    "outdoor_score": {"type": "number", "minimum": 0, "maximum": 100},
    "components": {
      "type": "object",
      "description": "Raw metric values",
      "additionalProperties": true
    }
  }
}
```

---

### RiskAssessment

```python
from dataclasses import dataclass

@dataclass
class RiskAssessment:
    """Risk scores and multiplier for underwriting."""
    wildfire_score: float  # 0-100, higher = more risk
    flood_score: float  # 0-100, higher = more risk
    seismic_score: float  # 0-100, higher = more risk
    regulatory_friction: float  # 0-100, higher = more friction
    water_stress: float  # 0-100, higher = more constrained
    multiplier: float  # 0.85-1.10, applied to market score or cap rate

    @property
    def composite_risk(self) -> float:
        """Weighted composite risk score."""
        return (
            self.wildfire_score * 0.25 +
            self.flood_score * 0.25 +
            self.regulatory_friction * 0.30 +
            (self.seismic_score + self.water_stress) * 0.10
        )
```

**JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "wildfire_score", "flood_score", "seismic_score",
    "regulatory_friction", "water_stress", "multiplier"
  ],
  "properties": {
    "wildfire_score": {"type": "number", "minimum": 0, "maximum": 100},
    "flood_score": {"type": "number", "minimum": 0, "maximum": 100},
    "seismic_score": {"type": "number", "minimum": 0, "maximum": 100},
    "regulatory_friction": {"type": "number", "minimum": 0, "maximum": 100},
    "water_stress": {"type": "number", "minimum": 0, "maximum": 100},
    "multiplier": {"type": "number", "minimum": 0.85, "maximum": 1.10}
  }
}
```

---

### ScoredMarket

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScoredMarket:
    """Complete scoring result for a submarket."""
    submarket: Submarket
    metrics: MarketMetrics
    risks: RiskAssessment
    final_score: float  # Risk-adjusted composite score
    rank: int  # Rank among all analyzed markets (1 = best)
    confidence: float  # 0-100, data completeness and quality
    timestamp: datetime  # When analysis was performed
    model_version: str  # Git tag or semantic version
```

**JSON Schema:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "submarket", "metrics", "risks", "final_score",
    "rank", "confidence", "timestamp", "model_version"
  ],
  "properties": {
    "submarket": {"$ref": "#/definitions/Submarket"},
    "metrics": {"$ref": "#/definitions/MarketMetrics"},
    "risks": {"$ref": "#/definitions/RiskAssessment"},
    "final_score": {"type": "number", "minimum": 0, "maximum": 100},
    "rank": {"type": "integer", "minimum": 1},
    "confidence": {"type": "number", "minimum": 0, "maximum": 100},
    "timestamp": {"type": "string", "format": "date-time"},
    "model_version": {"type": "string", "pattern": "^v?\\d+\\.\\d+\\.\\d+$"}
  }
}
```

---

## API Response Schemas

### Census ACS Response

```python
from typing import List, Any

class CensusACSResponse:
    """Typed response from Census ACS API."""
    data: List[List[Any]]  # First row is headers, rest are data

    # Example:
    # [
    #   ["B01001_001E", "B19013_001E", "NAME", "state", "county"],
    #   ["243455", "72661", "Denver County, Colorado", "08", "031"]
    # ]
```

### BLS QCEW Response

```python
from typing import List, Dict

class BLSQCEWResponse:
    """Typed response from BLS QCEW API."""
    status: str  # "REQUEST_SUCCEEDED"
    Results: Dict[str, List[Dict]]

    # Example Results structure:
    # {
    #   "series": [
    #     {
    #       "seriesID": "ENU0800510",
    #       "data": [
    #         {"year": "2021", "period": "A01", "value": "1234567"}
    #       ]
    #     }
    #   ]
    # }
```

---

## Configuration Schema

```yaml
# config.yaml
data_sources:
  census:
    api_key: ${CENSUS_API_KEY}
    base_url: "https://api.census.gov/data"
    cache_ttl_days: 30
    rate_limit: 500

  bls:
    api_key: ${BLS_API_KEY}
    base_url: "https://api.bls.gov/publicAPI/v2"
    cache_ttl_days: 7
    rate_limit: 500

scoring:
  weights:
    supply: 0.30
    jobs: 0.30
    urban: 0.20
    outdoor: 0.20

  risk_multiplier:
    weights:
      wildfire: 0.25
      flood: 0.25
      regulatory: 0.30
      other: 0.20
    range:
      min: 0.85
      max: 1.10

output:
  formats: ["json", "csv", "html"]
  report_template: "templates/market_report.html"
  visualization_dpi: 300
```

**JSON Schema for config.yaml:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["data_sources", "scoring"],
  "properties": {
    "data_sources": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "api_key": {"type": "string"},
          "base_url": {"type": "string", "format": "uri"},
          "cache_ttl_days": {"type": "integer", "minimum": 1},
          "rate_limit": {"type": "integer", "minimum": 1}
        }
      }
    },
    "scoring": {
      "type": "object",
      "properties": {
        "weights": {
          "type": "object",
          "properties": {
            "supply": {"type": "number", "minimum": 0, "maximum": 1},
            "jobs": {"type": "number", "minimum": 0, "maximum": 1},
            "urban": {"type": "number", "minimum": 0, "maximum": 1},
            "outdoor": {"type": "number", "minimum": 0, "maximum": 1}
          }
        }
      }
    }
  }
}
```

---

## Exception Schema

```python
from typing import Optional

class AkerPlatformError(Exception):
    """Base exception with structured error info."""
    def __init__(
        self,
        message: str,
        code: str,
        details: Optional[dict] = None
    ):
        self.message = message
        self.code = code  # e.g., "RATE_LIMIT_EXCEEDED"
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }
```

**JSON Schema for error responses:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["error"],
  "properties": {
    "error": {
      "type": "object",
      "required": ["code", "message"],
      "properties": {
        "code": {
          "type": "string",
          "enum": [
            "RATE_LIMIT_EXCEEDED",
            "DATA_VALIDATION_ERROR",
            "API_ERROR",
            "SCORING_ERROR",
            "CONFIGURATION_ERROR"
          ]
        },
        "message": {"type": "string"},
        "details": {"type": "object", "additionalProperties": true}
      }
    }
  }
}
```

---

## Usage in Code

```python
# Validation example using pydantic (optional dependency)
from pydantic import BaseModel, Field, validator

class SubmarketModel(BaseModel):
    """Pydantic model for runtime validation."""
    id: str = Field(..., regex=r'^[a-z0-9-]+$')
    name: str
    state: str = Field(..., regex=r'^(CO|UT|ID)$')

    @validator('id')
    def validate_id(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('ID must be 3-50 characters')
        return v

# Usage
try:
    market = SubmarketModel(
        id="denver-metro",
        name="Denver Metro",
        state="CO"
    )
except ValidationError as e:
    print(e.json())
```

---

## Type Hints for AI Understanding

```python
from typing import TypedDict, List, Optional

class CensusVariable(TypedDict):
    """Census variable specification."""
    code: str  # e.g., "B01001_001E"
    name: str  # e.g., "Total Population"
    universe: str  # e.g., "Total population"


class ScoringWeights(TypedDict):
    """Weights for composite scoring."""
    supply: float
    jobs: float
    urban: float
    outdoor: float


class APIResponse(TypedDict):
    """Generic API response structure."""
    status: str
    data: dict
    metadata: Optional[dict]
```

These type definitions help AI agents:

1. Generate valid function signatures
2. Understand expected data structures
3. Create proper validation logic
4. Generate accurate documentation

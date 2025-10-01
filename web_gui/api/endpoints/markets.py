"""Markets API endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class MarketFilters(BaseModel):
    """Market screening filters."""

    supply_min: float = Field(0, ge=0, le=100, description="Minimum supply score")
    jobs_min: float = Field(0, ge=0, le=100, description="Minimum jobs score")
    urban_min: float = Field(0, ge=0, le=100, description="Minimum urban score")
    outdoor_min: float = Field(0, ge=0, le=100, description="Minimum outdoor score")
    risk_max: float = Field(1.3, ge=0.7, le=1.3, description="Maximum risk multiplier")
    composite_min: float = Field(0, ge=0, le=100, description="Minimum composite score")


class ScreenRequest(BaseModel):
    """Market screening request."""

    search: Optional[str] = Field(None, description="Search term for market name")
    filters: MarketFilters = Field(default_factory=MarketFilters)
    limit: int = Field(100, gt=0, le=500, description="Maximum results")


class MarketDetail(BaseModel):
    """Detailed market information."""

    market: str
    state: str
    cbsa: str
    composite_score: float
    supply_score: float
    jobs_score: float
    urban_score: float
    outdoor_score: float
    risk_multiplier: float
    population: int
    median_income: int
    employment: int


@router.post("/screen")
async def screen_markets(request: ScreenRequest) -> List[Dict[str, Any]]:
    """Screen markets based on criteria.

    This endpoint filters markets based on score thresholds and search terms.
    In production, this would query the actual scoring engine.
    """
    # Mock response - in production, integrate with scoring engine
    mock_markets = [
        {
            "Market": "Boulder, CO",
            "State": "CO",
            "Composite": 87.2,
            "Supply": 95.1,
            "Jobs": 82.3,
            "Urban": 78.9,
            "Outdoor": 91.5,
            "Risk": 0.92,
        },
        {
            "Market": "Fort Collins, CO",
            "State": "CO",
            "Composite": 84.5,
            "Supply": 89.7,
            "Jobs": 85.2,
            "Urban": 75.1,
            "Outdoor": 88.3,
            "Risk": 0.95,
        },
        {
            "Market": "Boise, ID",
            "State": "ID",
            "Composite": 83.8,
            "Supply": 88.2,
            "Jobs": 79.5,
            "Urban": 81.2,
            "Outdoor": 89.7,
            "Risk": 0.98,
        },
    ]

    # Apply filters
    filtered = [
        m
        for m in mock_markets
        if (
            m["Supply"] >= request.filters.supply_min
            and m["Jobs"] >= request.filters.jobs_min
            and m["Urban"] >= request.filters.urban_min
            and m["Outdoor"] >= request.filters.outdoor_min
            and m["Risk"] <= request.filters.risk_max
            and m["Composite"] >= request.filters.composite_min
        )
    ]

    # Apply search
    if request.search:
        filtered = [
            m
            for m in filtered
            if request.search.lower() in m["Market"].lower()
            or request.search.lower() in m["State"].lower()
        ]

    return filtered[: request.limit]


@router.get("/{market_id}")
async def get_market_details(market_id: str) -> MarketDetail:
    """Get detailed information for a specific market.

    In production, this would fetch from the database or scoring engine.
    """
    # Mock response
    mock_data = {
        "market": market_id.replace("_", ", ").title(),
        "state": "CO",
        "cbsa": "14500",
        "composite_score": 87.2,
        "supply_score": 95.1,
        "jobs_score": 82.3,
        "urban_score": 78.9,
        "outdoor_score": 91.5,
        "risk_multiplier": 0.92,
        "population": 330758,
        "median_income": 78642,
        "employment": 185420,
    }

    return MarketDetail(**mock_data)


@router.get("/")
async def list_markets(
    state: Optional[str] = Query(None, description="Filter by state"),
    min_score: float = Query(0, ge=0, le=100, description="Minimum composite score"),
    limit: int = Query(50, gt=0, le=500, description="Maximum results"),
) -> List[Dict[str, Any]]:
    """List all available markets.

    In production, this would query the database of scored markets.
    """
    # Mock response
    all_markets = [
        {"market": "Boulder, CO", "state": "CO", "score": 87.2},
        {"market": "Fort Collins, CO", "state": "CO", "score": 84.5},
        {"market": "Boise, ID", "state": "ID", "score": 83.8},
        {"market": "Provo, UT", "state": "UT", "score": 82.9},
        {"market": "Denver, CO", "state": "CO", "score": 82.1},
    ]

    # Apply filters
    filtered = all_markets
    if state:
        filtered = [m for m in filtered if m["state"] == state.upper()]
    if min_score > 0:
        filtered = [m for m in filtered if m["score"] >= min_score]

    return filtered[:limit]


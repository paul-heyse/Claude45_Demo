"""Portfolio API endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class PortfolioEntry(BaseModel):
    """Portfolio entry model."""

    market_id: str = Field(..., description="Market identifier")
    market_name: str = Field(..., description="Market display name")
    state: str = Field(..., description="State code")
    score: float = Field(..., ge=0, le=100, description="Composite score")
    risk: float = Field(..., ge=0.7, le=1.3, description="Risk multiplier")
    status: str = Field("prospect", description="Investment status")
    notes: str = Field("", description="User notes")
    added_date: datetime = Field(default_factory=datetime.now)


class AddToPortfolioRequest(BaseModel):
    """Request to add market to portfolio."""

    market_id: str
    notes: str = ""
    status: str = "prospect"


class UpdatePortfolioRequest(BaseModel):
    """Request to update portfolio entry."""

    notes: Optional[str] = None
    status: Optional[str] = None


# Mock in-memory portfolio storage
_portfolio: List[Dict[str, Any]] = [
    {
        "market_id": "boulder_co",
        "market_name": "Boulder, CO",
        "state": "CO",
        "score": 87.2,
        "risk": 0.92,
        "status": "prospect",
        "notes": "High innovation employment, excellent outdoor access",
        "added_date": "2024-01-15T10:30:00",
    },
    {
        "market_id": "fort_collins_co",
        "market_name": "Fort Collins, CO",
        "state": "CO",
        "score": 84.5,
        "risk": 0.95,
        "status": "committed",
        "notes": "Strong university presence, growing tech sector",
        "added_date": "2024-01-10T14:20:00",
    },
]


@router.get("/")
async def get_portfolio() -> List[Dict[str, Any]]:
    """Get user's portfolio markets."""
    return _portfolio


@router.post("/")
async def add_to_portfolio(request: AddToPortfolioRequest) -> Dict[str, Any]:
    """Add market to portfolio."""
    # Check if already in portfolio
    if any(m["market_id"] == request.market_id for m in _portfolio):
        raise HTTPException(
            status_code=400, detail="Market already in portfolio"
        )

    # Mock market lookup
    market_name = request.market_id.replace("_", ", ").title()
    state = request.market_id.split("_")[-1].upper()

    entry = {
        "market_id": request.market_id,
        "market_name": market_name,
        "state": state,
        "score": 80.0,  # Mock score
        "risk": 1.0,  # Mock risk
        "status": request.status,
        "notes": request.notes,
        "added_date": datetime.now().isoformat(),
    }

    _portfolio.append(entry)
    return entry


@router.patch("/{market_id}")
async def update_portfolio_entry(
    market_id: str, request: UpdatePortfolioRequest
) -> Dict[str, Any]:
    """Update portfolio entry."""
    # Find entry
    entry = next((m for m in _portfolio if m["market_id"] == market_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Market not found in portfolio")

    # Update fields
    if request.notes is not None:
        entry["notes"] = request.notes
    if request.status is not None:
        entry["status"] = request.status

    return entry


@router.delete("/{market_id}")
async def remove_from_portfolio(market_id: str) -> Dict[str, str]:
    """Remove market from portfolio."""
    global _portfolio
    initial_len = len(_portfolio)
    _portfolio = [m for m in _portfolio if m["market_id"] != market_id]

    if len(_portfolio) == initial_len:
        raise HTTPException(status_code=404, detail="Market not found in portfolio")

    return {"status": "success", "message": f"Removed {market_id} from portfolio"}


@router.get("/stats")
async def get_portfolio_stats() -> Dict[str, Any]:
    """Get portfolio statistics."""
    if not _portfolio:
        return {
            "total_markets": 0,
            "avg_score": 0,
            "avg_risk": 0,
            "status_breakdown": {},
        }

    total = len(_portfolio)
    avg_score = sum(m["score"] for m in _portfolio) / total
    avg_risk = sum(m["risk"] for m in _portfolio) / total

    # Status breakdown
    status_counts = {}
    for entry in _portfolio:
        status = entry["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "total_markets": total,
        "avg_score": round(avg_score, 1),
        "avg_risk": round(avg_risk, 2),
        "status_breakdown": status_counts,
    }


"""Cache management API endpoints."""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class CacheWarmRequest(BaseModel):
    """Cache warming request."""

    markets: List[str] = Field(..., description="List of market names")
    sources: List[str] = Field(
        default=["census", "bls", "osm"], description="Data sources to warm"
    )


class CacheStats(BaseModel):
    """Cache statistics."""

    hit_rate: float = Field(..., description="Overall cache hit rate (%)")
    memory_usage_mb: float = Field(..., description="Memory cache usage (MB)")
    sqlite_size_gb: float = Field(..., description="SQLite cache size (GB)")
    total_entries: int = Field(..., description="Total cache entries")


@router.get("/stats")
async def get_cache_stats() -> CacheStats:
    """Get cache statistics."""
    # Mock statistics
    return CacheStats(
        hit_rate=87.3,
        memory_usage_mb=198.5,
        sqlite_size_gb=2.3,
        total_entries=1247,
    )


@router.post("/warm")
async def warm_cache(request: CacheWarmRequest) -> Dict[str, Any]:
    """Warm cache for specified markets and data sources.

    In production, this would trigger the cache warming system.
    """
    total_items = len(request.markets) * len(request.sources)

    return {
        "status": "completed",
        "markets_warmed": len(request.markets),
        "sources_warmed": len(request.sources),
        "total_items": total_items,
        "duration_seconds": total_items * 0.5,  # Mock duration
    }


@router.delete("/clear")
async def clear_cache(
    tier: Optional[str] = None, expired_only: bool = False
) -> Dict[str, Any]:
    """Clear cache entries.

    Args:
        tier: Cache tier to clear (memory, sqlite, all)
        expired_only: Only clear expired entries
    """
    if expired_only:
        return {
            "status": "success",
            "message": "Cleared expired cache entries",
            "entries_cleared": 127,
            "space_freed_mb": 245,
        }

    tier_display = tier or "all tiers"
    return {
        "status": "success",
        "message": f"Cleared cache for {tier_display}",
        "entries_cleared": 1247 if not tier else 450,
        "space_freed_mb": 2300 if not tier else 850,
    }


@router.get("/sources")
async def get_data_sources() -> List[Dict[str, Any]]:
    """Get status of all data sources."""
    return [
        {
            "name": "Census Bureau (ACS)",
            "status": "active",
            "last_update": "2 days ago",
            "cache_hit_rate": 89.2,
        },
        {
            "name": "Bureau of Labor Statistics",
            "status": "active",
            "last_update": "5 days ago",
            "cache_hit_rate": 85.7,
        },
        {
            "name": "OpenStreetMap",
            "status": "active",
            "last_update": "Real-time",
            "cache_hit_rate": 92.3,
        },
        {
            "name": "FEMA Flood Maps",
            "status": "warning",
            "last_update": "30 days ago",
            "cache_hit_rate": 78.5,
        },
        {
            "name": "EPA Air Quality",
            "status": "active",
            "last_update": "1 day ago",
            "cache_hit_rate": 81.2,
        },
    ]


@router.get("/inspect/{key}")
async def inspect_cache_entry(key: str) -> Dict[str, Any]:
    """Inspect a specific cache entry."""
    # Mock cache entry
    return {
        "key": key,
        "value": {"data": "Mock cached data"},
        "size_bytes": 15420,
        "created_at": "2024-01-15T10:30:00",
        "expires_at": "2024-02-15T10:30:00",
        "tier": "sqlite",
        "hit_count": 42,
    }


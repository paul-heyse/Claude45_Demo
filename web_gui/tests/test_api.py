"""Tests for FastAPI backend."""

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestRootEndpoints:
    """Test root and health endpoints."""

    def test_root(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Aker Investment Platform API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "healthy"

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "aker-platform-api"


class TestMarketsEndpoints:
    """Test markets API endpoints."""

    def test_screen_markets(self):
        """Test market screening."""
        response = client.post(
            "/api/markets/screen",
            json={
                "search": "Boulder",
                "filters": {
                    "supply_min": 80,
                    "jobs_min": 70,
                    "urban_min": 60,
                    "outdoor_min": 70,
                    "risk_max": 1.0,
                    "composite_min": 80,
                },
                "limit": 10,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "Market" in data[0]
            assert "Composite" in data[0]

    def test_list_markets(self):
        """Test listing markets."""
        response = client.get("/api/markets/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_list_markets_with_filters(self):
        """Test listing markets with filters."""
        response = client.get("/api/markets/?state=CO&min_score=80&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All results should be from CO
        for market in data:
            assert market["state"] == "CO"
            assert market["score"] >= 80

    def test_get_market_details(self):
        """Test getting market details."""
        response = client.get("/api/markets/boulder_co")
        assert response.status_code == 200
        data = response.json()
        assert "market" in data
        assert "composite_score" in data
        assert "risk_multiplier" in data


class TestPortfolioEndpoints:
    """Test portfolio API endpoints."""

    def test_get_portfolio(self):
        """Test getting portfolio."""
        response = client.get("/api/portfolio/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_add_to_portfolio(self):
        """Test adding market to portfolio."""
        response = client.post(
            "/api/portfolio/",
            json={
                "market_id": "test_market_co",
                "notes": "Test market",
                "status": "prospect",
            },
        )
        assert response.status_code in [200, 400]  # 400 if already exists

    def test_get_portfolio_stats(self):
        """Test getting portfolio statistics."""
        response = client.get("/api/portfolio/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_markets" in data
        assert "avg_score" in data
        assert "avg_risk" in data


class TestReportsEndpoints:
    """Test reports API endpoints."""

    def test_list_templates(self):
        """Test listing report templates."""
        response = client.get("/api/reports/templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "title" in data[0]

    def test_generate_report(self):
        """Test generating a report."""
        response = client.post(
            "/api/reports/generate",
            json={
                "market_ids": ["boulder_co", "denver_co"],
                "template": "market_analysis",
                "format": "pdf",
            },
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_get_report_history(self):
        """Test getting report history."""
        response = client.get("/api/reports/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCacheEndpoints:
    """Test cache management API endpoints."""

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        response = client.get("/api/cache/stats")
        assert response.status_code == 200
        data = response.json()
        assert "hit_rate" in data
        assert "memory_usage_mb" in data
        assert "total_entries" in data

    def test_warm_cache(self):
        """Test warming cache."""
        response = client.post(
            "/api/cache/warm",
            json={
                "markets": ["Boulder, CO", "Denver, CO"],
                "sources": ["census", "bls"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["markets_warmed"] == 2

    def test_get_data_sources(self):
        """Test getting data sources."""
        response = client.get("/api/cache/sources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_clear_cache(self):
        """Test clearing cache."""
        response = client.delete("/api/cache/clear?expired_only=true")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


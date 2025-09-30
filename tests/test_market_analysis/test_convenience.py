"""Tests for urban convenience scorer."""

import pytest

from Claude45_Demo.market_analysis.convenience import UrbanConvenienceScorer


@pytest.fixture
def scorer() -> UrbanConvenienceScorer:
    """Create urban convenience scorer for testing."""
    return UrbanConvenienceScorer()


def test_15min_accessibility_score(scorer: UrbanConvenienceScorer) -> None:
    """Test 15-minute accessibility scoring."""
    result = scorer.calculate_15min_accessibility_score(
        grocery_count=3,
        pharmacy_count=2,
        school_count=4,
        transit_stop_count=6,
        intersection_density_per_sqkm=120.0,
    )
    assert 70 <= result["score"] <= 100
    assert result["amenity_counts"]["grocery"] == 3


def test_retail_health_score(scorer: UrbanConvenienceScorer) -> None:
    """Test retail health scoring."""
    result = scorer.calculate_retail_health_score(
        daytime_population=12000,
        retail_vacancy_rate=0.06,
        population_density_per_sqkm=3500,
    )
    assert 50 <= result["score"] <= 90


def test_transit_quality_score(scorer: UrbanConvenienceScorer) -> None:
    """Test transit quality scoring."""
    result = scorer.calculate_transit_quality_score(
        stops_within_800m=4,
        avg_weekday_headway_min=12.0,
        weekend_service_available=True,
    )
    assert 60 <= result["score"] <= 100
    assert result["components"]["weekend_service"] is True

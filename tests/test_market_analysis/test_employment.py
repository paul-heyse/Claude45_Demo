"""Tests for employment analyzer."""

import pytest

from Claude45_Demo.market_analysis.employment import EmploymentAnalyzer


@pytest.fixture
def analyzer() -> EmploymentAnalyzer:
    """Create employment analyzer for testing."""
    return EmploymentAnalyzer()


def test_calculate_location_quotient(analyzer: EmploymentAnalyzer) -> None:
    """Test LQ calculation for sector concentration."""
    local_employment = {"tech": 50000, "healthcare": 30000, "other": 100000}
    national_employment = {"tech": 500000, "healthcare": 600000, "other": 2000000}

    lq = analyzer.calculate_location_quotient(local_employment, national_employment)

    # Tech: (50k/180k) / (500k/3100k) = 0.278 / 0.161 = 1.72 (concentrated)
    assert lq["tech"] > 1.5
    # Healthcare: (30k/180k) / (600k/3100k) = 0.167 / 0.194 = 0.86 (underrepresented)
    assert lq["healthcare"] < 1.0


def test_calculate_cagr(analyzer: EmploymentAnalyzer) -> None:
    """Test CAGR calculation."""
    cagr = analyzer.calculate_cagr(start_value=100.0, end_value=110.0, years=3)
    # Should be approximately 3.23% annually
    assert 0.03 <= cagr <= 0.035


def test_calculate_innovation_employment_score(analyzer: EmploymentAnalyzer) -> None:
    """Test innovation employment scoring with CAGR and LQ."""
    sector_cagr = {
        "tech": 0.04,
        "healthcare": 0.03,
        "education": 0.02,
        "manufacturing": 0.01,
    }
    sector_lq = {"tech": 1.5, "healthcare": 1.2, "education": 1.0, "manufacturing": 0.8}

    result = analyzer.calculate_innovation_employment_score(sector_cagr, sector_lq)

    assert 60 <= result["score"] <= 90
    assert "sector_scores" in result
    assert result["sector_scores"]["tech"] > result["sector_scores"]["manufacturing"]

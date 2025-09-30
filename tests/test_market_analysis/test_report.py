"""Tests for market analysis report generator."""

import pytest

from Claude45_Demo.market_analysis.report import MarketAnalysisReport


@pytest.fixture
def reporter() -> MarketAnalysisReport:
    """Create report generator for testing."""
    return MarketAnalysisReport()


@pytest.fixture
def sample_data() -> dict:
    """Create sample market analysis data."""
    return {
        "supply_constraint": {
            "score": 75.0,
            "metadata": {"complete": True, "missing_components": []},
        },
        "employment_score": {"score": 70.0},
        "demographic_scores": {
            "population": {"score": 72.0},
            "income": {"score": 68.0},
            "migration": {"score": 75.0},
        },
        "convenience_scores": {
            "accessibility": {"score": 80.0},
            "retail": {"score": 65.0},
            "transit": {"score": 70.0},
        },
        "elasticity_scores": {"vacancy": {"score": 78.0}, "momentum": {"score": 73.0}},
    }


def test_generate_report(reporter: MarketAnalysisReport, sample_data: dict) -> None:
    """Test complete report generation."""
    report = reporter.generate_report(submarket_name="Boulder, CO", **sample_data)

    assert report["submarket"] == "Boulder, CO"
    assert "generated_at" in report
    assert "executive_summary" in report
    assert "component_scores" in report
    assert "composite_scores" in report
    assert "strengths" in report
    assert "weaknesses" in report
    assert "recommendations" in report
    assert "data_completeness" in report


def test_executive_summary(reporter: MarketAnalysisReport, sample_data: dict) -> None:
    """Test executive summary generation."""
    report = reporter.generate_report(submarket_name="Test Market", **sample_data)

    summary = report["executive_summary"]

    assert "overall_score" in summary
    assert 0 <= summary["overall_score"] <= 100
    assert "market_tier" in summary
    assert summary["market_tier"].startswith("Tier")


def test_composite_scores(reporter: MarketAnalysisReport, sample_data: dict) -> None:
    """Test composite score calculations."""
    report = reporter.generate_report(submarket_name="Test Market", **sample_data)

    composites = report["composite_scores"]

    assert "supply_constraint" in composites
    assert "innovation_employment" in composites
    assert "demographics" in composites
    assert "urban_convenience" in composites
    assert "market_elasticity" in composites

    # All composites should be valid scores
    for score in composites.values():
        assert 0 <= score <= 100


def test_strengths_identification(
    reporter: MarketAnalysisReport, sample_data: dict
) -> None:
    """Test strength identification logic."""
    report = reporter.generate_report(submarket_name="Test Market", **sample_data)

    strengths = report["strengths"]

    assert isinstance(strengths, list)
    assert len(strengths) > 0  # Should have some strengths with these scores
    assert all(isinstance(s, str) for s in strengths)


def test_weaknesses_identification(
    reporter: MarketAnalysisReport, sample_data: dict
) -> None:
    """Test weakness identification logic."""
    # Create data with some low scores
    weak_data = sample_data.copy()
    weak_data["employment_score"] = {"score": 35.0}
    weak_data["elasticity_scores"]["vacancy"] = {"score": 40.0}

    report = reporter.generate_report(submarket_name="Test Market", **weak_data)

    weaknesses = report["weaknesses"]

    assert isinstance(weaknesses, list)
    assert len(weaknesses) > 0  # Should identify weaknesses


def test_recommendations_strong_market(
    reporter: MarketAnalysisReport, sample_data: dict
) -> None:
    """Test recommendations for strong market."""
    report = reporter.generate_report(submarket_name="Test Market", **sample_data)

    recommendations = report["recommendations"]

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0


def test_recommendations_weak_market(reporter: MarketAnalysisReport) -> None:
    """Test recommendations for weak market."""
    weak_data = {
        "supply_constraint": {
            "score": 35.0,
            "metadata": {"complete": True, "missing_components": []},
        },
        "employment_score": {"score": 40.0},
        "demographic_scores": {
            "population": {"score": 38.0},
            "income": {"score": 42.0},
            "migration": {"score": 35.0},
        },
        "convenience_scores": {
            "accessibility": {"score": 45.0},
            "retail": {"score": 40.0},
            "transit": {"score": 38.0},
        },
        "elasticity_scores": {"vacancy": {"score": 35.0}, "momentum": {"score": 40.0}},
    }

    report = reporter.generate_report(submarket_name="Test Market", **weak_data)

    recommendations = report["recommendations"]

    assert any("CAUTION" in r or "AVOID" in r for r in recommendations)


def test_data_completeness_full(
    reporter: MarketAnalysisReport, sample_data: dict
) -> None:
    """Test data completeness assessment with complete data."""
    report = reporter.generate_report(submarket_name="Test Market", **sample_data)

    completeness = report["data_completeness"]

    assert completeness["completeness_percentage"] == 100.0
    assert completeness["confidence_level"] == "High"
    assert len(completeness["missing_components"]) == 0


def test_data_completeness_partial(reporter: MarketAnalysisReport) -> None:
    """Test data completeness assessment with missing data."""
    partial_data = {
        "supply_constraint": {
            "score": 75.0,
            "metadata": {
                "complete": False,
                "missing_components": ["topographic_constraint", "regulatory_friction"],
            },
        },
        "employment_score": {"score": 70.0},
        "demographic_scores": {
            "population": {"score": 72.0},
            "income": {"score": 68.0},
            "migration": {"score": 75.0},
        },
        "convenience_scores": {
            "accessibility": {"score": 80.0},
            "retail": {"score": 65.0},
            "transit": {"score": 70.0},
        },
        "elasticity_scores": {"vacancy": {"score": 78.0}, "momentum": {"score": 73.0}},
    }

    report = reporter.generate_report(submarket_name="Test Market", **partial_data)

    completeness = report["data_completeness"]

    assert completeness["completeness_percentage"] < 100.0
    assert completeness["confidence_level"] in ["Medium", "Medium-High", "Low"]
    assert len(completeness["missing_components"]) > 0


def test_export_to_markdown(reporter: MarketAnalysisReport, sample_data: dict) -> None:
    """Test markdown export functionality."""
    report = reporter.generate_report(submarket_name="Boulder, CO", **sample_data)

    markdown = reporter.export_to_markdown(report)

    assert isinstance(markdown, str)
    assert "# Market Analysis Report: Boulder, CO" in markdown
    assert "## Executive Summary" in markdown
    assert "## Strengths" in markdown
    assert "## Weaknesses" in markdown
    assert "## Recommendations" in markdown
    assert "## Data Quality" in markdown


def test_market_tier_classification(reporter: MarketAnalysisReport) -> None:
    """Test market tier classification logic."""
    # Tier 1: >= 80
    tier1_data = {
        "supply_constraint": {
            "score": 85.0,
            "metadata": {"complete": True, "missing_components": []},
        },
        "employment_score": {"score": 82.0},
        "demographic_scores": {
            "population": {"score": 80.0},
            "income": {"score": 78.0},
            "migration": {"score": 85.0},
        },
        "convenience_scores": {
            "accessibility": {"score": 82.0},
            "retail": {"score": 75.0},
            "transit": {"score": 80.0},
        },
        "elasticity_scores": {"vacancy": {"score": 85.0}, "momentum": {"score": 80.0}},
    }

    report = reporter.generate_report(submarket_name="Tier 1 Market", **tier1_data)

    assert report["executive_summary"]["market_tier"] == "Tier 1 (Highly Attractive)"
    assert report["executive_summary"]["overall_score"] >= 80

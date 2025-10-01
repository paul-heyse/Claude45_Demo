"""Tests for asset fit report generation."""

from __future__ import annotations

import pytest

from Claude45_Demo.asset_evaluation.reporting import ReportGenerator


@pytest.fixture
def generator():
    """Create report generator."""
    return ReportGenerator()


@pytest.fixture
def sample_property_data():
    """Sample property data."""
    return {
        "property_id": "PROP-001",
        "name": "Mountain View Apartments",
        "location": "Denver, CO",
        "units": 200,
        "year_built": 2005,
    }


@pytest.fixture
def sample_analyses():
    """Sample analysis results."""
    return {
        "product_classification": {
            "product_type": "low-rise",
            "aker_fit_score": 85,
            "description": "Low-rise multifamily",
        },
        "deal_archetype": {
            "archetype": "value_add_light",
            "score": 82,
            "rent_lift_range": (90, 180),
        },
        "unit_mix": {
            "mix": {"studio": 0.2, "one_bed": 0.4, "two_bed": 0.3, "three_bed": 0.1},
            "rationale": "Balanced mix",
        },
        "amenities": {
            "outdoor_brand_score": 75,
            "ev_readiness_score": 60,
            "remote_work_score": 70,
        },
        "parking": {
            "recommended_ratio": 1.1,
            "rationale": "Suburban location",
        },
        "capex": {
            "interior_capex_per_unit": 8000,
            "rent_lift": 135,
            "payback_years": 4.2,
        },
        "portfolio_fit": {
            "diversification_score": 75,
            "geographic_impact": "improves",
        },
        "exit_strategy": {
            "base_irr": 0.18,
            "recommended_hold": 5,
        },
        "diligence": {
            "physical": ["Roof inspection", "HVAC assessment"],
            "financial": ["Rent roll audit", "T-12 review"],
        },
    }


def test_generate_asset_report_complete(
    generator, sample_property_data, sample_analyses
):
    """Test generating complete asset report."""
    report = generator.generate_asset_report(
        property_id="PROP-001",
        property_data=sample_property_data,
        analyses=sample_analyses,
    )

    # Verify summary
    assert report.summary.property_id == "PROP-001"
    assert report.summary.property_name == "Mountain View Apartments"
    assert report.summary.location == "Denver, CO"
    assert report.summary.units == 200
    assert report.summary.vintage == 2005
    assert report.summary.product_type == "low-rise"
    assert report.summary.aker_fit_score == 85
    assert report.summary.deal_archetype == "value_add_light"

    # Verify analyses included
    assert report.product_classification == sample_analyses["product_classification"]
    assert report.deal_archetype == sample_analyses["deal_archetype"]
    assert report.unit_mix_recommendation == sample_analyses["unit_mix"]
    assert report.amenity_scores == sample_analyses["amenities"]
    assert report.parking_recommendation == sample_analyses["parking"]
    assert report.capex_estimates == sample_analyses["capex"]
    assert report.portfolio_fit == sample_analyses["portfolio_fit"]
    assert report.exit_projections == sample_analyses["exit_strategy"]

    # Verify diligence checklist compiled
    assert len(report.diligence_checklist) == 4
    assert any("roof" in item.lower() for item in report.diligence_checklist)

    # Verify overall recommendation
    assert report.overall_recommendation
    assert "strong buy" in report.overall_recommendation.lower()


def test_generate_asset_report_strong_buy(generator, sample_property_data):
    """Test strong buy recommendation for high-fit property."""
    analyses = {
        "product_classification": {"product_type": "garden", "aker_fit_score": 95},
        "deal_archetype": {"archetype": "value_add_light"},
        "portfolio_fit": {"diversification_score": 85},
    }

    report = generator.generate_asset_report(
        property_id="PROP-002",
        property_data=sample_property_data,
        analyses=analyses,
    )

    assert "strong buy" in report.overall_recommendation.lower()
    assert "95" in report.overall_recommendation


def test_generate_asset_report_pass_recommendation(generator, sample_property_data):
    """Test pass recommendation for low-fit property."""
    analyses = {
        "product_classification": {"product_type": "high-rise", "aker_fit_score": 35},
        "deal_archetype": {"archetype": "heavy_lift_reposition"},
        "portfolio_fit": {"diversification_score": 40},
    }

    report = generator.generate_asset_report(
        property_id="PROP-003",
        property_data=sample_property_data,
        analyses=analyses,
    )

    assert "pass" in report.overall_recommendation.lower()
    assert "below" in report.overall_recommendation.lower()


def test_generate_asset_report_conditional_recommendation(
    generator, sample_property_data
):
    """Test conditional recommendation for moderate-fit property."""
    analyses = {
        "product_classification": {"product_type": "mid-rise", "aker_fit_score": 65},
        "deal_archetype": {"archetype": "value_add_medium"},
        "portfolio_fit": {"diversification_score": 60},
    }

    report = generator.generate_asset_report(
        property_id="PROP-004",
        property_data=sample_property_data,
        analyses=analyses,
    )

    assert "conditional" in report.overall_recommendation.lower()
    assert "moderate" in report.overall_recommendation.lower()


def test_batch_screen_properties_with_filters(generator):
    """Test batch screening with filters."""
    properties = [
        {
            "data": {
                "property_id": "P1",
                "name": "Property 1",
                "location": "Denver",
                "units": 150,
                "year_built": 2000,
            },
            "analyses": {
                "product_classification": {
                    "aker_fit_score": 85,
                    "product_type": "garden",
                },
                "deal_archetype": {"archetype": "value_add_light"},
                "portfolio_fit": {"diversification_score": 75},
                "exit_strategy": {"base_irr": 0.18},
            },
        },
        {
            "data": {
                "property_id": "P2",
                "name": "Property 2",
                "location": "Salt Lake City",
                "units": 200,
                "year_built": 2010,
            },
            "analyses": {
                "product_classification": {
                    "aker_fit_score": 90,
                    "product_type": "low-rise",
                },
                "deal_archetype": {"archetype": "value_add_light"},
                "portfolio_fit": {"diversification_score": 80},
                "exit_strategy": {"base_irr": 0.20},
            },
        },
        {
            "data": {
                "property_id": "P3",
                "name": "Property 3",
                "location": "Boise",
                "units": 30,  # Below minimum
                "year_built": 2005,
            },
            "analyses": {
                "product_classification": {
                    "aker_fit_score": 80,
                    "product_type": "garden",
                },
                "deal_archetype": {"archetype": "value_add_light"},
                "portfolio_fit": {"diversification_score": 70},
                "exit_strategy": {"base_irr": 0.16},
            },
        },
        {
            "data": {
                "property_id": "P4",
                "name": "Property 4",
                "location": "Denver",
                "units": 100,
                "year_built": 1995,
            },
            "analyses": {
                "product_classification": {
                    "aker_fit_score": 75,
                    "product_type": "low-rise",
                },
                "deal_archetype": {"archetype": "value_add_medium"},
                "portfolio_fit": {"diversification_score": 65},
                "exit_strategy": {"base_irr": 0.15},
            },
        },
    ]

    result = generator.batch_screen_properties(
        properties=properties,
        min_aker_fit=70,
        min_units=50,
        max_vintage=2015,
        preferred_archetypes=["value_add_light", "value_add_medium"],
        max_results=10,
    )

    # P3 should be filtered out (units too low)
    assert result.properties_evaluated == 4
    assert len(result.comparison_table) == 3  # P1, P2, P4
    assert len(result.top_candidates) == 3

    # P2 should be ranked first (highest scores)
    assert result.top_candidates[0]["property_id"] == "P2"
    assert result.top_candidates[0]["aker_fit_score"] == 90

    # Verify filters applied
    assert len(result.filters_applied) == 4
    assert result.recommendation


def test_batch_screen_properties_ranking(generator):
    """Test that properties are ranked by composite score."""
    properties = [
        {
            "data": {
                "property_id": "P1",
                "units": 100,
                "year_built": 2005,
            },
            "analyses": {
                "product_classification": {"aker_fit_score": 70},
                "deal_archetype": {"archetype": "value_add_light"},
                "portfolio_fit": {"diversification_score": 60},
                "exit_strategy": {"base_irr": 0.12},
            },
        },
        {
            "data": {
                "property_id": "P2",
                "units": 100,
                "year_built": 2005,
            },
            "analyses": {
                "product_classification": {"aker_fit_score": 85},
                "deal_archetype": {"archetype": "value_add_light"},
                "portfolio_fit": {"diversification_score": 75},
                "exit_strategy": {"base_irr": 0.18},
            },
        },
    ]

    result = generator.batch_screen_properties(
        properties=properties,
        min_aker_fit=60,
        min_units=50,
        max_vintage=2015,
        max_results=10,
    )

    # P2 should rank higher (better scores across the board)
    assert result.top_candidates[0]["property_id"] == "P2"
    assert result.top_candidates[1]["property_id"] == "P1"
    assert (
        result.top_candidates[0]["composite_score"]
        > result.top_candidates[1]["composite_score"]
    )


def test_batch_screen_no_qualifying_properties(generator):
    """Test batch screening when no properties meet criteria."""
    properties = [
        {
            "data": {
                "property_id": "P1",
                "units": 100,
                "year_built": 2005,
            },
            "analyses": {
                "product_classification": {"aker_fit_score": 45},  # Too low
                "deal_archetype": {"archetype": "value_add_light"},
            },
        }
    ]

    result = generator.batch_screen_properties(
        properties=properties,
        min_aker_fit=60,
        min_units=50,
        max_vintage=2015,
    )

    assert result.properties_evaluated == 1
    assert len(result.comparison_table) == 0
    assert len(result.top_candidates) == 0
    assert "no properties met" in result.recommendation.lower()


def test_batch_screen_limited_pipeline(generator):
    """Test recommendation for limited qualifying properties."""
    properties = [
        {
            "data": {"property_id": f"P{i}", "units": 100, "year_built": 2005},
            "analyses": {
                "product_classification": {"aker_fit_score": 70},
                "deal_archetype": {"archetype": "value_add_light"},
            },
        }
        for i in range(3)  # Only 3 properties
    ]

    result = generator.batch_screen_properties(
        properties=properties,
        min_aker_fit=60,
        min_units=50,
        max_vintage=2015,
    )

    assert len(result.comparison_table) == 3
    assert "limited pipeline" in result.recommendation.lower()


def test_batch_screen_strong_pipeline(generator):
    """Test recommendation for strong pipeline."""
    properties = [
        {
            "data": {"property_id": f"P{i}", "units": 100, "year_built": 2005},
            "analyses": {
                "product_classification": {"aker_fit_score": 75},
                "deal_archetype": {"archetype": "value_add_light"},
            },
        }
        for i in range(10)  # Strong pipeline
    ]

    result = generator.batch_screen_properties(
        properties=properties,
        min_aker_fit=60,
        min_units=50,
        max_vintage=2015,
        max_results=5,
    )

    assert len(result.comparison_table) == 10
    assert len(result.top_candidates) == 5  # Limited to max_results
    assert "strong pipeline" in result.recommendation.lower()


def test_export_to_excel(generator, sample_property_data, sample_analyses):
    """Test Excel export structure."""
    report = generator.generate_asset_report(
        property_id="PROP-001",
        property_data=sample_property_data,
        analyses=sample_analyses,
    )

    excel_data = generator.export_to_excel(report)

    # Verify sheets created
    assert "Summary" in excel_data
    assert "CapEx" in excel_data
    assert "Exit_Strategy" in excel_data
    assert "Diligence" in excel_data

    # Verify Summary sheet has property ID
    summary_sheet = excel_data["Summary"]
    assert any("PROP-001" in str(row) for row in summary_sheet)

    # Verify CapEx sheet has data
    capex_sheet = excel_data["CapEx"]
    assert len(capex_sheet) > 1  # Header + data rows

    # Verify Diligence sheet has checklist items
    diligence_sheet = excel_data["Diligence"]
    assert len(diligence_sheet) > 1


def test_generate_report_with_missing_analyses(generator, sample_property_data):
    """Test report generation with partial analyses."""
    minimal_analyses = {
        "product_classification": {"product_type": "garden", "aker_fit_score": 75},
    }

    report = generator.generate_asset_report(
        property_id="PROP-005",
        property_data=sample_property_data,
        analyses=minimal_analyses,
    )

    # Should handle missing analyses gracefully
    assert report.summary.aker_fit_score == 75
    assert report.product_classification == minimal_analyses["product_classification"]
    assert report.deal_archetype == {}  # Missing
    assert report.diligence_checklist == []  # No diligence data
    assert report.overall_recommendation  # Should still generate recommendation

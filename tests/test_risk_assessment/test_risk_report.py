"""Tests for risk report generation."""

import pytest

from Claude45_Demo.risk_assessment.risk_report import RiskReportGenerator


@pytest.fixture
def report_generator():
    """Risk report generator fixture."""
    return RiskReportGenerator()


@pytest.fixture
def sample_risk_scores():
    """Sample risk scores for testing."""
    return {
        "wildfire_score": 75,
        "flood_score": 45,
        "seismic_risk_score": 55,
        "hail_risk_score": 60,
        "environmental_risk_score": 40,
        "regulatory_score": 65,
        "composite_risk_score": 58,
        "risk_multiplier": 1.04,
        "cap_rate_adjustment_bps": 40,
        "exclude_market": False,
    }


@pytest.fixture
def sample_insurance_estimates():
    """Sample insurance cost estimates."""
    return {
        "insurance_cost_pct_replacement": 0.8,
        "insurance_multiplier": 2.67,
        "wildfire_premium_pct": 0.3,
        "flood_premium_pct": 0.15,
        "hail_premium_pct": 0.05,
    }


@pytest.fixture
def sample_regulatory_analysis():
    """Sample regulatory analysis."""
    return {
        "risk_level": "moderate",
        "composite_regulatory_score": 65,
        "median_days_to_permit": 145,
    }


class TestRiskScorecard:
    """Test risk scorecard generation."""

    def test_generate_scorecard(
        self,
        report_generator,
        sample_risk_scores,
        sample_insurance_estimates,
        sample_regulatory_analysis,
    ):
        """Test comprehensive scorecard generation."""
        location = {"latitude": 40.0150, "longitude": -105.2705}

        report = report_generator.generate_risk_scorecard(
            submarket_name="Boulder, CO",
            location=location,
            risk_scores=sample_risk_scores,
            insurance_estimates=sample_insurance_estimates,
            regulatory_analysis=sample_regulatory_analysis,
        )

        assert report["report_type"] == "Risk Scorecard"
        assert report["submarket"] == "Boulder, CO"
        assert "executive_summary" in report
        assert "risk_multiplier_summary" in report
        assert "component_scores" in report
        assert "mitigation_recommendations" in report

    def test_executive_summary_high_risk(
        self, report_generator, sample_insurance_estimates, sample_regulatory_analysis
    ):
        """Test executive summary for high risk market."""
        high_risk_scores = {
            "wildfire_score": 95,
            "flood_score": 85,
            "composite_risk_score": 88,
            "risk_multiplier": 1.10,
        }

        report = report_generator.generate_risk_scorecard(
            submarket_name="High Risk Area",
            location={"latitude": 40.0, "longitude": -105.0},
            risk_scores=high_risk_scores,
            insurance_estimates=sample_insurance_estimates,
            regulatory_analysis=sample_regulatory_analysis,
        )

        summary = report["executive_summary"]
        assert summary["overall_risk_level"] == "HIGH"
        assert "Not Recommended" in summary["investment_recommendation"]
        assert len(summary["top_risks"]) > 0

    def test_mitigation_recommendations(self, report_generator, sample_risk_scores):
        """Test mitigation recommendation generation."""
        location = {"latitude": 40.0, "longitude": -105.0}

        report = report_generator.generate_risk_scorecard(
            submarket_name="Test Market",
            location=location,
            risk_scores=sample_risk_scores,
            insurance_estimates={},
            regulatory_analysis={},
        )

        recommendations = report["mitigation_recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Should have wildfire mitigation (score 75 >= 60)
        wildfire_recs = [r for r in recommendations if "defensible space" in r.lower()]
        assert len(wildfire_recs) > 0

    def test_risk_flags(
        self,
        report_generator,
        sample_insurance_estimates,
        sample_regulatory_analysis,
    ):
        """Test risk flag identification."""
        extreme_risk_scores = {
            "wildfire_score": 95,
            "flood_score": 92,
            "environmental_risk_score": 75,
            "composite_risk_score": 85,
        }

        report = report_generator.generate_risk_scorecard(
            submarket_name="Extreme Risk Area",
            location={"latitude": 40.0, "longitude": -105.0},
            risk_scores=extreme_risk_scores,
            insurance_estimates=sample_insurance_estimates,
            regulatory_analysis=sample_regulatory_analysis,
        )

        flags = report["risk_flags"]
        assert len(flags) >= 2  # Should have at least wildfire and flood critical

        critical_flags = [f for f in flags if f["severity"] == "CRITICAL"]
        assert len(critical_flags) >= 2


class TestDiligenceChecklist:
    """Test due diligence checklist generation."""

    def test_generate_checklist(self, report_generator, sample_risk_scores):
        """Test diligence checklist generation."""
        checklist = report_generator.generate_diligence_checklist(
            submarket_name="Boulder, CO",
            risk_scores=sample_risk_scores,
            project_type="multifamily",
        )

        assert checklist["submarket"] == "Boulder, CO"
        assert checklist["project_type"] == "multifamily"
        assert "required_studies" in checklist
        assert "contractor_requirements" in checklist
        assert "risk_mitigation_budget" in checklist

    def test_required_studies_high_risk(self, report_generator):
        """Test that high risks trigger required studies."""
        high_risk_scores = {
            "environmental_risk_score": 75,
            "flood_score": 70,
            "seismic_risk_score": 65,
            "wildfire_score": 85,
        }

        checklist = report_generator.generate_diligence_checklist(
            submarket_name="Test Market",
            risk_scores=high_risk_scores,
        )

        studies = checklist["required_studies"]
        assert len(studies) >= 3  # Should require multiple studies

        # Check for Phase I ESA
        phase_i = [s for s in studies if "Phase I" in s["study"]]
        assert len(phase_i) > 0

        # Check for elevation certificate
        elevation = [s for s in studies if "Elevation" in s["study"]]
        assert len(elevation) > 0

    def test_mitigation_budget(self, report_generator):
        """Test mitigation budget estimation."""
        high_risk_scores = {
            "wildfire_score": 80,
            "seismic_risk_score": 70,
        }

        checklist = report_generator.generate_diligence_checklist(
            submarket_name="Test Market",
            risk_scores=high_risk_scores,
        )

        budget = checklist["risk_mitigation_budget"]
        assert budget["total_estimate_low"] > 0
        assert budget["total_estimate_high"] > budget["total_estimate_low"]
        assert len(budget["budget_items"]) > 0


class TestMarkdownExport:
    """Test markdown report export."""

    def test_scorecard_to_markdown(
        self,
        report_generator,
        sample_risk_scores,
        sample_insurance_estimates,
        sample_regulatory_analysis,
    ):
        """Test scorecard export to markdown."""
        report = report_generator.generate_risk_scorecard(
            submarket_name="Boulder, CO",
            location={"latitude": 40.0150, "longitude": -105.2705},
            risk_scores=sample_risk_scores,
            insurance_estimates=sample_insurance_estimates,
            regulatory_analysis=sample_regulatory_analysis,
        )

        markdown = report_generator.export_to_markdown(report)

        assert isinstance(markdown, str)
        assert "# Risk Assessment Scorecard" in markdown
        assert "Boulder, CO" in markdown
        assert "## Executive Summary" in markdown
        assert "## Component Risk Scores" in markdown

    def test_checklist_to_markdown(self, report_generator, sample_risk_scores):
        """Test checklist export to markdown."""
        checklist = report_generator.generate_diligence_checklist(
            submarket_name="Boulder, CO",
            risk_scores=sample_risk_scores,
        )

        markdown = report_generator.export_to_markdown(checklist)

        assert isinstance(markdown, str)
        assert "# Due Diligence Checklist" in markdown
        assert "Boulder, CO" in markdown
        assert "## Required Studies" in markdown

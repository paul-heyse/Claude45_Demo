"""Risk assessment report generation with comprehensive scoring and recommendations.

Generates human-readable risk reports with scores, hazard maps, cost implications,
and mitigation recommendations for investment committee review.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


class RiskReportGenerator:
    """Generate comprehensive risk assessment reports."""

    def __init__(self) -> None:
        """Initialize risk report generator."""
        logger.info("RiskReportGenerator initialized")

    def generate_risk_scorecard(
        self,
        submarket_name: str,
        location: dict[str, float],
        risk_scores: dict[str, Any],
        insurance_estimates: dict[str, Any],
        regulatory_analysis: dict[str, Any],
        mitigation_recommendations: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate comprehensive risk scorecard report.

        Implements:
        - Req: Risk Report Generation
        - Scenario: Risk scorecard export

        Args:
            submarket_name: Name of the submarket
            location: Dictionary with latitude, longitude
            risk_scores: Dictionary with all risk component scores
            insurance_estimates: Insurance cost estimates
            regulatory_analysis: Regulatory friction analysis
            mitigation_recommendations: Optional custom mitigation list

        Returns:
            Comprehensive risk scorecard dictionary
        """
        report = {
            "report_type": "Risk Scorecard",
            "submarket": submarket_name,
            "location": location,
            "generated_at": datetime.now(UTC).isoformat(),
            "executive_summary": self._generate_executive_summary(
                risk_scores, insurance_estimates, regulatory_analysis
            ),
            "risk_multiplier_summary": self._generate_multiplier_summary(risk_scores),
            "component_scores": self._format_component_scores(risk_scores),
            "hazard_assessment": self._format_hazard_assessment(risk_scores),
            "insurance_cost_estimates": insurance_estimates,
            "regulatory_friction": regulatory_analysis,
            "mitigation_recommendations": mitigation_recommendations
            or self._generate_mitigation_recommendations(risk_scores),
            "data_sources": self._list_data_sources(risk_scores),
            "risk_flags": self._identify_risk_flags(risk_scores),
        }

        logger.info(f"Generated risk scorecard for {submarket_name}")
        return report

    def generate_diligence_checklist(
        self,
        submarket_name: str,
        risk_scores: dict[str, Any],
        project_type: str = "multifamily",
    ) -> dict[str, Any]:
        """Generate risk-specific due diligence checklist.

        Implements:
        - Req: Risk Report Generation
        - Scenario: Diligence checklist generation

        Args:
            submarket_name: Name of the submarket
            risk_scores: Dictionary with all risk component scores
            project_type: Type of project (multifamily, mixed-use, etc.)

        Returns:
            Due diligence checklist with required studies and contacts
        """
        checklist = {
            "submarket": submarket_name,
            "project_type": project_type,
            "generated_at": datetime.now(UTC).isoformat(),
            "required_studies": self._identify_required_studies(risk_scores),
            "contractor_requirements": self._identify_contractor_requirements(
                risk_scores
            ),
            "insurance_carriers": self._list_insurance_carriers(risk_scores),
            "regulatory_milestones": self._identify_regulatory_milestones(risk_scores),
            "risk_mitigation_budget": self._estimate_mitigation_budget(risk_scores),
        }

        logger.info(f"Generated diligence checklist for {submarket_name}")
        return checklist

    def export_to_markdown(self, report: dict[str, Any]) -> str:
        """Export risk report to markdown format.

        Args:
            report: Risk scorecard or diligence checklist

        Returns:
            Markdown-formatted report string
        """
        if report.get("report_type") == "Risk Scorecard":
            return self._scorecard_to_markdown(report)
        else:
            return self._checklist_to_markdown(report)

    def _generate_executive_summary(
        self,
        risk_scores: dict[str, Any],
        insurance_estimates: dict[str, Any],
        regulatory_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate executive summary of risk assessment."""
        # Calculate overall risk level
        composite_risk = risk_scores.get("composite_risk_score", 50)

        if composite_risk >= 70:
            overall_risk = "HIGH"
            investment_recommendation = "Not Recommended - High risk exposure"
        elif composite_risk >= 50:
            overall_risk = "MODERATE"
            investment_recommendation = "Proceed with Caution - Apply risk multiplier"
        else:
            overall_risk = "LOW"
            investment_recommendation = "Favorable - Low risk environment"

        # Identify top risks
        top_risks = []
        for risk_type, score in risk_scores.items():
            if isinstance(score, (int, float)) and score >= 70:
                top_risks.append(
                    {
                        "risk_type": risk_type.replace("_score", "").title(),
                        "score": score,
                    }
                )

        # Sort by score descending
        top_risks.sort(key=lambda x: x["score"], reverse=True)

        return {
            "overall_risk_level": overall_risk,
            "composite_risk_score": composite_risk,
            "investment_recommendation": investment_recommendation,
            "top_risks": top_risks[:3],  # Top 3 risks
            "estimated_insurance_cost_pct": insurance_estimates.get(
                "insurance_cost_pct_replacement", 0.5
            ),
            "regulatory_friction_level": regulatory_analysis.get(
                "risk_level", "unknown"
            ),
        }

    def _generate_multiplier_summary(
        self, risk_scores: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate risk multiplier summary."""
        multiplier = risk_scores.get("risk_multiplier", 1.0)
        cap_rate_adjustment = risk_scores.get("cap_rate_adjustment_bps", 0)
        exclude_market = risk_scores.get("exclude_market", False)

        return {
            "risk_multiplier": multiplier,
            "cap_rate_adjustment_bps": cap_rate_adjustment,
            "market_exclusion_recommended": exclude_market,
            "multiplier_description": self._describe_multiplier(multiplier),
        }

    def _describe_multiplier(self, multiplier: float) -> str:
        """Describe what the multiplier means."""
        if multiplier >= 1.08:
            return "High risk - significant premium required"
        elif multiplier >= 1.04:
            return "Moderate risk - apply risk adjustment"
        elif multiplier <= 0.95:
            return "Low risk - favorable market conditions"
        else:
            return "Baseline risk - standard underwriting"

    def _format_component_scores(self, risk_scores: dict[str, Any]) -> dict[str, int]:
        """Format individual risk component scores."""
        components = {}
        score_keys = [
            "wildfire_score",
            "flood_score",
            "seismic_risk_score",
            "hail_risk_score",
            "radon_risk_score",
            "snow_load_risk_score",
            "water_risk_score",
            "environmental_risk_score",
            "regulatory_score",
        ]

        for key in score_keys:
            if key in risk_scores:
                clean_name = key.replace("_score", "").replace("_", " ").title()
                components[clean_name] = risk_scores[key]

        return components

    def _format_hazard_assessment(self, risk_scores: dict[str, Any]) -> dict[str, str]:
        """Format hazard assessment by category."""
        hazards = {}

        hazard_mapping = {
            "wildfire_score": "Wildfire",
            "flood_score": "Flood",
            "seismic_risk_score": "Seismic",
            "hail_risk_score": "Hail",
        }

        for score_key, hazard_name in hazard_mapping.items():
            if score_key in risk_scores:
                score = risk_scores[score_key]
                if score >= 70:
                    level = "HIGH RISK"
                elif score >= 50:
                    level = "MODERATE RISK"
                else:
                    level = "LOW RISK"
                hazards[hazard_name] = level

        return hazards

    def _generate_mitigation_recommendations(
        self, risk_scores: dict[str, Any]
    ) -> list[str]:
        """Generate risk-specific mitigation recommendations."""
        recommendations = []

        # Wildfire mitigation
        if risk_scores.get("wildfire_score", 0) >= 60:
            recommendations.extend(
                [
                    "Implement defensible space (minimum 30-100ft depending on risk)",
                    "Use fire-resistant roofing and siding materials",
                    "Install ember-resistant vents",
                    "Obtain wildfire insurance with appropriate deductible",
                ]
            )

        # Flood mitigation
        if risk_scores.get("flood_score", 0) >= 60:
            recommendations.extend(
                [
                    "Obtain elevation certificate",
                    "Design for base flood elevation + 2ft freeboard",
                    "Secure flood insurance (NFIP or private)",
                    "Consider dry floodproofing for lower levels",
                ]
            )

        # Seismic mitigation
        if risk_scores.get("seismic_risk_score", 0) >= 50:
            recommendations.extend(
                [
                    "Engage structural engineer for seismic design",
                    "Follow ASCE 7 seismic design category requirements",
                    "Budget for seismic bracing and reinforcement",
                ]
            )

        # Regulatory mitigation
        if risk_scores.get("regulatory_score", 0) >= 60:
            recommendations.extend(
                [
                    "Engage local land use attorney",
                    "Budget extended timeline (6-12 months additional)",
                    "Pre-application meeting with planning department",
                    "Consider community engagement strategy",
                ]
            )

        # Environmental mitigation
        if risk_scores.get("environmental_risk_score", 0) >= 50:
            recommendations.extend(
                [
                    "Conduct Phase I Environmental Site Assessment",
                    "Review EPA ECHO database for nearby violations",
                    "Consider environmental insurance",
                ]
            )

        return (
            recommendations
            if recommendations
            else ["Standard due diligence sufficient"]
        )

    def _list_data_sources(self, risk_scores: dict[str, Any]) -> list[str]:
        """List data sources used in risk assessment."""
        sources = [
            "USFS Wildfire Hazard Potential (WHP)",
            "LANDFIRE Fuel Models",
            "FEMA National Flood Hazard Layer (NFHL)",
            "USGS National Seismic Hazard Model",
            "NOAA Storm Prediction Center",
            "EPA Map of Radon Zones",
            "ASCE 7 Snow Load Maps",
            "State Water Rights Databases (CO/UT/ID)",
            "EPA ECHO and Facility Registry Services",
        ]
        return sources

    def _identify_risk_flags(self, risk_scores: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify critical risk flags requiring attention."""
        flags = []

        # Check for exclusion-level risks
        if risk_scores.get("wildfire_score", 0) > 90:
            flags.append(
                {
                    "severity": "CRITICAL",
                    "category": "Wildfire",
                    "message": "Extreme wildfire risk - market exclusion recommended",
                }
            )

        if risk_scores.get("flood_score", 0) > 90:
            flags.append(
                {
                    "severity": "CRITICAL",
                    "category": "Flood",
                    "message": "Extreme flood risk - market exclusion recommended",
                }
            )

        # Check for high risks
        high_risk_threshold = 70
        for risk_type in [
            "seismic_risk_score",
            "environmental_risk_score",
            "regulatory_score",
        ]:
            if risk_scores.get(risk_type, 0) >= high_risk_threshold:
                category = risk_type.replace("_score", "").replace("_risk", "").title()
                flags.append(
                    {
                        "severity": "HIGH",
                        "category": category,
                        "message": f"High {category.lower()} risk - detailed due diligence required",
                    }
                )

        return flags

    def _identify_required_studies(
        self, risk_scores: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Identify required studies based on risk scores."""
        studies = []

        # Phase I ESA
        if risk_scores.get("environmental_risk_score", 0) >= 50:
            studies.append(
                {
                    "study": "Phase I Environmental Site Assessment",
                    "priority": "Required",
                    "estimated_cost": "$3,000 - $5,000",
                }
            )

        # Elevation Certificate
        if risk_scores.get("flood_score", 0) >= 50:
            studies.append(
                {
                    "study": "FEMA Elevation Certificate",
                    "priority": "Required",
                    "estimated_cost": "$500 - $1,500",
                }
            )

        # Geotechnical Study
        if risk_scores.get("seismic_risk_score", 0) >= 50:
            studies.append(
                {
                    "study": "Geotechnical Investigation",
                    "priority": "Required",
                    "estimated_cost": "$5,000 - $15,000",
                }
            )

        # Wildfire Risk Assessment
        if risk_scores.get("wildfire_score", 0) >= 70:
            studies.append(
                {
                    "study": "Wildfire Risk Assessment & Mitigation Plan",
                    "priority": "Required",
                    "estimated_cost": "$2,000 - $5,000",
                }
            )

        return studies

    def _identify_contractor_requirements(
        self, risk_scores: dict[str, Any]
    ) -> list[str]:
        """Identify contractor requirements based on risks."""
        requirements = []

        if risk_scores.get("wildfire_score", 0) >= 60:
            requirements.append("Wildfire-resistant construction (Class A roofing)")

        if risk_scores.get("seismic_risk_score", 0) >= 50:
            requirements.append("Seismic design specialist required")

        if risk_scores.get("snow_load_risk_score", 0) >= 60:
            requirements.append("Heavy snow load structural design (>50 psf)")

        return requirements if requirements else ["Standard construction practices"]

    def _list_insurance_carriers(
        self, risk_scores: dict[str, Any]
    ) -> dict[str, list[str]]:
        """List relevant insurance carriers based on risk profile."""
        carriers = {}

        # Wildfire insurance
        if risk_scores.get("wildfire_score", 0) >= 50:
            carriers["Wildfire"] = [
                "California FAIR Plan (high risk)",
                "Chubb",
                "AIG Private Client Group",
            ]

        # Flood insurance
        if risk_scores.get("flood_score", 0) >= 50:
            carriers["Flood"] = [
                "FEMA National Flood Insurance Program (NFIP)",
                "Private flood carriers",
            ]

        return carriers

    def _identify_regulatory_milestones(self, risk_scores: dict[str, Any]) -> list[str]:
        """Identify key regulatory milestones."""
        if risk_scores.get("regulatory_score", 0) >= 60:
            return [
                "Pre-application meeting",
                "Community outreach (if required)",
                "Design review submission",
                "Planning commission hearing",
                "Building permit application",
                "Certificate of Occupancy",
            ]
        else:
            return [
                "Site plan review",
                "Building permit application",
                "Certificate of Occupancy",
            ]

    def _estimate_mitigation_budget(
        self, risk_scores: dict[str, Any]
    ) -> dict[str, Any]:
        """Estimate budget for risk mitigation measures."""
        budget_items = []
        total_estimate_low = 0
        total_estimate_high = 0

        # Wildfire mitigation
        if risk_scores.get("wildfire_score", 0) >= 60:
            budget_items.append(
                {
                    "category": "Wildfire Mitigation",
                    "items": ["Defensible space", "Fire-resistant materials"],
                    "estimate_low": 10000,
                    "estimate_high": 30000,
                }
            )
            total_estimate_low += 10000
            total_estimate_high += 30000

        # Seismic upgrades
        if risk_scores.get("seismic_risk_score", 0) >= 50:
            budget_items.append(
                {
                    "category": "Seismic Design",
                    "items": ["Enhanced structural design", "Seismic bracing"],
                    "estimate_low": 20000,
                    "estimate_high": 50000,
                }
            )
            total_estimate_low += 20000
            total_estimate_high += 50000

        return {
            "budget_items": budget_items,
            "total_estimate_low": total_estimate_low,
            "total_estimate_high": total_estimate_high,
            "total_estimate_range": f"${total_estimate_low:,} - ${total_estimate_high:,}",
        }

    def _scorecard_to_markdown(self, report: dict[str, Any]) -> str:
        """Convert scorecard report to markdown format."""
        md = "# Risk Assessment Scorecard\n\n"
        md += f"**Submarket:** {report['submarket']}\n"
        md += f"**Location:** {report['location']['latitude']}, {report['location']['longitude']}\n"
        md += f"**Generated:** {report['generated_at']}\n\n"

        # Executive Summary
        summary = report["executive_summary"]
        md += "## Executive Summary\n\n"
        md += f"- **Overall Risk Level:** {summary['overall_risk_level']}\n"
        md += f"- **Composite Risk Score:** {summary['composite_risk_score']}/100\n"
        md += f"- **Recommendation:** {summary['investment_recommendation']}\n"
        md += f"- **Insurance Cost Estimate:** {summary['estimated_insurance_cost_pct']}% of replacement cost\n\n"

        # Risk Multiplier
        multiplier = report["risk_multiplier_summary"]
        md += "## Risk Multiplier\n\n"
        md += f"- **Multiplier:** {multiplier['risk_multiplier']}\n"
        md += (
            f"- **Cap Rate Adjustment:** +{multiplier['cap_rate_adjustment_bps']} bps\n"
        )
        md += f"- **Market Exclusion:** {'Yes' if multiplier['market_exclusion_recommended'] else 'No'}\n\n"

        # Component Scores
        md += "## Component Risk Scores\n\n"
        for component, score in report["component_scores"].items():
            md += f"- **{component}:** {score}/100\n"
        md += "\n"

        # Mitigation Recommendations
        md += "## Mitigation Recommendations\n\n"
        for rec in report["mitigation_recommendations"]:
            md += f"- {rec}\n"
        md += "\n"

        # Risk Flags
        if report["risk_flags"]:
            md += "## Risk Flags\n\n"
            for flag in report["risk_flags"]:
                md += f"- **[{flag['severity']}]** {flag['category']}: {flag['message']}\n"
            md += "\n"

        return md

    def _checklist_to_markdown(self, checklist: dict[str, Any]) -> str:
        """Convert diligence checklist to markdown format."""
        md = "# Due Diligence Checklist\n\n"
        md += f"**Submarket:** {checklist['submarket']}\n"
        md += f"**Project Type:** {checklist['project_type']}\n"
        md += f"**Generated:** {checklist['generated_at']}\n\n"

        # Required Studies
        md += "## Required Studies\n\n"
        for study in checklist["required_studies"]:
            md += f"- **{study['study']}** ({study['priority']})\n"
            md += f"  - Estimated Cost: {study['estimated_cost']}\n"
        md += "\n"

        # Contractor Requirements
        md += "## Contractor Requirements\n\n"
        for req in checklist["contractor_requirements"]:
            md += f"- {req}\n"
        md += "\n"

        # Mitigation Budget
        budget = checklist["risk_mitigation_budget"]
        if budget["budget_items"]:
            md += "## Risk Mitigation Budget\n\n"
            for item in budget["budget_items"]:
                estimate_range = (
                    f"${item['estimate_low']:,} - ${item['estimate_high']:,}"
                )
                md += f"- **{item['category']}:** {estimate_range}\n"
            md += f"\n**Total Estimate:** {budget['total_estimate_range']}\n\n"

        return md

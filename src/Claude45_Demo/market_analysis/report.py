"""Market analysis report generator."""

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


class MarketAnalysisReport:
    """Generate comprehensive market analysis reports."""

    def generate_report(
        self,
        submarket_name: str,
        supply_constraint: dict[str, Any],
        employment_score: dict[str, Any],
        demographic_scores: dict[str, dict[str, Any]],
        convenience_scores: dict[str, dict[str, Any]],
        elasticity_scores: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Generate comprehensive market analysis report.

        Implements Task 3.10: Market analysis report generator

        Args:
            submarket_name: Name of the submarket being analyzed
            supply_constraint: Supply constraint analysis results
            employment_score: Innovation employment analysis results
            demographic_scores: Dict of demographic analysis results
            convenience_scores: Dict of urban convenience analysis results
            elasticity_scores: Dict of market elasticity analysis results

        Returns:
            Comprehensive market analysis report with scores and insights
        """
        report = {
            "submarket": submarket_name,
            "generated_at": datetime.now(UTC).isoformat(),
            "executive_summary": self._generate_executive_summary(
                supply_constraint,
                employment_score,
                demographic_scores,
                convenience_scores,
                elasticity_scores,
            ),
            "component_scores": {
                "supply_constraint": supply_constraint["score"],
                "innovation_employment": employment_score["score"],
                "population_growth": demographic_scores["population"]["score"],
                "income_trend": demographic_scores["income"]["score"],
                "migration": demographic_scores["migration"]["score"],
                "accessibility": convenience_scores["accessibility"]["score"],
                "retail_health": convenience_scores["retail"]["score"],
                "transit_quality": convenience_scores["transit"]["score"],
                "vacancy": elasticity_scores["vacancy"]["score"],
                "momentum": elasticity_scores["momentum"]["score"],
            },
            "composite_scores": self._calculate_composite_scores(
                supply_constraint,
                employment_score,
                demographic_scores,
                convenience_scores,
                elasticity_scores,
            ),
            "strengths": self._identify_strengths(
                supply_constraint,
                employment_score,
                demographic_scores,
                convenience_scores,
                elasticity_scores,
            ),
            "weaknesses": self._identify_weaknesses(
                supply_constraint,
                employment_score,
                demographic_scores,
                convenience_scores,
                elasticity_scores,
            ),
            "recommendations": self._generate_recommendations(
                supply_constraint,
                employment_score,
                demographic_scores,
                convenience_scores,
                elasticity_scores,
            ),
            "data_completeness": self._assess_data_completeness(
                supply_constraint,
                employment_score,
                demographic_scores,
                convenience_scores,
                elasticity_scores,
            ),
        }

        logger.info(f"Generated market analysis report for {submarket_name}")
        return report

    def _generate_executive_summary(
        self,
        supply_constraint: dict[str, Any],
        employment_score: dict[str, Any],
        demographic_scores: dict[str, dict[str, Any]],
        convenience_scores: dict[str, dict[str, Any]],
        elasticity_scores: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate executive summary with key findings."""
        # Calculate overall market attractiveness
        avg_supply = supply_constraint["score"]
        avg_employment = employment_score["score"]
        avg_demographics = (
            sum(
                s["score"]
                for s in [
                    demographic_scores["population"],
                    demographic_scores["income"],
                    demographic_scores["migration"],
                ]
            )
            / 3
        )
        avg_convenience = (
            sum(
                s["score"]
                for s in [
                    convenience_scores["accessibility"],
                    convenience_scores["retail"],
                    convenience_scores["transit"],
                ]
            )
            / 3
        )
        avg_elasticity = (
            sum(
                s["score"]
                for s in [elasticity_scores["vacancy"], elasticity_scores["momentum"]]
            )
            / 2
        )

        overall_score = (
            avg_supply * 0.25
            + avg_employment * 0.25
            + avg_demographics * 0.20
            + avg_convenience * 0.15
            + avg_elasticity * 0.15
        )

        # Determine market tier
        if overall_score >= 80:
            tier = "Tier 1 (Highly Attractive)"
        elif overall_score >= 65:
            tier = "Tier 2 (Attractive)"
        elif overall_score >= 50:
            tier = "Tier 3 (Moderate)"
        else:
            tier = "Tier 4 (Below Target)"

        return {
            "overall_score": round(overall_score, 1),
            "market_tier": tier,
            "supply_score": round(avg_supply, 1),
            "employment_score": round(avg_employment, 1),
            "demographics_score": round(avg_demographics, 1),
            "convenience_score": round(avg_convenience, 1),
            "elasticity_score": round(avg_elasticity, 1),
        }

    def _calculate_composite_scores(
        self,
        supply_constraint: dict[str, Any],
        employment_score: dict[str, Any],
        demographic_scores: dict[str, dict[str, Any]],
        convenience_scores: dict[str, dict[str, Any]],
        elasticity_scores: dict[str, dict[str, Any]],
    ) -> dict[str, float]:
        """Calculate composite scores for major categories."""
        demographics_composite = (
            demographic_scores["population"]["score"] * 0.40
            + demographic_scores["income"]["score"] * 0.35
            + demographic_scores["migration"]["score"] * 0.25
        )

        convenience_composite = (
            convenience_scores["accessibility"]["score"] * 0.50
            + convenience_scores["retail"]["score"] * 0.30
            + convenience_scores["transit"]["score"] * 0.20
        )

        elasticity_composite = (
            elasticity_scores["vacancy"]["score"] * 0.60
            + elasticity_scores["momentum"]["score"] * 0.40
        )

        return {
            "supply_constraint": round(supply_constraint["score"], 1),
            "innovation_employment": round(employment_score["score"], 1),
            "demographics": round(demographics_composite, 1),
            "urban_convenience": round(convenience_composite, 1),
            "market_elasticity": round(elasticity_composite, 1),
        }

    def _identify_strengths(
        self,
        supply_constraint: dict[str, Any],
        employment_score: dict[str, Any],
        demographic_scores: dict[str, dict[str, Any]],
        convenience_scores: dict[str, dict[str, Any]],
        elasticity_scores: dict[str, dict[str, Any]],
    ) -> list[str]:
        """Identify market strengths (scores >= 70)."""
        strengths = []

        if supply_constraint["score"] >= 70:
            strengths.append(
                f"Strong supply constraints ({supply_constraint['score']:.0f}/100) - "
                "Limited competition and scarcity value"
            )

        if employment_score["score"] >= 70:
            strengths.append(
                f"Robust innovation employment ({employment_score['score']:.0f}/100) - "
                "Strong job growth in key sectors"
            )

        if demographic_scores["population"]["score"] >= 70:
            strengths.append(
                "Strong population growth - Expanding resident base and rental demand"
            )

        if demographic_scores["migration"]["score"] >= 70:
            strengths.append(
                "Positive net migration - Attracting high-income households"
            )

        if convenience_scores["accessibility"]["score"] >= 70:
            strengths.append(
                "Excellent 15-minute accessibility - High walkability and amenity access"
            )

        if elasticity_scores["vacancy"]["score"] >= 70:
            strengths.append(
                "Tight rental market - Low vacancy indicates strong demand"
            )

        if elasticity_scores["momentum"]["score"] >= 70:
            strengths.append("Strong market momentum - Positive 3-year growth trends")

        return strengths

    def _identify_weaknesses(
        self,
        supply_constraint: dict[str, Any],
        employment_score: dict[str, Any],
        demographic_scores: dict[str, dict[str, Any]],
        convenience_scores: dict[str, dict[str, Any]],
        elasticity_scores: dict[str, dict[str, Any]],
    ) -> list[str]:
        """Identify market weaknesses (scores < 50)."""
        weaknesses = []

        if supply_constraint["score"] < 50:
            weaknesses.append(
                f"Weak supply constraints ({supply_constraint['score']:.0f}/100) - "
                "High permit issuance and elastic supply"
            )

        if employment_score["score"] < 50:
            weaknesses.append(
                "Limited innovation employment - Weak job growth in key sectors"
            )

        if demographic_scores["population"]["score"] < 50:
            weaknesses.append("Slow population growth - Limited demand expansion")

        if demographic_scores["income"]["score"] < 50:
            weaknesses.append("Weak income trends - Limited rent growth potential")

        if demographic_scores["migration"]["score"] < 50:
            weaknesses.append("Net out-migration - Losing residents to other markets")

        if convenience_scores["accessibility"]["score"] < 50:
            weaknesses.append(
                "Poor walkability - Limited amenity access within 15 minutes"
            )

        if convenience_scores["transit"]["score"] < 50:
            weaknesses.append(
                "Weak transit service - Infrequent service or limited coverage"
            )

        if elasticity_scores["vacancy"]["score"] < 50:
            weaknesses.append("Elevated vacancy - Indicates oversupply or weak demand")

        return weaknesses

    def _generate_recommendations(
        self,
        supply_constraint: dict[str, Any],
        employment_score: dict[str, Any],
        demographic_scores: dict[str, dict[str, Any]],
        convenience_scores: dict[str, dict[str, Any]],
        elasticity_scores: dict[str, dict[str, Any]],
    ) -> list[str]:
        """Generate investment recommendations."""
        recommendations = []

        # High supply constraint + strong demand = excellent opportunity
        if (
            supply_constraint["score"] >= 70
            and elasticity_scores["vacancy"]["score"] >= 70
        ):
            recommendations.append(
                "STRONG BUY: Constrained supply with tight market conditions - "
                "Pricing power and limited competition"
            )

        # Strong employment + demographics = demand drivers
        if (
            employment_score["score"] >= 70
            and demographic_scores["population"]["score"] >= 70
        ):
            recommendations.append(
                "Favorable demand fundamentals - Job and population growth support rent growth"
            )

        # Good convenience + transit = urbanist appeal
        if (
            convenience_scores["accessibility"]["score"] >= 70
            and convenience_scores["transit"]["score"] >= 70
        ):
            recommendations.append(
                "Target walkable, transit-oriented product - Appeals to urban lifestyle preferences"
            )

        # Weak supply constraints = caution
        if supply_constraint["score"] < 50:
            recommendations.append(
                "CAUTION: Elastic supply - Focus on differentiated product or unique locations"
            )

        # High vacancy = market risk
        if elasticity_scores["vacancy"]["score"] < 40:
            recommendations.append(
                "AVOID: Elevated vacancy indicates oversupply - Wait for market rebalancing"
            )

        # Mixed signals
        if not recommendations:
            recommendations.append(
                "HOLD: Mixed market signals - Conduct deeper submarket analysis"
            )

        return recommendations

    def _assess_data_completeness(
        self,
        supply_constraint: dict[str, Any],
        employment_score: dict[str, Any],
        demographic_scores: dict[str, dict[str, Any]],
        convenience_scores: dict[str, dict[str, Any]],
        elasticity_scores: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Assess data completeness and confidence."""
        missing_components = []

        if not supply_constraint.get("metadata", {}).get("complete", True):
            missing_components.extend(
                supply_constraint["metadata"].get("missing_components", [])
            )

        # Count total metrics and available metrics
        total_metrics = 10
        available_metrics = total_metrics - len(missing_components)

        completeness_pct = (available_metrics / total_metrics) * 100

        if completeness_pct == 100:
            confidence = "High"
        elif completeness_pct >= 80:
            confidence = "Medium-High"
        elif completeness_pct >= 60:
            confidence = "Medium"
        else:
            confidence = "Low"

        return {
            "completeness_percentage": round(completeness_pct, 1),
            "confidence_level": confidence,
            "missing_components": missing_components,
            "recommendation": (
                "Data complete - High confidence in analysis"
                if completeness_pct == 100
                else f"Missing {len(missing_components)} components - "
                "Consider supplementing data for more robust analysis"
            ),
        }

    def export_to_markdown(self, report: dict[str, Any]) -> str:
        """Export report to markdown format."""
        md = f"""# Market Analysis Report: {report['submarket']}

**Generated:** {report['generated_at']}

## Executive Summary

**Overall Market Score:** {report['executive_summary']['overall_score']:.1f}/100
**Market Tier:** {report['executive_summary']['market_tier']}

### Category Scores
- Supply Constraint: {report['executive_summary']['supply_score']:.1f}/100
- Innovation Employment: {report['executive_summary']['employment_score']:.1f}/100
- Demographics: {report['executive_summary']['demographics_score']:.1f}/100
- Urban Convenience: {report['executive_summary']['convenience_score']:.1f}/100
- Market Elasticity: {report['executive_summary']['elasticity_score']:.1f}/100

## Strengths

{self._format_list(report['strengths'])}

## Weaknesses

{self._format_list(report['weaknesses'])}

## Recommendations

{self._format_list(report['recommendations'])}

## Data Quality

**Completeness:** {report['data_completeness']['completeness_percentage']:.1f}%
**Confidence Level:** {report['data_completeness']['confidence_level']}

{report['data_completeness']['recommendation']}
"""
        return md

    def _format_list(self, items: list[str]) -> str:
        """Format list items for markdown."""
        if not items:
            return "- None identified\n"
        return "\n".join(f"- {item}" for item in items) + "\n"

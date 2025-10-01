"""Asset fit report generation and batch property screening.

Generates comprehensive evaluation reports and ranks properties by fit score.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class AssetSummary:
    """Summary information for a single property."""

    property_id: str
    property_name: str
    location: str
    product_type: str
    aker_fit_score: int  # 0-100
    units: int
    vintage: int
    deal_archetype: str


@dataclass(frozen=True)
class AssetReport:
    """Comprehensive asset evaluation report."""

    summary: AssetSummary
    product_classification: Dict[str, Any]
    deal_archetype: Dict[str, Any]
    unit_mix_recommendation: Dict[str, Any]
    amenity_scores: Dict[str, Any]
    parking_recommendation: Dict[str, Any]
    capex_estimates: Dict[str, Any]
    portfolio_fit: Dict[str, Any]
    exit_projections: Dict[str, Any]
    diligence_checklist: List[str]
    overall_recommendation: str


@dataclass(frozen=True)
class BatchScreeningResult:
    """Batch property screening results."""

    properties_evaluated: int
    top_candidates: List[Dict[str, Any]]  # Top 10 by fit score
    comparison_table: List[Dict[str, Any]]  # All properties with key metrics
    filters_applied: List[str]
    recommendation: str


class ReportGenerator:
    """Generate asset evaluation reports and batch screening."""

    def __init__(self) -> None:
        """Initialize report generator."""
        pass

    def generate_asset_report(
        self,
        *,
        property_id: str,
        property_data: Dict[str, Any],
        analyses: Dict[str, Any],  # Results from various analyzers
    ) -> AssetReport:
        """Generate comprehensive asset evaluation report.

        Args:
            property_id: Unique property identifier
            property_data: Core property characteristics
            analyses: Dictionary of analysis results from asset_evaluation modules
                Expected keys:
                - product_classification: ProductTypeClassifier results
                - deal_archetype: DealArchetypeClassifier results
                - unit_mix: UnitMixOptimizer results
                - amenities: AmenityScores
                - parking: ParkingRecommendation
                - capex: CapexEstimator results
                - portfolio_fit: PortfolioAnalyzer results
                - exit_strategy: ExitAnalyzer results
                - diligence: DiligenceChecklistBuilder results

        Returns:
            AssetReport with all analyses compiled

        Spec: Requirement 12, Scenario "Asset summary report"
        """
        # Extract summary data
        summary = AssetSummary(
            property_id=property_id,
            property_name=property_data.get("name", property_id),
            location=property_data.get("location", "Unknown"),
            product_type=analyses.get("product_classification", {}).get(
                "product_type", "unknown"
            ),
            aker_fit_score=analyses.get("product_classification", {}).get(
                "aker_fit_score", 0
            ),
            units=property_data.get("units", 0),
            vintage=property_data.get("year_built", 0),
            deal_archetype=analyses.get("deal_archetype", {}).get(
                "archetype", "unknown"
            ),
        )

        # Compile all analysis sections
        product_classification = analyses.get("product_classification", {})
        deal_archetype = analyses.get("deal_archetype", {})
        unit_mix_recommendation = analyses.get("unit_mix", {})
        amenity_scores = analyses.get("amenities", {})
        parking_recommendation = analyses.get("parking", {})
        capex_estimates = analyses.get("capex", {})
        portfolio_fit = analyses.get("portfolio_fit", {})
        exit_projections = analyses.get("exit_strategy", {})

        # Generate diligence checklist
        diligence_data = analyses.get("diligence", {})
        if isinstance(diligence_data, dict):
            diligence_checklist = []
            for section, items in diligence_data.items():
                diligence_checklist.extend([f"[{section}] {item}" for item in items])
        else:
            diligence_checklist = []

        # Generate overall recommendation
        aker_fit = summary.aker_fit_score
        archetype = summary.deal_archetype
        portfolio_score = (
            portfolio_fit.get("diversification_score", 50) if portfolio_fit else 50
        )

        if aker_fit >= 85 and portfolio_score >= 70:
            overall_recommendation = (
                f"STRONG BUY: Excellent Aker fit ({aker_fit}/100), {archetype} archetype. "
                f"Strong portfolio fit. Recommend proceeding to LOI."
            )
        elif aker_fit >= 70 and portfolio_score >= 60:
            overall_recommendation = (
                f"PURSUE: Good Aker fit ({aker_fit}/100), {archetype} opportunity. "
                f"Proceed to detailed diligence."
            )
        elif aker_fit >= 60:
            overall_recommendation = (
                f"CONDITIONAL: Moderate fit ({aker_fit}/100). Evaluate against alternatives. "
                f"Requires strong execution on value-add plan."
            )
        else:
            overall_recommendation = (
                f"PASS: Below Aker fit threshold ({aker_fit}/100). "
                f"Focus on higher-scoring opportunities."
            )

        return AssetReport(
            summary=summary,
            product_classification=product_classification,
            deal_archetype=deal_archetype,
            unit_mix_recommendation=unit_mix_recommendation,
            amenity_scores=amenity_scores,
            parking_recommendation=parking_recommendation,
            capex_estimates=capex_estimates,
            portfolio_fit=portfolio_fit,
            exit_projections=exit_projections,
            diligence_checklist=diligence_checklist,
            overall_recommendation=overall_recommendation,
        )

    def batch_screen_properties(
        self,
        *,
        properties: List[Dict[str, Any]],  # List of property data + analyses
        min_aker_fit: int = 60,
        min_units: int = 50,
        max_vintage: int = 2015,
        preferred_archetypes: List[str] | None = None,
        max_results: int = 10,
    ) -> BatchScreeningResult:
        """Rank and filter properties by Aker fit score.

        Args:
            properties: List of property dicts with data and analyses
            min_aker_fit: Minimum Aker fit score (0-100)
            min_units: Minimum unit count
            max_vintage: Maximum year built for value-add
            preferred_archetypes: List of preferred deal archetypes (None = all)
            max_results: Maximum number of top candidates to return

        Returns:
            BatchScreeningResult with ranked properties and comparison table

        Spec: Requirement 12, Scenario "Batch property screening"
        """
        if preferred_archetypes is None:
            preferred_archetypes = [
                "value_add_light",
                "value_add_medium",
                "ground_up_infill",
            ]

        filters_applied = [
            f"Min Aker Fit: {min_aker_fit}",
            f"Min Units: {min_units}",
            f"Max Vintage: {max_vintage}",
            f"Archetypes: {', '.join(preferred_archetypes)}",
        ]

        # Filter and score properties
        filtered_properties = []
        for prop in properties:
            prop_data = prop.get("data", {})
            analyses = prop.get("analyses", {})

            # Extract key metrics
            aker_fit_score = analyses.get("product_classification", {}).get(
                "aker_fit_score", 0
            )
            units = prop_data.get("units", 0)
            vintage = prop_data.get("year_built", 9999)
            archetype = analyses.get("deal_archetype", {}).get("archetype", "unknown")

            # Apply filters
            if aker_fit_score < min_aker_fit:
                continue
            if units < min_units:
                continue
            if vintage > max_vintage:
                continue
            if archetype not in preferred_archetypes:
                continue

            # Calculate composite score for ranking
            # Weight: Aker fit 60%, portfolio fit 20%, IRR potential 20%
            portfolio_score = analyses.get("portfolio_fit", {}).get(
                "diversification_score", 50
            )
            exit_irr = analyses.get("exit_strategy", {}).get("base_irr", 0.12)

            composite_score = (
                (aker_fit_score * 0.6)
                + (portfolio_score * 0.2)
                + (exit_irr * 1000 * 0.2)
            )

            filtered_properties.append(
                {
                    "property_id": prop_data.get("property_id", "unknown"),
                    "property_name": prop_data.get("name", "Unknown"),
                    "location": prop_data.get("location", "Unknown"),
                    "units": units,
                    "vintage": vintage,
                    "product_type": analyses.get("product_classification", {}).get(
                        "product_type", "unknown"
                    ),
                    "archetype": archetype,
                    "aker_fit_score": aker_fit_score,
                    "portfolio_score": portfolio_score,
                    "projected_irr": exit_irr,
                    "composite_score": round(composite_score, 1),
                }
            )

        # Sort by composite score descending
        filtered_properties.sort(key=lambda p: p["composite_score"], reverse=True)

        # Extract top candidates
        top_candidates = filtered_properties[:max_results]

        # Generate recommendation
        if len(filtered_properties) == 0:
            recommendation = (
                "No properties met screening criteria. "
                "Consider relaxing filters or expanding market search."
            )
        elif len(top_candidates) >= 5:
            recommendation = (
                f"Strong pipeline: {len(filtered_properties)} properties passed screening. "
                f"Focus on top {len(top_candidates)} candidates for detailed diligence."
            )
        else:
            recommendation = (
                f"Limited pipeline: {len(filtered_properties)} properties passed screening. "
                f"Pursue all qualified candidates while expanding deal flow."
            )

        return BatchScreeningResult(
            properties_evaluated=len(properties),
            top_candidates=top_candidates,
            comparison_table=filtered_properties,  # All filtered properties
            filters_applied=filters_applied,
            recommendation=recommendation,
        )

    def export_to_excel(self, report: AssetReport) -> Dict[str, List[List[Any]]]:
        """Export report data to Excel-ready format.

        Args:
            report: AssetReport to export

        Returns:
            Dictionary mapping sheet names to row data

        Note: This returns structured data for Excel export.
        Actual file writing would use pandas/openpyxl.
        """
        sheets = {}

        # Summary sheet
        sheets["Summary"] = [
            ["Property ID", report.summary.property_id],
            ["Property Name", report.summary.property_name],
            ["Location", report.summary.location],
            ["Units", report.summary.units],
            ["Vintage", report.summary.vintage],
            ["Product Type", report.summary.product_type],
            ["Deal Archetype", report.summary.deal_archetype],
            ["Aker Fit Score", report.summary.aker_fit_score],
            [""],
            ["RECOMMENDATION"],
            ["", report.overall_recommendation],
        ]

        # CapEx sheet
        capex_rows = [["CapEx Analysis", ""]]
        for key, value in report.capex_estimates.items():
            capex_rows.append([key, value])
        sheets["CapEx"] = capex_rows

        # Exit Projections sheet
        exit_rows = [["Exit Strategy", ""]]
        for key, value in report.exit_projections.items():
            exit_rows.append([key, value])
        sheets["Exit_Strategy"] = exit_rows

        # Diligence Checklist sheet
        diligence_rows = [["Diligence Checklist"]]
        for item in report.diligence_checklist:
            diligence_rows.append([item])
        sheets["Diligence"] = diligence_rows

        return sheets

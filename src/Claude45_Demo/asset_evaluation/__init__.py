"""Asset Evaluation Module - Property classification and deal analysis."""

from __future__ import annotations

from .amenities import AmenityScores, evaluate_amenities
from .capex import CapexEstimator
from .construction import ConstructionAdjuster
from .deal_archetype import ArchetypeResult, DealArchetypeClassifier
from .diligence import DiligenceChecklistBuilder
from .exit_strategy import ExitAnalyzer
from .operations import LeaseUpForecast, NPSImpact, OperationsSupport, ProgrammingBudget
from .parking import ParkingAdvisor, ParkingRecommendation
from .portfolio import PortfolioAnalyzer
from .product_type import ProductTypeClassifier
from .reporting import ReportGenerator
from .unit_mix import UnitMixOptimizer, UnitMixRecommendation

__all__ = [
    # Product classification and deal analysis
    "ProductTypeClassifier",
    "DealArchetypeClassifier",
    "ArchetypeResult",
    # Unit mix and parking
    "UnitMixOptimizer",
    "UnitMixRecommendation",
    "ParkingAdvisor",
    "ParkingRecommendation",
    # Amenities and features
    "evaluate_amenities",
    "AmenityScores",
    # CapEx and ROI
    "CapexEstimator",
    # Operations support
    "OperationsSupport",
    "NPSImpact",
    "ProgrammingBudget",
    "LeaseUpForecast",
    # Diligence
    "DiligenceChecklistBuilder",
    # Portfolio fit analysis
    "PortfolioAnalyzer",
    # Exit strategy
    "ExitAnalyzer",
    # Construction adjustments
    "ConstructionAdjuster",
    # Reporting
    "ReportGenerator",
]

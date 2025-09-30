"""Employment and innovation scoring for market analysis."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class EmploymentAnalyzer:
    """Analyze employment trends, job mix, and innovation sectors."""

    # NAICS code groupings for innovation sectors
    TECH_NAICS = ["5112", "5415", "5182"]  # Software, Computer Systems, Data Processing
    HEALTHCARE_NAICS = ["621", "622", "6216"]  # Medical, Hospitals, Home Health
    EDUCATION_NAICS = ["6111", "6112", "6113"]  # Elementary, Secondary, Colleges
    MANUFACTURING_NAICS = ["3254", "3344", "3364"]  # Pharma, Semiconductors, Aerospace

    DEFAULT_SECTOR_WEIGHTS = {
        "tech": 0.40,
        "healthcare": 0.30,
        "education": 0.20,
        "manufacturing": 0.10,
    }

    def calculate_location_quotient(
        self, local_employment: dict[str, int], national_employment: dict[str, int]
    ) -> dict[str, float]:
        """
        Calculate Location Quotient (LQ) for sectors.

        LQ = (Local sector employment / Local total employment) /
             (National sector employment / National total employment)

        LQ > 1.0 indicates concentration, LQ < 1.0 indicates underrepresentation

        Args:
            local_employment: Dict of sector -> employment count (local area)
            national_employment: Dict of sector -> employment count (national)

        Returns:
            Dict of sector -> LQ value
        """
        local_total = sum(local_employment.values())
        national_total = sum(national_employment.values())

        if local_total == 0 or national_total == 0:
            return {sector: 0.0 for sector in local_employment}

        lq_scores = {}
        for sector in local_employment:
            if sector not in national_employment:
                lq_scores[sector] = 0.0
                continue

            local_share = local_employment[sector] / local_total
            national_share = national_employment[sector] / national_total

            if national_share == 0:
                lq_scores[sector] = 0.0
            else:
                lq_scores[sector] = round(local_share / national_share, 2)

        return lq_scores

    def calculate_cagr(self, start_value: float, end_value: float, years: int) -> float:
        """
        Calculate Compound Annual Growth Rate (CAGR).

        CAGR = ((end_value / start_value) ^ (1 / years)) - 1

        Args:
            start_value: Starting value
            end_value: Ending value
            years: Number of years

        Returns:
            CAGR as decimal (0.05 = 5% annual growth)
        """
        if start_value <= 0 or end_value <= 0 or years <= 0:
            return 0.0

        cagr = ((end_value / start_value) ** (1 / years)) - 1
        return round(cagr, 4)

    def calculate_innovation_employment_score(
        self,
        sector_cagr: dict[str, float],
        sector_lq: dict[str, float],
        sector_weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """
        Calculate innovation employment score based on job growth and concentration.

        Implements:
        - Req: Innovation Employment Scoring
        - Scenario: Sector job growth analysis

        Args:
            sector_cagr: Dict of sector -> 3-year CAGR
            sector_lq: Dict of sector -> Location Quotient
            sector_weights: Optional custom sector weights

        Returns:
            Dict with composite score and component details
        """
        if sector_weights is None:
            sector_weights = self.DEFAULT_SECTOR_WEIGHTS.copy()

        # Normalize CAGR to 0-100 score
        # Benchmark: 2% CAGR = 50, 5% CAGR = 100, negative = 0
        cagr_scores = {}
        for sector, cagr in sector_cagr.items():
            if cagr <= 0:
                cagr_scores[sector] = 0.0
            elif cagr >= 0.05:
                cagr_scores[sector] = 100.0
            else:
                # Linear scale from 0% to 5%
                cagr_scores[sector] = (cagr / 0.05) * 100.0

        # Normalize LQ to 0-100 score
        # Benchmark: LQ 1.0 = 50, LQ 1.5+ = 100, LQ 0.5 = 0
        lq_scores = {}
        for sector, lq in sector_lq.items():
            if lq <= 0.5:
                lq_scores[sector] = 0.0
            elif lq >= 1.5:
                lq_scores[sector] = 100.0
            else:
                # Linear scale from 0.5 to 1.5
                lq_scores[sector] = ((lq - 0.5) / 1.0) * 100.0

        # Combine CAGR and LQ scores (50/50 weight)
        sector_composite = {}
        for sector in sector_cagr:
            cagr_component = cagr_scores.get(sector, 0)
            lq_component = lq_scores.get(sector, 0)
            sector_composite[sector] = (cagr_component + lq_component) / 2

        # Apply sector weights
        weighted_score = sum(
            sector_composite.get(sector, 0) * weight
            for sector, weight in sector_weights.items()
        )

        return {
            "score": round(weighted_score, 1),
            "sector_scores": sector_composite,
            "sector_cagr": sector_cagr,
            "sector_lq": sector_lq,
            "weights": sector_weights,
        }

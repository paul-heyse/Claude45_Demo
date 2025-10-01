"""EPA ECHO environmental compliance and contamination risk assessment.

Identifies nearby regulated sites, violations, and environmental compliance issues
using EPA Facility Registry Services (FRS) and Enforcement & Compliance History
Online (ECHO).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class EnvironmentalComplianceAnalyzer:
    """Analyze environmental compliance and contamination risk."""

    # Site types by severity
    SITE_SEVERITY = {
        "Superfund": 100,
        "RCRA_Corrective_Action": 80,
        "Brownfield": 60,
        "RCRA_Generator": 40,
        "NPDES_Major": 50,
        "Air_Major": 50,
    }

    def __init__(self) -> None:
        """Initialize environmental compliance analyzer."""
        logger.info("EnvironmentalComplianceAnalyzer initialized")

    def assess_nearby_contaminated_sites(
        self,
        latitude: float,
        longitude: float,
        search_radius_km: float = 1.0,
        mock_sites: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Assess proximity to contaminated sites using EPA FRS.

        Implements:
        - Req: Environmental Compliance and Contamination Risk
        - Scenario: Nearby contaminated sites

        Args:
            latitude: Location latitude
            longitude: Location longitude
            search_radius_km: Search radius in kilometers (default 1.0)
            mock_sites: Optional mock site data for testing

        Returns:
            Dictionary with nearby sites, risk score, and flags
        """
        if mock_sites is None:
            raise ValueError("Production EPA FRS API not yet implemented")

        # Filter sites within radius
        sites_within_radius = [
            site for site in mock_sites if site["distance_km"] <= search_radius_km
        ]

        # Count by type
        site_counts = {}
        for site_type in self.SITE_SEVERITY:
            count = sum(1 for s in sites_within_radius if s["site_type"] == site_type)
            site_counts[site_type] = count

        # Calculate risk score based on site types and proximity
        risk_score = 0
        high_risk_sites = []

        for site in sites_within_radius:
            site_type = site["site_type"]
            base_severity = self.SITE_SEVERITY.get(site_type, 30)

            # Adjust for proximity (closer = higher risk)
            distance_km = site["distance_km"]
            if distance_km < 0.5:
                proximity_multiplier = 1.5
            elif distance_km < 1.0:
                proximity_multiplier = 1.0
            else:
                proximity_multiplier = 0.7

            site_risk = base_severity * proximity_multiplier

            # Check for ongoing issues
            if site.get("active_remediation", False):
                site_risk *= 1.3
            if site.get("uncontrolled_release", False):
                site_risk *= 1.5

            risk_score += site_risk

            if site_risk >= 80.0:
                high_risk_sites.append(
                    {
                        "name": site.get("name", "Unknown"),
                        "site_type": site_type,
                        "distance_km": distance_km,
                        "risk": int(site_risk),
                    }
                )

        # Cap risk score at 100
        risk_score = min(100, int(risk_score))

        return {
            "environmental_risk_score": risk_score,
            "sites_within_radius": len(sites_within_radius),
            "site_counts": site_counts,
            "high_risk_sites": high_risk_sites,
            "search_radius_km": search_radius_km,
        }

    def assess_discharge_permits(
        self,
        latitude: float,
        longitude: float,
        search_radius_km: float = 2.0,
        lookback_years: int = 3,
        mock_permits: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Assess proximity to air and water discharge permits.

        Implements:
        - Req: Environmental Compliance and Contamination Risk
        - Scenario: Air and water discharge proximity

        Args:
            latitude: Location latitude
            longitude: Location longitude
            search_radius_km: Search radius in kilometers (default 2.0)
            lookback_years: Years to look back for violations (default 3)
            mock_permits: Optional mock permit data for testing

        Returns:
            Dictionary with nearby permits, violations, and risk flags
        """
        if mock_permits is None:
            raise ValueError("Production EPA ECHO API not yet implemented")

        # Filter permits within radius
        permits_within_radius = [
            permit
            for permit in mock_permits
            if permit["distance_km"] <= search_radius_km
        ]

        # Count by permit type
        npdes_permits = sum(
            1 for p in permits_within_radius if p["permit_type"] == "NPDES"
        )
        air_permits = sum(1 for p in permits_within_radius if p["permit_type"] == "Air")

        # Identify significant violations (CAA, CWA)
        significant_violations = []
        violation_count = 0

        for permit in permits_within_radius:
            violations = permit.get("violations", [])
            for violation in violations:
                if violation.get("significant", False):
                    violation_count += 1
                    significant_violations.append(
                        {
                            "facility": permit.get("facility_name", "Unknown"),
                            "permit_type": permit["permit_type"],
                            "violation_type": violation.get("type", "Unknown"),
                            "date": violation.get("date", "Unknown"),
                            "pollutants": violation.get("pollutants", []),
                        }
                    )

        # Calculate pollution proximity risk
        if violation_count >= 5:
            risk_flag = "high"
            risk_score = 85
        elif violation_count >= 2:
            risk_flag = "moderate"
            risk_score = 60
        elif violation_count >= 1:
            risk_flag = "low"
            risk_score = 35
        else:
            risk_flag = "minimal"
            risk_score = 10

        return {
            "pollution_proximity_risk_score": risk_score,
            "risk_flag": risk_flag,
            "npdes_permits_nearby": npdes_permits,
            "air_permits_nearby": air_permits,
            "total_permits": len(permits_within_radius),
            "significant_violations": significant_violations,
            "violation_count": violation_count,
            "search_radius_km": search_radius_km,
            "lookback_years": lookback_years,
        }

    def calculate_composite_environmental_risk(
        self, components: dict[str, float]
    ) -> dict[str, Any]:
        """Calculate overall environmental risk from components.

        Args:
            components: Dictionary with environmental_risk_score,
                       pollution_proximity_risk_score

        Returns:
            Dictionary with composite score, risk level, recommendations
        """
        # Weighted: Contaminated sites 60%, Discharge permits 40%
        composite_score = int(
            components.get("environmental_risk_score", 0) * 0.60
            + components.get("pollution_proximity_risk_score", 0) * 0.40
        )

        # Determine risk level
        if composite_score >= 70:
            risk_level = "high"
            recommendations = [
                "Phase I Environmental Site Assessment (ESA) required",
                "Review EPA ECHO compliance history",
                "Consider Phase II ESA if contamination suspected",
                "Engage environmental consultant",
            ]
        elif composite_score >= 50:
            risk_level = "moderate"
            recommendations = [
                "Phase I ESA recommended",
                "Review EPA databases for nearby sites",
                "Consider pollution proximity in underwriting",
            ]
        else:
            risk_level = "low"
            recommendations = ["Standard environmental due diligence sufficient"]

        return {
            "composite_environmental_score": composite_score,
            "risk_level": risk_level,
            "recommendations": recommendations,
            "components": components,
        }

"""Product type classification for multifamily assets.

Classifies properties by type (garden, low-rise, mid-rise, high-rise, mixed-use)
and assesses fit with Aker Companies' investment thesis.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ProductTypeClassifier:
    """Classify multifamily product types and assess Aker investment fit."""

    # Aker fit scores by product type
    PRODUCT_FIT_SCORES = {
        "garden": 100,  # 1-2 stories, surface parking - core target
        "low-rise": 100,  # 3-4 stories - core target
        "mid-rise": 70,  # 5-8 stories - selective opportunities
        "high-rise": 20,  # 9+ stories - rare, high bar
    }

    # Preferred retail tenant types for mixed-use (Aker thesis)
    PREFERRED_RETAIL_TENANTS = {
        "coffee_shop",
        "outdoor_gear",
        "bodega",
        "local_restaurant",
        "bike_shop",
        "farmers_market",
    }

    def __init__(self) -> None:
        """Initialize product type classifier."""
        logger.info("ProductTypeClassifier initialized")

    def classify_product_type(self, property_data: dict[str, Any]) -> dict[str, Any]:
        """Classify property by product type and assess Aker fit.

        Args:
            property_data: Dictionary with property characteristics
                - stories: Number of stories (required)
                - parking_type: surface, tuck-under, structured
                - units: Unit count
                - unit_density: Units per acre

        Returns:
            Dictionary with product_type, aker_fit_score, description, features
        """
        stories = property_data.get("stories", 0)

        # Classify by story count
        if stories <= 2:
            product_type = "garden"
            description = "Garden-style (1-2 stories, surface parking)"
            typical_features = ["Surface parking", "Lower density", "Outdoor-oriented"]
            notes = ""
        elif 3 <= stories <= 4:
            product_type = "low-rise"
            description = "Low-rise (3-4 stories)"
            typical_features = [
                "Tuck-under or surface parking",
                "Walkable scale",
                "Wood-frame construction",
            ]
            notes = ""
        elif 5 <= stories <= 8:
            product_type = "mid-rise"
            description = "Mid-rise (5-8 stories)"
            typical_features = [
                "Structured parking",
                "Urban infill",
                "Elevator required",
            ]
            notes = "Select opportunities only"
        else:  # 9+ stories
            product_type = "high-rise"
            description = "High-rise (9+ stories)"
            typical_features = [
                "Urban core",
                "Concrete/steel construction",
                "High density",
            ]
            notes = "Rare opportunity, high bar"

        aker_fit_score = self.PRODUCT_FIT_SCORES[product_type]

        return {
            "product_type": product_type,
            "aker_fit_score": aker_fit_score,
            "description": description,
            "typical_features": typical_features,
            "notes": notes,
        }

    def assess_mixed_use(self, property_data: dict[str, Any]) -> dict[str, Any]:
        """Assess mixed-use property fit with Aker thesis.

        Args:
            property_data: Property characteristics including:
                - ground_floor_commercial: bool
                - location_type: town_center, urban, suburban, etc.
                - walk_score: 0-100
                - retail_tenants: list of tenant types

        Returns:
            Dictionary with mixed_use assessment, location fit, retail profile
        """
        is_mixed_use = property_data.get("ground_floor_commercial", False)

        if not is_mixed_use:
            return {
                "is_mixed_use": False,
                "mixed_use_fit_score": 0,
                "retail_assessment": "Not a mixed-use property",
            }

        # Assess location fit (walkable node = high, auto-oriented = low)
        location_type = property_data.get("location_type", "unknown")
        walk_score = property_data.get("walk_score", 0)

        if location_type == "town_center" or walk_score >= 70:
            location_fit = "high"
            location_score = 100
        elif location_type == "urban" or walk_score >= 50:
            location_fit = "medium"
            location_score = 70
        else:
            location_fit = "low"
            location_score = 30

        # Assess retail tenant mix (prefer coffee, gear, bodega per Aker)
        retail_tenants = property_data.get("retail_tenants", [])
        preferred_count = sum(
            1 for tenant in retail_tenants if tenant in self.PREFERRED_RETAIL_TENANTS
        )
        total_tenants = len(retail_tenants)

        if total_tenants > 0:
            retail_profile_score = int((preferred_count / total_tenants) * 100)
        else:
            retail_profile_score = 50  # Unknown, default to neutral

        # Overall mixed-use fit (weighted: location 60%, retail 40%)
        mixed_use_fit_score = int(location_score * 0.6 + retail_profile_score * 0.4)

        retail_assessment = (
            f"Location fit: {location_fit}, "
            f"Preferred tenants: {preferred_count}/{total_tenants}"
        )

        return {
            "is_mixed_use": True,
            "location_fit": location_fit,
            "retail_profile_score": retail_profile_score,
            "mixed_use_fit_score": mixed_use_fit_score,
            "retail_assessment": retail_assessment,
        }

    def evaluate_adaptive_reuse(self, property_data: dict[str, Any]) -> dict[str, Any]:
        """Evaluate adaptive reuse potential for non-residential properties.

        Args:
            property_data: Property characteristics including:
                - current_use: office, retail, industrial, etc.
                - ceiling_height_ft: Ceiling height
                - floor_plate_sf: Floor plate size
                - window_to_floor_ratio: Natural light ratio

        Returns:
            Dictionary with reuse_candidate flag, complexity, potential score
        """
        current_use = property_data.get("current_use", "").lower()

        # Already residential = not a conversion candidate
        if "multifamily" in current_use or "residential" in current_use:
            return {
                "reuse_candidate": False,
                "conversion_complexity": "n/a",
                "reuse_potential_score": 0,
                "notes": "Already residential - not a conversion candidate",
            }

        # Assess conversion feasibility factors
        ceiling_height = property_data.get("ceiling_height_ft", 0)
        floor_plate = property_data.get("floor_plate_sf", 0)
        window_ratio = property_data.get("window_to_floor_ratio", 0)

        positive_factors = []
        challenges = []
        score = 50  # Start at neutral

        # Ceiling height (ideal: 9-12 ft)
        if 9 <= ceiling_height <= 12:
            positive_factors.append("Ideal ceiling height for residential")
            score += 15
        elif ceiling_height > 15:
            challenges.append("Ceiling height too high (excess volume)")
            score -= 10

        # Floor plate (ideal: <20k sf for natural light penetration)
        if floor_plate < 20000:
            positive_factors.append("Manageable floor plate for unit layouts")
            score += 15
        elif floor_plate > 40000:
            challenges.append("Large floor plate limits natural light")
            score -= 15

        # Natural light (window-to-floor ratio > 0.20 is good)
        if window_ratio >= 0.20:
            positive_factors.append("Good natural light (high window ratio)")
            score += 20
        elif window_ratio < 0.10:
            challenges.append("Poor natural light - limited windows")
            score -= 20

        # Determine complexity
        if score >= 70:
            conversion_complexity = "low"
        elif score >= 50:
            conversion_complexity = "medium"
        else:
            conversion_complexity = "high"

        # Clamp score to 0-100
        reuse_potential_score = max(0, min(100, score))

        return {
            "reuse_candidate": True,
            "conversion_complexity": conversion_complexity,
            "reuse_potential_score": reuse_potential_score,
            "positive_factors": positive_factors,
            "challenges": challenges,
            "notes": f"Conversion from {current_use} to residential",
        }

"""Urban convenience scoring for market analysis."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class UrbanConvenienceScorer:
    """Calculate urban convenience scores for walkability and retail health."""

    def calculate_15min_accessibility_score(
        self,
        grocery_count: int,
        pharmacy_count: int,
        school_count: int,
        transit_stop_count: int,
        intersection_density_per_sqkm: float,
    ) -> dict[str, Any]:
        """
        Calculate 15-minute accessibility score.

        Implements:
        - Req: Urban Convenience Scoring
        - Scenario: 15-minute accessibility analysis

        Args:
            grocery_count: Grocery stores within 15-min walk
            pharmacy_count: Pharmacies within 15-min walk
            school_count: K-8 schools within 15-min walk
            transit_stop_count: Transit stops within 15-min walk
            intersection_density_per_sqkm: 3/4-way intersections per km²

        Returns:
            Dict with accessibility score and details
        """
        # Score each amenity type (0-25 points each)
        grocery_score = min(25.0, grocery_count * 12.5)  # 2+ stores = max
        pharmacy_score = min(25.0, pharmacy_count * 12.5)
        school_score = min(25.0, school_count * 8.3)  # 3+ schools = max
        transit_score = min(25.0, transit_stop_count * 5.0)  # 5+ stops = max

        amenity_score = grocery_score + pharmacy_score + school_score + transit_score

        # Score intersection density: 100+ per km² = excellent, 50 = good, <25 = poor
        if intersection_density_per_sqkm >= 100:
            intersection_score = 100.0
        elif intersection_density_per_sqkm >= 50:
            intersection_score = (
                50.0 + ((intersection_density_per_sqkm - 50) / 50) * 50.0
            )
        else:
            intersection_score = (intersection_density_per_sqkm / 50) * 50.0

        # Composite: 60% amenities, 40% street network
        composite = (amenity_score * 0.6) + (intersection_score * 0.4)

        return {
            "score": round(composite, 1),
            "components": {
                "amenity_access": round(amenity_score, 1),
                "street_network": round(intersection_score, 1),
            },
            "amenity_counts": {
                "grocery": grocery_count,
                "pharmacy": pharmacy_count,
                "school": school_count,
                "transit_stop": transit_stop_count,
            },
        }

    def calculate_retail_health_score(
        self,
        daytime_population: int,
        retail_vacancy_rate: float,
        population_density_per_sqkm: int,
    ) -> dict[str, Any]:
        """
        Calculate retail health score.

        Implements:
        - Req: Urban Convenience Scoring
        - Scenario: Retail health assessment

        Args:
            daytime_population: Daytime population within 1-mile radius
            retail_vacancy_rate: Local retail vacancy rate (0-1)
            population_density_per_sqkm: Population density (proxy for delivery)

        Returns:
            Dict with retail health score
        """
        # Normalize daytime population: 5k = 33, 10k = 66, 15k+ = 100
        if daytime_population >= 15000:
            daytime_score = 100.0
        else:
            daytime_score = (daytime_population / 15000) * 100.0

        # Normalize vacancy (inverse): 5% = 100, 10% = 50, 20%+ = 0
        if retail_vacancy_rate <= 0.05:
            vacancy_score = 100.0
        elif retail_vacancy_rate >= 0.20:
            vacancy_score = 0.0
        else:
            vacancy_score = 100.0 - ((retail_vacancy_rate - 0.05) / 0.15) * 100.0

        # Normalize density: 1000 = 33, 2500 = 66, 5000+ = 100
        if population_density_per_sqkm >= 5000:
            density_score = 100.0
        else:
            density_score = (population_density_per_sqkm / 5000) * 100.0

        # Composite: 40% daytime pop, 40% vacancy, 20% density
        composite = (
            (daytime_score * 0.4) + (vacancy_score * 0.4) + (density_score * 0.2)
        )

        return {
            "score": round(composite, 1),
            "components": {
                "daytime_population": round(daytime_score, 1),
                "retail_vacancy": round(vacancy_score, 1),
                "delivery_viability": round(density_score, 1),
            },
        }

    def calculate_transit_quality_score(
        self,
        stops_within_800m: int,
        avg_weekday_headway_min: float,
        weekend_service_available: bool,
    ) -> dict[str, Any]:
        """
        Calculate transit service quality score.

        Implements:
        - Req: Urban Convenience Scoring
        - Scenario: Transit service quality

        Args:
            stops_within_800m: Transit stops within 800m
            avg_weekday_headway_min: Average wait time for high-frequency routes
            weekend_service_available: Weekend service available

        Returns:
            Dict with transit quality score
        """
        # Normalize stop count: 1 = 33, 3 = 66, 5+ = 100
        if stops_within_800m >= 5:
            stop_score = 100.0
        else:
            stop_score = (stops_within_800m / 5) * 100.0

        # Normalize headway (inverse): 10min = 100, 20min = 50, 30min+ = 0
        if avg_weekday_headway_min <= 10:
            frequency_score = 100.0
        elif avg_weekday_headway_min >= 30:
            frequency_score = 0.0
        else:
            frequency_score = 100.0 - ((avg_weekday_headway_min - 10) / 20) * 100.0

        # Weekend service bonus
        weekend_bonus = 20.0 if weekend_service_available else 0.0

        # Composite: 40% stops, 40% frequency, 20% weekend
        composite = (stop_score * 0.4) + (frequency_score * 0.4) + weekend_bonus
        composite = min(100.0, composite)

        return {
            "score": round(composite, 1),
            "components": {
                "stop_coverage": round(stop_score, 1),
                "service_frequency": round(frequency_score, 1),
                "weekend_service": weekend_service_available,
            },
        }

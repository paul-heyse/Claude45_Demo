"""EPA Enforcement and Compliance History Online (ECHO) API connector.

EPA ECHO provides facility compliance and enforcement data.
Useful for identifying environmental compliance risks near properties.

API Documentation: https://echo.epa.gov/tools/web-services
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import requests

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager

logger = logging.getLogger(__name__)


class EPAECHOConnector(APIConnector):
    """
    EPA ECHO (Enforcement and Compliance History Online) API connector.

    Provides methods for querying facility compliance and enforcement data.
    Useful for environmental due diligence.
    """

    DEFAULT_BASE_URL = "https://echodata.epa.gov/echo/rest_lookups.get_facilities"

    PROGRAM_TYPES = {
        "CAA": "Clean Air Act",
        "CWA": "Clean Water Act",
        "RCRA": "Resource Conservation and Recovery Act",
        "SDWA": "Safe Drinking Water Act",
        "TRI": "Toxics Release Inventory",
    }

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        cache_ttl_days: int = 30,
        cache_manager: CacheManager | None = None,
    ) -> None:
        """
        Initialize EPA ECHO connector.

        Args:
            base_url: EPA ECHO API endpoint
            cache_ttl_days: Cache TTL in days (default: 30)
            cache_manager: Optional cache manager instance
        """
        super().__init__(
            api_key="",  # No API key needed
            base_url=base_url,
            cache_ttl_days=cache_ttl_days,
            cache_manager=cache_manager,
        )

    def _load_api_key(self) -> str | None:
        """No API key needed for EPA ECHO."""
        return None

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve facility data from EPA ECHO API.

        Args:
            params: API request parameters. Expected keys:
                    - 'p_fn': Facility name search
                    - 'p_sa': Street address
                    - 'p_ct': City
                    - 'p_st': State (2-letter)
                    - 'p_c1lat', 'p_c1lon', 'p_c1r': Center lat/lon + radius (miles)
                    - 'output': Response format (JSON, XML, CSV)

        Returns:
            JSON response with facility data

        Raises:
            DataSourceError: If API request fails
        """
        self._check_rate_limit()
        self._track_request()

        # Ensure output format is JSON
        query_params = {**params, "output": "JSON"}

        def _make_request() -> Dict[str, Any]:
            response = requests.get(self.base_url, params=query_params, timeout=30)
            response.raise_for_status()
            return response.json()

        return self._retry_with_backoff(_make_request)

    def parse(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse EPA ECHO facility response.

        Args:
            response: Raw API response

        Returns:
            Parsed facility data
        """
        results = response.get("Results", {})
        facilities = results.get("Facilities", [])

        return {
            "facility_count": len(facilities),
            "facilities": facilities,
            "query_info": results.get("QueryInfo", {}),
        }

    def search_facilities_by_radius(
        self, latitude: float, longitude: float, radius_miles: float = 1.0
    ) -> Dict[str, Any]:
        """
        Search for EPA-regulated facilities within radius.

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_miles: Search radius in miles (default: 1.0)

        Returns:
            Dictionary with facility data
        """
        cache_key = f"echo_facilities_{latitude}_{longitude}_{radius_miles}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for EPA ECHO facilities: {cache_key}")
                return cached  # type: ignore[return-value]

        params = {
            "p_c1lat": latitude,
            "p_c1lon": longitude,
            "p_c1r": radius_miles,
            "responseset": "5",  # More comprehensive response
        }

        response = self.fetch(params)
        parsed_data = self.parse(response)

        if self.cache:
            self.cache.set(cache_key, parsed_data, ttl=self.cache_ttl)

        return parsed_data

    def assess_environmental_risk(
        self, latitude: float, longitude: float, radius_miles: float = 1.0
    ) -> Dict[str, Any]:
        """
        Assess environmental compliance risk near a location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            radius_miles: Search radius in miles

        Returns:
            Dictionary with risk assessment
        """
        facility_data = self.search_facilities_by_radius(
            latitude, longitude, radius_miles
        )

        facilities = facility_data.get("facilities", [])
        facility_count = len(facilities)

        # Analyze violation history
        facilities_with_violations = 0
        total_violations = 0
        high_priority_violations = 0
        programs_affected: set[str] = set()

        for facility in facilities:
            # Check for recent violations (3-year)
            violations_3yr = facility.get("CurrVio", "N") == "Y"
            if violations_3yr:
                facilities_with_violations += 1

            # Count enforcement actions
            enforcement_actions = facility.get("Insp5yr", 0)
            if isinstance(enforcement_actions, int):
                total_violations += enforcement_actions

            # Check formal enforcement actions (more serious)
            formal_actions = facility.get("FormalActions5yr", 0)
            if isinstance(formal_actions, int) and formal_actions > 0:
                high_priority_violations += formal_actions

            # Track which programs are involved
            for program_code in self.PROGRAM_TYPES.keys():
                if facility.get(f"{program_code}Facility", "N") == "Y":
                    programs_affected.add(program_code)

        # Calculate risk score (0-100)
        risk_score = min(
            (facility_count * 5)
            + (facilities_with_violations * 15)
            + (high_priority_violations * 20),
            100,
        )

        risk_level = "low"
        if risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "moderate"

        return {
            "latitude": latitude,
            "longitude": longitude,
            "search_radius_miles": radius_miles,
            "facility_count": facility_count,
            "facilities_with_violations": facilities_with_violations,
            "total_enforcement_actions_5yr": total_violations,
            "high_priority_violations": high_priority_violations,
            "programs_affected": sorted(programs_affected),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommendation": (
                "Conduct detailed environmental due diligence"
                if risk_level == "high"
                else "Standard environmental review"
            ),
            "data_source": "EPA ECHO",
        }

    def get_facility_details(self, registry_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific facility.

        Args:
            registry_id: EPA Registry ID for the facility

        Returns:
            Dictionary with facility details
        """
        cache_key = f"echo_facility_{registry_id}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for EPA ECHO facility: {cache_key}")
                return cached  # type: ignore[return-value]

        params = {"p_id": registry_id}

        response = self.fetch(params)
        parsed_data = self.parse(response)

        # Extract first facility (should only be one with specific ID)
        facilities = parsed_data.get("facilities", [])
        facility_details = facilities[0] if facilities else {}

        if self.cache:
            self.cache.set(cache_key, facility_details, ttl=self.cache_ttl)

        return facility_details

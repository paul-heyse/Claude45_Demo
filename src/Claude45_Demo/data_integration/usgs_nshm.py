"""USGS National Seismic Hazard Model (NSHM) API connector.

The USGS NSHM provides seismic hazard data including Peak Ground Acceleration (PGA)
and spectral acceleration values for earthquake risk assessment.

API Documentation: https://earthquake.usgs.gov/ws/designmaps/
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import requests

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager

logger = logging.getLogger(__name__)


class USGSNSHMConnector(APIConnector):
    """
    USGS National Seismic Hazard Model API connector.

    Provides seismic hazard values (PGA, spectral acceleration) for locations
    in the United States using the USGS Design Maps API.
    """

    DEFAULT_BASE_URL = "https://earthquake.usgs.gov/ws/designmaps/asce7-16.json"

    # ASCE 7 Site Classes (soil conditions)
    SITE_CLASSES = {
        "A": "Hard rock",
        "B": "Rock",
        "C": "Very dense soil and soft rock (default)",
        "D": "Stiff soil",
        "E": "Soft clay soil",
    }

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        cache_ttl_days: int = 365,  # Seismic hazard data rarely changes
        cache_manager: CacheManager | None = None,
    ) -> None:
        """
        Initialize USGS NSHM connector.

        Args:
            base_url: USGS Design Maps API endpoint
            cache_ttl_days: Cache TTL in days (default: 365)
            cache_manager: Optional cache manager instance
        """
        super().__init__(
            api_key="",  # No API key needed
            base_url=base_url,
            cache_ttl_days=cache_ttl_days,
            cache_manager=cache_manager,
        )

    def _load_api_key(self) -> str | None:
        """No API key needed for USGS NSHM."""
        return None

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve seismic hazard data from USGS NSHM API.

        Args:
            params: API request parameters. Expected keys:
                    - 'latitude': Location latitude
                    - 'longitude': Location longitude
                    - 'riskCategory': Risk category (I, II, III, IV) default III
                    - 'siteClass': Site class (A-E) default C
                    - 'title': Optional title for the request

        Returns:
            JSON response with seismic hazard parameters

        Raises:
            DataSourceError: If API request fails
        """
        self._check_rate_limit()
        self._track_request()

        def _make_request() -> Dict[str, Any]:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        return self._retry_with_backoff(_make_request)

    def parse(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse USGS NSHM response into structured seismic data.

        Args:
            response: Raw API response

        Returns:
            Dictionary with seismic hazard parameters
        """
        data = response.get("response", {}).get("data", {})

        # Extract key seismic parameters
        pga = data.get("pga", 0.0)  # Peak Ground Acceleration (g)
        ss = data.get("ss", 0.0)  # Short-period spectral acceleration
        s1 = data.get("s1", 0.0)  # 1-second spectral acceleration

        # Site-modified values
        sms = data.get("sms", 0.0)  # Site-modified short-period
        sm1 = data.get("sm1", 0.0)  # Site-modified 1-second

        # Design values (2/3 of site-modified)
        sds = data.get("sds", 0.0)  # Design short-period
        sd1 = data.get("sd1", 0.0)  # Design 1-second

        # Seismic Design Category (SDC)
        sdc = data.get("sdc", "A")

        # Determine risk level from PGA
        if pga >= 0.5:
            risk_level = "very_high"
            risk_score = 90
        elif pga >= 0.33:
            risk_level = "high"
            risk_score = 70
        elif pga >= 0.17:
            risk_level = "moderate"
            risk_score = 50
        elif pga >= 0.05:
            risk_level = "low"
            risk_score = 30
        else:
            risk_level = "very_low"
            risk_score = 10

        return {
            "pga": pga,
            "ss": ss,
            "s1": s1,
            "sms": sms,
            "sm1": sm1,
            "sds": sds,
            "sd1": sd1,
            "seismic_design_category": sdc,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "data_source": "USGS NSHM (ASCE 7-16)",
        }

    def get_seismic_hazard(
        self,
        latitude: float,
        longitude: float,
        risk_category: str = "III",
        site_class: str = "C",
    ) -> Dict[str, Any]:
        """
        Get seismic hazard parameters for a location.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            risk_category: ASCE 7 Risk Category (I, II, III, IV)
            site_class: ASCE 7 Site Class (A, B, C, D, E)

        Returns:
            Dictionary with seismic hazard data
        """
        cache_key = f"usgs_nshm_{latitude}_{longitude}_{risk_category}_{site_class}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for USGS NSHM: {cache_key}")
                return cached  # type: ignore[return-value]

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "riskCategory": risk_category,
            "siteClass": site_class,
            "title": f"Seismic Hazard at {latitude},{longitude}",
        }

        response = self.fetch(params)
        parsed_data = self.parse(response)

        if self.cache:
            self.cache.set(cache_key, parsed_data, ttl=self.cache_ttl)

        return parsed_data

    def assess_earthquake_risk(
        self,
        latitude: float,
        longitude: float,
        site_class: str = "C",
        fault_distance_km: float | None = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive earthquake risk assessment.

        Args:
            latitude: Location latitude
            longitude: Location longitude
            site_class: ASCE 7 Site Class (A-E)
            fault_distance_km: Optional distance to nearest active fault

        Returns:
            Dictionary with earthquake risk assessment
        """
        seismic_data = self.get_seismic_hazard(
            latitude, longitude, site_class=site_class
        )

        risk_score = seismic_data["risk_score"]

        # Adjust for fault proximity
        fault_rupture_zone = False
        if fault_distance_km is not None:
            if fault_distance_km < 0.1:  # Within 100m of fault
                fault_rupture_zone = True
                risk_score = min(100, risk_score + 15)
            elif fault_distance_km < 1.0:  # Within 1km
                risk_score = min(100, risk_score + 10)
            elif fault_distance_km < 5.0:  # Within 5km
                risk_score = min(100, risk_score + 5)

        # Determine mitigation requirements
        sdc = seismic_data["seismic_design_category"]
        requires_special_design = sdc in ["D", "E", "F"]

        return {
            **seismic_data,
            "adjusted_risk_score": risk_score,
            "fault_distance_km": fault_distance_km,
            "fault_rupture_zone": fault_rupture_zone,
            "requires_special_design": requires_special_design,
            "site_class": site_class,
            "site_class_description": self.SITE_CLASSES.get(site_class, "Unknown"),
            "recommendation": (
                "Seismic design required per ASCE 7"
                if requires_special_design
                else "Standard seismic provisions"
            ),
        }

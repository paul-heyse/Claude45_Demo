"""EPA Radon Zone lookup connector.

EPA Map of Radon Zones classifies counties into three zones:
- Zone 1: Highest potential (predicted average >4 pCi/L)
- Zone 2: Moderate potential (predicted average 2-4 pCi/L)
- Zone 3: Low potential (predicted average <2 pCi/L)

Data Source: EPA static county mapping
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager
from Claude45_Demo.data_integration.exceptions import DataSourceError

logger = logging.getLogger(__name__)


class EPARadonConnector(APIConnector):
    """
    EPA Radon Zone lookup connector.

    Uses EPA's static county-level radon zone classification.
    Data is based on EPA's Map of Radon Zones document.
    """

    # Subset of EPA radon zone data (full dataset would be loaded from file)
    # Format: {state_fips: {county_fips: zone}}
    RADON_ZONES: Dict[str, Dict[str, int]] = {
        "08": {  # Colorado
            "001": 1,  # Adams - High
            "005": 1,  # Arapahoe - High
            "013": 1,  # Boulder - High
            "014": 1,  # Broomfield - High
            "031": 1,  # Denver - High
            "035": 1,  # Douglas - High
            "041": 1,  # El Paso - High
            "059": 1,  # Jefferson - High
            "069": 1,  # Larimer - High
            "097": 1,  # Pitkin - High
            "101": 1,  # Pueblo - High
            "123": 1,  # Weld - High
        },
        "49": {  # Utah
            "003": 2,  # Box Elder - Moderate
            "005": 2,  # Cache - Moderate
            "011": 2,  # Davis - Moderate
            "035": 2,  # Salt Lake - Moderate
            "043": 2,  # Summit - Moderate
            "045": 2,  # Tooele - Moderate
            "049": 2,  # Utah - Moderate
            "051": 2,  # Wasatch - Moderate
            "057": 2,  # Weber - Moderate
        },
        "16": {  # Idaho
            "001": 2,  # Ada - Moderate
            "019": 2,  # Bonneville - Moderate
            "027": 2,  # Canyon - Moderate
            "055": 2,  # Kootenai - Moderate
            "069": 2,  # Nez Perce - Moderate
            "075": 2,  # Payette - Moderate
            "083": 2,  # Twin Falls - Moderate
        },
    }

    ZONE_DESCRIPTIONS = {
        1: {
            "name": "High Potential",
            "predicted_avg": ">4 pCi/L",
            "risk_level": "high",
            "recommendation": "Test all buildings; consider radon-resistant construction",
        },
        2: {
            "name": "Moderate Potential",
            "predicted_avg": "2-4 pCi/L",
            "risk_level": "moderate",
            "recommendation": "Test all buildings; consider radon mitigation if elevated",
        },
        3: {
            "name": "Low Potential",
            "predicted_avg": "<2 pCi/L",
            "risk_level": "low",
            "recommendation": "Testing still recommended but lower priority",
        },
    }

    def __init__(
        self,
        *,
        cache_ttl_days: int = 365,  # Radon zones rarely change
        cache_manager: CacheManager | None = None,
    ) -> None:
        """
        Initialize EPA Radon connector.

        Args:
            cache_ttl_days: Cache TTL in days (default: 365, data is static)
            cache_manager: Optional cache manager instance
        """
        super().__init__(
            api_key="",  # No API key needed for static data
            base_url="",  # No API endpoint
            cache_ttl_days=cache_ttl_days,
            cache_manager=cache_manager,
        )

    def _load_api_key(self) -> str | None:
        """No API key needed for static data."""
        return None

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve radon zone for a county.

        Args:
            params: Dictionary with 'state_fips' and 'county_fips' keys

        Returns:
            Dictionary with radon zone data

        Raises:
            DataSourceError: If state/county not found
        """
        state_fips = params.get("state_fips", "").zfill(2)
        county_fips = params.get("county_fips", "").zfill(3)

        if state_fips not in self.RADON_ZONES:
            raise DataSourceError(f"State FIPS {state_fips} not in radon zone data")

        if county_fips not in self.RADON_ZONES[state_fips]:
            # Default to zone 2 (moderate) if county not explicitly mapped
            logger.warning(
                f"County {county_fips} in state {state_fips} not in radon data, "
                "defaulting to Zone 2 (moderate)"
            )
            zone = 2
        else:
            zone = self.RADON_ZONES[state_fips][county_fips]

        return {"zone": zone, "state_fips": state_fips, "county_fips": county_fips}

    def parse(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse radon zone lookup into structured data.

        Args:
            response: Raw zone lookup result

        Returns:
            Dictionary with radon zone details
        """
        zone = response["zone"]
        zone_info = self.ZONE_DESCRIPTIONS[zone]

        return {
            "state_fips": response["state_fips"],
            "county_fips": response["county_fips"],
            "radon_zone": zone,
            "zone_name": zone_info["name"],
            "predicted_avg": zone_info["predicted_avg"],
            "risk_level": zone_info["risk_level"],
            "recommendation": zone_info["recommendation"],
            "data_source": "EPA Map of Radon Zones",
        }

    def get_radon_zone(self, state_fips: str, county_fips: str) -> Dict[str, Any]:
        """
        Get radon zone classification for a county.

        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code

        Returns:
            Dictionary with radon zone information
        """
        cache_key = f"radon_zone_{state_fips}_{county_fips}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for radon zone: {cache_key}")
                return cached  # type: ignore[return-value]

        params = {"state_fips": state_fips, "county_fips": county_fips}
        response = self.fetch(params)
        parsed_data = self.parse(response)

        if self.cache:
            self.cache.set(cache_key, parsed_data, ttl=self.cache_ttl)

        return parsed_data

    def assess_radon_risk(self, state_fips: str, county_fips: str) -> Dict[str, Any]:
        """
        Assess radon risk for a location.

        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code

        Returns:
            Dictionary with risk assessment
        """
        zone_data = self.get_radon_zone(state_fips, county_fips)

        # Calculate risk score (0-100)
        zone_scores = {1: 80, 2: 50, 3: 20}
        risk_score = zone_scores.get(zone_data["radon_zone"], 50)

        return {
            **zone_data,
            "risk_score": risk_score,
            "requires_testing": zone_data["radon_zone"] <= 2,
            "mitigation_priority": (
                "high" if zone_data["radon_zone"] == 1 else "medium"
            ),
        }

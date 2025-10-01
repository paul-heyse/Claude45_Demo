"""Wildland-Urban Interface (WUI) classification lookup.

WUI classification identifies areas where human development meets wildland vegetation.
Based on USFS WUI data and density criteria.

Reference: https://www.fs.usda.gov/rds/archive/Catalog/RDS-2015-0012-3
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager

logger = logging.getLogger(__name__)


class WUIClassifier(APIConnector):
    """
    Wildland-Urban Interface (WUI) classification connector.

    Classifies locations based on housing density and wildland vegetation proximity.
    Uses USFS WUI categories and density thresholds.
    """

    WUI_CATEGORIES = {
        "interface": {
            "name": "Interface WUI",
            "description": "High density housing adjacent to wildland vegetation",
            "housing_density_min": 50,  # houses per sq km
            "vegetation_threshold": 50,  # % wildland within 2.4 km
            "risk_level": "high",
        },
        "intermix": {
            "name": "Intermix WUI",
            "description": "Housing intermixed with wildland vegetation",
            "housing_density_min": 6.17,  # houses per sq km
            "vegetation_threshold": 50,  # % wildland
            "risk_level": "high",
        },
        "low_density": {
            "name": "Low Density WUI",
            "description": "Scattered housing near wildland",
            "housing_density_min": 6.17,
            "housing_density_max": 50,
            "risk_level": "moderate",
        },
        "non_wui": {
            "name": "Non-WUI",
            "description": "Not in Wildland-Urban Interface",
            "risk_level": "low",
        },
    }

    # Sample WUI classifications by county (subset for CO/UT/ID)
    # Full data would come from USFS WUI dataset
    COUNTY_WUI_PREVALENCE: Dict[str, Dict[str, float]] = {
        "08": {  # Colorado
            "013": 0.65,  # Boulder - High WUI prevalence
            "031": 0.45,  # Denver - Moderate (urban core)
            "041": 0.55,  # El Paso (Colorado Springs)
            "069": 0.60,  # Larimer (Fort Collins/mountains)
            "097": 0.75,  # Pitkin (Aspen) - Very high
            "123": 0.50,  # Weld
        },
        "49": {  # Utah
            "035": 0.50,  # Salt Lake - Moderate
            "043": 0.70,  # Summit (Park City) - High
            "045": 0.55,  # Tooele
            "049": 0.45,  # Utah County (Provo)
            "057": 0.40,  # Weber (Ogden)
        },
        "16": {  # Idaho
            "001": 0.55,  # Ada (Boise) - Moderate/high
            "055": 0.60,  # Kootenai (Coeur d'Alene) - High
            "083": 0.50,  # Twin Falls
        },
    }

    def __init__(
        self,
        *,
        cache_ttl_days: int = 365,  # WUI classifications rarely change
        cache_manager: CacheManager | None = None,
    ) -> None:
        """
        Initialize WUI Classifier.

        Args:
            cache_ttl_days: Cache TTL in days (default: 365)
            cache_manager: Optional cache manager instance
        """
        super().__init__(
            api_key="",  # No API key needed
            base_url="",  # No API endpoint (static data)
            cache_ttl_days=cache_ttl_days,
            cache_manager=cache_manager,
        )

    def _load_api_key(self) -> str | None:
        """No API key needed for static classification."""
        return None

    def fetch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieve WUI classification for a location.

        Args:
            params: Dictionary with location parameters:
                    - 'state_fips': 2-digit state code
                    - 'county_fips': 3-digit county code
                    - 'housing_density': Optional housing units per sq km
                    - 'vegetation_pct': Optional % wildland vegetation

        Returns:
            Dictionary with WUI classification data
        """
        state_fips = params.get("state_fips", "").zfill(2)
        county_fips = params.get("county_fips", "").zfill(3)
        housing_density = params.get("housing_density")
        vegetation_pct = params.get("vegetation_pct")

        # Get county WUI prevalence (if available)
        wui_prevalence = 0.3  # Default moderate prevalence
        if state_fips in self.COUNTY_WUI_PREVALENCE:
            if county_fips in self.COUNTY_WUI_PREVALENCE[state_fips]:
                wui_prevalence = self.COUNTY_WUI_PREVALENCE[state_fips][county_fips]

        # Classify based on provided density and vegetation data
        if housing_density is not None and vegetation_pct is not None:
            category = self._classify_precise(housing_density, vegetation_pct)
        else:
            # Use county prevalence as proxy
            category = self._classify_by_prevalence(wui_prevalence)

        return {
            "state_fips": state_fips,
            "county_fips": county_fips,
            "wui_category": category,
            "wui_prevalence": wui_prevalence,
            "housing_density": housing_density,
            "vegetation_pct": vegetation_pct,
        }

    def _classify_precise(self, housing_density: float, vegetation_pct: float) -> str:
        """
        Classify WUI based on precise density and vegetation data.

        Args:
            housing_density: Housing units per sq km
            vegetation_pct: Percentage wildland vegetation within 2.4 km

        Returns:
            WUI category key
        """
        if housing_density >= 50 and vegetation_pct >= 50:
            return "interface"
        elif 6.17 <= housing_density < 50 and vegetation_pct >= 50:
            return "intermix"
        elif 6.17 <= housing_density < 50:
            return "low_density"
        else:
            return "non_wui"

    def _classify_by_prevalence(self, prevalence: float) -> str:
        """
        Estimate WUI category from county prevalence.

        Args:
            prevalence: Fraction of county in WUI (0-1)

        Returns:
            WUI category key
        """
        if prevalence >= 0.6:
            return "interface"
        elif prevalence >= 0.4:
            return "intermix"
        elif prevalence >= 0.2:
            return "low_density"
        else:
            return "non_wui"

    def parse(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse WUI classification into structured data.

        Args:
            response: Raw classification result

        Returns:
            Dictionary with WUI details
        """
        category_key = response["wui_category"]
        category_info = self.WUI_CATEGORIES[category_key]

        return {
            "state_fips": response["state_fips"],
            "county_fips": response["county_fips"],
            "wui_category": category_key,
            "category_name": category_info["name"],
            "category_description": category_info["description"],
            "risk_level": category_info["risk_level"],
            "wui_prevalence": response["wui_prevalence"],
            "housing_density": response.get("housing_density"),
            "vegetation_pct": response.get("vegetation_pct"),
            "data_source": "USFS WUI Classification",
        }

    def get_wui_classification(
        self,
        state_fips: str,
        county_fips: str,
        housing_density: Optional[float] = None,
        vegetation_pct: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get WUI classification for a location.

        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code
            housing_density: Optional housing units per sq km
            vegetation_pct: Optional % wildland vegetation

        Returns:
            Dictionary with WUI classification
        """
        cache_key = (
            f"wui_class_{state_fips}_{county_fips}_"
            f"{housing_density or 'county'}_{vegetation_pct or 'county'}"
        )

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.info(f"Cache hit for WUI classification: {cache_key}")
                return cached  # type: ignore[return-value]

        params = {
            "state_fips": state_fips,
            "county_fips": county_fips,
            "housing_density": housing_density,
            "vegetation_pct": vegetation_pct,
        }

        response = self.fetch(params)
        parsed_data = self.parse(response)

        if self.cache:
            self.cache.set(cache_key, parsed_data, ttl=self.cache_ttl)

        return parsed_data

    def assess_wildfire_interface_risk(
        self,
        state_fips: str,
        county_fips: str,
        housing_density: Optional[float] = None,
        vegetation_pct: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Assess wildfire risk based on WUI classification.

        Args:
            state_fips: 2-digit state FIPS code
            county_fips: 3-digit county FIPS code
            housing_density: Optional housing units per sq km
            vegetation_pct: Optional % wildland vegetation

        Returns:
            Dictionary with risk assessment
        """
        wui_data = self.get_wui_classification(
            state_fips, county_fips, housing_density, vegetation_pct
        )

        # Calculate risk score (0-100)
        risk_scores = {
            "interface": 85,
            "intermix": 75,
            "low_density": 50,
            "non_wui": 20,
        }
        risk_score = risk_scores.get(wui_data["wui_category"], 50)

        return {
            **wui_data,
            "risk_score": risk_score,
            "high_risk": wui_data["risk_level"] == "high",
            "requires_mitigation": wui_data["wui_category"]
            in ["interface", "intermix"],
            "recommendation": (
                "Implement defensible space and fire-resistant construction"
                if wui_data["risk_level"] == "high"
                else "Standard wildfire preparedness"
            ),
        }

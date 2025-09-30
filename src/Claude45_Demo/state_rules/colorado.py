"""
Colorado state-specific analysis and adjustments.

Implements CO-specific logic for:
- Front Range hail risk premium
- CDSS HydroBase water rights integration
- Mountain snow load adjustments (ASCE 7 + elevation)
- Denver metro permit timeline patterns
- Mountain wildfire WUI adjustments
"""

from typing import Any


class ColoradoStateAnalyzer:
    """
    Colorado-specific analysis and risk adjustments.

    Provides CO-specific augmentation to core risk assessment, market
    analysis, and geographic modules. Integrates with CO Division of Water
    Resources CDSS HydroBase for water rights.
    """

    # Front Range hail alley bounding box (approximate)
    HAIL_ALLEY_NORTH = 41.0  # ~CO/WY border
    HAIL_ALLEY_SOUTH = 38.0  # ~Pueblo
    HAIL_ALLEY_WEST = -105.5  # ~foothills
    HAIL_ALLEY_EAST = -103.0  # ~eastern plains

    # CO mountain counties with elevated WUI risk
    MOUNTAIN_WUI_COUNTIES = {
        "08117",  # Summit
        "08037",  # Eagle
        "08067",  # La Plata
        "08097",  # Pitkin
        "08107",  # Routt
        "08065",  # Lake
    }

    # Known permit timelines by jurisdiction (days)
    PERMIT_TIMELINES = {
        "Boulder": {"median": 210, "design_review": True, "iz_pct": 25},
        "Denver": {"median": 120, "design_review": False, "iz_pct": 10},
        "Aurora": {"median": 45, "design_review": False, "iz_pct": 0},
        "Fort Collins": {"median": 90, "design_review": False, "iz_pct": 0},
        "Colorado Springs": {"median": 75, "design_review": False, "iz_pct": 0},
    }

    def __init__(self, cdss_connector=None):
        """
        Initialize Colorado state analyzer.

        Args:
            cdss_connector: Optional CDSS HydroBase API connector (for DI/testing)
        """
        self.cdss = cdss_connector

    def calculate_hail_risk_premium(
        self, latitude: float, longitude: float
    ) -> dict[str, Any]:
        """
        Calculate hail risk premium for CO Front Range hail alley.

        CO Front Range (Denver to Pueblo corridor) experiences 10+ hail
        events per decade, requiring elevated roof replacement reserves
        and insurance deductibles.

        Args:
            latitude: Property latitude
            longitude: Property longitude

        Returns:
            dict with keys:
                - hail_events_per_decade: int
                - risk_category: str (low|moderate|high|extreme)
                - roof_reserve_per_unit_per_year: float ($)
                - insurance_deductible_pct: float
                - risk_multiplier_adjustment: float
        """
        # Check if in Front Range hail alley
        in_hail_alley = (
            self.HAIL_ALLEY_SOUTH <= latitude <= self.HAIL_ALLEY_NORTH
            and self.HAIL_ALLEY_WEST <= longitude <= self.HAIL_ALLEY_EAST
        )

        if in_hail_alley:
            # Front Range hail alley has high frequency
            hail_events = 12  # events per decade
            risk_category = "high"
            roof_reserve = 18.0  # $/unit/year
            deductible_pct = 5.0
            risk_adjustment = 0.05
        else:
            # Mountains and western slope have lower hail frequency
            hail_events = 4
            risk_category = "moderate"
            roof_reserve = 10.0
            deductible_pct = 2.0
            risk_adjustment = 0.02

        return {
            "hail_events_per_decade": hail_events,
            "risk_category": risk_category,
            "roof_reserve_per_unit_per_year": roof_reserve,
            "insurance_deductible_pct": deductible_pct,
            "risk_multiplier_adjustment": risk_adjustment,
        }

    def assess_water_rights(self, county_fips: str, parcel_id: str) -> dict[str, Any]:
        """
        Query CDSS HydroBase for water rights and availability.

        CO uses prior appropriation doctrine with complex water court system.
        This method queries CDSS REST API for structures, decreed rights,
        and calculates tap fee estimates by municipality.

        Args:
            county_fips: 5-digit county FIPS code
            parcel_id: Parcel identifier

        Returns:
            dict with keys:
                - availability_score: int (0-100)
                - estimated_tap_fee: float ($)
                - water_court_district: int (1-7)
                - priority_date: str (YYYY-MM-DD) or None
                - structures: list of dicts
                - augmentation_required: bool (optional)
        """
        # Query CDSS HydroBase (mocked for now, will connect in Task 7.4)
        cdss_data = self._query_cdss_hydrobase(county_fips, parcel_id)

        # Calculate availability score based on structures and rights
        structures = cdss_data.get("structures", [])
        water_rights = cdss_data.get("water_rights", [])
        augmentation_required = cdss_data.get("augmentation_required", False)

        if not structures and not water_rights:
            # No water structures or rights identified
            availability_score = 30
            tap_fee = 25000  # High fee for constrained supply
        elif augmentation_required:
            # Augmentation plan required (costly, complex)
            availability_score = 45
            tap_fee = 22000
        else:
            # Water structures identified, better availability
            availability_score = 75
            tap_fee = 12000

        priority_date = None
        if water_rights:
            priority_date = water_rights[0].get("appropriation_date")

        return {
            "availability_score": availability_score,
            "estimated_tap_fee": tap_fee,
            "water_court_district": cdss_data.get("water_court_district", 1),
            "priority_date": priority_date,
            "structures": structures,
            "augmentation_required": augmentation_required,
        }

    def _query_cdss_hydrobase(self, county_fips: str, parcel_id: str) -> dict[str, Any]:
        """
        Query CDSS HydroBase REST API (stub for now).

        This will be implemented in Task 7.4 with actual API connector.
        For now, returns mock data for testing.

        Args:
            county_fips: County FIPS code
            parcel_id: Parcel ID

        Returns:
            dict: CDSS API response
        """
        # Stub implementation - will be replaced with actual API call
        return {
            "structures": [],
            "water_rights": [],
            "water_court_district": 1,
            "augmentation_required": False,
        }

    def calculate_snow_load_adjustment(
        self, latitude: float, longitude: float, elevation_ft: int
    ) -> dict[str, Any]:
        """
        Calculate ASCE 7 ground snow load and cost adjustments.

        CO mountain properties above 7,000 ft require structural design for
        heavy snow loads (50+ psf), increasing construction cost 10-15%.
        Winter construction (Nov-Mar) adds 15%+ premium.

        Args:
            latitude: Property latitude
            longitude: Property longitude
            elevation_ft: Elevation in feet

        Returns:
            dict with keys:
                - ground_snow_load_psf: float (pounds per square foot)
                - structural_cost_premium_pct: float
                - winter_construction_months: list[str]
                - winter_cost_premium_pct: float
        """
        # Simplified ASCE 7 snow load estimation by elevation
        if elevation_ft >= 9000:
            snow_load_psf = 80.0
            structural_premium = 15.0
        elif elevation_ft >= 7500:
            snow_load_psf = 60.0
            structural_premium = 12.0
        elif elevation_ft >= 6000:
            snow_load_psf = 40.0
            structural_premium = 8.0
        else:
            snow_load_psf = 25.0
            structural_premium = 3.0

        winter_months = [
            "November",
            "December",
            "January",
            "February",
            "March",
        ]
        winter_premium = 15.0 if elevation_ft >= 7000 else 5.0

        return {
            "ground_snow_load_psf": snow_load_psf,
            "structural_cost_premium_pct": structural_premium,
            "winter_construction_months": winter_months,
            "winter_cost_premium_pct": winter_premium,
        }

    def assess_regulatory_environment(self, jurisdiction: str) -> dict[str, Any]:
        """
        Assess regulatory friction by CO jurisdiction.

        CO municipalities vary widely in permit timelines and regulatory
        complexity (Boulder >180 days, Aurora ~45 days). Includes design
        review requirements and inclusionary zoning mandates.

        Args:
            jurisdiction: Municipality name (e.g., "Boulder", "Denver")

        Returns:
            dict with keys:
                - median_permit_days: int
                - design_review_required: bool
                - inclusionary_zoning_pct: float
                - friction_score: int (0-100, higher = more friction)
                - data_source: str (jurisdiction_specific | state_default)
        """
        if jurisdiction in self.PERMIT_TIMELINES:
            data = self.PERMIT_TIMELINES[jurisdiction]
            data_source = "jurisdiction_specific"
        else:
            # CO state default (moderate friction)
            data = {"median": 90, "design_review": False, "iz_pct": 0}
            data_source = "state_default"

        # Calculate friction score (0-100)
        # Based on: permit days (0.4), design review (0.3), IZ (0.3)
        days_score = min(100, (data["median"] / 200) * 100)
        design_score = 30 if data["design_review"] else 0
        iz_score = data["iz_pct"] * 1.2  # 25% IZ = 30 points

        friction_score = int(days_score * 0.4 + design_score * 1.0 + iz_score * 1.0)

        return {
            "median_permit_days": data["median"],
            "design_review_required": data["design_review"],
            "inclusionary_zoning_pct": data["iz_pct"],
            "friction_score": friction_score,
            "data_source": data_source,
        }

    def apply_wildfire_wui_adjustment(
        self, county_fips: str, base_wildfire_score: float
    ) -> dict[str, Any]:
        """
        Apply CO mountain WUI wildfire adjustment.

        Mountain counties (Summit, Eagle, La Plata, etc.) have elevated
        wildfire risk beyond base WHP score due to limited insurance
        carriers and high defensible space requirements.

        Args:
            county_fips: 5-digit county FIPS code
            base_wildfire_score: Base wildfire risk score (0-100)

        Returns:
            dict with keys:
                - wui_multiplier: float (1.0+ for high WUI counties)
                - insurance_impact: str (limited_carriers | high_deductible)
                - recommendations: list[str]
        """
        if county_fips in self.MOUNTAIN_WUI_COUNTIES:
            wui_multiplier = 1.2
            insurance_impact = "limited_carriers"
            recommendations = [
                "firewise_community",
                "extensive_defensible_space",
                "metal_roof_required",
            ]
        else:
            wui_multiplier = 1.0
            insurance_impact = "standard"
            recommendations = ["standard_defensible_space"]

        return {
            "wui_multiplier": wui_multiplier,
            "insurance_impact": insurance_impact,
            "recommendations": recommendations,
        }

    def calculate_state_multiplier(
        self,
        latitude: float,
        longitude: float,
        elevation_ft: int,
        county_fips: str,
        parcel_id: str,
        jurisdiction: str,
    ) -> dict[str, Any]:
        """
        Calculate composite CO state multiplier.

        Combines hail risk, water availability, snow load, and regulatory
        friction into a single CO-specific adjustment factor (0.9-1.1).

        Args:
            latitude: Property latitude
            longitude: Property longitude
            elevation_ft: Elevation in feet
            county_fips: County FIPS code
            parcel_id: Parcel ID
            jurisdiction: Municipality name

        Returns:
            dict with keys:
                - co_multiplier: float (0.9-1.1)
                - adjustments: list[dict] (component breakdowns)
                - risk_premium_pct: float (total risk premium)
        """
        # Calculate individual components
        hail = self.calculate_hail_risk_premium(latitude, longitude)
        water = self.assess_water_rights(county_fips, parcel_id)
        snow = self.calculate_snow_load_adjustment(latitude, longitude, elevation_ft)
        regulatory = self.assess_regulatory_environment(jurisdiction)

        # Composite multiplier calculation
        # Hail adjustment: +0.05 for high risk
        hail_adj = hail["risk_multiplier_adjustment"]

        # Water adjustment: -0.02 for low availability (<50 score)
        water_adj = -0.02 if water["availability_score"] < 50 else 0.0

        # Snow adjustment: structural premium converts to risk premium
        snow_adj = snow["structural_cost_premium_pct"] / 1000  # Scale down

        # Regulatory adjustment: +0.03 for high friction (>70 score)
        reg_adj = 0.03 if regulatory["friction_score"] > 70 else 0.0

        # Total multiplier (clamp to 0.9-1.1)
        base_multiplier = 1.0
        total_adj = hail_adj + water_adj + snow_adj + reg_adj
        co_multiplier = max(0.9, min(1.1, base_multiplier + total_adj))

        risk_premium_pct = (co_multiplier - 1.0) * 100

        adjustments = [
            {"factor": "hail_risk", "adjustment": hail_adj},
            {"factor": "water_availability", "adjustment": water_adj},
            {"factor": "snow_load", "adjustment": snow_adj},
            {"factor": "regulatory_friction", "adjustment": reg_adj},
        ]

        return {
            "co_multiplier": co_multiplier,
            "adjustments": adjustments,
            "risk_premium_pct": risk_premium_pct,
        }

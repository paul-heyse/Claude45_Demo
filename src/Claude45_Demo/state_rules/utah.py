"""
Utah state-specific analysis and adjustments.

Implements UT-specific logic for:
- Wasatch Front topography constraints
- Silicon Slopes employment growth
- Utah DWR water rights integration
- Seismic risk (Wasatch Fault)
- Pro-development regulatory environment
"""

from typing import Any


class UtahStateAnalyzer:
    """
    Utah-specific analysis and risk adjustments.

    Provides UT-specific augmentation to core risk assessment, market
    analysis, and geographic modules. Integrates with Utah Division of
    Water Rights for water availability assessment.
    """

    # Silicon Slopes tech corridor counties
    SILICON_SLOPES_COUNTIES = {
        "49049",  # Utah County (Provo, Lehi, American Fork)
        "49035",  # Salt Lake County
        "49011",  # Davis County (partial - Farmington/Layton)
    }

    # Wasatch Fault approximate trace (latitude range)
    WASATCH_FAULT_LAT_MIN = 38.5
    WASATCH_FAULT_LAT_MAX = 42.0
    WASATCH_FAULT_LONG_CENTER = -111.85  # Approximate longitude

    # Known permit timelines by jurisdiction (days)
    PERMIT_TIMELINES = {
        "Salt Lake City": {
            "median": 90,
            "design_review": True,
            "state_context": "pro_development",
        },
        "Provo": {
            "median": 60,
            "design_review": False,
            "state_context": "pro_development",
        },
        "Ogden": {
            "median": 75,
            "design_review": False,
            "state_context": "pro_development",
        },
        "West Jordan": {
            "median": 50,
            "design_review": False,
            "state_context": "pro_development",
        },
    }

    def __init__(self, ut_dwr_connector=None, edc_connector=None):
        """
        Initialize Utah state analyzer.

        Args:
            ut_dwr_connector: Optional UT DWR API connector (for DI/testing)
            edc_connector: Optional EDCUtah data connector
        """
        self.ut_dwr = ut_dwr_connector
        self.edc = edc_connector

    def assess_topography_constraints(
        self, latitude: float, longitude: float, elevation_ft: int
    ) -> dict[str, Any]:
        """
        Assess Wasatch Front topography constraints.

        Wasatch Front bench development faces steep slopes (>15% grade),
        fault-adjacent parcels, and geotechnical challenges that increase
        development costs 10-20%.

        Args:
            latitude: Property latitude
            longitude: Property longitude
            elevation_ft: Elevation in feet

        Returns:
            dict with keys:
                - slope_pct: float (estimated grade)
                - development_feasibility: str (high|moderate|low)
                - geotechnical_investigation_required: bool
                - cost_premium_pct: float
                - fault_proximity_miles: float
                - seismic_investigation_required: bool
        """
        # Estimate slope from elevation and Wasatch Front position
        # Properties on benches (5000-5500 ft) typically steeper
        if 5000 <= elevation_ft <= 5500:
            slope_pct = 18.0  # Steep bench development
            feasibility = "moderate"
            geotech_required = True
            cost_premium = 15.0
        elif elevation_ft > 5500:
            slope_pct = 25.0  # Very steep
            feasibility = "low"
            geotech_required = True
            cost_premium = 20.0
        else:
            slope_pct = 5.0  # Valley floor
            feasibility = "high"
            geotech_required = False
            cost_premium = 2.0

        # Estimate Wasatch Fault proximity (simplified)
        fault_distance = abs(longitude - self.WASATCH_FAULT_LONG_CENTER) * 69  # ~miles

        seismic_investigation = fault_distance < 1.0

        return {
            "slope_pct": slope_pct,
            "development_feasibility": feasibility,
            "geotechnical_investigation_required": geotech_required,
            "cost_premium_pct": cost_premium,
            "fault_proximity_miles": fault_distance,
            "seismic_investigation_required": seismic_investigation,
        }

    def analyze_silicon_slopes_employment(self, county_fips: str) -> dict[str, Any]:
        """
        Analyze Silicon Slopes tech cluster employment growth.

        Silicon Slopes (Utah County, Salt Lake County) has 8%+ annual tech
        job growth, with major expansions from Adobe, Qualtrics, and others.

        Args:
            county_fips: 5-digit county FIPS code

        Returns:
            dict with keys:
                - tech_job_growth_score: int (0-100)
                - innovation_momentum: str (low|moderate|high|very_high)
                - employment_multiplier: float
                - announced_expansions: list[dict]
        """
        # Query EDCUtah data (mocked for now, real connector in Task 7.4)
        edc_data = self._query_edc_utah(county_fips)

        tech_cagr = edc_data.get("tech_job_cagr_3yr", 0)
        expansions = edc_data.get("announced_expansions", [])
        _ = edc_data.get("startup_density", 0)  # Reserved for future use

        # Calculate tech job growth score
        if tech_cagr >= 8.0:
            growth_score = 90
            momentum = "very_high"
            multiplier = 1.08
        elif tech_cagr >= 5.0:
            growth_score = 75
            momentum = "high"
            multiplier = 1.05
        elif tech_cagr >= 3.0:
            growth_score = 55
            momentum = "moderate"
            multiplier = 1.02
        else:
            growth_score = 30
            momentum = "low"
            multiplier = 1.0

        # Boost for Silicon Slopes counties
        if county_fips in self.SILICON_SLOPES_COUNTIES:
            growth_score = min(100, growth_score + 10)

        return {
            "tech_job_growth_score": growth_score,
            "innovation_momentum": momentum,
            "employment_multiplier": multiplier,
            "announced_expansions": expansions,
        }

    def _query_edc_utah(self, county_fips: str) -> dict[str, Any]:
        return {
            "tech_job_cagr_3yr": 3.0,
            "announced_expansions": [],
            "startup_density": 15,
        }

    def assess_water_rights(self, county_fips: str, parcel_id: str) -> dict[str, Any]:
        dwr_data = self._query_ut_dwr(county_fips, parcel_id)

        points = dwr_data.get("points_of_diversion", [])
        critical_area = dwr_data.get("critical_management_area", False)
        drought_status = dwr_data.get("drought_status", "moderate")

        if critical_area:
            availability_score = 40
            connection_fee = 20000
        elif not points:
            availability_score = 50
            connection_fee = 18000
        else:
            availability_score = 70
            connection_fee = 14000

        if drought_status == "severe":
            drought_impact = "high"
            availability_score = max(0, availability_score - 15)
        elif drought_status == "moderate":
            drought_impact = "moderate"
            availability_score = max(0, availability_score - 8)
        else:
            drought_impact = "low"

        return {
            "availability_score": availability_score,
            "drought_impact_level": drought_impact,
            "critical_management_area": critical_area,
            "estimated_connection_fee": connection_fee,
            "points_of_diversion": points,
        }

    def _query_ut_dwr(self, county_fips: str, parcel_id: str) -> dict[str, Any]:
        return {
            "points_of_diversion": [],
            "critical_management_area": False,
            "drought_status": "moderate",
        }

    def assess_seismic_risk(self, latitude: float, longitude: float) -> dict[str, Any]:
        fault_distance = abs(longitude - self.WASATCH_FAULT_LONG_CENTER) * 69

        if fault_distance < 2.0:
            design_category = "E"
            cost_premium = 10.0
            recommendations = [
                "seismic_retrofit",
                "enhanced_foundation",
                "structural_engineer_required",
            ]
        elif fault_distance < 5.0:
            design_category = "D"
            cost_premium = 7.0
            recommendations = ["seismic_retrofit", "structural_engineer_required"]
        elif fault_distance < 15.0:
            design_category = "C"
            cost_premium = 4.0
            recommendations = ["standard_seismic_design"]
        else:
            design_category = "B"
            cost_premium = 2.0
            recommendations = ["standard_building_code"]

        return {
            "fault_proximity_miles": fault_distance,
            "seismic_design_category": design_category,
            "structural_cost_premium_pct": cost_premium,
            "recommendations": recommendations,
        }

    def assess_regulatory_environment(self, jurisdiction: str) -> dict[str, Any]:
        if jurisdiction in self.PERMIT_TIMELINES:
            data = self.PERMIT_TIMELINES[jurisdiction]
            data_source = "jurisdiction_specific"
        else:
            data = {
                "median": 70,
                "design_review": False,
                "state_context": "pro_development",
            }
            data_source = "state_default"

        days_score = min(100, (data["median"] / 200) * 100)
        design_score = 20 if data["design_review"] else 0

        friction_score = int(days_score * 0.5 + design_score * 1.0)

        return {
            "median_permit_days": data["median"],
            "design_review_required": data["design_review"],
            "state_policy_context": data["state_context"],
            "friction_score": friction_score,
            "data_source": data_source,
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
        topo = self.assess_topography_constraints(latitude, longitude, elevation_ft)
        employment = self.analyze_silicon_slopes_employment(county_fips)
        water = self.assess_water_rights(county_fips, parcel_id)
        seismic = self.assess_seismic_risk(latitude, longitude)
        regulatory = self.assess_regulatory_environment(jurisdiction)

        topo_adj = topo["cost_premium_pct"] / 1000
        employment_adj = -(employment["employment_multiplier"] - 1.0)
        water_adj = 0.02 if water["availability_score"] < 50 else 0.0
        seismic_adj = seismic["structural_cost_premium_pct"] / 1000
        reg_adj = -0.02 if regulatory["friction_score"] < 50 else 0.0

        base_multiplier = 1.0
        total_adj = topo_adj + employment_adj + water_adj + seismic_adj + reg_adj
        ut_multiplier = max(0.9, min(1.1, base_multiplier + total_adj))

        risk_premium_pct = (ut_multiplier - 1.0) * 100

        adjustments = [
            {"factor": "topography", "adjustment": topo_adj},
            {"factor": "silicon_slopes_employment", "adjustment": employment_adj},
            {"factor": "water_availability", "adjustment": water_adj},
            {"factor": "seismic_risk", "adjustment": seismic_adj},
            {"factor": "regulatory_advantage", "adjustment": reg_adj},
        ]

        return {
            "ut_multiplier": ut_multiplier,
            "adjustments": adjustments,
            "risk_premium_pct": risk_premium_pct,
        }

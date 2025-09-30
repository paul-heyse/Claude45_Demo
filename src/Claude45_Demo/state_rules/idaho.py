"""
Idaho state-specific analysis and adjustments.

Implements ID-specific logic for:
- Treasure Valley in-migration tracking
- North Idaho wildland-urban interface fire risk
- Idaho DWR water rights and SRBA adjudication
- Property tax advantage and regulatory simplicity
"""

from typing import Any


class IdahoStateAnalyzer:
    """
    Idaho-specific analysis and risk adjustments.

    Provides ID-specific augmentation to core risk assessment, market
    analysis, and geographic modules. Integrates with Idaho Department of
    Water Resources for water rights assessment.
    """

    # Treasure Valley high-growth counties
    TREASURE_VALLEY_COUNTIES = {
        "16001",  # Ada County (Boise)
        "16027",  # Canyon County (Nampa, Caldwell)
        "16075",  # Payette County
    }

    # North Idaho panhandle counties (high WUI risk)
    NORTH_IDAHO_WUI_COUNTIES = {
        "16055",  # Kootenai (Coeur d'Alene)
        "16017",  # Bonner
        "16021",  # Boundary
        "16009",  # Benewah
        "16057",  # Latah (partial)
    }

    def __init__(self, idwr_connector=None):
        """
        Initialize Idaho state analyzer.

        Args:
            idwr_connector: Optional IDWR API connector (for DI/testing)
        """
        self.idwr = idwr_connector

    def analyze_treasure_valley_migration(self, county_fips: str) -> dict[str, Any]:
        """
        Analyze Treasure Valley in-migration momentum.

        Treasure Valley (Boise metro) experienced surge in net in-migration
        2020-2024, driven by remote work from CA/WA/OR. Tracks IRS SOI data,
        housing supply elasticity, and remote-work patterns.

        Args:
            county_fips: 5-digit county FIPS code

        Returns:
            dict with keys:
                - migration_momentum_score: int (0-100)
                - supply_elasticity: str (low|moderate|high)
                - top_origin_states: list[str]
                - remote_work_factor: float
        """
        # Query IRS SOI and local migration data (mocked for now)
        migration_data = self._query_migration_data(county_fips)

        net_migration = migration_data.get("net_migration_annual", 0)
        origin_states = migration_data.get("top_origin_states", [])
        remote_work_pct = migration_data.get("remote_work_share_pct", 0)
        _ = migration_data.get(
            "permits_per_household_growth", 0
        )  # Reserved for future use

        # Calculate momentum score
        if net_migration >= 7000:
            momentum_score = 90
            elasticity = "high"
        elif net_migration >= 3000:
            momentum_score = 75
            elasticity = "moderate"
        elif net_migration >= 1000:
            momentum_score = 55
            elasticity = "moderate"
        else:
            momentum_score = 35
            elasticity = "low"

        # Remote work factor (1.0 = baseline, higher = more remote workers)
        remote_work_factor = 1.0 + (remote_work_pct / 100)

        return {
            "migration_momentum_score": momentum_score,
            "supply_elasticity": elasticity,
            "top_origin_states": origin_states,
            "remote_work_factor": remote_work_factor,
        }

    def _query_migration_data(self, county_fips: str) -> dict[str, Any]:
        """
        Query IRS SOI migration data and local sources (stub).

        Will be implemented in Task 7.4 with actual connector.

        Args:
            county_fips: County FIPS code

        Returns:
            dict: Migration data
        """
        # Stub - return moderate defaults
        return {
            "net_migration_annual": 2000,
            "top_origin_states": ["WA", "CA"],
            "remote_work_share_pct": 20,
            "permits_per_household_growth": 0.9,
        }

    def assess_wildfire_wui_risk(
        self, latitude: float, longitude: float, county_fips: str
    ) -> dict[str, Any]:
        """
        Assess North Idaho wildland-urban interface fire risk.

        North Idaho panhandle (Kootenai, Bonner counties) has elevated WUI
        wildfire risk with limited insurance carriers. Requires extensive
        defensible space and Firewise community participation.

        Args:
            latitude: Property latitude
            longitude: Property longitude
            county_fips: 5-digit county FIPS code

        Returns:
            dict with keys:
                - wui_risk_category: str (low|moderate|high|extreme)
                - insurance_availability: str (standard|limited|very_limited)
                - defensible_space_ft: int (required clearance)
                - firewise_required: bool
        """
        # Check if in North Idaho WUI counties
        if county_fips in self.NORTH_IDAHO_WUI_COUNTIES:
            risk_category = "high"
            insurance = "limited"
            defensible_space = 100
            firewise = True
        elif latitude >= 44.0:  # Northern ID (above Boise latitude)
            risk_category = "moderate"
            insurance = "standard"
            defensible_space = 50
            firewise = False
        else:
            risk_category = "low"
            insurance = "standard"
            defensible_space = 30
            firewise = False

        return {
            "wui_risk_category": risk_category,
            "insurance_availability": insurance,
            "defensible_space_ft": defensible_space,
            "firewise_required": firewise,
        }

    def assess_water_rights(self, county_fips: str, parcel_id: str) -> dict[str, Any]:
        """
        Query Idaho DWR for water rights and SRBA status.

        Idaho uses prior appropriation with Snake River Basin Adjudication
        (SRBA) complexity. Senior rights have priority during drought
        curtailment. Tracks municipal hook-up availability.

        Args:
            county_fips: 5-digit county FIPS code
            parcel_id: Parcel identifier

        Returns:
            dict with keys:
                - availability_score: int (0-100)
                - srba_area: bool
                - curtailment_risk: str (low|moderate|high)
                - estimated_hookup_fee: float ($)
                - water_right_claims: list[dict]
        """
        # Query IDWR (mocked for now, real connector in Task 7.4)
        idwr_data = self._query_idwr(county_fips, parcel_id)

        claims = idwr_data.get("water_right_claims", [])
        srba_area = idwr_data.get("srba_area", False)
        municipal_available = idwr_data.get("municipal_service_available", False)
        curtailment = idwr_data.get("curtailment_risk", "low")

        # Calculate availability score
        if municipal_available:
            availability_score = 80
            hookup_fee = 12000
        elif claims and not srba_area:
            availability_score = 70
            hookup_fee = 15000
        elif claims and srba_area:
            # SRBA adds complexity
            availability_score = 60
            hookup_fee = 18000
        else:
            # No identified water rights
            availability_score = 45
            hookup_fee = 22000

        return {
            "availability_score": availability_score,
            "srba_area": srba_area,
            "curtailment_risk": curtailment,
            "estimated_hookup_fee": hookup_fee,
            "water_right_claims": claims,
        }

    def _query_idwr(self, county_fips: str, parcel_id: str) -> dict[str, Any]:
        """
        Query Idaho DWR water rights database (stub).

        Will be implemented in Task 7.4 with actual API connector.

        Args:
            county_fips: County FIPS code
            parcel_id: Parcel ID

        Returns:
            dict: IDWR data
        """
        # Stub implementation
        return {
            "water_right_claims": [],
            "srba_area": False,
            "municipal_service_available": False,
            "curtailment_risk": "low",
        }

    def assess_tax_and_regulatory_environment(
        self, jurisdiction: str
    ) -> dict[str, Any]:
        """
        Assess Idaho property tax and regulatory advantages.

        Idaho has favorable property tax rates (~1% effective), state-level
        rent control prohibition, and streamlined permitting in most
        jurisdictions.

        Args:
            jurisdiction: Municipality name

        Returns:
            dict with keys:
                - effective_property_tax_rate_pct: float
                - rent_control_status: str (prohibited|allowed)
                - tax_advantage_score: int (0-100)
                - median_permit_days: int
                - regulatory_friction_score: int (0-100)
        """
        # Idaho property tax typically 1.0-1.2% effective rate
        effective_tax_rate = 1.0

        # Rent control prohibited by state law
        rent_control_status = "prohibited"

        # Tax advantage score (high)
        tax_advantage = 80

        # Permitting timelines (generally streamlined)
        if jurisdiction in ["Boise", "Meridian", "Nampa"]:
            permit_days = 60
            friction_score = 40
        else:
            permit_days = 50
            friction_score = 30

        return {
            "effective_property_tax_rate_pct": effective_tax_rate,
            "rent_control_status": rent_control_status,
            "tax_advantage_score": tax_advantage,
            "median_permit_days": permit_days,
            "regulatory_friction_score": friction_score,
        }

    def calculate_state_multiplier(
        self,
        latitude: float,
        longitude: float,
        county_fips: str,
        parcel_id: str,
        jurisdiction: str,
    ) -> dict[str, Any]:
        """
        Calculate composite ID state multiplier.

        Combines migration momentum, wildfire WUI risk, water availability,
        and tax/regulatory advantages into single adjustment (0.9-1.1).

        Args:
            latitude: Property latitude
            longitude: Property longitude
            county_fips: County FIPS code
            parcel_id: Parcel ID
            jurisdiction: Municipality name

        Returns:
            dict with keys:
                - id_multiplier: float (0.9-1.1)
                - adjustments: list[dict]
                - risk_premium_pct: float
        """
        # Calculate components
        migration = self.analyze_treasure_valley_migration(county_fips)
        wildfire = self.assess_wildfire_wui_risk(latitude, longitude, county_fips)
        water = self.assess_water_rights(county_fips, parcel_id)
        tax_reg = self.assess_tax_and_regulatory_environment(jurisdiction)

        # Composite multiplier
        # Migration momentum: high growth reduces risk (negative adjustment)
        if migration["migration_momentum_score"] >= 75:
            migration_adj = -0.03
        elif migration["migration_momentum_score"] >= 50:
            migration_adj = -0.01
        else:
            migration_adj = 0.0

        # Wildfire WUI: North Idaho adds risk
        if wildfire["wui_risk_category"] == "extreme":
            wildfire_adj = 0.06
        elif wildfire["wui_risk_category"] == "high":
            wildfire_adj = 0.04
        elif wildfire["wui_risk_category"] == "moderate":
            wildfire_adj = 0.02
        else:
            wildfire_adj = 0.0

        # Water: low availability increases risk
        water_adj = 0.02 if water["availability_score"] < 50 else 0.0

        # Tax/regulatory: favorable environment reduces risk
        tax_reg_adj = -0.02 if tax_reg["tax_advantage_score"] >= 70 else 0.0

        # Total multiplier (clamped)
        base_multiplier = 1.0
        total_adj = migration_adj + wildfire_adj + water_adj + tax_reg_adj
        id_multiplier = max(0.9, min(1.1, base_multiplier + total_adj))

        risk_premium_pct = (id_multiplier - 1.0) * 100

        adjustments = [
            {"factor": "migration_momentum", "adjustment": migration_adj},
            {"factor": "wildfire_wui", "adjustment": wildfire_adj},
            {"factor": "water_availability", "adjustment": water_adj},
            {"factor": "tax_regulatory_advantage", "adjustment": tax_reg_adj},
        ]

        return {
            "id_multiplier": id_multiplier,
            "adjustments": adjustments,
            "risk_premium_pct": risk_premium_pct,
        }

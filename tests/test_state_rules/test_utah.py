"""
Tests for Utah state-specific analysis.

Tests scenarios from specs/state-rules/spec.md covering:
- Wasatch Front topography constraints
- Silicon Slopes employment growth
- Utah DWR water rights integration
- Seismic risk (Wasatch Fault)
"""

import pytest

from Claude45_Demo.state_rules.utah import UtahStateAnalyzer


@pytest.fixture
def ut_analyzer():
    """Utah state analyzer with mocked data connectors."""
    return UtahStateAnalyzer()


class TestWasatchTopography:
    """Test Wasatch Front topography constraint analysis."""

    def test_steep_slope_constraints(self, ut_analyzer):
        """
        WHEN: Property on Wasatch Front with steep slopes (>15% grade)
        THEN: Analyze slope constraints, geotechnical requirements,
              development feasibility score
        """
        # Salt Lake City foothills (steep bench development)
        result = ut_analyzer.assess_topography_constraints(
            latitude=40.7608, longitude=-111.8910, elevation_ft=5200
        )

        assert result["slope_pct"] > 15
        assert result["development_feasibility"] in ["moderate", "low"]
        assert result["geotechnical_investigation_required"] is True
        assert result["cost_premium_pct"] >= 10

    def test_fault_adjacent_parcel(self, ut_analyzer):
        """
        WHEN: Property adjacent to Wasatch Fault
        THEN: Identify fault proximity, seismic requirements
        """
        # Near Wasatch Fault trace
        result = ut_analyzer.assess_topography_constraints(
            latitude=40.7608, longitude=-111.8910, elevation_ft=4800
        )

        assert "fault_proximity_miles" in result
        if result["fault_proximity_miles"] < 1.0:
            assert result["seismic_investigation_required"] is True

    def test_flat_valley_floor(self, ut_analyzer):
        """
        WHEN: Property on flat valley floor
        THEN: Minimal topography constraints
        """
        # Salt Lake valley floor
        result = ut_analyzer.assess_topography_constraints(
            latitude=40.7589, longitude=-111.8910, elevation_ft=4200
        )

        assert result["slope_pct"] < 10
        assert result["development_feasibility"] == "high"
        assert result["cost_premium_pct"] < 5


class TestSiliconSlopesEmployment:
    """Test Silicon Slopes tech employment growth analysis."""

    def test_silicon_slopes_tech_growth(self, ut_analyzer, monkeypatch):
        """
        WHEN: Analyze Utah County or Salt Lake County employment
        THEN: Apply Silicon Slopes tech cluster job growth multipliers,
              EDCUtah expansions, innovation momentum score
        """
        # Mock EDCUtah data
        mock_data = {
            "tech_job_cagr_3yr": 8.5,
            "announced_expansions": [
                {"company": "Adobe", "jobs": 1200},
                {"company": "Qualtrics", "jobs": 800},
            ],
            "startup_density": 45,  # per 100k residents
        }

        monkeypatch.setattr(ut_analyzer, "_query_edc_utah", lambda *a, **k: mock_data)

        result = ut_analyzer.analyze_silicon_slopes_employment(
            county_fips="49049"  # Utah County
        )

        assert result["tech_job_growth_score"] >= 75
        assert result["innovation_momentum"] in ["high", "very_high"]
        assert result["employment_multiplier"] > 1.0
        assert len(result["announced_expansions"]) >= 2

    def test_non_silicon_slopes_county(self, ut_analyzer, monkeypatch):
        """
        WHEN: County outside Silicon Slopes corridor
        THEN: Lower innovation scores, standard employment patterns
        """
        mock_data = {
            "tech_job_cagr_3yr": 2.0,
            "announced_expansions": [],
            "startup_density": 10,
        }

        monkeypatch.setattr(ut_analyzer, "_query_edc_utah", lambda *a, **k: mock_data)

        result = ut_analyzer.analyze_silicon_slopes_employment(
            county_fips="49027"  # Cache County
        )

        assert result["tech_job_growth_score"] < 50
        assert result["innovation_momentum"] in ["low", "moderate"]


class TestUtahWaterRights:
    """Test Utah DWR Points of Diversion water rights."""

    def test_ut_water_rights_query(self, ut_analyzer, monkeypatch):
        """
        WHEN: System evaluates water availability for Utah property
        THEN: Query UT DWR Points of Diversion, identify critical
              management areas, assess drought impact
        """
        mock_response = {
            "points_of_diversion": [
                {
                    "water_right_number": "57-1234",
                    "source": "Jordan River",
                    "priority_date": "1890-05-15",
                    "quantity": 2.5,
                    "use": "Municipal",
                }
            ],
            "critical_management_area": False,
            "drought_status": "moderate",
        }

        monkeypatch.setattr(ut_analyzer, "_query_ut_dwr", lambda *a, **k: mock_response)

        result = ut_analyzer.assess_water_rights(
            county_fips="49035", parcel_id="12-34-56"  # Salt Lake County
        )

        assert "availability_score" in result
        assert 0 <= result["availability_score"] <= 100
        assert result["drought_impact_level"] in ["low", "moderate", "high"]
        assert "estimated_connection_fee" in result
        assert len(result["points_of_diversion"]) > 0

    def test_great_salt_lake_watershed_constraints(self, ut_analyzer, monkeypatch):
        """
        WHEN: Property in Great Salt Lake watershed (critical management area)
        THEN: Lower availability, higher constraints
        """
        mock_response = {
            "points_of_diversion": [],
            "critical_management_area": True,
            "drought_status": "severe",
        }

        monkeypatch.setattr(ut_analyzer, "_query_ut_dwr", lambda *a, **k: mock_response)

        result = ut_analyzer.assess_water_rights(
            county_fips="49057", parcel_id="99"  # Weber County
        )

        assert result["availability_score"] < 50
        assert result["drought_impact_level"] == "high"
        assert result["critical_management_area"] is True


class TestUtahRegulatoryEnvironment:
    """Test Utah pro-development regulatory context."""

    def test_salt_lake_city_design_review(self, ut_analyzer):
        """
        WHEN: Property in Salt Lake City (design review complexity)
        THEN: Identify design review requirements, but generally
              faster permits than CO
        """
        result = ut_analyzer.assess_regulatory_environment("Salt Lake City")

        assert result["median_permit_days"] < 120
        assert result["friction_score"] < 60  # Lower than Boulder CO
        assert "design_review_required" in result

    def test_utah_state_pro_development(self, ut_analyzer):
        """
        WHEN: Evaluate Utah state-level regulatory environment
        THEN: Note pro-development policy context, favorable timelines
        """
        result = ut_analyzer.assess_regulatory_environment("Provo")

        assert result["median_permit_days"] < 90
        assert result["state_policy_context"] == "pro_development"
        assert result["friction_score"] < 50


class TestUtahSeismicRisk:
    """Test Wasatch Fault seismic risk assessment."""

    def test_wasatch_fault_high_risk(self, ut_analyzer):
        """
        WHEN: Property near active Wasatch Fault
        THEN: High seismic risk, structural requirements
        """
        # Salt Lake City near fault trace
        result = ut_analyzer.assess_seismic_risk(latitude=40.7608, longitude=-111.8910)

        assert result["fault_proximity_miles"] < 5.0
        assert result["seismic_design_category"] in ["D", "E"]
        assert result["structural_cost_premium_pct"] >= 5
        assert "seismic_retrofit" in result["recommendations"]

    def test_distance_from_fault(self, ut_analyzer):
        """
        WHEN: Property far from Wasatch Fault
        THEN: Lower seismic risk
        """
        # Eastern Utah (far from fault)
        result = ut_analyzer.assess_seismic_risk(latitude=40.0, longitude=-109.5)

        assert result["fault_proximity_miles"] > 50
        assert result["seismic_design_category"] in ["A", "B", "C"]


class TestUtahComposite:
    """Test composite UT state multiplier calculation."""

    def test_composite_state_multiplier(self, ut_analyzer, monkeypatch):
        """
        WHEN: Calculate UT-specific adjustment for all factors
        THEN: Composite multiplier for topography, employment,
              water, seismic
        """
        # Mock components
        monkeypatch.setattr(
            ut_analyzer,
            "assess_topography_constraints",
            lambda *a, **k: {"cost_premium_pct": 8},
        )
        monkeypatch.setattr(
            ut_analyzer,
            "analyze_silicon_slopes_employment",
            lambda *a, **k: {"employment_multiplier": 1.05},
        )
        monkeypatch.setattr(
            ut_analyzer,
            "assess_water_rights",
            lambda *a, **k: {"availability_score": 65},
        )
        monkeypatch.setattr(
            ut_analyzer,
            "assess_seismic_risk",
            lambda *a, **k: {"structural_cost_premium_pct": 5},
        )
        monkeypatch.setattr(
            ut_analyzer,
            "assess_regulatory_environment",
            lambda *a, **k: {"friction_score": 40},
        )

        result = ut_analyzer.calculate_state_multiplier(
            latitude=40.7608,
            longitude=-111.8910,
            elevation_ft=4500,
            county_fips="49035",
            parcel_id="123",
            jurisdiction="Salt Lake City",
        )

        assert "ut_multiplier" in result
        assert 0.9 <= result["ut_multiplier"] <= 1.1
        assert "adjustments" in result
        assert len(result["adjustments"]) >= 4

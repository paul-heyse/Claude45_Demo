"""Tests for OpenStreetMap Overpass API connector."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from Claude45_Demo.data_integration import CacheManager
from Claude45_Demo.data_integration.exceptions import DataSourceError
from Claude45_Demo.geo_analysis.osm import OSMConnector


@pytest.fixture
def cache_manager(tmp_path) -> CacheManager:  # type: ignore[no-untyped-def]
    """Create cache manager with temporary database for each test."""
    cache_file = tmp_path / "test_cache.db"
    return CacheManager(db_path=cache_file)


@pytest.fixture
def osm_connector(cache_manager: CacheManager) -> OSMConnector:
    """Create OSM connector for testing."""
    return OSMConnector(cache_manager=cache_manager)


class TestOSMConnectorInit:
    """Test OSM connector initialization."""

    def test_init_sets_default_overpass_url(self, cache_manager: CacheManager) -> None:
        """OSM connector should set default Overpass API URL."""
        connector = OSMConnector(cache_manager=cache_manager)
        assert connector.base_url == "https://overpass-api.de/api/interpreter"
        assert connector.cache_ttl.days == 30
        assert connector.api_key is None  # No API key needed for OSM


class TestPOIQuery:
    """Test POI querying functionality (Req: POI Category Counting)."""

    @patch("Claude45_Demo.geo_analysis.osm.requests.get")
    def test_query_grocery_stores_within_1km(
        self, mock_get: MagicMock, osm_connector: OSMConnector
    ) -> None:
        """
        Scenario: Grocery store accessibility
        WHEN the system evaluates food access
        THEN it queries OSM Overpass for shop=supermarket, shop=grocery within 1km
        AND counts stores and calculates stores per 10k population
        """
        lat, lon, radius = 40.0150, -105.2705, 1000  # Boulder, CO

        # Mock Overpass response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "type": "node",
                    "id": 1,
                    "lat": 40.02,
                    "lon": -105.27,
                    "tags": {"name": "Safeway", "shop": "supermarket"},
                },
                {
                    "type": "node",
                    "id": 2,
                    "lat": 40.01,
                    "lon": -105.28,
                    "tags": {"name": "King Soopers", "shop": "supermarket"},
                },
                {
                    "type": "node",
                    "id": 3,
                    "lat": 40.015,
                    "lon": -105.265,
                    "tags": {"name": "Natural Grocers", "shop": "grocery"},
                },
            ]
        }
        mock_get.return_value = mock_response

        result = osm_connector.query_pois(
            lat=lat,
            lon=lon,
            radius=radius,
            poi_types=["supermarket", "grocery"],
            category="shop",
        )

        assert len(result) == 3
        assert result[0]["name"] == "Safeway"
        assert result[0]["type"] == "supermarket"
        assert "lat" in result[0]
        assert "lon" in result[0]

        # Check Overpass query was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "overpass" in call_args[0][0]

    @patch("Claude45_Demo.geo_analysis.osm.requests.get")
    def test_query_schools_within_1500m(
        self, mock_get: MagicMock, osm_connector: OSMConnector
    ) -> None:
        """
        Scenario: School proximity
        WHEN the system evaluates family-friendliness
        THEN it identifies K-8 schools within 1.5km walk distance
        AND counts schools and normalizes by child population
        """
        lat, lon, radius = 40.0150, -105.2705, 1500

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "type": "node",
                    "id": 10,
                    "lat": 40.02,
                    "lon": -105.26,
                    "tags": {"name": "Whittier Elementary", "amenity": "school"},
                },
                {
                    "type": "way",
                    "id": 11,
                    "center": {"lat": 40.018, "lon": -105.275},
                    "tags": {"name": "Casey Middle School", "amenity": "school"},
                },
            ]
        }
        mock_get.return_value = mock_response

        result = osm_connector.query_pois(
            lat=lat,
            lon=lon,
            radius=radius,
            poi_types=["school"],
            category="amenity",
        )

        assert len(result) == 2
        assert result[0]["name"] == "Whittier Elementary"

    @patch("Claude45_Demo.geo_analysis.osm.requests.get")
    def test_query_third_places_within_1km(
        self, mock_get: MagicMock, osm_connector: OSMConnector
    ) -> None:
        """
        Scenario: Third-place density
        WHEN the system evaluates neighborhood vibrancy
        THEN it counts cafes, restaurants, pubs, libraries, community centers
        AND calculates third-place density per square kilometer
        """
        lat, lon, radius = 40.0150, -105.2705, 1000

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "type": "node",
                    "id": 20,
                    "lat": 40.015,
                    "lon": -105.27,
                    "tags": {"name": "Laughing Goat", "amenity": "cafe"},
                },
                {
                    "type": "node",
                    "id": 21,
                    "lat": 40.016,
                    "lon": -105.272,
                    "tags": {"name": "Pearl Street Library", "amenity": "library"},
                },
            ]
        }
        mock_get.return_value = mock_response

        result = osm_connector.query_pois(
            lat=lat,
            lon=lon,
            radius=radius,
            poi_types=["cafe", "restaurant", "pub", "library", "community_centre"],
            category="amenity",
        )

        assert len(result) == 2


class TestRoadNetworkRetrieval:
    """Test road network data retrieval (Req: Intersection Density)."""

    @patch("Claude45_Demo.geo_analysis.osm.requests.get")
    def test_retrieve_road_network_for_submarket(
        self, mock_get: MagicMock, osm_connector: OSMConnector
    ) -> None:
        """
        Scenario: Intersection density calculation
        WHEN the system evaluates walkability infrastructure
        THEN it retrieves OSM road network for submarket
        AND counts 3-way and 4-way intersections per square kilometer
        """
        bbox = (40.01, -105.28, 40.02, -105.27)  # min_lat, min_lon, max_lat, max_lon

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "type": "way",
                    "id": 100,
                    "nodes": [1, 2, 3],
                    "tags": {"highway": "residential"},
                },
                {
                    "type": "way",
                    "id": 101,
                    "nodes": [3, 4, 5],
                    "tags": {"highway": "secondary"},
                },
            ]
        }
        mock_get.return_value = mock_response

        result = osm_connector.get_road_network(bbox=bbox, road_types=["residential"])

        assert "ways" in result
        assert len(result["ways"]) == 2

    @patch("Claude45_Demo.geo_analysis.osm.requests.get")
    def test_retrieve_bikeway_network(
        self, mock_get: MagicMock, osm_connector: OSMConnector
    ) -> None:
        """
        Scenario: Bikeway network analysis
        WHEN the system evaluates bicycle infrastructure
        THEN it retrieves OSM bikeways tagged as cycleway, lane, or path
        """
        bbox = (40.01, -105.28, 40.02, -105.27)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "type": "way",
                    "id": 200,
                    "nodes": [10, 11, 12],
                    "tags": {"highway": "cycleway"},
                },
                {
                    "type": "way",
                    "id": 201,
                    "nodes": [12, 13, 14],
                    "tags": {"highway": "path", "bicycle": "designated"},
                },
            ]
        }
        mock_get.return_value = mock_response

        result = osm_connector.get_road_network(
            bbox=bbox, road_types=["cycleway", "path"]
        )

        assert len(result["ways"]) == 2


class TestCaching:
    """Test caching behavior for OSM queries."""

    @patch("Claude45_Demo.geo_analysis.osm.requests.get")
    def test_poi_query_uses_cache(
        self, mock_get: MagicMock, osm_connector: OSMConnector
    ) -> None:
        """POI queries should be cached to avoid repeated API calls."""
        lat, lon, radius = 40.0150, -105.2705, 1000

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"elements": []}
        mock_get.return_value = mock_response

        # First call should hit API
        result1 = osm_connector.query_pois(
            lat=lat, lon=lon, radius=radius, poi_types=["cafe"], category="amenity"
        )

        # Second call should use cache
        result2 = osm_connector.query_pois(
            lat=lat, lon=lon, radius=radius, poi_types=["cafe"], category="amenity"
        )

        assert result1 == result2
        # API should only be called once
        assert mock_get.call_count == 1


class TestErrorHandling:
    """Test error handling for OSM API failures."""

    @patch("Claude45_Demo.geo_analysis.osm.requests.get")
    def test_rate_limit_handling(
        self, mock_get: MagicMock, osm_connector: OSMConnector
    ) -> None:
        """OSM connector should handle rate limiting gracefully."""
        lat, lon, radius = 40.0150, -105.2705, 1000

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "429 Client Error"
        )
        mock_get.return_value = mock_response

        with pytest.raises(DataSourceError, match="rate limit|429"):
            osm_connector.query_pois(
                lat=lat, lon=lon, radius=radius, poi_types=["cafe"], category="amenity"
            )

    @patch("Claude45_Demo.geo_analysis.osm.requests.get")
    def test_invalid_overpass_query(
        self, mock_get: MagicMock, osm_connector: OSMConnector
    ) -> None:
        """OSM connector should handle invalid Overpass queries."""
        lat, lon, radius = 40.0150, -105.2705, 1000

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request: Invalid query syntax"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "400 Client Error"
        )
        mock_get.return_value = mock_response

        with pytest.raises(DataSourceError, match="400|Bad Request"):
            osm_connector.query_pois(
                lat=lat, lon=lon, radius=radius, poi_types=["cafe"], category="amenity"
            )


class TestQueryConstruction:
    """Test Overpass QL query construction."""

    def test_build_poi_query_string(self, osm_connector: OSMConnector) -> None:
        """OSM connector should build correct Overpass QL queries."""
        query = osm_connector._build_poi_query(
            lat=40.0, lon=-105.0, radius=1000, poi_types=["cafe"], category="amenity"
        )

        assert "[out:json]" in query
        assert 'node["amenity"~"cafe"]' in query or "node[amenity=cafe]" in query
        assert "40.0" in query or "40" in query
        assert "105" in query or "105.0" in query
        assert "1000" in query

    def test_build_road_network_query(self, osm_connector: OSMConnector) -> None:
        """OSM connector should build road network queries for bounding boxes."""
        query = osm_connector._build_road_query(
            bbox=(40.01, -105.28, 40.02, -105.27), road_types=["residential"]
        )

        assert "[out:json]" in query
        assert 'way["highway"~"residential"]' in query or "way[highway" in query
        assert "40.01" in query or "40" in query
        assert "105.27" in query or "105" in query

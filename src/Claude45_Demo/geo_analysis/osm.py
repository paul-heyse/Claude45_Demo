"""OpenStreetMap Overpass API connector for POI and road network data."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Sequence

import requests

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.exceptions import DataSourceError

if TYPE_CHECKING:  # pragma: no cover
    from Claude45_Demo.data_integration.cache import CacheManager

logger = logging.getLogger(__name__)


class OSMConnector(APIConnector):
    """
    OpenStreetMap Overpass API connector.

    Provides methods for querying POIs (points of interest) and road networks
    from OpenStreetMap using the Overpass API.

    No API key required for Overpass API (public service with rate limits).
    """

    DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_OVERPASS_URL,
        cache_ttl_days: int = 30,
        cache_manager: "CacheManager | None" = None,
    ) -> None:
        """
        Initialize OSM connector.

        Args:
            base_url: Overpass API endpoint (default: public instance)
            cache_ttl_days: Cache TTL in days (default: 30)
            cache_manager: Optional cache manager instance
        """
        super().__init__(
            api_key=None,
            base_url=base_url,
            cache_ttl_days=cache_ttl_days,
            cache_manager=cache_manager,
        )

    def _load_api_key(self) -> str | None:
        """OSM Overpass API does not require an API key."""
        return None

    def fetch(self, params: dict[str, Any]) -> Any:
        """
        Retrieve raw data from OSM Overpass API.

        This method is required by the APIConnector abstract base class,
        but OSMConnector uses specialized methods (query_pois, get_road_network)
        for different query types rather than a generic fetch.

        Args:
            params: Query parameters

        Returns:
            Raw API response
        """
        raise NotImplementedError(
            "OSMConnector uses specialized methods (query_pois, get_road_network)"
        )

    def parse(self, response: Any) -> Any:
        """
        Transform raw Overpass response into structured data.

        This method is required by the APIConnector abstract base class,
        but OSMConnector uses specialized parsing in _parse_pois for each
        query type.

        Args:
            response: Raw API response

        Returns:
            Parsed data
        """
        raise NotImplementedError("OSMConnector uses specialized parsing (_parse_pois)")

    def query_pois(
        self,
        lat: float,
        lon: float,
        radius: int,
        poi_types: Sequence[str],
        category: str,
    ) -> list[dict[str, Any]]:
        """
        Query POIs within a radius of a point.

        Implements requirements from:
        - Req: POI Category Counting and Density
        - Scenario: Grocery store accessibility (shop=supermarket, shop=grocery)
        - Scenario: School proximity (amenity=school)
        - Scenario: Third-place density (amenity=cafe, library, etc.)

        Args:
            lat: Latitude of center point
            lon: Longitude of center point
            radius: Search radius in meters
            poi_types: List of OSM tag values (e.g., ["cafe", "restaurant"])
            category: OSM tag key (e.g., "amenity", "shop")

        Returns:
            List of POI dictionaries with keys: id, name, type, lat, lon

        Raises:
            DataSourceError: If API request fails
        """
        cache_key = f"osm_poi_{lat}_{lon}_{radius}_{category}_{'_'.join(poi_types)}"

        # Check cache first
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for OSM POI query: {cache_key}")
                return cached  # type: ignore[no-any-return]

        # Build Overpass query
        query = self._build_poi_query(
            lat=lat, lon=lon, radius=radius, poi_types=poi_types, category=category
        )

        # Execute request
        try:
            response = requests.get(self.base_url, params={"data": query}, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise DataSourceError(
                    f"OSM Overpass API rate limit exceeded (429): {response.text}"
                ) from e
            raise DataSourceError(
                f"OSM Overpass API error ({response.status_code}): {response.text}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise DataSourceError(f"OSM Overpass API request failed: {e}") from e

        # Parse response
        data = response.json()
        pois = self._parse_pois(data, category)

        # Cache result
        if self.cache:
            self.cache.set(cache_key, pois, ttl=self.cache_ttl)

        logger.info(f"Retrieved {len(pois)} POIs from OSM Overpass API")
        return pois

    def get_road_network(
        self, bbox: tuple[float, float, float, float], road_types: Sequence[str]
    ) -> dict[str, Any]:
        """
        Retrieve road network data for a bounding box.

        Implements requirements from:
        - Req: Intersection Density and Network Connectivity
        - Scenario: Intersection density calculation (road network retrieval)
        - Scenario: Bikeway network analysis (cycleway, path)

        Args:
            bbox: Bounding box (min_lat, min_lon, max_lat, max_lon)
            road_types: List of highway types (e.g., ["residential", "cycleway"])

        Returns:
            Dictionary with 'ways' key containing list of road ways

        Raises:
            DataSourceError: If API request fails
        """
        min_lat, min_lon, max_lat, max_lon = bbox
        cache_key = (
            f"osm_roads_{min_lat}_{min_lon}_{max_lat}_{max_lon}_{'_'.join(road_types)}"
        )

        # Check cache
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for OSM road network query: {cache_key}")
                return cached  # type: ignore[no-any-return]

        # Build query
        query = self._build_road_query(bbox=bbox, road_types=road_types)

        # Execute request
        try:
            response = requests.get(self.base_url, params={"data": query}, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise DataSourceError(
                    f"OSM Overpass API rate limit exceeded (429): {response.text}"
                ) from e
            raise DataSourceError(
                f"OSM Overpass API error ({response.status_code}): {response.text}"
            ) from e
        except requests.exceptions.RequestException as e:
            raise DataSourceError(f"OSM Overpass API request failed: {e}") from e

        # Parse response
        data = response.json()
        roads = {"ways": data.get("elements", [])}

        # Cache result
        if self.cache:
            self.cache.set(cache_key, roads, ttl=self.cache_ttl)

        logger.info(f"Retrieved {len(roads['ways'])} road ways from OSM")
        return roads

    def _build_poi_query(
        self,
        lat: float,
        lon: float,
        radius: int,
        poi_types: Sequence[str],
        category: str,
    ) -> str:
        """
        Build Overpass QL query for POI search.

        Args:
            lat: Latitude
            lon: Longitude
            radius: Radius in meters
            poi_types: POI type tags
            category: Tag category (amenity, shop, etc.)

        Returns:
            Overpass QL query string
        """
        # Build tag filter (e.g., [amenity~"cafe|restaurant"])
        tag_filter = "|".join(poi_types)

        query = f"""
        [out:json][timeout:25];
        (
          node["{category}"~"{tag_filter}"](around:{radius},{lat},{lon});
          way["{category}"~"{tag_filter}"](around:{radius},{lat},{lon});
        );
        out center;
        """
        return query.strip()

    def _build_road_query(
        self, bbox: tuple[float, float, float, float], road_types: Sequence[str]
    ) -> str:
        """
        Build Overpass QL query for road network.

        Args:
            bbox: Bounding box (min_lat, min_lon, max_lat, max_lon)
            road_types: Highway type tags

        Returns:
            Overpass QL query string
        """
        min_lat, min_lon, max_lat, max_lon = bbox
        tag_filter = "|".join(road_types)

        query = f"""
        [out:json][timeout:25];
        (
          way["highway"~"{tag_filter}"]({min_lat},{min_lon},{max_lat},{max_lon});
        );
        out geom;
        """
        return query.strip()

    def _parse_pois(self, data: dict[str, Any], category: str) -> list[dict[str, Any]]:
        """
        Parse Overpass API response into POI list.

        Args:
            data: Raw Overpass API response
            category: Tag category used in query

        Returns:
            List of POI dictionaries
        """
        pois = []
        elements = data.get("elements", [])

        for element in elements:
            tags = element.get("tags", {})
            poi_type = tags.get(category, "unknown")

            # Extract coordinates (nodes have lat/lon, ways have center)
            if element["type"] == "node":
                lat = element.get("lat")
                lon = element.get("lon")
            elif element["type"] == "way" and "center" in element:
                lat = element["center"].get("lat")
                lon = element["center"].get("lon")
            else:
                continue  # Skip elements without coordinates

            poi = {
                "id": element["id"],
                "name": tags.get("name", "Unnamed"),
                "type": poi_type,
                "lat": lat,
                "lon": lon,
            }
            pois.append(poi)

        return pois

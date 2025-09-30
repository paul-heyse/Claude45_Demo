"""Isochrone calculations using OpenRouteService-compatible APIs."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence

import requests
from shapely.geometry import Point, shape
from shapely.ops import unary_union

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager
from Claude45_Demo.data_integration.exceptions import (
    ConfigurationError,
    DataSourceError,
    ValidationError,
)

logger = logging.getLogger(__name__)


@dataclass
class IsochroneResult:
    """Container for computed isochrone metrics."""

    geometry: Any
    poi_counts: Dict[str, int]
    population: int
    area_sq_km: float
    travel_mode: str
    range_minutes: int


class IsochroneCalculator(APIConnector):
    """Calculate travel-time isochrones for walk, drive, and multimodal trips."""

    DEFAULT_BASE_URL = "https://api.openrouteservice.org/v2/isochrones"

    def __init__(
        self,
        *,
        api_key: str | None,
        cache_manager: CacheManager | None = None,
        base_url: str = DEFAULT_BASE_URL,
        cache_ttl_days: int = 1,
        rate_limit: int = 2000,
    ) -> None:
        if not api_key:
            raise ConfigurationError(
                "OpenRouteService API key is required for isochrones"
            )

        super().__init__(
            api_key=api_key,
            base_url=base_url,
            cache_ttl_days=cache_ttl_days,
            rate_limit=rate_limit,
            cache_manager=cache_manager,
        )

    def fetch(self, params: Mapping[str, Any]) -> Dict[str, Any]:
        profile = params["profile"]
        payload = params["payload"]

        url = self._build_url(profile)
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

        self._check_rate_limit()
        self._track_request()

        def _request() -> Dict[str, Any]:
            response = requests.post(url, json=payload, headers=headers, timeout=45)
            try:
                response.raise_for_status()
            except requests.HTTPError as exc:  # pragma: no cover
                raise DataSourceError(
                    f"Isochrone API error ({response.status_code})"
                ) from exc
            return response.json()

        return self._retry_with_backoff(_request)

    def parse(self, response: Mapping[str, Any]) -> Dict[str, Any]:
        features = response.get("features")
        if not features:
            raise ValidationError("Isochrone response missing features")

        feature = features[0]
        geometry_mapping = feature.get("geometry")
        if not geometry_mapping:
            raise ValidationError("Isochrone feature missing geometry")

        geometry = shape(geometry_mapping)
        properties = feature.get("properties", {})

        return {
            "geometry": geometry,
            "properties": properties,
        }

    def calculate_walk_isochrone(
        self,
        *,
        latitude: float,
        longitude: float,
        range_minutes: int,
        amenities: Sequence[Mapping[str, Any]],
        population_blocks: Sequence[Mapping[str, Any]],
    ) -> IsochroneResult:
        return self._calculate_isochrone(
            profile="foot-walking",
            latitude=latitude,
            longitude=longitude,
            range_minutes=range_minutes,
            amenities=amenities,
            population_blocks=population_blocks,
        )

    def calculate_drive_isochrone(
        self,
        *,
        latitude: float,
        longitude: float,
        range_minutes: int,
        amenities: Sequence[Mapping[str, Any]],
        population_blocks: Sequence[Mapping[str, Any]],
        residential_population: int | None = None,
    ) -> IsochroneResult:
        result = self._calculate_isochrone(
            profile="driving-car",
            latitude=latitude,
            longitude=longitude,
            range_minutes=range_minutes,
            amenities=amenities,
            population_blocks=population_blocks,
        )
        if residential_population and residential_population > 0:
            reach_ratio = result.population / residential_population
            result.poi_counts = dict(result.poi_counts)
            result.poi_counts["reach_ratio"] = reach_ratio
        return result

    def calculate_multimodal_isochrone(
        self,
        *,
        latitude: float,
        longitude: float,
        legs: Sequence[Mapping[str, Any]],
        amenities: Sequence[Mapping[str, Any]],
        population_blocks: Sequence[Mapping[str, Any]],
    ) -> IsochroneResult:
        if not legs:
            raise ValidationError("At least one leg required for multimodal isochrone")

        geometries = []
        areas_sqm = []

        for leg in legs:
            profile = leg.get("profile")
            range_minutes = leg.get("range_minutes")
            if profile is None or range_minutes is None:
                raise ValidationError("Each leg must include profile and range_minutes")

            parsed = self._generate_isochrone(
                profile=profile,
                latitude=latitude,
                longitude=longitude,
                range_minutes=int(range_minutes),
            )
            geometries.append(parsed["geometry"])
            areas_sqm.append(self._extract_area(parsed))

        combined_geometry = unary_union(geometries)
        amenities_counts, population = self._summarize(
            combined_geometry, amenities, population_blocks
        )

        area_sq_km = 0.0
        if areas_sqm:
            area_sq_km = sum(a for a in areas_sqm if a is not None) / 1_000_000
            if area_sq_km == 0:
                area_sq_km = combined_geometry.area / 1_000_000

        travel_mode = "+".join(str(leg["profile"]) for leg in legs)
        total_minutes = sum(int(leg["range_minutes"]) for leg in legs)

        return IsochroneResult(
            geometry=combined_geometry,
            poi_counts=amenities_counts,
            population=int(round(population)),
            area_sq_km=area_sq_km,
            travel_mode=travel_mode,
            range_minutes=total_minutes,
        )

    def _calculate_isochrone(
        self,
        *,
        profile: str,
        latitude: float,
        longitude: float,
        range_minutes: int,
        amenities: Sequence[Mapping[str, Any]],
        population_blocks: Sequence[Mapping[str, Any]],
    ) -> IsochroneResult:
        parsed = self._generate_isochrone(
            profile=profile,
            latitude=latitude,
            longitude=longitude,
            range_minutes=range_minutes,
        )

        geometry = parsed["geometry"]
        amenities_counts, population = self._summarize(
            geometry, amenities, population_blocks
        )
        area_sq_km = self._extract_area(parsed) or geometry.area / 1_000_000

        return IsochroneResult(
            geometry=geometry,
            poi_counts=amenities_counts,
            population=int(round(population)),
            area_sq_km=area_sq_km,
            travel_mode=profile,
            range_minutes=range_minutes,
        )

    def _generate_isochrone(
        self,
        *,
        profile: str,
        latitude: float,
        longitude: float,
        range_minutes: int,
    ) -> Dict[str, Any]:
        cache_key = (
            f"isochrone_{profile}_{latitude:.5f}_{longitude:.5f}_{range_minutes}"
        )
        cached = self.cache.get(cache_key) if self.cache else None

        if cached is None:
            payload = {
                "locations": [[longitude, latitude]],
                "range": [range_minutes * 60],
                "units": "m",
            }
            response = self.fetch({"profile": profile, "payload": payload})
            if self.cache:
                self.cache.set(cache_key, response, ttl=self.cache_ttl)
        else:
            response = cached

        return self.parse(response)

    def _summarize(
        self,
        geometry,
        amenities: Sequence[Mapping[str, Any]],
        population_blocks: Sequence[Mapping[str, Any]],
    ) -> tuple[Dict[str, int], float]:
        counts: Dict[str, int] = {}
        for amenity in amenities:
            category = str(amenity.get("category", "unknown"))
            lat = amenity.get("lat")
            lon = amenity.get("lon")
            if lat is None or lon is None:
                continue
            point = Point(lon, lat)
            if geometry.contains(point) or geometry.touches(point):
                counts[category] = counts.get(category, 0) + 1

        population = 0.0
        for block in population_blocks:
            block_geometry = block.get("geometry")
            block_population = float(block.get("population", 0))
            if block_geometry is None:
                continue
            if geometry.intersects(block_geometry):
                intersection = geometry.intersection(block_geometry)
                if not intersection.is_empty and block_geometry.area > 0:
                    ratio = intersection.area / block_geometry.area
                else:
                    ratio = 0.0
                population += block_population * max(0.0, min(1.0, ratio))

        return counts, population

    @staticmethod
    def _extract_area(parsed: Mapping[str, Any]) -> float | None:
        properties = parsed.get("properties", {})
        summary = (
            properties.get("summary", {}) if isinstance(properties, Mapping) else {}
        )
        area = summary.get("area") if isinstance(summary, Mapping) else None
        return float(area) if area is not None else None

"""Transitland connector and GTFS analysis utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import pandas as pd

from Claude45_Demo.data_integration.base import APIConnector
from Claude45_Demo.data_integration.cache import CacheManager

BBOX_PARAM_ORDER = ("min_lon", "min_lat", "max_lon", "max_lat")


@dataclass(frozen=True)
class StopRecord:
    """Normalized Transitland stop representation used in summaries."""

    onestop_id: str
    name: str
    longitude: float
    latitude: float
    min_headway_minutes: Optional[float]


class TransitlandConnector(APIConnector):
    """Connector for the Transitland v2 REST API and GTFS analytics."""

    BASE_URL = "https://transit.land/api/v2/rest"

    def __init__(
        self,
        api_key: str,
        *,
        cache_manager: CacheManager | None = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=self.BASE_URL,
            cache_ttl_days=1,
            rate_limit=5_000,
            cache_manager=cache_manager,
        )

    def fetch(self, params):  # pragma: no cover - generic API usage
        """Transitland connectors use specialized helpers instead of fetch."""
        return self._retry_with_backoff(lambda: self._make_request("stops", params))

    def parse(self, response):  # pragma: no cover - passthrough
        return response

    # ------------------------------------------------------------------
    # Transitland stop retrieval
    # ------------------------------------------------------------------
    def fetch_stops_within_bbox(
        self,
        *,
        bbox: Sequence[float],
        per_page: int = 500,
    ) -> List[StopRecord]:
        """Fetch stops within bounding box from Transitland."""

        if len(bbox) != 4:
            raise ValueError(
                "bbox must contain four values: (min_lon, min_lat, max_lon, max_lat)"
            )

        cache_key = f"transitland_stops_{json.dumps(bbox)}_{per_page}"
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached

        params = {
            "bbox": ",".join(str(value) for value in bbox),
            "per_page": per_page,
            "apikey": self.api_key,
        }

        response = self._retry_with_backoff(lambda: self._make_request("stops", params))
        stops = self._parse_stops(response)

        if self.cache:
            self.cache.set(cache_key, stops, ttl=self.cache_ttl)
        return stops

    def _parse_stops(self, payload: dict) -> List[StopRecord]:
        stops = []
        for raw in payload.get("stops", []):
            coordinates = raw.get("geometry", {}).get("coordinates", [None, None])
            lon, lat = coordinates
            served_routes = raw.get("served_by_routes", []) or raw.get("routes", [])
            headways = [
                route.get("min_headway_minutes")
                for route in served_routes
                if route.get("min_headway_minutes") is not None
            ]
            min_headway = min(headways) if headways else None
            stops.append(
                StopRecord(
                    onestop_id=raw.get("onestop_id", ""),
                    name=raw.get("name", ""),
                    longitude=float(lon) if lon is not None else float("nan"),
                    latitude=float(lat) if lat is not None else float("nan"),
                    min_headway_minutes=(
                        float(min_headway) if min_headway is not None else None
                    ),
                )
            )
        return stops

    def get_stop_density_summary(
        self,
        *,
        bbox: Sequence[float],
        area_sq_km: float,
        population: float,
    ) -> dict:
        """Return summary metrics for stop density and frequency."""

        stops = self.fetch_stops_within_bbox(bbox=bbox)
        stop_count = len(stops)
        high_frequency = [
            stop
            for stop in stops
            if stop.min_headway_minutes is not None and stop.min_headway_minutes <= 15
        ]
        high_frequency_count = len(high_frequency)

        stops_per_sq_km = stop_count / area_sq_km if area_sq_km > 0 else 0.0
        stops_per_10k_population = (
            stop_count / population * 10_000 if population > 0 else 0.0
        )
        high_frequency_ratio = high_frequency_count / stop_count if stop_count else 0.0

        return {
            "stop_count": stop_count,
            "high_frequency_stop_count": high_frequency_count,
            "stops_per_sq_km": stops_per_sq_km,
            "stops_per_10k_population": stops_per_10k_population,
            "high_frequency_ratio": high_frequency_ratio,
        }

    # ------------------------------------------------------------------
    # GTFS service frequency analysis
    # ------------------------------------------------------------------
    def analyze_service_frequency(
        self,
        *,
        gtfs_path: Path,
        route_ids: Optional[Iterable[str]] = None,
        peak_window: tuple[int, int] = (7 * 60, 9 * 60),
        offpeak_window: tuple[int, int] = (10 * 60, 16 * 60),
        evening_threshold: int = 22 * 60,
    ) -> dict:
        """Analyze GTFS files to calculate headways and service coverage."""

        gtfs_path = Path(gtfs_path)
        trips = pd.read_csv(gtfs_path / "trips.txt", dtype=str)
        stop_times = pd.read_csv(gtfs_path / "stop_times.txt", dtype=str)
        calendar = pd.read_csv(gtfs_path / "calendar.txt")

        if route_ids is not None:
            trips = trips[trips["route_id"].isin(route_ids)]

        first_stop_times = self._extract_first_stop_departures(stop_times)
        departures = first_stop_times.merge(trips, on="trip_id", how="inner")

        weekday_services = calendar[
            calendar[["monday", "tuesday", "wednesday", "thursday", "friday"]].sum(
                axis=1
            )
            > 0
        ]["service_id"].astype(str)

        weekend_services = calendar[calendar[["saturday", "sunday"]].sum(axis=1) > 0][
            "service_id"
        ].astype(str)

        weekday_departures = departures[departures["service_id"].isin(weekday_services)]
        weekend_departures = departures[departures["service_id"].isin(weekend_services)]

        peak_headway = self._average_headway_minutes(weekday_departures, peak_window)
        offpeak_headway = self._average_headway_minutes(
            weekday_departures, offpeak_window
        )

        weekday_minutes = weekday_departures["departure_minutes"].tolist()
        weekday_service_hours = (
            (max(weekday_minutes) - min(weekday_minutes)) / 60
            if len(weekday_minutes) >= 2
            else 0.0
        )

        provides_evening = any(
            minute >= evening_threshold for minute in weekday_minutes
        )
        has_weekend = not weekend_departures.empty
        weekday_trip_count = int(len(weekday_departures))

        all_day_service = weekday_service_hours >= 16 and weekday_trip_count > 0

        return {
            "peak_headway_minutes": peak_headway,
            "offpeak_headway_minutes": offpeak_headway,
            "weekday_service_hours": weekday_service_hours,
            "weekday_trip_count": weekday_trip_count,
            "provides_evening_service": provides_evening,
            "has_weekend_service": has_weekend,
            "all_day_service": all_day_service,
        }

    def _extract_first_stop_departures(self, stop_times: pd.DataFrame) -> pd.DataFrame:
        minimal_sequence = stop_times.groupby("trip_id")["stop_sequence"].transform(
            "min"
        )
        first_stops = stop_times[minimal_sequence == stop_times["stop_sequence"]].copy()
        first_stops["departure_minutes"] = first_stops["departure_time"].map(
            self._time_to_minutes
        )
        return first_stops[["trip_id", "departure_minutes"]]

    @staticmethod
    def _average_headway_minutes(
        dataframe: pd.DataFrame, window: tuple[int, int]
    ) -> float:
        start, end = window
        window_departures = dataframe[
            dataframe["departure_minutes"].between(start, end, inclusive="left")
        ]["departure_minutes"].sort_values()

        times = window_departures.tolist()
        if len(times) <= 1:
            return 0.0

        diffs = [times[i + 1] - times[i] for i in range(len(times) - 1)]
        return sum(diffs) / len(diffs)

    @staticmethod
    def _time_to_minutes(value: str) -> int:
        hours, minutes, seconds = value.split(":")
        total_minutes = int(hours) * 60 + int(minutes)
        if int(seconds) >= 30:
            total_minutes += 1
        return total_minutes

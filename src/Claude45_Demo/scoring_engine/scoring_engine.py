"""Weighted scoring engine for investment analysis."""

from __future__ import annotations

import logging
import math
from typing import Any, Iterable, Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Calculate composite and risk-adjusted investment scores."""

    DEFAULT_WEIGHTS = {
        "supply_constraint": 0.30,
        "innovation_employment": 0.30,
        "urban_convenience": 0.20,
        "outdoor_access": 0.20,
    }

    EXTREME_RISK_THRESHOLD = 0.85

    # ------------------------------------------------------------------
    # Composite and risk scoring
    # ------------------------------------------------------------------
    def calculate_composite_score(
        self,
        component_scores: dict[str, float | None],
        weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        if weights is None:
            weights = self.DEFAULT_WEIGHTS.copy()

        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0, got {weight_sum:.3f}. Weights: {weights}"
            )

        available = {k: v for k, v in component_scores.items() if v is not None}
        missing = [k for k, v in component_scores.items() if v is None]
        if not available:
            raise ValueError("At least one component score must be provided")

        available_weight_sum = sum(weights.get(k, 0) for k in available)
        adjusted_weights = {
            k: weights.get(k, 0) / available_weight_sum
            for k in available
            if k in weights
        }

        composite_score = sum(available[k] * adjusted_weights[k] for k in available)

        return {
            "score": round(composite_score, 1),
            "components": component_scores,
            "weights": adjusted_weights,
            "metadata": {
                "complete": len(missing) == 0,
                "missing_components": missing,
                "n_components": len(available),
                "weight_adjusted": len(missing) > 0,
            },
        }

    def apply_risk_adjustment(
        self, market_score: float, risk_multiplier: float
    ) -> dict[str, Any]:
        final_score = market_score * risk_multiplier
        points_change = final_score - market_score
        is_extreme_risk = risk_multiplier < self.EXTREME_RISK_THRESHOLD

        if is_extreme_risk:
            logger.warning(
                "Market flagged as non-fit due to extreme risk multiplier %.2f",
                risk_multiplier,
            )

        return {
            "final_score": round(final_score, 1),
            "market_score": round(market_score, 1),
            "risk_multiplier": risk_multiplier,
            "risk_adjustment": {
                "points_lost": (
                    round(abs(points_change), 1) if points_change < 0 else 0.0
                ),
                "points_gained": round(points_change, 1) if points_change > 0 else 0.0,
            },
            "flagged_non_fit": is_extreme_risk,
            "exclusion_reason": "extreme_risk" if is_extreme_risk else None,
        }

    # ------------------------------------------------------------------
    # Normalization utilities
    # ------------------------------------------------------------------
    def normalize_linear(
        self, value: float, min_val: float, max_val: float, inverse: bool = False
    ) -> float:
        if max_val == min_val:
            return 50.0

        normalized = (value - min_val) / (max_val - min_val)
        normalized = max(0.0, min(1.0, normalized))
        if inverse:
            normalized = 1.0 - normalized
        return round(normalized * 100.0, 1)

    def normalize_percentile(
        self, target_value: float, all_values: list[float]
    ) -> float:
        if not all_values:
            return 50.0

        sorted_values = sorted(all_values)
        count_below = sum(1 for v in sorted_values if v < target_value)
        percentile = (count_below / len(sorted_values)) * 100.0
        return round(percentile, 1)

    def normalize_logarithmic(
        self, value: float, min_val: float, max_val: float, inverse: bool = False
    ) -> float:
        safe_min = max(min_val, 1e-6)
        safe_max = max(max_val, safe_min * 10)
        clipped = max(min(value, safe_max), safe_min)

        log_min = math.log10(safe_min)
        log_max = math.log10(safe_max)
        log_value = math.log10(clipped)

        normalized = (log_value - log_min) / (log_max - log_min)
        normalized = max(0.0, min(1.0, normalized))
        if inverse:
            normalized = 1.0 - normalized
        return round(normalized * 100.0, 1)

    def normalize_threshold(
        self,
        value: float,
        bands: Sequence[Mapping[str, float]],
        *,
        higher_is_better: bool = True,
    ) -> float:
        if not bands:
            return 0.0

        sorted_bands = sorted(
            bands, key=lambda b: b["threshold"], reverse=higher_is_better
        )
        selected_score = sorted_bands[-1]["score"]

        for band in sorted_bands:
            threshold = band["threshold"]
            score = band["score"]
            if higher_is_better and value >= threshold:
                selected_score = score
                break
            if not higher_is_better and value <= threshold:
                selected_score = score
                break
        return float(selected_score)

    # ------------------------------------------------------------------
    # Ranking and sensitivity
    # ------------------------------------------------------------------
    def rank_submarkets(
        self, submarkets: Sequence[Mapping[str, Any]]
    ) -> list[dict[str, Any]]:
        if not submarkets:
            return []

        def sort_key(entry: Mapping[str, Any]) -> tuple[float, float, float]:
            components = entry.get("component_scores", {})
            return (
                -entry.get("final_score", 0.0),
                -components.get("supply_constraint", 0.0),
                -components.get("innovation_employment", 0.0),
            )

        sorted_entries = sorted(submarkets, key=sort_key)
        count = len(sorted_entries)
        results: list[dict[str, Any]] = []

        for idx, entry in enumerate(sorted_entries):
            rank = idx + 1
            percentile = (
                100.0 if count == 1 else round(100 - (idx / (count - 1)) * 100, 1)
            )
            peers = [
                other["submarket_id"]
                for other in sorted_entries
                if other is not entry
                and other.get("final_score") == entry.get("final_score")
            ]

            results.append(
                {
                    "submarket_id": entry["submarket_id"],
                    "final_score": entry.get("final_score"),
                    "rank": rank,
                    "percentile": percentile,
                    "component_scores": entry.get("component_scores", {}),
                    "peers": peers,
                }
            )

        return results

    def run_weight_sensitivity(
        self,
        components: Mapping[str, float],
        scenarios: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        base_weights = self.DEFAULT_WEIGHTS.copy()
        results = []

        for scenario in scenarios:
            deltas = scenario.get("delta", {})
            adjusted = base_weights.copy()
            for key, delta in deltas.items():
                adjusted[key] = adjusted.get(key, 0.0) + delta

            total = sum(adjusted.values())
            if total <= 0:
                continue

            normalized = {k: v / total for k, v in adjusted.items()}
            composite = self.calculate_composite_score(dict(components), normalized)
            results.append(
                {
                    "scenario": scenario.get("name", "variant"),
                    "score": composite["score"],
                    "weights": composite["weights"],
                }
            )

        return results

    # ------------------------------------------------------------------
    # Visualization
    # ------------------------------------------------------------------
    def create_component_radar_chart(
        self,
        *,
        submarket_id: str,
        component_scores: Mapping[str, float],
        benchmark_scores: Mapping[str, Mapping[str, float]] | None = None,
    ):
        labels = list(component_scores.keys())
        values = [component_scores[label] for label in labels]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
        ax.plot(angles, values, label=submarket_id)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(np.linspace(0, 2 * np.pi, len(labels), endpoint=False))
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 100)
        ax.set_title(f"Component Scores – {submarket_id}")

        if benchmark_scores:
            for name, scores in benchmark_scores.items():
                bench_values = [scores.get(label, 0.0) for label in labels] + [
                    scores.get(labels[0], 0.0)
                ]
                ax.plot(angles, bench_values, linestyle="--", label=name)

        ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1))
        fig.tight_layout()
        return fig

    def create_comparison_heatmap(
        self, submarkets: Sequence[Mapping[str, Mapping[str, float]]]
    ):
        components = sorted(
            {key for entry in submarkets for key in entry["component_scores"]}
        )
        labels = [entry["submarket_id"] for entry in submarkets]
        matrix = [
            [entry["component_scores"].get(component, 0.0) for component in components]
            for entry in submarkets
        ]

        data = np.array(matrix)
        fig, ax = plt.subplots()
        im = ax.imshow(data, cmap="YlGnBu", vmin=0, vmax=100)
        ax.set_xticks(np.arange(len(components)))
        ax.set_xticklabels(components, rotation=45, ha="right")
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels(labels)
        fig.colorbar(im, ax=ax, label="Score")
        fig.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # Non-fit filtering and confidence scoring
    # ------------------------------------------------------------------
    def apply_non_fit_filters(
        self,
        *,
        component_scores: Mapping[str, float],
        risk_flags: Mapping[str, Any],
        risk_multiplier: float,
        insurance_override: bool,
    ) -> dict[str, Any]:
        reasons: list[str] = []
        supply = component_scores.get("supply_constraint", 0)
        urban = component_scores.get("urban_convenience", 0)
        transit = component_scores.get(
            "transit", component_scores.get("urban_convenience", 0)
        )
        outdoor = component_scores.get("outdoor_access", 0)

        if supply < 40 and urban < 35:
            reasons.append("commodity_sprawl")
        if transit < 25 and outdoor < 45:
            reasons.append("auto_only_desert")
        if risk_flags.get("hard_rent_control"):
            reasons.append("hard_rent_control")
        if (
            risk_flags.get("wildfire_score", 0) >= 90
            or risk_flags.get("flood_score", 0) >= 85
        ):
            reasons.append("chronic_hazard")
        if risk_multiplier < self.EXTREME_RISK_THRESHOLD:
            reasons.append("extreme_risk")

        flagged = bool(reasons)
        requires_override = flagged and not insurance_override

        return {
            "flagged": flagged,
            "reasons": reasons,
            "requires_override": requires_override,
        }

    def calculate_completeness_factor(
        self,
        *,
        available_metrics: Mapping[str, bool],
        critical_metrics: Iterable[str],
    ) -> dict[str, Any]:
        total = len(available_metrics)
        available_count = sum(1 for value in available_metrics.values() if value)
        missing = [key for key, value in available_metrics.items() if not value]
        critical_missing = [
            metric
            for metric in critical_metrics
            if not available_metrics.get(metric, False)
        ]

        base_factor = (available_count / total * 100) if total else 100.0
        if critical_missing:
            base_factor *= 0.7

        return {
            "factor": round(base_factor, 1),
            "missing": missing,
            "missing_critical": bool(critical_missing),
            "critical_missing_list": critical_missing,
        }

    def calculate_freshness_factor(
        self, metric_ages_months: Mapping[str, int]
    ) -> dict[str, Any]:
        if not metric_ages_months:
            return {"factor": 100.0, "max_age": 0, "stale_metrics": []}

        ages = list(metric_ages_months.values())
        average_age = sum(ages) / len(ages)
        max_age = max(ages)
        factor = max(10.0, 100.0 - average_age * 3)
        stale = [metric for metric, age in metric_ages_months.items() if age > 12]

        return {
            "factor": round(factor, 1),
            "max_age": max_age,
            "stale_metrics": stale,
        }

    def calculate_method_factor(
        self, metric_methods: Mapping[str, str]
    ) -> dict[str, Any]:
        method_weights = {"direct": 1.0, "proxy": 0.85, "estimate": 0.7}
        weights = [
            method_weights.get(method, 0.6) for method in metric_methods.values()
        ]
        factor = (sum(weights) / len(weights) * 100) if weights else 100.0

        return {
            "factor": round(factor, 1),
            "methods": metric_methods,
        }

    def calculate_confidence_score(
        self,
        *,
        completeness_factor: float,
        freshness_factor: float,
        method_factor: float,
        missing_critical: bool,
    ) -> dict[str, Any]:
        confidence = (
            completeness_factor * 0.5 + freshness_factor * 0.3 + method_factor * 0.2
        )
        if missing_critical:
            confidence *= 0.85

        flagged_low = confidence < 60
        return {
            "confidence": round(confidence, 1),
            "flagged_low_confidence": flagged_low,
            "diagnostics": {
                "completeness_factor": completeness_factor,
                "freshness_factor": freshness_factor,
                "method_factor": method_factor,
                "missing_critical": missing_critical,
            },
        }

    # ------------------------------------------------------------------
    # Validation reporting
    # ------------------------------------------------------------------
    def generate_validation_report(
        self,
        current_scores: Sequence[Mapping[str, Any]],
        reference_scores: Mapping[str, Mapping[str, Any]],
    ) -> pd.DataFrame:
        current_df = pd.DataFrame(current_scores)
        reference_df = (
            pd.DataFrame.from_dict(reference_scores, orient="index")
            .rename_axis("submarket_id")
            .reset_index()
        )

        merged = current_df.merge(
            reference_df,
            on="submarket_id",
            how="left",
            suffixes=("", "_ref"),
        )
        merged["score_delta"] = merged["final_score"] - merged["score"]
        merged["rank_delta"] = merged["rank"] - merged["rank_ref"]
        return merged

    # ------------------------------------------------------------------
    # Derived methods for convenience
    # ------------------------------------------------------------------
    def estimate_flood_insurance(
        self,
        *,
        flood_data: Mapping[str, Any],
        building_elevation: float | None,
        replacement_cost: float,
    ) -> Mapping[str, Any]:
        """Proxy through to FEMA analyzer when embedded in workflows."""

        from Claude45_Demo.risk_assessment.fema_flood import FEMAFloodAnalyzer

        analyzer = FEMAFloodAnalyzer()
        return analyzer.estimate_flood_insurance(
            flood_data=flood_data,
            building_elevation=building_elevation,
            replacement_cost=replacement_cost,
        )

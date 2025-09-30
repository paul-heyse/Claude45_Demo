"""Weighted scoring engine for investment analysis."""

from __future__ import annotations

import logging
import math
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Mapping, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Calculate composite investment scores using weighted components.

    Combines market analysis, geographic analysis, and risk assessment
    into final investment attractiveness scores.
    """

    DEFAULT_WEIGHTS = {
        "supply_constraint": 0.30,
        "innovation_employment": 0.30,
        "urban_convenience": 0.20,
        "outdoor_access": 0.20,
    }

    EXTREME_RISK_THRESHOLD = 0.85

    def calculate_composite_score(
        self,
        component_scores: dict[str, float | None],
        weights: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """
        Calculate composite market score with weighted components.

        Implements:
        - Req: Weighted Composite Scoring
        - Scenario: Default weighted score calculation
        - Scenario: Custom weight configuration
        - Scenario: Missing component handling

        Args:
            component_scores: Dict of component scores (0-100 or None if missing)
            weights: Optional custom weights (default: 30/30/20/20)

        Returns:
            Dict with composite score, components, weights, metadata

        Raises:
            ValueError: If weights don't sum to 1.0 or all components missing
        """
        if weights is None:
            weights = self.DEFAULT_WEIGHTS.copy()

        # Validate weights sum to 1.0 (within tolerance)
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0, got {weight_sum:.3f}. " f"Weights: {weights}"
            )

        # Filter to available components
        available = {k: v for k, v in component_scores.items() if v is not None}
        missing = [k for k, v in component_scores.items() if v is None]

        if not available:
            raise ValueError("At least one component score must be provided")

        # Redistribute weights for missing components
        available_weight_sum = sum(weights[k] for k in available if k in weights)
        adjusted_weights = {
            k: weights.get(k, 0) / available_weight_sum
            for k in available
            if k in weights
        }

        # Calculate weighted average
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
        """
        Apply risk multiplier to market score.

        Implements:
        - Req: Risk-Adjusted Scoring
        - Scenario: Risk multiplier application
        - Scenario: Extreme risk exclusion

        Args:
            market_score: Base market score (0-100)
            risk_multiplier: Risk adjustment factor (0.9-1.1 typical)

        Returns:
            Dict with final score, risk adjustment details, and exclusion flags
        """
        final_score = market_score * risk_multiplier
        points_change = final_score - market_score

        # Check for extreme risk
        is_extreme_risk = risk_multiplier < self.EXTREME_RISK_THRESHOLD
        flagged_non_fit = is_extreme_risk

        result = {
            "final_score": round(final_score, 1),
            "market_score": round(market_score, 1),
            "risk_multiplier": risk_multiplier,
            "risk_adjustment": {
                "points_lost": (
                    round(abs(points_change), 1) if points_change < 0 else 0.0
                ),
                "points_gained": round(points_change, 1) if points_change > 0 else 0.0,
            },
            "flagged_non_fit": flagged_non_fit,
            "exclusion_reason": "extreme_risk" if is_extreme_risk else None,
        }

        if flagged_non_fit:
            logger.warning(
                f"Market flagged as non-fit: risk_multiplier={risk_multiplier:.2f} "
                f"(threshold={self.EXTREME_RISK_THRESHOLD})"
            )

        return result

    def normalize_linear(
        self, value: float, min_val: float, max_val: float, inverse: bool = False
    ) -> float:
        """
        Normalize value to 0-100 using linear scaling.

        Implements:
        - Req: Normalization Functions
        - Scenario: Linear normalization

        Args:
            value: Raw value to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value
            inverse: If True, reverse scale (lower is better)

        Returns:
            Normalized score 0-100
        """
        if max_val == min_val:
            return 50.0  # Return mid-point if range is zero

        # Linear scaling to 0-1
        normalized = (value - min_val) / (max_val - min_val)

        # Clamp to 0-1
        normalized = max(0.0, min(1.0, normalized))

        # Apply inverse if specified
        if inverse:
            normalized = 1.0 - normalized

        # Scale to 0-100
        return round(normalized * 100.0, 1)

    def normalize_percentile(
        self, target_value: float, all_values: Sequence[float]
    ) -> float:
        """
        Normalize value using percentile rank.

        Implements:
        - Req: Normalization Functions
        - Scenario: Percentile-based normalization

        Args:
            target_value: Value to rank
            all_values: List of all values for comparison

        Returns:
            Percentile score 0-100
        """
        if not all_values:
            return 50.0

        # Sort values
        sorted_values = sorted(all_values)

        # Count values less than target
        count_below = sum(1 for v in sorted_values if v < target_value)

        # Calculate percentile rank
        percentile = (count_below / len(sorted_values)) * 100.0

        return round(percentile, 1)

    def normalize_logarithmic(
        self, value: float, min_val: float, max_val: float, inverse: bool = False
    ) -> float:
        """Apply logarithmic normalization for exponentially distributed metrics."""

        if value <= 0:
            raise ValueError("Value must be positive for logarithmic normalization")

        min_val = max(min_val, 1e-6)
        max_val = max(max_val, min_val * 10)
        value = max(value, min_val)

        log_min = math.log(min_val)
        log_max = math.log(max_val)
        log_val = math.log(value)

        if log_max == log_min:
            return 50.0

        normalized = (log_val - log_min) / (log_max - log_min)
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
        """Apply threshold/step based scoring."""

        if not bands:
            raise ValueError("At least one threshold band is required")

        sorted_bands = sorted(bands, key=lambda b: b["threshold"])

        if higher_is_better:
            applicable = [band for band in sorted_bands if value >= band["threshold"]]
            band = applicable[-1] if applicable else sorted_bands[0]
        else:
            applicable = [band for band in sorted_bands if value <= band["threshold"]]
            band = applicable[0] if applicable else sorted_bands[-1]

        return float(band["score"])

    def rank_submarkets(
        self,
        submarkets: Sequence[Mapping[str, Any]],
        *,
        peer_window: float = 5.0,
    ) -> List[Dict[str, Any]]:
        """Rank submarkets and compute percentile/quartile/peer group metadata."""

        if not submarkets:
            return []

        def _tie_breaker(item: Mapping[str, Any]) -> tuple:
            comps = item.get("component_scores", {})
            supply = comps.get("supply_constraint", 0.0)
            jobs = comps.get("innovation_employment", 0.0)
            urban = comps.get("urban_convenience", 0.0)
            outdoor = comps.get("outdoor_access", 0.0)
            return (-item.get("final_score", 0.0), -supply, -jobs, -urban, -outdoor)

        ordered = sorted(submarkets, key=_tie_breaker)
        total = len(ordered)
        results: List[Dict[str, Any]] = []

        for idx, entry in enumerate(ordered, start=1):
            final_score = float(entry.get("final_score", 0.0))
            percentile = round(100.0 * (total - idx + 1) / total, 1)

            if percentile > 75:
                quartile = "Q1"
            elif percentile > 50:
                quartile = "Q2"
            elif percentile > 25:
                quartile = "Q3"
            else:
                quartile = "Q4"

            peers = [
                item.get("submarket_id")
                for item in ordered
                if item is not entry
                and abs(item.get("final_score", 0.0) - final_score) <= peer_window
            ]

            results.append(
                {
                    "submarket_id": entry.get("submarket_id"),
                    "rank": idx,
                    "final_score": final_score,
                    "percentile": percentile,
                    "quartile": quartile,
                    "peers": peers,
                }
            )

        return results

    def run_weight_sensitivity(
        self,
        component_scores: Mapping[str, float],
        scenarios: Sequence[Mapping[str, Any]],
        *,
        base_weights: Mapping[str, float] | None = None,
    ) -> List[Dict[str, Any]]:
        """Evaluate score sensitivity to weight adjustments."""

        base = dict(base_weights or self.DEFAULT_WEIGHTS)
        results: List[Dict[str, Any]] = []

        for scenario in scenarios:
            delta = scenario.get("delta", {})
            weights = {**base}
            for key, change in delta.items():
                weights[key] = max(0.0, weights.get(key, 0.0) + change)

            total = sum(weights.values())
            if total == 0:
                continue
            weights = {k: v / total for k, v in weights.items()}

            score_details = self.calculate_composite_score(
                component_scores, weights=weights
            )
            results.append(
                {
                    "scenario": scenario.get("name", "unnamed"),
                    "weights": weights,
                    "score": score_details["score"],
                }
            )

        return results

    def create_component_radar_chart(
        self,
        *,
        submarket_id: str,
        component_scores: Mapping[str, float],
        benchmark_scores: Mapping[str, Mapping[str, float]] | None = None,
    ):
        """Create radar chart comparing component scores."""

        labels = list(component_scores.keys())
        values = [component_scores[label] for label in labels]

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values_cycle = values + [values[0]]
        angles_cycle = angles + [angles[0]]

        fig, ax = plt.subplots(subplot_kw={"polar": True})
        ax.plot(angles_cycle, values_cycle, label=submarket_id, linewidth=2)
        ax.fill(angles_cycle, values_cycle, alpha=0.1)

        if benchmark_scores:
            for name, scores in benchmark_scores.items():
                bench_values = [scores.get(label, 0.0) for label in labels]
                bench_cycle = bench_values + [bench_values[0]]
                ax.plot(angles_cycle, bench_cycle, linestyle="--", label=name)

        ax.set_xticks(angles)
        ax.set_xticklabels(labels)
        ax.set_yticklabels([])
        ax.set_title(f"Component Radar – {submarket_id}")
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
        ax.set_ylim(0, 100)

        return fig

    def create_comparison_heatmap(
        self, submarkets: Sequence[Mapping[str, Any]]
    ):
        """Create heatmap figure for component comparisons."""

        if not submarkets:
            raise ValueError("At least one submarket required for heatmap")

        df = pd.DataFrame(
            {
                item["submarket_id"]: item.get("component_scores", {})
                for item in submarkets
            }
        )

        df = df.reindex(sorted(df.index), axis=0)
        fig, ax = plt.subplots(figsize=(max(6, len(submarkets) * 1.5), 4))
        im = ax.imshow(df.values, aspect="auto", cmap="viridis", vmin=0, vmax=100)
        ax.set_xticks(np.arange(df.shape[1]))
        ax.set_xticklabels(df.columns)
        ax.set_yticks(np.arange(df.shape[0]))
        ax.set_yticklabels(df.index)
        ax.set_title("Component Comparison Heatmap")
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Score")

        return fig

    def apply_non_fit_filters(
        self,
        *,
        component_scores: Mapping[str, float],
        risk_flags: Mapping[str, Any],
        risk_multiplier: float,
        insurance_override: bool,
    ) -> Dict[str, Any]:
        """Evaluate non-fit rules and return exclusion metadata."""

        reasons: List[str] = []
        supply = component_scores.get("supply_constraint", 0.0)
        urban = component_scores.get("urban_convenience", 0.0)
        transit = component_scores.get("transit", component_scores.get("transit_access", 0.0))
        outdoor = component_scores.get("outdoor_access", 0.0)

        if supply < 40 and urban < 40:
            reasons.append("commodity_sprawl")

        if transit < 20 and urban < 30 and outdoor < 40:
            reasons.append("auto_only_desert")

        if risk_multiplier < self.EXTREME_RISK_THRESHOLD:
            reasons.append("extreme_risk")

        if risk_flags.get("hard_rent_control"):
            reasons.append("hard_rent_control")

        wildfire_score = risk_flags.get("wildfire_score", 0)
        flood_score = risk_flags.get("flood_score", 0)
        if wildfire_score > 90 and flood_score > 80:
            reasons.append("chronic_hazard")

        requires_override = any(
            reason in {"hard_rent_control", "chronic_hazard", "extreme_risk"}
            for reason in reasons
        )

        if "chronic_hazard" in reasons and insurance_override:
            reasons.remove("chronic_hazard")

        return {
            "flagged": bool(reasons),
            "reasons": reasons,
            "requires_override": requires_override and bool(reasons),
        }

    def calculate_completeness_factor(
        self,
        *,
        available_metrics: Mapping[str, bool],
        critical_metrics: Iterable[str],
    ) -> Dict[str, Any]:
        """Calculate completeness factor and capture missing critical metrics."""

        total = len(available_metrics)
        if total == 0:
            return {"factor": 100.0, "missing": [], "missing_critical": []}

        available_count = sum(1 for v in available_metrics.values() if v)
        pct_complete = (available_count / total) * 100.0
        factor = min(100.0, pct_complete * 1.2)

        missing = [k for k, v in available_metrics.items() if not v]
        critical_missing = [m for m in critical_metrics if not available_metrics.get(m, False)]

        if critical_missing:
            factor = max(0.0, factor - 15 * len(critical_missing))

        return {
            "factor": round(factor, 1),
            "missing": missing,
            "missing_critical": critical_missing,
        }

    def calculate_freshness_factor(self, data_ages_months: Mapping[str, float]) -> Dict[str, Any]:
        """Calculate freshness factor with penalties for stale data."""

        if not data_ages_months:
            return {"factor": 100.0, "stale_sources": []}

        scores = []
        stale = []
        for source, age in data_ages_months.items():
            if age <= 12:
                scores.append(100.0)
            else:
                stale.append(source)
                decay = (age - 12) * 5
                scores.append(max(30.0, 100.0 - decay))

        factor = round(sum(scores) / len(scores), 1)
        return {"factor": factor, "stale_sources": stale}

    def calculate_method_factor(self, methods: Mapping[str, str]) -> Dict[str, Any]:
        """Calculate method uncertainty factor based on data provenance."""

        penalties = {
            "direct": 0,
            "primary": 0,
            "hybrid": 10,
            "proxy": 20,
            "estimate": 30,
        }

        if not methods:
            return {"factor": 100.0, "penalties": {}}

        scores = []
        applied = {}
        for metric, method in methods.items():
            penalty = penalties.get(method, 25)
            applied[metric] = penalty
            scores.append(max(0.0, 100.0 - penalty))

        factor = round(sum(scores) / len(scores), 1)
        return {"factor": factor, "penalties": applied}

    def calculate_confidence_score(
        self,
        *,
        completeness_factor: float,
        freshness_factor: float,
        method_factor: float,
        missing_critical: Iterable[str],
    ) -> Dict[str, Any]:
        """Combine factors into overall confidence score."""

        confidence = (
            0.5 * completeness_factor
            + 0.3 * freshness_factor
            + 0.2 * method_factor
        )

        if missing_critical:
            confidence = max(0.0, confidence - 5 * len(list(missing_critical)))

        confidence = round(min(100.0, max(0.0, confidence)), 1)
        return {
            "confidence": confidence,
            "flagged_low_confidence": confidence < 70.0,
            "diagnostics": {
                "completeness": completeness_factor,
                "freshness": freshness_factor,
                "method": method_factor,
                "missing_critical": list(missing_critical),
            },
        }

    def generate_validation_report(
        self,
        current_results: Sequence[Mapping[str, Any]],
        reference_results: Mapping[str, Mapping[str, Any]],
    ) -> pd.DataFrame:
        """Generate validation report comparing current vs reference scores."""

        records = []
        for entry in current_results:
            submarket_id = entry.get("submarket_id")
            current_score = float(entry.get("final_score", 0.0))
            current_rank = int(entry.get("rank", 0))

            reference = reference_results.get(submarket_id, {})
            reference_score = reference.get("score")
            reference_rank = reference.get("rank")

            score_delta = (
                None
                if reference_score is None
                else round(current_score - float(reference_score), 1)
            )
            rank_delta = (
                None
                if reference_rank is None
                else int(current_rank - int(reference_rank))
            )

            records.append(
                {
                    "submarket_id": submarket_id,
                    "final_score": current_score,
                    "rank": current_rank,
                    "reference_score": reference_score,
                    "reference_rank": reference_rank,
                    "score_delta": score_delta,
                    "rank_delta": rank_delta,
                    "large_rank_delta": abs(rank_delta) >= 10 if rank_delta is not None else False,
                }
            )

        df = pd.DataFrame(records)
        df.sort_values(by="final_score", ascending=False, inplace=True)
        return df.reset_index(drop=True)

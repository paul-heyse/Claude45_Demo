"""Sensitivity analysis for scoring weights."""

import itertools
from typing import Any

from Claude45_Demo.scoring_engine import ScoringEngine


def run_sensitivity_analysis(
    component_scores: dict[str, float],
    weight_variations: list[float] = None,
) -> dict[str, Any]:
    """
    Perform sensitivity analysis on scoring weights.

    Tests how composite scores change when weights are varied.

    Args:
        component_scores: Base component scores
        weight_variations: List of weight deltas to test (default: [-0.10, -0.05, 0, +0.05, +0.10])

    Returns:
        Dictionary with sensitivity analysis results
    """
    if weight_variations is None:
        weight_variations = [-0.10, -0.05, 0.0, +0.05, +0.10]

    engine = ScoringEngine()
    base_weights = engine.DEFAULT_WEIGHTS.copy()
    base_result = engine.calculate_composite_score(component_scores, base_weights)
    base_score = base_result["score"]

    results = {
        "base_score": base_score,
        "base_weights": base_weights,
        "component_scores": component_scores,
        "sensitivity": {},
        "most_sensitive_component": None,
        "least_sensitive_component": None,
    }

    # Test each component individually
    component_sensitivity = {}

    for component in base_weights.keys():
        component_results = []

        for delta in weight_variations:
            # Create modified weights
            modified_weights = base_weights.copy()
            new_weight = base_weights[component] + delta

            # Skip if weight goes negative or > 1
            if new_weight < 0 or new_weight > 1:
                continue

            # Redistribute delta across other components proportionally
            other_components = [c for c in base_weights.keys() if c != component]
            remaining_weight = 1.0 - new_weight
            current_other_sum = sum(base_weights[c] for c in other_components)

            if current_other_sum > 0:
                for other in other_components:
                    modified_weights[other] = (
                        base_weights[other] / current_other_sum
                    ) * remaining_weight

            modified_weights[component] = new_weight

            # Calculate new score
            try:
                result = engine.calculate_composite_score(
                    component_scores, modified_weights
                )
                new_score = result["score"]
                score_delta = new_score - base_score

                component_results.append({
                    "weight": round(new_weight, 2),
                    "weight_delta": round(delta, 2),
                    "score": round(new_score, 1),
                    "score_delta": round(score_delta, 1),
                    "percent_change": round((score_delta / base_score) * 100, 1)
                    if base_score > 0
                    else 0,
                })
            except ValueError:
                continue

        if component_results:
            # Calculate average absolute impact
            avg_impact = sum(
                abs(r["score_delta"]) for r in component_results
            ) / len(component_results)

            component_sensitivity[component] = {
                "average_impact": round(avg_impact, 2),
                "results": component_results,
            }

    results["sensitivity"] = component_sensitivity

    # Identify most/least sensitive
    if component_sensitivity:
        most_sensitive = max(
            component_sensitivity.items(), key=lambda x: x[1]["average_impact"]
        )
        least_sensitive = min(
            component_sensitivity.items(), key=lambda x: x[1]["average_impact"]
        )

        results["most_sensitive_component"] = {
            "name": most_sensitive[0],
            "average_impact": most_sensitive[1]["average_impact"],
        }
        results["least_sensitive_component"] = {
            "name": least_sensitive[0],
            "average_impact": least_sensitive[1]["average_impact"],
        }

    return results


def generate_sensitivity_report(analysis_results: dict[str, Any]) -> str:
    """Generate human-readable sensitivity analysis report."""
    report = []
    report.append("=" * 70)
    report.append("SCORING WEIGHT SENSITIVITY ANALYSIS")
    report.append("=" * 70)
    report.append("")

    report.append(f"Base Composite Score: {analysis_results['base_score']:.1f}")
    report.append("")

    report.append("Base Weights:")
    for component, weight in analysis_results["base_weights"].items():
        report.append(f"  {component}: {weight:.2f}")
    report.append("")

    report.append("Component Scores:")
    for component, score in analysis_results["component_scores"].items():
        report.append(f"  {component}: {score:.1f}")
    report.append("")

    report.append("-" * 70)
    report.append("SENSITIVITY RESULTS")
    report.append("-" * 70)
    report.append("")

    for component, data in analysis_results["sensitivity"].items():
        report.append(f"{component.upper()}:")
        report.append(f"  Average Impact: {data['average_impact']:.2f} points")
        report.append("  Weight Variations:")
        for result in data["results"]:
            report.append(
                f"    Weight {result['weight']:.2f} ({result['weight_delta']:+.2f}): "
                f"Score {result['score']:.1f} ({result['score_delta']:+.1f}, "
                f"{result['percent_change']:+.1f}%)"
            )
        report.append("")

    if analysis_results["most_sensitive_component"]:
        report.append("-" * 70)
        report.append("KEY FINDINGS")
        report.append("-" * 70)
        report.append("")
        report.append(
            f"Most Sensitive Component: {analysis_results['most_sensitive_component']['name']}"
        )
        report.append(
            f"  Average Impact: {analysis_results['most_sensitive_component']['average_impact']:.2f} points"
        )
        report.append("")
        report.append(
            f"Least Sensitive Component: {analysis_results['least_sensitive_component']['name']}"
        )
        report.append(
            f"  Average Impact: {analysis_results['least_sensitive_component']['average_impact']:.2f} points"
        )
        report.append("")

    report.append("=" * 70)

    return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    sample_scores = {
        "supply_constraint": 75.0,
        "innovation_employment": 70.0,
        "urban_convenience": 65.0,
        "outdoor_access": 80.0,
    }

    print("Running sensitivity analysis...")
    results = run_sensitivity_analysis(sample_scores)
    print(generate_sensitivity_report(results))


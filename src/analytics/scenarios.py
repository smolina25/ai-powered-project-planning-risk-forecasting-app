from __future__ import annotations

import copy
from collections.abc import Callable, Sequence
from typing import Any

import pandas as pd

from src.analytics.metrics import compute_metrics
from src.simulation.monte_carlo import run_monte_carlo


TaskRecord = dict[str, Any]


def apply_capacity_boost(tasks: Sequence[TaskRecord], factor: float = 0.85) -> list[TaskRecord]:
    """Increase capacity by reducing duration and uncertainty by a factor."""
    boosted = copy.deepcopy(list(tasks))
    for task in boosted:
        task["mean_duration"] = max(1.0, float(task["mean_duration"]) * factor)
        task["std_dev"] = max(0.0, float(task["std_dev"]) * factor)
    return boosted


def scenario_comparison(
    build_graph_fn: Callable[[Sequence[TaskRecord]], Any],
    tasks: Sequence[TaskRecord],
    deadline_days: float,
    iterations: int,
    seed: int | None = None,
    capacity_factor: float = 0.85,
    aggressive_deadline_factor: float = 0.85,
) -> pd.DataFrame:
    """Evaluate baseline, aggressive deadline, and increased-capacity scenarios."""
    deadline = float(deadline_days)
    tight_deadline = deadline * float(aggressive_deadline_factor)

    baseline_graph = build_graph_fn(tasks)
    baseline_completion = run_monte_carlo(baseline_graph, iterations=iterations, seed=seed)

    baseline_metrics = compute_metrics(baseline_completion, deadline)
    aggressive_metrics = compute_metrics(baseline_completion, tight_deadline)

    boosted_tasks = apply_capacity_boost(tasks, factor=capacity_factor)
    boosted_graph = build_graph_fn(boosted_tasks)
    boosted_completion = run_monte_carlo(
        boosted_graph,
        iterations=iterations,
        seed=None if seed is None else seed + 1,
    )
    boosted_metrics = compute_metrics(boosted_completion, deadline)

    rows = [
        {
            "Scenario": "Baseline",
            "Delay Prob (%)": round(baseline_metrics["delay_probability"] * 100.0, 1),
            "P80 (days)": round(baseline_metrics["p80"], 1),
            "Mean (days)": round(baseline_metrics["mean"], 1),
            "Notes": f"Deadline: {deadline:.1f} days",
        },
        {
            "Scenario": "Aggressive Deadline (-15%)",
            "Delay Prob (%)": round(aggressive_metrics["delay_probability"] * 100.0, 1),
            "P80 (days)": round(aggressive_metrics["p80"], 1),
            "Mean (days)": round(aggressive_metrics["mean"], 1),
            "Notes": f"Deadline evaluated at {tight_deadline:.1f} days",
        },
        {
            "Scenario": "Increased Capacity (+15% faster)",
            "Delay Prob (%)": round(boosted_metrics["delay_probability"] * 100.0, 1),
            "P80 (days)": round(boosted_metrics["p80"], 1),
            "Mean (days)": round(boosted_metrics["mean"], 1),
            "Notes": "Mean/std dev reduced by 15%",
        },
    ]

    return pd.DataFrame(rows)

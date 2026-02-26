from __future__ import annotations

from collections.abc import Sequence

import networkx as nx
import numpy as np

from src.config import settings
from src.modeling.critical_path import longest_path_for_durations


def run_monte_carlo(
    graph: nx.DiGraph,
    iterations: int = 1000,
    seed: int | None = None,
    return_paths: bool = False,
) -> np.ndarray | tuple[np.ndarray, Sequence[list[str]]]:
    """Run Monte Carlo simulation with dynamic critical path per iteration."""
    if iterations <= 0:
        raise ValueError("iterations must be a positive integer.")

    rng = np.random.default_rng(seed)
    nodes = list(graph.nodes)

    completion_times = np.zeros(iterations, dtype=float)
    critical_paths: list[list[str]] = []

    for idx in range(iterations):
        sampled_durations: dict[str, float] = {}
        for node in nodes:
            mean_duration = float(graph.nodes[node].get("mean_duration", 0.0))
            std_dev = float(graph.nodes[node].get("std_dev", 0.0))
            sampled_value = rng.normal(mean_duration, std_dev) if std_dev > 0 else mean_duration
            sampled_durations[node] = max(float(sampled_value), settings.min_duration)

        path, total_duration = longest_path_for_durations(graph, sampled_durations)
        completion_times[idx] = total_duration

        if return_paths:
            critical_paths.append(path)

    if return_paths:
        return completion_times, critical_paths
    return completion_times

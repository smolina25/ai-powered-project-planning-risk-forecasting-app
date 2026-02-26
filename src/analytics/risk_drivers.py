from __future__ import annotations

from collections import Counter

import networkx as nx

from src.simulation.monte_carlo import run_monte_carlo


def rank_delay_drivers(
    graph: nx.DiGraph,
    iterations: int = 500,
    seed: int | None = None,
) -> list[dict]:
    """Rank tasks by simulated critical-path frequency."""
    _, critical_paths = run_monte_carlo(
        graph,
        iterations=iterations,
        seed=seed,
        return_paths=True,
    )

    counts: Counter[str] = Counter()
    for path in critical_paths:
        counts.update(path)

    ranked: list[dict] = []
    for task_id, frequency in counts.most_common():
        node = graph.nodes[task_id]
        ranked.append(
            {
                "task_id": task_id,
                "task_name": node.get("name", task_id),
                "critical_path_frequency": int(frequency),
                "critical_path_frequency_pct": round(100.0 * frequency / iterations, 1),
                "risk_factor": float(node.get("risk_factor", 0.0)),
            }
        )

    return ranked

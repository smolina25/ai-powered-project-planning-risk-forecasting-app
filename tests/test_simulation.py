from __future__ import annotations

from src.modeling.graph_builder import build_project_graph
from src.simulation.monte_carlo import run_monte_carlo


def _branching_tasks() -> list[dict]:
    return [
        {
            "id": "T1",
            "name": "Path A",
            "mean_duration": 7,
            "std_dev": 2,
            "dependencies": [],
            "risk_factor": 0.2,
        },
        {
            "id": "T2",
            "name": "Path B",
            "mean_duration": 7,
            "std_dev": 2,
            "dependencies": [],
            "risk_factor": 0.2,
        },
        {
            "id": "T3",
            "name": "Merge",
            "mean_duration": 2,
            "std_dev": 0.4,
            "dependencies": ["T1", "T2"],
            "risk_factor": 0.1,
        },
    ]


def test_monte_carlo_reproducibility_with_seed() -> None:
    graph = build_project_graph(_branching_tasks())

    a = run_monte_carlo(graph, iterations=120, seed=42)
    b = run_monte_carlo(graph, iterations=120, seed=42)

    assert a.shape == (120,)
    assert (a == b).all()


def test_dynamic_critical_path_changes_across_iterations() -> None:
    graph = build_project_graph(_branching_tasks())

    _, paths = run_monte_carlo(graph, iterations=250, seed=99, return_paths=True)
    unique_paths = {tuple(path) for path in paths}

    assert len(unique_paths) >= 2

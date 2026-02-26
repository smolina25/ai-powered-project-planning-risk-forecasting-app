from __future__ import annotations

from src.analytics.risk_drivers import rank_delay_drivers
from src.analytics.scenarios import apply_capacity_boost, scenario_comparison
from src.modeling.graph_builder import build_project_graph


TASKS = [
    {"id": "T1", "name": "Start", "mean_duration": 5, "std_dev": 1.0, "dependencies": [], "risk_factor": 0.2},
    {"id": "T2", "name": "Build", "mean_duration": 9, "std_dev": 2.0, "dependencies": ["T1"], "risk_factor": 0.4},
    {"id": "T3", "name": "Test", "mean_duration": 4, "std_dev": 1.0, "dependencies": ["T2"], "risk_factor": 0.3},
]


def test_apply_capacity_boost_reduces_duration() -> None:
    boosted = apply_capacity_boost(TASKS, factor=0.85)
    assert boosted[1]["mean_duration"] < TASKS[1]["mean_duration"]
    assert boosted[1]["std_dev"] < TASKS[1]["std_dev"]


def test_scenario_comparison_returns_expected_rows_and_columns() -> None:
    result = scenario_comparison(
        build_graph_fn=build_project_graph,
        tasks=TASKS,
        deadline_days=22,
        iterations=150,
        seed=7,
    )

    assert len(result) == 3
    assert set(result.columns) == {
        "Scenario",
        "Delay Prob (%)",
        "P80 (days)",
        "Mean (days)",
        "Notes",
    }


def test_rank_delay_drivers_returns_expected_shape() -> None:
    graph = build_project_graph(TASKS)
    drivers = rank_delay_drivers(graph, iterations=100, seed=12)

    assert len(drivers) >= 1
    assert {"task_id", "task_name", "critical_path_frequency", "critical_path_frequency_pct", "risk_factor"}.issubset(
        set(drivers[0].keys())
    )

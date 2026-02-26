from __future__ import annotations

import pytest

from src.modeling.graph_builder import build_project_graph
from src.utils.errors import GraphValidationError


VALID_TASKS = [
    {"id": "T1", "name": "Start", "mean_duration": 4, "std_dev": 1, "dependencies": [], "risk_factor": 0.1},
    {"id": "T2", "name": "Build", "mean_duration": 8, "std_dev": 2, "dependencies": ["T1"], "risk_factor": 0.3},
    {"id": "T3", "name": "QA", "mean_duration": 5, "std_dev": 1.2, "dependencies": ["T2"], "risk_factor": 0.2},
]


def test_build_project_graph_success() -> None:
    graph = build_project_graph(VALID_TASKS)
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2
    assert ("T1", "T2") in graph.edges


def test_missing_dependency_raises_graph_validation_error() -> None:
    tasks = [
        {"id": "T1", "name": "Start", "mean_duration": 4, "std_dev": 1, "dependencies": ["T9"], "risk_factor": 0.1}
    ]
    with pytest.raises(GraphValidationError):
        build_project_graph(tasks)


def test_cycle_raises_graph_validation_error() -> None:
    tasks = [
        {"id": "T1", "name": "Start", "mean_duration": 4, "std_dev": 1, "dependencies": ["T2"], "risk_factor": 0.1},
        {"id": "T2", "name": "Build", "mean_duration": 8, "std_dev": 2, "dependencies": ["T1"], "risk_factor": 0.3},
    ]
    with pytest.raises(GraphValidationError):
        build_project_graph(tasks)

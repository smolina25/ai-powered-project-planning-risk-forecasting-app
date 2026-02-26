from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import networkx as nx

from src.utils.errors import GraphValidationError


TaskRecord = Mapping[str, Any]


def build_project_graph(tasks: Sequence[TaskRecord]) -> nx.DiGraph:
    """Build and validate a project dependency graph.

    Nodes represent tasks and directed edges represent dependencies.
    Each edge points from dependency -> dependent task.
    """
    graph = nx.DiGraph()
    seen_ids: set[str] = set()

    for task in tasks:
        task_id = str(task.get("id", "")).strip()
        if not task_id:
            raise GraphValidationError("Task id is required for every task.")
        if task_id in seen_ids:
            raise GraphValidationError(f"Duplicate task id found: {task_id}")
        seen_ids.add(task_id)
        graph.add_node(task_id, **dict(task))

    for task in tasks:
        task_id = str(task["id"]).strip()
        dependencies = task.get("dependencies", []) or []
        if not isinstance(dependencies, list):
            raise GraphValidationError(f"Dependencies for task {task_id} must be a list.")

        for dependency in dependencies:
            dependency_id = str(dependency).strip()
            if dependency_id not in graph.nodes:
                raise GraphValidationError(
                    f"Dependency {dependency_id} not found for task {task_id}."
                )
            graph.add_edge(dependency_id, task_id)

    if not nx.is_directed_acyclic_graph(graph):
        raise GraphValidationError("Project graph contains cycles (not a DAG).")

    return graph

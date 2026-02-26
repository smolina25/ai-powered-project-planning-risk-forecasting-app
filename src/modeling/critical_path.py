from __future__ import annotations

from collections.abc import Mapping

import networkx as nx


def longest_path_for_durations(
    graph: nx.DiGraph,
    durations: Mapping[str, float],
) -> tuple[list[str], float]:
    """Compute the longest node-weighted path for a DAG.

    The duration for a path is the sum of node durations.
    """
    if graph.number_of_nodes() == 0:
        return [], 0.0

    topo_order = list(nx.topological_sort(graph))
    best_score: dict[str, float] = {}
    predecessor: dict[str, str | None] = {}

    for node in topo_order:
        if node not in durations:
            raise KeyError(f"Missing sampled duration for node: {node}")

        own_duration = float(durations[node])
        parent_nodes = list(graph.predecessors(node))

        if not parent_nodes:
            best_score[node] = own_duration
            predecessor[node] = None
            continue

        best_parent = max(parent_nodes, key=lambda parent: best_score[parent])
        best_score[node] = best_score[best_parent] + own_duration
        predecessor[node] = best_parent

    end_node = max(topo_order, key=lambda node: best_score[node])
    total_duration = best_score[end_node]

    path: list[str] = []
    cursor: str | None = end_node
    while cursor is not None:
        path.append(cursor)
        cursor = predecessor[cursor]
    path.reverse()

    return path, float(total_duration)


def critical_path_by_mean(graph: nx.DiGraph) -> tuple[list[str], float]:
    """Compute baseline critical path using each task's mean duration."""
    durations = {
        node: float(graph.nodes[node].get("mean_duration", 0.0))
        for node in graph.nodes
    }
    return longest_path_for_durations(graph, durations)

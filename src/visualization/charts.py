from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def completion_histogram(
    completion_times: np.ndarray,
    deadline: float,
    p50: float,
    p80: float,
) -> go.Figure:
    """Build histogram for completion-time distribution."""
    figure = go.Figure()
    figure.add_trace(
        go.Histogram(
            x=completion_times,
            nbinsx=40,
            name="Simulated completion",
            marker_color="#0e7490",
            opacity=0.78,
        )
    )

    figure.add_vline(
        x=deadline,
        line_dash="dash",
        line_color="#b91c1c",
        annotation_text=f"Deadline ({deadline:.1f}d)",
        annotation_position="top",
    )
    figure.add_vline(
        x=p50,
        line_dash="dot",
        line_color="#0f766e",
        annotation_text=f"P50 ({p50:.1f}d)",
        annotation_position="top",
    )
    figure.add_vline(
        x=p80,
        line_dash="dot",
        line_color="#ca8a04",
        annotation_text=f"P80 ({p80:.1f}d)",
        annotation_position="top",
    )

    figure.update_layout(
        title="Monte Carlo Completion Distribution",
        xaxis_title="Completion time (days)",
        yaxis_title="Frequency",
        bargap=0.05,
        template="plotly_white",
        height=430,
    )
    return figure


def dependency_graph_figure(graph: nx.DiGraph, critical_path: list[str]) -> go.Figure:
    """Build dependency graph with critical path highlighting."""
    if graph.number_of_nodes() == 0:
        return go.Figure()

    positions = nx.spring_layout(graph, seed=42, k=1.5)
    critical_set = set(critical_path)

    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    for source, target in graph.edges():
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_x = [positions[node][0] for node in graph.nodes()]
    node_y = [positions[node][1] for node in graph.nodes()]
    node_labels = [str(node) for node in graph.nodes()]
    node_names = [str(graph.nodes[node].get("name", node)) for node in graph.nodes()]
    node_colors = ["#b91c1c" if node in critical_set else "#1d4ed8" for node in graph.nodes()]

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=1.5, color="#94a3b8"),
            hoverinfo="none",
            name="Dependencies",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_labels,
            customdata=node_names,
            textposition="middle center",
            textfont=dict(color="white", size=11),
            marker=dict(size=30, color=node_colors, line=dict(width=2, color="white")),
            hovertemplate="<b>%{text}</b><br>%{customdata}<extra></extra>",
            name="Tasks",
        )
    )
    figure.update_layout(
        title="Task Dependency Graph (Critical path in red)",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        template="plotly_white",
        height=500,
        margin=dict(l=10, r=10, t=60, b=10),
    )
    return figure


def risk_drivers_bar(drivers_df: pd.DataFrame) -> go.Figure:
    """Build horizontal bar chart for critical-path frequency."""
    if drivers_df.empty:
        return go.Figure()

    chart_df = drivers_df.copy()
    label_column = "task_name" if "task_name" in chart_df.columns else chart_df.columns[0]
    value_column = (
        "critical_path_frequency_pct"
        if "critical_path_frequency_pct" in chart_df.columns
        else chart_df.columns[1]
    )

    figure = go.Figure(
        go.Bar(
            x=chart_df[value_column],
            y=chart_df[label_column],
            orientation="h",
            marker_color="#ea580c",
            hovertemplate="%{y}: %{x}%<extra></extra>",
        )
    )
    figure.update_layout(
        title="Top Delay Drivers (Critical-path frequency)",
        xaxis_title="Frequency (%)",
        yaxis_title="",
        template="plotly_white",
        height=420,
        yaxis=dict(autorange="reversed"),
    )
    return figure


def scenario_comparison_chart(scenarios_df: pd.DataFrame) -> go.Figure:
    """Build grouped bar chart for scenario comparison."""
    if scenarios_df.empty:
        return go.Figure()

    figure = go.Figure()
    metric_columns = ["Delay Prob (%)", "P80 (days)", "Mean (days)"]
    color_map = ["#0f766e", "#b91c1c", "#1d4ed8"]

    for index, row in scenarios_df.iterrows():
        figure.add_trace(
            go.Bar(
                name=str(row["Scenario"]),
                x=metric_columns,
                y=[float(row[col]) for col in metric_columns],
                marker_color=color_map[index % len(color_map)],
            )
        )

    figure.update_layout(
        barmode="group",
        title="Scenario Comparison",
        template="plotly_white",
        height=430,
    )
    return figure

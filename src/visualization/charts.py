from __future__ import annotations

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[index : index + 2], 16) for index in (0, 2, 4))


def _blend_hex(start: str, end: str, fraction: float) -> str:
    start_rgb = _hex_to_rgb(start)
    end_rgb = _hex_to_rgb(end)
    channels = [
        round(start_value + (end_value - start_value) * fraction)
        for start_value, end_value in zip(start_rgb, end_rgb)
    ]
    return "#" + "".join(f"{channel:02x}" for channel in channels)


def _bin_index(edges: np.ndarray, value: float) -> int:
    return int(np.clip(np.searchsorted(edges, value, side="right") - 1, 0, len(edges) - 2))


def completion_histogram(
    completion_times: np.ndarray,
    deadline: float,
    p50: float,
    p80: float,
) -> go.Figure:
    """Build histogram for completion-time distribution."""
    values = np.asarray(completion_times, dtype=float)
    if values.size == 0:
        return go.Figure()

    counts, edges = np.histogram(values, bins=10)
    centers = (edges[:-1] + edges[1:]) / 2
    widths = np.diff(edges) * 0.66

    p50_index = _bin_index(edges, p50)
    p80_index = _bin_index(edges, p80)
    deadline_index = _bin_index(edges, deadline)

    edge_blue = "#3568ff"
    peak_cyan = "#25e6ff"
    accent_blue = "#59b7ff"
    coral = "#e6684b"
    gold = "#c88b16"

    normalized_counts = counts / max(float(counts.max()), 1.0)
    base_colors = [
        _blend_hex(
            edge_blue,
            peak_cyan,
            min(1.0, 0.24 + (float(level) ** 0.72) * 0.76),
        )
        for level in normalized_counts
    ]
    bar_colors = base_colors

    customdata = np.column_stack((edges[:-1], edges[1:]))

    figure = go.Figure(
        go.Bar(
            x=centers,
            y=counts,
            width=widths,
            marker=dict(
                color=bar_colors,
                line=dict(color="rgba(0,0,0,0)", width=0),
                cornerradius=12,
            ),
            customdata=customdata,
            hovertemplate=(
                "Completion window %{customdata[0]:.1f}-%{customdata[1]:.1f} days"
                "<br>Simulations %{y}<extra></extra>"
            ),
            name="Simulated completion",
            showlegend=False,
        )
    )

    # Add legend chips matching the prototype styling.
    figure.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=10, color=accent_blue),
            name="P50 anchor",
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=10, color=coral),
            name="P80 anchor",
            hoverinfo="skip",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=10, color=gold),
            name="Deadline",
            hoverinfo="skip",
        )
    )

    max_count = float(counts.max()) if counts.size else 1.0
    markers = [
        (p50_index, p50, "P50", accent_blue, 20),
        (p80_index, p80, "P80", coral, 44),
        (deadline_index, deadline, "Deadline", gold, 68),
    ]
    for index, value, label, color, y_shift in markers:
        figure.add_annotation(
            x=float(centers[index]),
            y=float(counts[index]),
            text=f"{label} {value:.1f}d",
            showarrow=False,
            yshift=y_shift,
            font=dict(color="#f4f8ff", size=11),
            bgcolor="rgba(7, 14, 26, 0.92)",
            bordercolor=color,
            borderwidth=1,
            borderpad=6,
        )

    figure.update_layout(
        title="Monte Carlo Completion Distribution",
        xaxis_title="Completion time (days)",
        yaxis_title="Simulation count",
        bargap=0.22,
        barcornerradius=12,
        template="plotly_white",
        height=430,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
        ),
        margin=dict(l=18, r=18, t=88, b=18),
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

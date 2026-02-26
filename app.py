from __future__ import annotations

import json
import logging
from typing import Any

import pandas as pd
import streamlit as st

from src.ai.schema import TaskPlan
from src.ai.task_generator import generate_task_plan
from src.analytics.metrics import compute_metrics
from src.analytics.risk_drivers import rank_delay_drivers
from src.analytics.scenarios import scenario_comparison
from src.config import settings
from src.modeling.critical_path import critical_path_by_mean
from src.modeling.graph_builder import build_project_graph
from src.simulation.monte_carlo import run_monte_carlo
from src.storage.db import init_db
from src.storage.repository import get_run_details, list_recent_runs, save_session_run
from src.utils.errors import GraphValidationError, TaskGenerationError
from src.visualization.charts import (
    completion_histogram,
    dependency_graph_figure,
    risk_drivers_bar,
    scenario_comparison_chart,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("projectsense.app")

st.set_page_config(page_title="ProjectSense AI", layout="wide")


@st.cache_resource
def _initialize_database() -> bool:
    init_db()
    return True


def _init_session_state() -> None:
    defaults = {
        "mode": settings.app_mode,
        "project_text": "",
        "deadline_days": 90.0,
        "iterations": min(settings.default_iterations, settings.max_iterations),
        "max_tasks": settings.max_tasks,
        "seed": 7,
        "run_payload": None,
        "task_editor_df": pd.DataFrame(),
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'IBM Plex Sans', sans-serif;
        }

        .hero-wrap {
            background: linear-gradient(135deg, #ecfeff 0%, #fff7ed 55%, #fefce8 100%);
            border: 1px solid #cbd5e1;
            border-radius: 16px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2rem;
            line-height: 1.1;
            color: #0f172a;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .hero-subtitle {
            color: #334155;
            margin-bottom: 0;
        }

        .risk-badge {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-top: 0.35rem;
        }

        .risk-low {
            background: #dcfce7;
            color: #166534;
            border: 1px solid #86efac;
        }

        .risk-medium {
            background: #fef9c3;
            color: #854d0e;
            border: 1px solid #fde047;
        }

        .risk-high {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
        }

        .kpi-note {
            color: #475569;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _risk_level(delay_probability: float) -> str:
    if delay_probability < 0.25:
        return "LOW"
    if delay_probability < 0.55:
        return "MEDIUM"
    return "HIGH"


def _executive_summary(metrics: dict[str, float], top_driver_name: str | None) -> str:
    risk_level = _risk_level(metrics["delay_probability"])
    driver_text = f" Primary delay driver: {top_driver_name}." if top_driver_name else ""
    return (
        f"Forecast: {metrics['delay_probability'] * 100:.1f}% probability of missing the deadline "
        f"(risk level: {risk_level}). Recommended commitment date: {metrics['p80']:.1f} days (P80)."
        f"{driver_text}"
    )


def _tasks_to_editor_df(tasks: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for task in tasks:
        rows.append(
            {
                "id": task["id"],
                "name": task["name"],
                "mean_duration": float(task["mean_duration"]),
                "std_dev": float(task["std_dev"]),
                "dependencies": ", ".join(task.get("dependencies", [])),
                "risk_factor": float(task["risk_factor"]),
            }
        )
    return pd.DataFrame(rows)


def _parse_dependencies(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [dep.strip() for dep in text.split(",") if dep.strip()]


def _editor_df_to_tasks(df: pd.DataFrame) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        task = {
            "id": str(row["id"]).strip(),
            "name": str(row["name"]).strip(),
            "mean_duration": float(row["mean_duration"]),
            "std_dev": float(row["std_dev"]),
            "dependencies": _parse_dependencies(row["dependencies"]),
            "risk_factor": float(row["risk_factor"]),
        }
        tasks.append(task)

    TaskPlan.model_validate({"tasks": tasks})
    return tasks


def _run_analysis(
    tasks: list[dict[str, Any]],
    deadline_days: float,
    iterations: int,
    seed: int | None,
) -> dict[str, Any]:
    graph = build_project_graph(tasks)
    critical_path, critical_path_days = critical_path_by_mean(graph)

    completion = run_monte_carlo(graph, iterations=iterations, seed=seed)
    metrics = compute_metrics(completion, deadline_days)
    drivers = rank_delay_drivers(
        graph,
        iterations=min(500, iterations),
        seed=seed,
    )
    scenarios_df = scenario_comparison(
        build_project_graph,
        tasks,
        deadline_days=deadline_days,
        iterations=iterations,
        seed=seed,
    )

    return {
        "graph": graph,
        "critical_path": critical_path,
        "critical_path_days": critical_path_days,
        "completion": completion,
        "metrics": metrics,
        "drivers": drivers,
        "scenarios_df": scenarios_df,
    }


def _save_run(payload: dict[str, Any]) -> None:
    try:
        run_id = save_session_run(
            project_text=payload["project_text"],
            mode=payload["mode"],
            params={
                "max_tasks": payload["max_tasks"],
                "min_duration": settings.min_duration,
                "groq_model": settings.groq_model,
            },
            tasks=payload["tasks"],
            deadline_days=payload["deadline_days"],
            iterations=payload["iterations"],
            seed=payload["seed"],
            metrics=payload["metrics"],
            completion_times=payload["completion"],
            scenarios_df=payload["scenarios_df"],
        )
        logger.info("saved_simulation_run run_id=%s", run_id)
    except Exception as exc:  # noqa: BLE001
        logger.exception("failed_to_save_simulation_run error=%s", exc)
        st.warning("Run completed, but saving to SQLite failed. Check logs for details.")


def _set_run_payload(
    tasks: list[dict[str, Any]],
    project_text: str,
    mode: str,
    deadline_days: float,
    iterations: int,
    max_tasks: int,
    seed: int | None,
    analysis: dict[str, Any],
) -> None:
    st.session_state.run_payload = {
        "tasks": tasks,
        "project_text": project_text,
        "mode": mode,
        "deadline_days": deadline_days,
        "iterations": iterations,
        "max_tasks": max_tasks,
        "seed": seed,
        **analysis,
    }
    st.session_state.task_editor_df = _tasks_to_editor_df(tasks)


_init_session_state()
_inject_styles()

try:
    _initialize_database()
except Exception as exc:  # noqa: BLE001
    st.error(f"Database initialization failed: {exc}")

st.markdown(
    """
    <div class="hero-wrap">
      <div class="hero-title">ProjectSense AI</div>
      <p class="hero-subtitle">
        AI-assisted project planning with workflow reasoning, Monte Carlo risk forecasting,
        and scenario decision support.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Planning Inputs")
    st.selectbox("Mode", options=["mock", "real"], key="mode")

    if st.session_state.mode == "real" and not settings.groq_api_key:
        st.error("GROQ_API_KEY is missing. Add it to .env or Streamlit secrets.")

    st.text_area(
        "Project description",
        key="project_text",
        height=140,
        placeholder="Example: Build a mobile app MVP with authentication, payments, and analytics.",
    )
    st.number_input("Deadline (days)", min_value=1.0, step=1.0, key="deadline_days")
    st.number_input(
        "Simulation runs",
        min_value=200,
        max_value=settings.max_iterations,
        step=100,
        key="iterations",
    )
    st.number_input("Max tasks", min_value=8, max_value=18, step=1, key="max_tasks")
    st.number_input("Random seed", min_value=0, max_value=100_000, step=1, key="seed")

    run_button = st.button("Generate & Simulate", type="primary", use_container_width=True)

if run_button:
    project_text = st.session_state.project_text.strip()
    if not project_text:
        st.error("Project description is required.")
    else:
        try:
            logger.info("starting_generation mode=%s", st.session_state.mode)
            with st.spinner("Generating task plan..."):
                plan = generate_task_plan(
                    project_text,
                    max_tasks=int(st.session_state.max_tasks),
                    mode=st.session_state.mode,
                )
                tasks = [task.model_dump() for task in plan.tasks]

            with st.spinner("Running risk simulation..."):
                analysis = _run_analysis(
                    tasks=tasks,
                    deadline_days=float(st.session_state.deadline_days),
                    iterations=int(st.session_state.iterations),
                    seed=int(st.session_state.seed),
                )

            _set_run_payload(
                tasks=tasks,
                project_text=project_text,
                mode=st.session_state.mode,
                deadline_days=float(st.session_state.deadline_days),
                iterations=int(st.session_state.iterations),
                max_tasks=int(st.session_state.max_tasks),
                seed=int(st.session_state.seed),
                analysis=analysis,
            )
            _save_run(st.session_state.run_payload)
            st.success("Plan generated and simulation completed.")
        except TaskGenerationError as exc:
            st.error(str(exc))
        except GraphValidationError as exc:
            st.error(f"Generated task graph is invalid: {exc}")
        except Exception as exc:  # noqa: BLE001
            logger.exception("run_failed error=%s", exc)
            st.error(f"Unexpected error: {exc}")

payload = st.session_state.run_payload

tab_exec, tab_plan, tab_workflow, tab_risk, tab_scenarios, tab_history = st.tabs(
    [
        "Executive Brief",
        "Task Plan",
        "Workflow",
        "Risk Dashboard",
        "Scenario Lab",
        "History & Export",
    ]
)

if not payload:
    with tab_exec:
        st.info("Enter a project description and click Generate & Simulate to start.")
else:
    metrics = payload["metrics"]
    drivers = payload["drivers"]
    scenarios_df = payload["scenarios_df"]
    top_driver = drivers[0]["task_name"] if drivers else None
    risk_level = _risk_level(metrics["delay_probability"])

    with tab_exec:
        st.subheader("Executive Forecast")
        st.markdown(
            f"<span class='risk-badge risk-{risk_level.lower()}'>Risk Level: {risk_level}</span>",
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Delay Probability", f"{metrics['delay_probability'] * 100:.1f}%")
        col2.metric("P80 Commitment", f"{metrics['p80']:.1f} days")
        col3.metric("P50", f"{metrics['p50']:.1f} days")
        col4.metric("Mean Completion", f"{metrics['mean']:.1f} days")

        st.markdown(_executive_summary(metrics, top_driver))
        st.caption(
            "Use the Scenario Lab to test mitigation options before committing the project schedule."
        )

    with tab_plan:
        st.subheader("Editable Task Plan")
        editor_df = st.data_editor(
            st.session_state.task_editor_df,
            hide_index=True,
            use_container_width=True,
            key="task_editor",
            column_config={
                "id": st.column_config.TextColumn("Task ID", disabled=True),
                "name": st.column_config.TextColumn("Task Name", required=True),
                "mean_duration": st.column_config.NumberColumn(
                    "Mean Duration (days)", min_value=1.0, step=0.5
                ),
                "std_dev": st.column_config.NumberColumn(
                    "Std Dev", min_value=0.0, step=0.25
                ),
                "dependencies": st.column_config.TextColumn(
                    "Dependencies (comma-separated task IDs)",
                ),
                "risk_factor": st.column_config.NumberColumn(
                    "Risk Factor", min_value=0.0, max_value=1.0, step=0.05
                ),
            },
        )

        if st.button("Recalculate with Edited Tasks", type="secondary"):
            try:
                edited_tasks = _editor_df_to_tasks(editor_df)
                analysis = _run_analysis(
                    tasks=edited_tasks,
                    deadline_days=float(st.session_state.deadline_days),
                    iterations=int(st.session_state.iterations),
                    seed=int(st.session_state.seed),
                )
                _set_run_payload(
                    tasks=edited_tasks,
                    project_text=payload["project_text"],
                    mode=payload["mode"],
                    deadline_days=float(st.session_state.deadline_days),
                    iterations=int(st.session_state.iterations),
                    max_tasks=int(st.session_state.max_tasks),
                    seed=int(st.session_state.seed),
                    analysis=analysis,
                )
                _save_run(st.session_state.run_payload)
                st.success("Simulation refreshed with edited tasks.")
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                st.error(f"Cannot recompute using edited tasks: {exc}")

    with tab_workflow:
        st.subheader("Workflow Graph & Critical Path")
        graph_figure = dependency_graph_figure(payload["graph"], payload["critical_path"])
        st.plotly_chart(graph_figure, use_container_width=True)

        st.code(" -> ".join(payload["critical_path"]))
        st.metric("Baseline Critical Path (mean)", f"{payload['critical_path_days']:.1f} days")

    with tab_risk:
        st.subheader("Risk Forecast Dashboard")

        histogram = completion_histogram(
            payload["completion"],
            payload["deadline_days"],
            payload["metrics"]["p50"],
            payload["metrics"]["p80"],
        )
        st.plotly_chart(histogram, use_container_width=True)

        drivers_df = pd.DataFrame(drivers)
        if drivers_df.empty:
            st.info("No delay drivers available.")
        else:
            st.dataframe(drivers_df.head(10), use_container_width=True, hide_index=True)
            st.plotly_chart(risk_drivers_bar(drivers_df.head(10)), use_container_width=True)

    with tab_scenarios:
        st.subheader("Scenario Decision Lab")
        st.dataframe(scenarios_df, use_container_width=True, hide_index=True)
        st.plotly_chart(scenario_comparison_chart(scenarios_df), use_container_width=True)

        best_row = scenarios_df.loc[scenarios_df["Delay Prob (%)"].idxmin()]
        st.markdown(
            f"**Recommended scenario:** {best_row['Scenario']} "
            f"(lowest delay risk: {best_row['Delay Prob (%)']:.1f}%)."
        )

with tab_history:
    st.subheader("Session History")
    recent_runs = list_recent_runs(limit=20)

    if not recent_runs:
        st.info("No saved sessions yet.")
    else:
        history_df = pd.DataFrame(recent_runs)
        history_df["delay_probability"] = (history_df["delay_probability"] * 100.0).round(1)
        history_df = history_df.rename(
            columns={
                "simulation_run_id": "Run ID",
                "project_text": "Project",
                "mode": "Mode",
                "created_at": "Created",
                "deadline_days": "Deadline (days)",
                "iterations": "Iterations",
                "delay_probability": "Delay Prob (%)",
                "p80": "P80",
            }
        )
        st.dataframe(history_df, use_container_width=True, hide_index=True)

        run_options = {
            f"Run {row['simulation_run_id']} | {row['created_at']} | {row['project_text'][:56]}": row[
                "simulation_run_id"
            ]
            for row in recent_runs
        }
        selected_label = st.selectbox("Select a saved run", options=list(run_options.keys()))

        if st.button("Load Selected Run"):
            run_id = run_options[selected_label]
            details = get_run_details(run_id)
            if details is None:
                st.error("Selected run could not be loaded.")
            else:
                try:
                    analysis = _run_analysis(
                        tasks=details["tasks"],
                        deadline_days=float(details["deadline_days"]),
                        iterations=int(details["iterations"]),
                        seed=details["seed"],
                    )
                    _set_run_payload(
                        tasks=details["tasks"],
                        project_text=details["project_text"],
                        mode=details["mode"],
                        deadline_days=float(details["deadline_days"]),
                        iterations=int(details["iterations"]),
                        max_tasks=int(details.get("params", {}).get("max_tasks", settings.max_tasks)),
                        seed=details["seed"],
                        analysis=analysis,
                    )
                    st.session_state.project_text = details["project_text"]
                    st.session_state.mode = details["mode"]
                    st.session_state.deadline_days = float(details["deadline_days"])
                    st.session_state.iterations = int(details["iterations"])
                    st.session_state.seed = int(details["seed"] or 0)
                    st.success(f"Loaded run {run_id}.")
                    st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Failed to load run: {exc}")

    st.subheader("Export")
    if payload:
        tasks_df = pd.DataFrame(payload["tasks"])
        scenarios_df = payload["scenarios_df"].copy()
        drivers_df = pd.DataFrame(payload["drivers"])

        export_json = {
            "project_text": payload["project_text"],
            "mode": payload["mode"],
            "deadline_days": payload["deadline_days"],
            "iterations": payload["iterations"],
            "seed": payload["seed"],
            "critical_path": payload["critical_path"],
            "critical_path_days": payload["critical_path_days"],
            "metrics": payload["metrics"],
            "drivers": payload["drivers"],
            "scenarios": scenarios_df.to_dict(orient="records"),
        }

        st.download_button(
            "Download Tasks CSV",
            data=tasks_df.to_csv(index=False).encode("utf-8"),
            file_name="task_plan.csv",
            mime="text/csv",
        )
        st.download_button(
            "Download Scenarios CSV",
            data=scenarios_df.to_csv(index=False).encode("utf-8"),
            file_name="scenario_comparison.csv",
            mime="text/csv",
        )
        st.download_button(
            "Download Drivers CSV",
            data=drivers_df.to_csv(index=False).encode("utf-8"),
            file_name="risk_drivers.csv",
            mime="text/csv",
        )
        st.download_button(
            "Download Full Run JSON",
            data=json.dumps(export_json, indent=2).encode("utf-8"),
            file_name="projectsense_run.json",
            mime="application/json",
        )
    else:
        st.caption("Generate one run to enable export files.")

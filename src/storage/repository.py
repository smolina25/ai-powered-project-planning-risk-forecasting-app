from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from src.storage.db import get_connection


def _to_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=True)


def _from_json(payload: str | None, fallback: Any) -> Any:
    if not payload:
        return fallback
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return fallback


def save_session_run(
    project_text: str,
    mode: str,
    params: dict[str, Any],
    tasks: Sequence[dict[str, Any]],
    deadline_days: float,
    iterations: int,
    seed: int | None,
    metrics: dict[str, Any],
    completion_times: np.ndarray,
    scenarios_df: pd.DataFrame,
) -> int:
    """Persist one project planning and simulation run."""
    completion_summary = {
        "count": int(completion_times.size),
        "min": float(np.min(completion_times)) if completion_times.size else 0.0,
        "max": float(np.max(completion_times)) if completion_times.size else 0.0,
        "mean": float(np.mean(completion_times)) if completion_times.size else 0.0,
        "std": float(np.std(completion_times)) if completion_times.size else 0.0,
        "p50": float(np.percentile(completion_times, 50)) if completion_times.size else 0.0,
        "p80": float(np.percentile(completion_times, 80)) if completion_times.size else 0.0,
    }

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO projects (project_text, mode, params_json)
            VALUES (?, ?, ?)
            """,
            (project_text, mode, _to_json(params)),
        )
        project_id = int(cursor.lastrowid)

        connection.execute(
            """
            INSERT INTO plans (project_id, tasks_json)
            VALUES (?, ?)
            """,
            (project_id, _to_json(list(tasks))),
        )

        sim_cursor = connection.execute(
            """
            INSERT INTO simulation_runs (
                project_id,
                deadline_days,
                iterations,
                seed,
                metrics_json,
                completion_summary_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                float(deadline_days),
                int(iterations),
                seed,
                _to_json(metrics),
                _to_json(completion_summary),
            ),
        )
        simulation_run_id = int(sim_cursor.lastrowid)

        for row in scenarios_df.to_dict(orient="records"):
            scenario_name = str(row.get("Scenario", "Scenario"))
            connection.execute(
                """
                INSERT INTO scenario_runs (simulation_run_id, scenario_name, metrics_json)
                VALUES (?, ?, ?)
                """,
                (simulation_run_id, scenario_name, _to_json(row)),
            )

        connection.commit()
        return simulation_run_id


def list_recent_runs(limit: int = 20) -> list[dict[str, Any]]:
    query = """
        SELECT
            s.id AS simulation_run_id,
            s.project_id AS project_id,
            p.project_text AS project_text,
            p.mode AS mode,
            p.created_at AS created_at,
            s.deadline_days AS deadline_days,
            s.iterations AS iterations,
            s.metrics_json AS metrics_json
        FROM simulation_runs s
        JOIN projects p ON p.id = s.project_id
        ORDER BY s.created_at DESC, s.id DESC
        LIMIT ?
    """

    with get_connection() as connection:
        rows = connection.execute(query, (int(limit),)).fetchall()

    results: list[dict[str, Any]] = []
    for row in rows:
        metrics = _from_json(row["metrics_json"], {})
        results.append(
            {
                "simulation_run_id": int(row["simulation_run_id"]),
                "project_id": int(row["project_id"]),
                "project_text": str(row["project_text"]),
                "mode": str(row["mode"]),
                "created_at": str(row["created_at"]),
                "deadline_days": float(row["deadline_days"]),
                "iterations": int(row["iterations"]),
                "delay_probability": float(metrics.get("delay_probability", 0.0)),
                "p80": float(metrics.get("p80", 0.0)),
            }
        )

    return results


def get_run_details(simulation_run_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        run_row = connection.execute(
            """
            SELECT
                s.id AS simulation_run_id,
                s.project_id AS project_id,
                s.deadline_days AS deadline_days,
                s.iterations AS iterations,
                s.seed AS seed,
                s.metrics_json AS metrics_json,
                s.completion_summary_json AS completion_summary_json,
                p.project_text AS project_text,
                p.mode AS mode,
                p.params_json AS params_json,
                p.created_at AS created_at
            FROM simulation_runs s
            JOIN projects p ON p.id = s.project_id
            WHERE s.id = ?
            """,
            (int(simulation_run_id),),
        ).fetchone()

        if run_row is None:
            return None

        plan_row = connection.execute(
            """
            SELECT tasks_json
            FROM plans
            WHERE project_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (int(run_row["project_id"]),),
        ).fetchone()

        scenario_rows = connection.execute(
            """
            SELECT scenario_name, metrics_json
            FROM scenario_runs
            WHERE simulation_run_id = ?
            ORDER BY id ASC
            """,
            (int(simulation_run_id),),
        ).fetchall()

    tasks = _from_json(plan_row["tasks_json"], []) if plan_row is not None else []
    scenarios = [_from_json(row["metrics_json"], {}) for row in scenario_rows]

    return {
        "simulation_run_id": int(run_row["simulation_run_id"]),
        "project_id": int(run_row["project_id"]),
        "project_text": str(run_row["project_text"]),
        "mode": str(run_row["mode"]),
        "created_at": str(run_row["created_at"]),
        "deadline_days": float(run_row["deadline_days"]),
        "iterations": int(run_row["iterations"]),
        "seed": int(run_row["seed"]) if run_row["seed"] is not None else None,
        "params": _from_json(run_row["params_json"], {}),
        "metrics": _from_json(run_row["metrics_json"], {}),
        "completion_summary": _from_json(run_row["completion_summary_json"], {}),
        "tasks": tasks,
        "scenarios": scenarios,
    }

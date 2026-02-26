from __future__ import annotations

import sqlite3
from pathlib import Path

from src.config import settings


def _resolve_db_path(db_path: str | None = None) -> Path:
    path = Path(db_path or settings.sqlite_db_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    path = _resolve_db_path(db_path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def init_db(db_path: str | None = None) -> None:
    schema_statements = [
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_text TEXT NOT NULL,
            mode TEXT NOT NULL,
            params_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            tasks_json TEXT NOT NULL,
            generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS simulation_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            deadline_days REAL NOT NULL,
            iterations INTEGER NOT NULL,
            seed INTEGER,
            metrics_json TEXT NOT NULL,
            completion_summary_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS scenario_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simulation_run_id INTEGER NOT NULL,
            scenario_name TEXT NOT NULL,
            metrics_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (simulation_run_id) REFERENCES simulation_runs(id) ON DELETE CASCADE
        );
        """,
        "CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_sim_runs_project ON simulation_runs(project_id);",
        "CREATE INDEX IF NOT EXISTS idx_scenario_run_sim ON scenario_runs(simulation_run_id);",
    ]

    with get_connection(db_path) as connection:
        for statement in schema_statements:
            connection.execute(statement)
        connection.commit()

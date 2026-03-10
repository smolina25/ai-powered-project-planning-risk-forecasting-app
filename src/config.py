from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _to_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def _to_float(value: str | None, default: float) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError:
        return default


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


@dataclass(frozen=True)
class Settings:
    app_mode: str = os.getenv("APP_MODE", "mock").strip().lower()  # "real" or "mock"
    demo_default_mode: str = os.getenv("DEMO_DEFAULT_MODE", "mock").strip().lower()
    groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

    default_iterations: int = _to_int(os.getenv("DEFAULT_ITERATIONS"), 1000)
    max_iterations: int = _to_int(os.getenv("MAX_ITERATIONS"), 2000)
    max_tasks: int = _to_int(os.getenv("MAX_TASKS"), 12)
    min_duration: float = _to_float(os.getenv("MIN_DURATION"), 0.1)
    groq_timeout_seconds: float = _to_float(os.getenv("GROQ_TIMEOUT_SECONDS"), 30.0)
    groq_max_retries: int = _to_int(os.getenv("GROQ_MAX_RETRIES"), 2)
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "data/app.db").strip()
    risk_model_enabled: bool = _to_bool(os.getenv("RISK_MODEL_ENABLED"), True)
    risk_model_path: str = os.getenv("RISK_MODEL_PATH", "models/risk_classifier.joblib").strip()
    risk_model_metrics_path: str = os.getenv(
        "RISK_MODEL_METRICS_PATH",
        "models/risk_model_metrics.json",
    ).strip()
    risk_model_version: str = os.getenv("RISK_MODEL_VERSION", "v1-advisory-multimodel").strip()

    def validate(self) -> None:
        if self.app_mode not in {"real", "mock"}:
            raise ValueError("APP_MODE must be either 'real' or 'mock'.")
        if self.demo_default_mode not in {"real", "mock"}:
            raise ValueError("DEMO_DEFAULT_MODE must be either 'real' or 'mock'.")
        if self.default_iterations <= 0:
            raise ValueError("DEFAULT_ITERATIONS must be greater than 0.")
        if self.max_iterations <= 0:
            raise ValueError("MAX_ITERATIONS must be greater than 0.")
        if self.max_tasks < 8:
            raise ValueError("MAX_TASKS must be at least 8.")
        if self.min_duration <= 0:
            raise ValueError("MIN_DURATION must be greater than 0.")
        if self.groq_max_retries < 0:
            raise ValueError("GROQ_MAX_RETRIES cannot be negative.")
        if not self.sqlite_db_path:
            raise ValueError("SQLITE_DB_PATH cannot be empty.")
        if not self.risk_model_path:
            raise ValueError("RISK_MODEL_PATH cannot be empty.")
        if not self.risk_model_metrics_path:
            raise ValueError("RISK_MODEL_METRICS_PATH cannot be empty.")
        if not self.risk_model_version:
            raise ValueError("RISK_MODEL_VERSION cannot be empty.")

    @property
    def sqlite_db_file(self) -> Path:
        return Path(self.sqlite_db_path)

    @property
    def risk_model_path_file(self) -> Path:
        return Path(self.risk_model_path)

    @property
    def risk_model_metrics_file(self) -> Path:
        return Path(self.risk_model_metrics_path)


settings = Settings()
settings.validate()

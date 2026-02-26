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


@dataclass(frozen=True)
class Settings:
    app_mode: str = os.getenv("APP_MODE", "mock").strip().lower()  # "real" or "mock"
    groq_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

    default_iterations: int = _to_int(os.getenv("DEFAULT_ITERATIONS"), 1000)
    max_iterations: int = _to_int(os.getenv("MAX_ITERATIONS"), 2000)
    max_tasks: int = _to_int(os.getenv("MAX_TASKS"), 12)
    min_duration: float = _to_float(os.getenv("MIN_DURATION"), 0.1)
    groq_timeout_seconds: float = _to_float(os.getenv("GROQ_TIMEOUT_SECONDS"), 30.0)
    groq_max_retries: int = _to_int(os.getenv("GROQ_MAX_RETRIES"), 2)
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "data/app.db").strip()

    def validate(self) -> None:
        if self.app_mode not in {"real", "mock"}:
            raise ValueError("APP_MODE must be either 'real' or 'mock'.")
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

    @property
    def sqlite_db_file(self) -> Path:
        return Path(self.sqlite_db_path)


settings = Settings()
settings.validate()

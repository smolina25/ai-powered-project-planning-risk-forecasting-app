from __future__ import annotations

import json
import logging
import re
import time

from src.ai.llm_client import get_groq_client
from src.ai.mock_data import mock_task_plan
from src.ai.prompt import build_task_generation_prompt
from src.ai.schema import TaskPlan
from src.config import settings
from src.utils.errors import TaskGenerationError

logger = logging.getLogger(__name__)


def _extract_json_object(text: str) -> dict:
    candidate = text.strip()
    if not candidate:
        raise json.JSONDecodeError("Empty response content.", "", 0)

    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?", "", candidate, flags=re.IGNORECASE).strip()
        candidate = re.sub(r"```$", "", candidate).strip()

    # Groq sometimes prefixes prose even with JSON mode enabled.
    candidate = re.sub(r"^[^{]*", "", candidate, count=1).strip()

    if not candidate.startswith("{"):
        start = candidate.find("{")
        if start >= 0:
            candidate = candidate[start:]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Best-effort bracket extraction fallback.
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        snippet = candidate[start : end + 1]
        return json.loads(snippet)


def _build_user_friendly_error(exc: Exception) -> str:
    if isinstance(exc, json.JSONDecodeError):
        return (
            "The model returned malformed JSON. Please rerun once, reduce max tasks, "
            "or switch to mock mode for the demo."
        )
    return (
        "Task generation failed. Please verify GROQ_API_KEY/GROQ_MODEL and try again. "
        f"Technical detail: {exc}"
    )


def _generate_once(prompt: str) -> TaskPlan:
    client = get_groq_client()
    response = client.chat.completions.create(
        model=settings.groq_model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Return only valid JSON. Do not include markdown."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        timeout=settings.groq_timeout_seconds,
    )
    content = response.choices[0].message.content or ""
    data = _extract_json_object(content)
    return TaskPlan.model_validate(data)


def generate_task_plan(
    project_description: str,
    max_tasks: int = 12,
    mode: str | None = None,
) -> TaskPlan:
    clean_description = project_description.strip()
    if not clean_description:
        raise TaskGenerationError("Project description cannot be empty.")

    active_mode = (mode or settings.app_mode).strip().lower()
    if active_mode not in {"real", "mock"}:
        raise TaskGenerationError(f"Unsupported app mode: {active_mode}")

    if active_mode == "mock":
        return TaskPlan.model_validate(mock_task_plan())

    prompt = build_task_generation_prompt(clean_description, max_tasks=max_tasks)

    attempts = settings.groq_max_retries + 1
    last_exc: Exception | None = None

    for attempt in range(1, attempts + 1):
        try:
            return _generate_once(prompt)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            logger.warning(
                "task_generation_attempt_failed",
                extra={"attempt": attempt, "max_attempts": attempts, "error": str(exc)},
            )
            if attempt < attempts:
                time.sleep(0.8 * attempt)

    assert last_exc is not None
    message = _build_user_friendly_error(last_exc)
    raise TaskGenerationError(message) from last_exc

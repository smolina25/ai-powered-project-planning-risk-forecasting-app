from __future__ import annotations

import pytest

from src.ai.task_generator import generate_task_plan
from src.utils.errors import TaskGenerationError


def test_mock_mode_end_to_end_generation() -> None:
    plan = generate_task_plan("Build a CRM rollout plan", max_tasks=12, mode="mock")
    assert len(plan.tasks) >= 8
    assert plan.tasks[0].id == "T1"


def test_real_mode_missing_client_fails_gracefully(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise() -> None:
        raise RuntimeError("missing API key")

    monkeypatch.setattr("src.ai.task_generator.get_groq_client", _raise)

    with pytest.raises(TaskGenerationError) as exc_info:
        generate_task_plan("Build a CRM rollout plan", max_tasks=10, mode="real")

    assert "Task generation failed" in str(exc_info.value)

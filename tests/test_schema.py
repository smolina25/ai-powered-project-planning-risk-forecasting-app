from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.ai.schema import TaskPlan


BASE_PLAN = {
    "tasks": [
        {
            "id": "T1",
            "name": "Discovery",
            "mean_duration": 5,
            "std_dev": 1,
            "dependencies": [],
            "risk_factor": 0.2,
        },
        {
            "id": "T2",
            "name": "Build",
            "mean_duration": 8,
            "std_dev": 2,
            "dependencies": ["T1"],
            "risk_factor": 0.4,
        },
    ]
}


def test_valid_plan_passes_schema() -> None:
    plan = TaskPlan.model_validate(BASE_PLAN)
    assert len(plan.tasks) == 2


def test_duplicate_ids_fail_validation() -> None:
    bad = {
        "tasks": [
            {**BASE_PLAN["tasks"][0]},
            {**BASE_PLAN["tasks"][1], "id": "T1"},
        ]
    }
    with pytest.raises(ValidationError):
        TaskPlan.model_validate(bad)


def test_non_sequential_ids_fail_validation() -> None:
    bad = {
        "tasks": [
            {**BASE_PLAN["tasks"][0]},
            {**BASE_PLAN["tasks"][1], "id": "T3", "dependencies": ["T1"]},
        ]
    }
    with pytest.raises(ValidationError):
        TaskPlan.model_validate(bad)


def test_invalid_dependency_order_fails_validation() -> None:
    bad = {
        "tasks": [
            {
                "id": "T1",
                "name": "Discovery",
                "mean_duration": 5,
                "std_dev": 1,
                "dependencies": ["T2"],
                "risk_factor": 0.2,
            },
            {
                "id": "T2",
                "name": "Build",
                "mean_duration": 8,
                "std_dev": 2,
                "dependencies": [],
                "risk_factor": 0.4,
            },
        ]
    }
    with pytest.raises(ValidationError):
        TaskPlan.model_validate(bad)


def test_invalid_risk_factor_fails_validation() -> None:
    bad = {
        "tasks": [
            {
                "id": "T1",
                "name": "Discovery",
                "mean_duration": 5,
                "std_dev": 1,
                "dependencies": [],
                "risk_factor": 1.2,
            }
        ]
    }
    with pytest.raises(ValidationError):
        TaskPlan.model_validate(bad)

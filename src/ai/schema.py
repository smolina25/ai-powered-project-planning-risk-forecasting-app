from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, field_validator


class Task(BaseModel):
    id: str = Field(..., description="Unique task ID like T1, T2...")
    name: str = Field(..., min_length=2, description="Short task name")
    mean_duration: float = Field(..., ge=1, description="Expected duration in days")
    std_dev: float = Field(..., ge=0, description="Standard deviation in days")
    dependencies: List[str] = Field(default_factory=list, description="List of prerequisite task IDs")
    risk_factor: float = Field(..., ge=0, le=1, description="0..1 risk score")

    @field_validator("id")
    @classmethod
    def id_format(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.startswith("T"):
            raise ValueError("Task id must start with 'T' (e.g., T1).")
        return cleaned

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip()


class TaskPlan(BaseModel):
    tasks: List[Task]

    @field_validator("tasks")
    @classmethod
    def unique_and_sequential_ids(cls, tasks: List[Task]) -> List[Task]:
        ids = [task.id for task in tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate task ids found.")

        expected = [f"T{i}" for i in range(1, len(ids) + 1)]
        if ids != expected:
            raise ValueError(f"Task IDs must be sequential starting at T1. Expected {expected}, got {ids}.")

        id_to_index = {task_id: index for index, task_id in enumerate(ids)}
        for task in tasks:
            for dependency in task.dependencies:
                if dependency not in id_to_index:
                    raise ValueError(f"Task {task.id} references unknown dependency: {dependency}.")
                if id_to_index[dependency] >= id_to_index[task.id]:
                    raise ValueError(
                        f"Task {task.id} has invalid dependency {dependency}. "
                        "Dependencies must reference earlier task IDs only."
                    )

        return tasks

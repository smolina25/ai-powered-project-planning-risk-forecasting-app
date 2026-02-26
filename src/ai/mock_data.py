from __future__ import annotations


def mock_task_plan() -> dict:
    return {
        "tasks": [
            {"id": "T1", "name": "Requirements and Scope", "mean_duration": 8, "std_dev": 2, "dependencies": [], "risk_factor": 0.30},
            {"id": "T2", "name": "Project Plan and Milestones", "mean_duration": 6, "std_dev": 1.5, "dependencies": ["T1"], "risk_factor": 0.20},
            {"id": "T3", "name": "Architecture and Design", "mean_duration": 10, "std_dev": 3, "dependencies": ["T1"], "risk_factor": 0.35},
            {"id": "T4", "name": "Core Development", "mean_duration": 18, "std_dev": 6, "dependencies": ["T3"], "risk_factor": 0.45},
            {"id": "T5", "name": "Integrations", "mean_duration": 10, "std_dev": 4, "dependencies": ["T4"], "risk_factor": 0.50},
            {"id": "T6", "name": "Testing and QA", "mean_duration": 12, "std_dev": 4, "dependencies": ["T5"], "risk_factor": 0.55},
            {"id": "T7", "name": "Documentation and Enablement", "mean_duration": 6, "std_dev": 2, "dependencies": ["T4"], "risk_factor": 0.25},
            {"id": "T8", "name": "Release and Handover", "mean_duration": 4, "std_dev": 1, "dependencies": ["T6", "T7"], "risk_factor": 0.20},
        ]
    }

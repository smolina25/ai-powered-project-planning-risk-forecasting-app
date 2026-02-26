def build_task_generation_prompt(project_description: str, max_tasks: int = 12) -> str:
    clean_description = project_description.strip()

    return f"""
You are a senior project planning assistant for a project risk forecasting tool.

Goal:
Generate a project task plan with dependencies and uncertainty estimates suitable for Monte Carlo simulation.

Hard requirements:
- Output ONLY valid JSON. No markdown and no commentary.
- JSON must match this shape exactly:
{{
  "tasks": [
    {{
      "id": "T1",
      "name": "Short Task Name",
      "mean_duration": 10,
      "std_dev": 2,
      "dependencies": [],
      "risk_factor": 0.2
    }}
  ]
}}

Rules:
- Create between 8 and {max_tasks} tasks.
- Task IDs must be sequential starting from T1, T2, T3... with no gaps.
- Dependencies must reference earlier IDs only.
- Ensure the graph is a DAG with no cycles.
- mean_duration is in days and must be realistic (>= 1).
- std_dev should reflect uncertainty (typically 10% to 40% of mean_duration).
- risk_factor is between 0 and 1.
- Use concise task names.

Project description:
{clean_description}
""".strip()

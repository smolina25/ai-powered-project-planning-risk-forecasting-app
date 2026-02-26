from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ai.task_generator import generate_task_plan
from src.analytics.metrics import compute_metrics
from src.modeling.graph_builder import build_project_graph
from src.simulation.monte_carlo import run_monte_carlo


def main() -> None:
    plan = generate_task_plan("Plan a marketing campaign launch", mode="mock")
    tasks = [task.model_dump() for task in plan.tasks]

    graph = build_project_graph(tasks)
    completion = run_monte_carlo(graph, iterations=300, seed=21)
    metrics = compute_metrics(completion, deadline_days=90)

    print("SMOKE TEST PASSED")
    print(f"tasks={len(tasks)} mean={metrics['mean']:.1f} p80={metrics['p80']:.1f}")


if __name__ == "__main__":
    main()

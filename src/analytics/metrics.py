from __future__ import annotations

import numpy as np


Metrics = dict[str, float]


def compute_metrics(completion_times: np.ndarray, deadline_days: float) -> Metrics:
    """Compute core schedule-risk metrics from completion samples."""
    if completion_times.size == 0:
        raise ValueError("completion_times cannot be empty.")

    deadline = float(deadline_days)
    return {
        "mean": float(np.mean(completion_times)),
        "p50": float(np.percentile(completion_times, 50)),
        "p80": float(np.percentile(completion_times, 80)),
        "delay_probability": float(np.mean(completion_times > deadline)),
    }

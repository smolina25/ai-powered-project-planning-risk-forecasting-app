from __future__ import annotations

import numpy as np

from src.analytics.metrics import compute_metrics


def test_compute_metrics_expected_values() -> None:
    samples = np.array([10.0, 12.0, 14.0, 16.0, 20.0])
    metrics = compute_metrics(samples, deadline_days=15.0)

    assert metrics["mean"] == 14.4
    assert metrics["p50"] == 14.0
    assert metrics["p80"] == 16.8
    assert metrics["delay_probability"] == 0.4

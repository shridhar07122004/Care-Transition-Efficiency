"""Isolation Forest anomaly detection for operational metrics."""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


FEATURE_COLS = [
    "transfer_efficiency",
    "discharge_effectiveness",
    "throughput_rate",
    "daily_backlog",
]


def detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    """Flag anomalous operational days using Isolation Forest."""
    result = df.copy()
    features = result[FEATURE_COLS].fillna(0)

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
    )
    predictions = model.fit_predict(features)
    result["anomaly"] = predictions == -1
    result["anomaly_score"] = -model.score_samples(features)
    return result

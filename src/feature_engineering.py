"""Derived metrics and rolling features for UAC analytics."""

import pandas as pd

from .utils import ROLLING_WINDOWS, safe_divide


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add KPI and rolling features to cleaned dataframe."""
    featured = df.copy()

    featured["transfer_efficiency"] = safe_divide(
        featured["transfers"], featured["cbp_custody"]
    )
    featured["discharge_effectiveness"] = safe_divide(
        featured["discharges"], featured["hhs_care"]
    )
    featured["throughput_rate"] = safe_divide(
        featured["discharges"], featured["apprehensions"]
    )
    featured["daily_backlog"] = featured["apprehensions"] - featured["discharges"]
    featured["cumulative_backlog"] = featured["daily_backlog"].cumsum()
    featured["outcome_stability"] = (
        featured["discharge_effectiveness"].rolling(7, min_periods=3).std()
    )

    rolling_cols = [
        "transfers",
        "discharges",
        "daily_backlog",
        "transfer_efficiency",
        "discharge_effectiveness",
        "throughput_rate",
    ]
    for window in ROLLING_WINDOWS:
        for col in rolling_cols:
            featured[f"{col}_ma{window}"] = (
                featured[col].rolling(window, min_periods=1).mean()
            )

    featured["year"] = featured["date"].dt.year
    featured["month"] = featured["date"].dt.month
    featured["year_month"] = featured["date"].dt.to_period("M").astype(str)

    return featured


ROLLING_METRIC_COLS = [
    "transfers",
    "discharges",
    "daily_backlog",
    "transfer_efficiency",
    "discharge_effectiveness",
    "throughput_rate",
]


def refresh_slice_metrics(df: pd.DataFrame, rolling_window: int = 7) -> pd.DataFrame:
    """Recalculate derived metrics for a filtered date slice."""
    refreshed = df.copy().sort_values("date").reset_index(drop=True)
    refreshed["daily_backlog"] = refreshed["apprehensions"] - refreshed["discharges"]
    refreshed["cumulative_backlog"] = refreshed["daily_backlog"].cumsum()
    refreshed["outcome_stability"] = (
        refreshed["discharge_effectiveness"].rolling(7, min_periods=3).std()
    )
    for col in ROLLING_METRIC_COLS:
        refreshed[f"{col}_ma_dynamic"] = (
            refreshed[col].rolling(rolling_window, min_periods=1).mean()
        )
    return refreshed

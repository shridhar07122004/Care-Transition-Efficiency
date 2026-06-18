"""Rule-based bottleneck detection for UAC care pipeline."""

import pandas as pd

from .utils import (
    BACKLOG_STREAK_DAYS,
    DISCHARGE_EFFECTIVENESS_THRESHOLD,
    TRANSFER_EFFICIENCY_THRESHOLD,
)


def _severity(score: float) -> str:
    if score >= 0.7:
        return "High"
    if score >= 0.4:
        return "Medium"
    return "Low"


def detect_bottlenecks(
    df: pd.DataFrame,
    transfer_threshold: float = TRANSFER_EFFICIENCY_THRESHOLD,
    discharge_threshold: float = DISCHARGE_EFFECTIVENESS_THRESHOLD,
    backlog_streak_days: int = BACKLOG_STREAK_DAYS,
) -> list[dict]:
    """Apply bottleneck rules and return alert records."""
    alerts: list[dict] = []
    if df.empty:
        return alerts

    hist_throughput_avg = df["throughput_rate"].mean()

    backlog_increase_streak = 0
    for _, row in df.iterrows():
        date_str = row["date"].strftime("%Y-%m-%d")

        if row["transfer_efficiency"] < transfer_threshold:
            gap = transfer_threshold - row["transfer_efficiency"]
            alerts.append(
                {
                    "date": date_str,
                    "issue": "Transfer Bottleneck",
                    "severity": _severity(gap / max(transfer_threshold, 1e-6)),
                    "metric_value": float(row["transfer_efficiency"]),
                }
            )

        if row["discharge_effectiveness"] < discharge_threshold:
            gap = discharge_threshold - row["discharge_effectiveness"]
            alerts.append(
                {
                    "date": date_str,
                    "issue": "Placement Bottleneck",
                    "severity": _severity(gap / max(discharge_threshold, 1e-6)),
                    "metric_value": float(row["discharge_effectiveness"]),
                }
            )

        if row["daily_backlog"] > 0:
            backlog_increase_streak += 1
        else:
            backlog_increase_streak = 0

        if backlog_increase_streak >= backlog_streak_days:
            alerts.append(
                {
                    "date": date_str,
                    "issue": "Accumulation Risk",
                    "severity": "High",
                    "metric_value": float(row["cumulative_backlog"]),
                }
            )

        if row["throughput_rate"] < hist_throughput_avg:
            gap = hist_throughput_avg - row["throughput_rate"]
            alerts.append(
                {
                    "date": date_str,
                    "issue": "Pipeline Slowdown",
                    "severity": _severity(gap / max(hist_throughput_avg, 1e-6)),
                    "metric_value": float(row["throughput_rate"]),
                }
            )

    return alerts


def get_active_alerts(alerts: list[dict], lookback_days: int = 30) -> list[dict]:
    """Return most recent alerts within lookback window."""
    if not alerts:
        return []
    latest_date = pd.to_datetime(max(a["date"] for a in alerts))
    cutoff = latest_date - pd.Timedelta(days=lookback_days)
    return [a for a in alerts if pd.to_datetime(a["date"]) >= cutoff]

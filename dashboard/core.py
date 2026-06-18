"""Framework-agnostic analytics core for the UAC dashboard."""

import sys
from functools import lru_cache
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.anomaly_detector import detect_anomalies
from src.bottleneck_detector import detect_bottlenecks, get_active_alerts
from src.feature_engineering import engineer_features, refresh_slice_metrics
from src.forecasting import forecast_all
from src.kpi_engine import compute_correlation_matrix, compute_monthly_aggregates, compute_summary_kpis
from src.preprocessing import load_and_clean, validate_data
from src.recommendation_engine import generate_recommendations

METRIC_CATALOG = {
    "apprehensions": {"label": "Apprehensions", "color": "#60a5fa", "fmt": ",.0f"},
    "transfers": {"label": "Transfers", "color": "#34d399", "fmt": ",.0f"},
    "discharges": {"label": "Discharges", "color": "#a78bfa", "fmt": ",.0f"},
    "cbp_custody": {"label": "CBP Custody", "color": "#38bdf8", "fmt": ",.0f"},
    "hhs_care": {"label": "HHS Population", "color": "#2563eb", "fmt": ",.0f"},
    "transfer_efficiency": {"label": "Transfer Efficiency", "color": "#3b82f6", "fmt": ".1%"},
    "discharge_effectiveness": {"label": "Discharge Effectiveness", "color": "#22d3ee", "fmt": ".1%"},
    "throughput_rate": {"label": "Throughput Rate", "color": "#f472b6", "fmt": ".1%"},
    "daily_backlog": {"label": "Daily Backlog", "color": "#f59e0b", "fmt": ",.0f"},
    "cumulative_backlog": {"label": "Cumulative Backlog", "color": "#fb923c", "fmt": ",.0f"},
}

FORECAST_LABELS = {
    "apprehensions": "Future Apprehensions",
    "transfers": "Future Transfers",
    "hhs_care": "Future HHS Population",
    "discharges": "Future Discharges",
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@lru_cache(maxsize=1)
def load_base_data() -> pd.DataFrame:
    return engineer_features(load_and_clean())


def default_config(base_df: pd.DataFrame) -> dict:
    return {
        "start_date": str(base_df["date"].min().date()),
        "end_date": str(base_df["date"].max().date()),
        "years": [int(y) for y in sorted(base_df["year"].unique())],
        "months": list(range(1, 13)),
        "aggregation": "Daily",
        "rolling_window": 7,
        "trend_window": 30,
        "transfer_threshold": 0.5,
        "discharge_threshold": 0.4,
        "backlog_streak": 7,
        "alert_lookback": 30,
        "anomaly_rate": 0.05,
        "forecast_days": 30,
        "trend_metrics": ["apprehensions", "transfers", "discharges"],
        "kpi_metrics": ["transfer_efficiency", "discharge_effectiveness", "throughput_rate"],
        "backlog_metrics": ["hhs_care", "cumulative_backlog"],
        "show_rolling": False,
        "flow_mode": "sum",
        "forecast_metric": "apprehensions",
        "heatmap_metric": "daily_backlog",
        "anomaly_metric": "throughput_rate",
    }


def plotly_layout(height: int = 380, **kwargs) -> dict:
    layout = dict(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        font=dict(family="Inter, Segoe UI, sans-serif", color="#cbd5e1"),
    )
    layout.update(kwargs)
    return layout


def filter_dataframe(base_df: pd.DataFrame, config: dict) -> pd.DataFrame:
    filtered = base_df[
        base_df["year"].isin(config["years"]) & base_df["month"].isin(config["months"])
    ].copy()
    start = pd.Timestamp(config["start_date"]).date()
    end = pd.Timestamp(config["end_date"]).date()
    filtered = filtered[
        (filtered["date"].dt.date >= start) & (filtered["date"].dt.date <= end)
    ]
    return filtered.sort_values("date").reset_index(drop=True)


def aggregate_timeseries(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    if df.empty or config["aggregation"] == "Daily":
        return df

    freq_map = {"Weekly": "W", "Monthly": "ME"}
    freq = freq_map[config["aggregation"]]
    numeric_cols = [
        "apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges",
        "transfer_efficiency", "discharge_effectiveness", "throughput_rate",
        "daily_backlog", "cumulative_backlog",
    ]
    indexed = df.set_index("date")
    agg_rules = {col: "mean" for col in numeric_cols if col in indexed.columns}
    agg_rules.update({
        "apprehensions": "sum", "transfers": "sum", "discharges": "sum", "daily_backlog": "sum",
    })
    resampled = indexed.resample(freq).agg(agg_rules).reset_index()
    resampled["year"] = resampled["date"].dt.year
    resampled["month"] = resampled["date"].dt.month
    resampled["year_month"] = resampled["date"].dt.to_period("M").astype(str)
    return resampled.dropna(subset=["apprehensions"], how="all")


@lru_cache(maxsize=16)
def _compute_forecasts_cached(start: str, end: str, periods: int, row_count: int) -> tuple:
    """Cache forecasts; returns tuple of (metric, json) pairs for hashability."""
    base = load_base_data()
    mask = (base["date"] >= pd.Timestamp(start)) & (base["date"] <= pd.Timestamp(end))
    sliced = base.loc[mask]
    if len(sliced) < 14:
        return tuple()
    results = forecast_all(sliced, periods=periods)
    return tuple((k, v.to_json(date_format="iso")) for k, v in results.items())


def _forecasts_from_cache(cached: tuple) -> dict[str, pd.DataFrame]:
    if not cached:
        return {}
    out = {}
    for k, v in cached:
        fc = pd.read_json(v)
        if "date" in fc.columns:
            fc["date"] = pd.to_datetime(fc["date"])
        out[k] = fc
    return out


def build_dynamic_context(base_df: pd.DataFrame, config: dict) -> dict:
    filtered = filter_dataframe(base_df, config)
    if filtered.empty:
        return {
            "df": filtered, "chart_df": filtered, "config": config,
            "kpis": {}, "monthly": pd.DataFrame(), "correlation": pd.DataFrame(),
            "alerts": [], "active_alerts": [], "forecasts": {},
            "recommendations": {"risk_level": "Low", "risk_score": 0.0, "recommendations": []},
            "validation": {"row_count": 0}, "empty": True,
        }

    df = refresh_slice_metrics(filtered, rolling_window=config["rolling_window"])
    chart_df = aggregate_timeseries(df, config)
    alerts = detect_bottlenecks(
        df,
        transfer_threshold=config["transfer_threshold"],
        discharge_threshold=config["discharge_threshold"],
        backlog_streak_days=config["backlog_streak"],
    )
    active_alerts = get_active_alerts(alerts, lookback_days=config["alert_lookback"])
    df = detect_anomalies(df, contamination=config["anomaly_rate"])
    recommendations = generate_recommendations(
        df, alerts,
        transfer_threshold=config["transfer_threshold"],
        discharge_threshold=config["discharge_threshold"],
        trend_window=config["trend_window"],
    )
    start, end = str(df["date"].min().date()), str(df["date"].max().date())
    forecasts = _forecasts_from_cache(
        _compute_forecasts_cached(start, end, config["forecast_days"], len(df))
    )

    return {
        "df": df, "chart_df": chart_df, "config": config,
        "kpis": compute_summary_kpis(df),
        "monthly": compute_monthly_aggregates(df),
        "correlation": compute_correlation_matrix(df),
        "alerts": alerts, "active_alerts": active_alerts,
        "forecasts": forecasts, "recommendations": recommendations,
        "validation": validate_data(df), "empty": False,
    }


def add_metric_traces(fig: go.Figure, df: pd.DataFrame, metrics: list[str], use_rolling: bool = False):
    for metric in metrics:
        if metric not in METRIC_CATALOG:
            continue
        meta = METRIC_CATALOG[metric]
        col = f"{metric}_ma_dynamic" if use_rolling and f"{metric}_ma_dynamic" in df.columns else metric
        if col not in df.columns:
            continue
        fig.add_trace(go.Scatter(
            x=df["date"], y=df[col], name=meta["label"],
            line=dict(color=meta["color"], width=2),
            hovertemplate=f"{meta['label']}: %{{y}}<extra></extra>",
        ))
    if any(m in {"transfer_efficiency", "discharge_effectiveness", "throughput_rate"} for m in metrics):
        fig.update_layout(yaxis_tickformat=".0%")

"""Aggregate KPI calculations for dashboard and reporting."""

import pandas as pd


def compute_summary_kpis(df: pd.DataFrame) -> dict:
    """Compute executive-level KPI summary."""
    latest = df.iloc[-1]
    return {
        "total_apprehensions": int(df["apprehensions"].sum()),
        "total_transfers": int(df["transfers"].sum()),
        "total_discharges": int(df["discharges"].sum()),
        "avg_transfer_efficiency": float(df["transfer_efficiency"].mean()),
        "avg_discharge_effectiveness": float(df["discharge_effectiveness"].mean()),
        "avg_throughput_rate": float(df["throughput_rate"].mean()),
        "current_backlog": int(latest["cumulative_backlog"]),
        "current_hhs_population": int(latest["hhs_care"]),
        "current_cbp_custody": int(latest["cbp_custody"]),
        "latest_date": latest["date"],
    }


def compute_monthly_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly rollups for trend analysis."""
    monthly = (
        df.groupby("year_month", as_index=False)
        .agg(
            apprehensions=("apprehensions", "sum"),
            transfers=("transfers", "sum"),
            discharges=("discharges", "sum"),
            hhs_care=("hhs_care", "mean"),
            transfer_efficiency=("transfer_efficiency", "mean"),
            discharge_effectiveness=("discharge_effectiveness", "mean"),
            throughput_rate=("throughput_rate", "mean"),
            daily_backlog=("daily_backlog", "sum"),
        )
        .sort_values("year_month")
    )
    return monthly


def compute_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Correlation matrix for key pipeline variables."""
    cols = [
        "apprehensions",
        "transfers",
        "hhs_care",
        "discharges",
        "daily_backlog",
        "transfer_efficiency",
        "discharge_effectiveness",
        "throughput_rate",
    ]
    return df[cols].corr()

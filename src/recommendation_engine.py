"""Automated operational recommendations from pipeline signals."""

import pandas as pd


def _risk_level(score: float) -> str:
    if score >= 0.7:
        return "High"
    if score >= 0.4:
        return "Moderate"
    return "Low"


def generate_recommendations(
    df: pd.DataFrame,
    alerts: list[dict],
    transfer_threshold: float = 0.5,
    discharge_threshold: float = 0.4,
    trend_window: int = 30,
) -> dict:
    """Produce human-readable recommendations from recent trends and alerts."""
    recommendations: list[dict] = []
    if df.empty:
        return {"risk_level": "Low", "risk_score": 0.0, "recommendations": []}

    recent = df.tail(trend_window)
    latest = df.iloc[-1]

    te_trend = recent["transfer_efficiency"].diff().mean()
    if te_trend < 0 or latest["transfer_efficiency"] < transfer_threshold:
        recommendations.append(
            {
                "priority": "High",
                "category": "Transfer Operations",
                "recommendation": (
                    "Increase transfer coordination capacity between CBP and HHS "
                    "to improve movement efficiency."
                ),
                "rationale": (
                    f"Transfer efficiency is {latest['transfer_efficiency']:.1%} "
                    f"with a declining 30-day trend."
                ),
            }
        )

    backlog_trend = recent["cumulative_backlog"].diff().mean()
    if backlog_trend > 0:
        recommendations.append(
            {
                "priority": "High",
                "category": "Capacity Planning",
                "recommendation": (
                    "Allocate additional shelter resources and surge staffing "
                    "to address rising backlog accumulation."
                ),
                "rationale": (
                    f"Cumulative backlog reached {int(latest['cumulative_backlog']):,} "
                    "with sustained positive growth."
                ),
            }
        )

    de_trend = recent["discharge_effectiveness"].diff().mean()
    if de_trend < 0 or latest["discharge_effectiveness"] < discharge_threshold:
        recommendations.append(
            {
                "priority": "High",
                "category": "Placement Outcomes",
                "recommendation": (
                    "Review sponsor placement workflow, vetting timelines, "
                    "and case management throughput."
                ),
                "rationale": (
                    f"Discharge effectiveness is {latest['discharge_effectiveness']:.1%}."
                ),
            }
        )

    throughput_gap = recent["throughput_rate"].mean() - latest["throughput_rate"]
    if throughput_gap > 0.05:
        recommendations.append(
            {
                "priority": "Medium",
                "category": "Pipeline Throughput",
                "recommendation": (
                    "Conduct end-to-end pipeline review to identify stage-specific delays."
                ),
                "rationale": "Throughput is below the recent 30-day average.",
            }
        )

    active_issues = {a["issue"] for a in alerts[-50:]}
    if "Accumulation Risk" in active_issues:
        recommendations.append(
            {
                "priority": "High",
                "category": "Risk Mitigation",
                "recommendation": (
                    "Activate contingency plans for prolonged positive daily backlog streaks."
                ),
                "rationale": "Accumulation risk alerts detected in recent operations.",
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "priority": "Low",
                "category": "Operations",
                "recommendation": (
                    "Maintain current coordination protocols; continue monitoring KPI trends."
                ),
                "rationale": "No critical degradation detected in recent pipeline metrics.",
            }
        )

    risk_score = min(
        1.0,
        (transfer_threshold - float(latest["transfer_efficiency"])) * 0.5
        + (discharge_threshold - float(latest["discharge_effectiveness"])) * 0.5
        + max(0, backlog_trend) * 0.1,
    )
    risk_score = max(0.0, risk_score)

    return {
        "risk_level": _risk_level(risk_score),
        "risk_score": risk_score,
        "recommendations": recommendations,
    }

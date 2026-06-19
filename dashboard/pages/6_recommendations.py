"""Recommendations and risk assessment page."""

import sys
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from shared import (
    apply_theme,
    get_dashboard_context,
    render_page_header,
    render_recommendation_cards,
    render_risk_banner,
    render_section,
)

st.set_page_config(page_title="Recommendations", layout="wide")
apply_theme()
render_page_header(
    "Recommendations & Risk",
    "Actionable insights based on your current filters and thresholds",
    badge="Actions",
)

ctx = get_dashboard_context()
if ctx["empty"]:
    st.warning("No data for the selected filters.")
    st.stop()

df, config, rec_data = ctx["df"], ctx["config"], ctx["recommendations"]

render_risk_banner(rec_data["risk_level"], rec_data["risk_score"])

c1, c2, c3 = st.columns(3)
c1.metric("Active Alerts", len(ctx["active_alerts"]))
c2.metric("Anomalies", int(df["anomaly"].sum()))
c3.metric("Trend Window", f"{config['trend_window']} days")

render_section("Suggested Actions")
render_recommendation_cards(rec_data["recommendations"])

render_section("Live KPI Snapshot")
latest = df.iloc[-1]
c1, c2, c3 = st.columns(3)
c1.metric("Transfer Efficiency", f"{latest['transfer_efficiency']:.1%}")
c2.metric("Discharge Effectiveness", f"{latest['discharge_effectiveness']:.1%}")
c3.metric("Throughput", f"{latest['throughput_rate']:.1%}")

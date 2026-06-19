"""Bottleneck detection and alerts page."""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from shared import METRIC_CATALOG, apply_theme, get_dashboard_context, render_page_header, render_section, themed_plotly_layout

st.set_page_config(page_title="Bottlenecks", layout="wide")
apply_theme()
render_page_header("Bottleneck Detection", "Automated pipeline inefficiency alerts and anomaly tracking", badge="Alerts")

ctx = get_dashboard_context()
if ctx["empty"]:
    st.warning("No data for the selected filters.")
    st.stop()

df, config = ctx["df"], ctx["config"]
active = ctx["active_alerts"]

heatmap_metric = st.selectbox("Heatmap metric", list(METRIC_CATALOG.keys()), index=list(METRIC_CATALOG.keys()).index("daily_backlog"), format_func=lambda m: METRIC_CATALOG[m]["label"])
anomaly_metric = st.selectbox("Anomaly metric", list(METRIC_CATALOG.keys()), index=list(METRIC_CATALOG.keys()).index("throughput_rate"), format_func=lambda m: METRIC_CATALOG[m]["label"])

render_section(f"Active Alerts · last {config['alert_lookback']} days")
if active:
    st.dataframe(pd.DataFrame(active).tail(30).iloc[::-1], use_container_width=True, hide_index=True)
else:
    st.success("No active alerts.")

if ctx["alerts"]:
    timeline = pd.DataFrame(ctx["alerts"]).groupby(["date", "issue"]).size().reset_index(name="count")
    tfig = px.scatter(timeline, x="date", y="issue", size="count", color="issue")
    tfig.update_layout(**themed_plotly_layout(400))
    st.plotly_chart(tfig, use_container_width=True)

df_heat = df.copy()
df_heat["weekday"] = df_heat["date"].dt.day_name()
df_heat["week"] = df_heat["date"].dt.isocalendar().week.astype(int)
pivot = df_heat.pivot_table(index="weekday", columns="week", values=heatmap_metric, aggfunc="mean")
pivot = pivot.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
hfig = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index, colorscale="Blues"))
hfig.update_layout(**themed_plotly_layout(400, title="Operational Heatmap"))
st.plotly_chart(hfig, use_container_width=True)

anomaly_df = df[df["anomaly"]]
afig = go.Figure()
afig.add_trace(go.Scatter(x=df["date"], y=df[anomaly_metric], name=anomaly_metric, line=dict(color="#60a5fa")))
if not anomaly_df.empty:
    afig.add_trace(go.Scatter(x=anomaly_df["date"], y=anomaly_df[anomaly_metric], mode="markers", name="Anomaly", marker=dict(color="#f87171", size=10, symbol="x")))
afig.update_layout(**themed_plotly_layout(350, title="Anomaly Timeline"))
st.plotly_chart(afig, use_container_width=True)

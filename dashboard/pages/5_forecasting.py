"""Forecasting page with Prophet predictions."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from shared import FORECAST_LABELS, apply_theme, get_dashboard_context, render_page_header, render_section, themed_plotly_layout

st.set_page_config(page_title="Forecasting", layout="wide")
apply_theme()
render_page_header("Operational Forecasting", "Prophet predictions with confidence intervals", badge="Forecast")

ctx = get_dashboard_context()
if ctx["empty"]:
    st.warning("No data for the selected filters.")
    st.stop()

df, forecasts, config = ctx["df"], ctx["forecasts"], ctx["config"]
forecast_days = config["forecast_days"]

if not forecasts:
    st.warning("Prophet forecasts unavailable. Install `prophet` and ensure at least 14 days of data.")
    st.stop()

selected = st.selectbox("Metric", list(FORECAST_LABELS.keys()), format_func=lambda k: FORECAST_LABELS[k])
fc = forecasts[selected]
hist = df[["date", selected]].rename(columns={selected: "actual"})
future = fc[fc["date"] > df["date"].max()].head(forecast_days)

fig = go.Figure()
fig.add_trace(go.Scatter(x=hist["date"], y=hist["actual"], name="Historical", line=dict(color="#60a5fa")))
fig.add_trace(go.Scatter(x=future["date"], y=future["yhat"], name="Forecast", line=dict(color="#34d399")))
fig.add_trace(go.Scatter(
    x=pd.concat([future["date"], future["date"].iloc[::-1]]),
    y=pd.concat([future["yhat_upper"], future["yhat_lower"].iloc[::-1]]),
    fill="toself", fillcolor="rgba(52,211,153,0.12)", line=dict(width=0), name="CI",
))
fig.update_layout(**themed_plotly_layout(450, title=FORECAST_LABELS[selected]))
st.plotly_chart(fig, use_container_width=True)

if not future.empty:
    trend = future["yhat"].iloc[-1] - future["yhat"].iloc[0]
    st.info(f"Trend: **{'increasing' if trend > 0 else 'decreasing'}** ({trend:+.0f} over {forecast_days} days)")

cols = st.columns(2)
for i, (metric, fcd) in enumerate(forecasts.items()):
    fut = fcd[fcd["date"] > df["date"].max()].head(forecast_days)
    with cols[i % 2]:
        mini = go.Figure(go.Scatter(x=fut["date"], y=fut["yhat"], line=dict(color="#3b82f6")))
        mini.update_layout(**themed_plotly_layout(250, title=FORECAST_LABELS[metric], margin=dict(l=20, r=20, t=40, b=20)))
        st.plotly_chart(mini, use_container_width=True)

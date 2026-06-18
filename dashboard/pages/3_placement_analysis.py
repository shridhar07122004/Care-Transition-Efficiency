"""Placement outcomes analytics page."""

import plotly.graph_objects as go
import streamlit as st

from shared import apply_theme, get_dashboard_context, render_page_header, themed_plotly_layout

st.set_page_config(page_title="Placement Outcomes", layout="wide")
apply_theme()
render_page_header("Placement Outcomes", "Sponsor discharge effectiveness and outcome stability", badge="Placement")

ctx = get_dashboard_context()
if ctx["empty"]:
    st.warning("No data for the selected filters.")
    st.stop()

df, chart_df, monthly, config = ctx["df"], ctx["chart_df"], ctx["monthly"], ctx["config"]

de_fig = go.Figure()
de_fig.add_trace(go.Scatter(x=chart_df["date"], y=chart_df["discharge_effectiveness"], name="Daily", line=dict(color="#a78bfa")))
if config["show_rolling"]:
    de_fig.add_trace(go.Scatter(x=df["date"], y=df["discharge_effectiveness_ma_dynamic"], name="Rolling Avg", line=dict(color="#34d399")))
de_fig.add_hline(y=config["discharge_threshold"], line_dash="dash", line_color="#f87171")
de_fig.update_layout(**themed_plotly_layout(400, yaxis_tickformat=".0%", title="Discharge Effectiveness"))
st.plotly_chart(de_fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    stab = go.Figure(go.Scatter(x=df["date"], y=df["outcome_stability"], line=dict(color="#f472b6")))
    stab.update_layout(**themed_plotly_layout(350, title="Outcome Stability"))
    st.plotly_chart(stab, use_container_width=True)
with c2:
    if not monthly.empty:
        p = go.Figure()
        p.add_trace(go.Bar(x=monthly["year_month"], y=monthly["discharges"], marker_color="#22c55e", name="Discharges"))
        p.update_layout(**themed_plotly_layout(350, title="Monthly Discharges"))
        st.plotly_chart(p, use_container_width=True)

st.metric("Avg Discharge Effectiveness", f"{df['discharge_effectiveness'].mean():.1%}")

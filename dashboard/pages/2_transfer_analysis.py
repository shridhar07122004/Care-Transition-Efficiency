"""Transfer analytics page."""

import plotly.graph_objects as go
import streamlit as st

from shared import apply_theme, get_dashboard_context, render_page_header, render_section, themed_plotly_layout

st.set_page_config(page_title="Transfer Analytics", layout="wide")
apply_theme()
render_page_header("Transfer Analytics", "CBP → HHS transfer efficiency and volume trends", badge="Transfers")

ctx = get_dashboard_context()
if ctx["empty"]:
    st.warning("No data for the selected filters.")
    st.stop()

df, chart_df, monthly, config = ctx["df"], ctx["chart_df"], ctx["monthly"], ctx["config"]

fig = go.Figure()
fig.add_trace(go.Scatter(x=chart_df["date"], y=chart_df["transfer_efficiency"], name="Daily", line=dict(color="#60a5fa")))
if config["show_rolling"]:
    fig.add_trace(go.Scatter(x=df["date"], y=df["transfer_efficiency_ma_dynamic"], name="Rolling Avg", line=dict(color="#f59e0b")))
fig.add_hline(y=config["transfer_threshold"], line_dash="dash", line_color="#f87171")
fig.update_layout(**themed_plotly_layout(400, yaxis_tickformat=".0%", title="Transfer Efficiency"))
st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    if not monthly.empty:
        m = go.Figure(go.Bar(x=monthly["year_month"], y=monthly["transfers"], marker_color="#3b82f6"))
        m.update_layout(**themed_plotly_layout(350, title="Monthly Transfers"))
        st.plotly_chart(m, use_container_width=True)
with c2:
    if not monthly.empty:
        e = go.Figure(go.Scatter(x=monthly["year_month"], y=monthly["transfer_efficiency"], mode="lines+markers", line=dict(color="#22d3ee")))
        e.update_layout(**themed_plotly_layout(350, yaxis_tickformat=".0%", title="Monthly Efficiency"))
        st.plotly_chart(e, use_container_width=True)

st.metric("Avg Transfer Efficiency", f"{df['transfer_efficiency'].mean():.1%}")

"""Care Pipeline Sankey flow visualization."""

import plotly.graph_objects as go
import streamlit as st

from shared import apply_theme, get_dashboard_context, render_page_header, render_section, themed_plotly_layout

st.set_page_config(page_title="Care Pipeline", layout="wide")
apply_theme()
render_page_header("Care Pipeline Flow", "Apprehension → CBP Custody → HHS Care → Sponsor Discharge", badge="Sankey")

ctx = get_dashboard_context()
if ctx["empty"]:
    st.warning("No data for the selected filters.")
    st.stop()

df, chart_df, config = ctx["chart_df"], ctx["chart_df"], ctx["config"]
flow_mode = st.radio("Flow calculation", ["Sum (total volume)", "Mean (average daily)"], horizontal=True)

if flow_mode.startswith("Sum"):
    total_app = int(df["apprehensions"].sum())
    total_transfers = int(df["transfers"].sum())
    total_discharges = int(df["discharges"].sum())
else:
    total_app = int(df["apprehensions"].mean())
    total_transfers = int(df["transfers"].mean())
    total_discharges = int(df["discharges"].mean())

c1, c2, c3 = st.columns(3)
c1.metric("CBP → HHS", f"{total_transfers / max(total_app, 1):.1%}")
c2.metric("Throughput", f"{total_discharges / max(total_app, 1):.1%}")
c3.metric("Records", f"{len(ctx['df']):,}")

fig = go.Figure(data=[go.Sankey(
    node=dict(pad=20, thickness=25, label=["Apprehended", "CBP Custody", "HHS Care", "Discharged"],
              color=["#3b82f6", "#2563eb", "#1d4ed8", "#22c55e"]),
    link=dict(
        source=[0, 1, 2], target=[1, 2, 3],
        value=[max(total_app, 1), max(total_transfers, 1), max(total_discharges, 1)],
        color=["rgba(59,130,246,0.45)", "rgba(37,99,235,0.45)", "rgba(34,197,94,0.45)"],
    ),
)])
fig.update_layout(**themed_plotly_layout(500, font=dict(color="#e2e8f0")))
st.plotly_chart(fig, use_container_width=True)

stage_fig = go.Figure()
for col, color in [("cbp_custody", "#60a5fa"), ("hhs_care", "#3b82f6"), ("discharges", "#34d399")]:
    stage_fig.add_trace(go.Scatter(x=chart_df["date"], y=chart_df[col], name=col.replace("_", " ").title(), line=dict(color=color)))
render_section("Stage Volumes")
stage_fig.update_layout(**themed_plotly_layout(400, title="Stage Volumes"))
st.plotly_chart(stage_fig, use_container_width=True)

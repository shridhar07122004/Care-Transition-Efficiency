"""Care Transition Analytics — Executive Overview."""

import plotly.graph_objects as go
import streamlit as st

from shared import (
    METRIC_CATALOG,
    add_metric_traces,
    apply_theme,
    get_dashboard_context,
    render_kpi_card,
    render_page_header,
    render_section,
    themed_plotly_layout,
)

st.set_page_config(
    page_title="UAC Care Transition Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
render_page_header(
    "Care Transition Analytics",
    "Unaccompanied Children Care Pipeline — Executive Overview",
    badge="Live Dashboard",
)

ctx = get_dashboard_context()
if ctx["empty"]:
    st.warning("No data for the selected filters.")
    st.stop()

chart_df, kpis, config = ctx["chart_df"], ctx["kpis"], ctx["config"]

c1, c2, c3 = st.columns(3)
with c1:
    trend_metrics = st.multiselect(
        "Pipeline metrics", list(METRIC_CATALOG.keys()), default=config["trend_metrics"],
        format_func=lambda m: METRIC_CATALOG[m]["label"],
    )
with c2:
    kpi_metrics = st.multiselect(
        "KPI metrics", list(METRIC_CATALOG.keys()), default=config["kpi_metrics"],
        format_func=lambda m: METRIC_CATALOG[m]["label"],
    )
with c3:
    backlog_metrics = st.multiselect(
        "Backlog metrics", list(METRIC_CATALOG.keys()), default=config["backlog_metrics"],
        format_func=lambda m: METRIC_CATALOG[m]["label"],
    )

config["show_rolling"] = st.toggle("Overlay rolling average", value=config["show_rolling"])

col1, col2, col3, col4, col5, col6 = st.columns(6)
cards = [
    ("Apprehensions", f"{kpis['total_apprehensions']:,}"),
    ("Transfers", f"{kpis['total_transfers']:,}"),
    ("Discharges", f"{kpis['total_discharges']:,}"),
    ("Transfer Eff.", f"{kpis['avg_transfer_efficiency']:.1%}"),
    ("Discharge Eff.", f"{kpis['avg_discharge_effectiveness']:.1%}"),
    ("Backlog", f"{kpis['current_backlog']:,}"),
]
for col, (label, val), i in zip([col1, col2, col3, col4, col5, col6], cards, range(6)):
    with col:
        render_kpi_card(label, val, index=i)

render_section(f"Pipeline Trend · {config['aggregation']}")
left, right = st.columns(2)
with left:
    fig = go.Figure()
    add_metric_traces(fig, chart_df, trend_metrics, config["show_rolling"])
    fig.update_layout(**themed_plotly_layout(400))
    st.plotly_chart(fig, use_container_width=True)
with right:
    kpi_fig = go.Figure()
    add_metric_traces(kpi_fig, chart_df, kpi_metrics, config["show_rolling"])
    kpi_fig.update_layout(**themed_plotly_layout(400))
    st.plotly_chart(kpi_fig, use_container_width=True)

render_section("Population & Backlog")
pop_fig = go.Figure()
add_metric_traces(pop_fig, chart_df, backlog_metrics, config["show_rolling"])
pop_fig.update_layout(**themed_plotly_layout(350))
st.plotly_chart(pop_fig, use_container_width=True)

with st.expander("Correlation Matrix"):
    st.dataframe(ctx["correlation"].round(2), use_container_width=True)
with st.expander("Data Validation"):
    st.json(ctx["validation"])

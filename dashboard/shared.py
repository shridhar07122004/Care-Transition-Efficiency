"""Streamlit dashboard utilities and dynamic data pipeline."""

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import (
    FORECAST_LABELS,
    METRIC_CATALOG,
    MONTH_NAMES,
    add_metric_traces,
    build_dynamic_context,
    load_base_data,
    plotly_layout,
)

THEME_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=IBM+Plex+Sans:ital,wght@0,500;0,600;0,700;1,500&family=JetBrains+Mono:wght@500;600;700&display=swap" rel="stylesheet">

<style>
    :root {
        --bg-deep: #050810;
        --bg-surface: #0c1222;
        --bg-elevated: #111827;
        --accent-blue: #3b82f6;
        --accent-cyan: #22d3ee;
        --accent-violet: #a78bfa;
        --accent-emerald: #34d399;
        --accent-amber: #fbbf24;
        --accent-rose: #fb7185;
        --text-primary: #f1f5f9;
        --text-muted: #94a3b8;
        --font-heading: 'IBM Plex Sans', 'Segoe UI', sans-serif;
        --font-body: 'DM Sans', 'Segoe UI', sans-serif;
        --border-glow: rgba(56, 189, 248, 0.2);
    }

    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes shimmer {
        0%   { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 0 0 var(--kpi-glow, rgba(59,130,246,0.4)); }
        50%      { box-shadow: 0 0 24px 4px var(--kpi-glow, rgba(59,130,246,0.25)); }
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes sidebarIn {
        from { opacity: 0; transform: translateX(-12px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    .stApp {
        background: var(--bg-deep) !important;
        background-image:
            radial-gradient(ellipse 80% 50% at 20% -10%, rgba(59, 130, 246, 0.18), transparent),
            radial-gradient(ellipse 60% 40% at 90% 10%, rgba(34, 211, 238, 0.1), transparent),
            radial-gradient(ellipse 50% 30% at 50% 100%, rgba(139, 92, 246, 0.08), transparent) !important;
        color: var(--text-primary) !important;
        font-family: 'DM Sans', 'Segoe UI', sans-serif !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0f1a 0%, #0c1222 100%) !important;
        border-right: 1px solid var(--border-glow) !important;
        animation: sidebarIn 0.5s ease-out;
    }
    [data-testid="stSidebar"] * {
        font-family: 'DM Sans', sans-serif !important;
    }
    [data-testid="stSidebar"] h3 {
        font-family: var(--font-heading) !important;
        font-weight: 700 !important;
        color: var(--accent-cyan) !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-size: 0.72rem !important;
    }

    h1, h2, h3, h4 {
        font-family: var(--font-heading) !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.03em;
    }

    .page-header {
        animation: fadeSlideUp 0.55s ease-out both;
        margin-bottom: 1.75rem;
        padding-bottom: 1.35rem;
        border-bottom: 1px solid rgba(56, 189, 248, 0.12);
    }
    .page-title {
        font-family: var(--font-heading) !important;
        font-size: 3.75rem !important;
        font-weight: 700 !important;
        line-height: 1.08 !important;
        margin: 0 !important;
        letter-spacing: -0.04em !important;
        text-transform: none;
        background: linear-gradient(135deg, #ffffff 0%, #dbeafe 40%, #38bdf8 70%, #93c5fd 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 8s ease infinite;
    }
    @media (max-width: 992px) {
        .page-title { font-size: 2.75rem !important; }
    }
    @media (max-width: 576px) {
        .page-title { font-size: 2.1rem !important; letter-spacing: -0.03em !important; }
    }
    .page-subtitle {
        color: var(--text-muted) !important;
        font-size: 1.05rem !important;
        margin: 0.5rem 0 0 0 !important;
        font-weight: 500;
        font-family: 'DM Sans', sans-serif !important;
        letter-spacing: 0.01em;
    }
    .page-badge {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        background: rgba(56, 189, 248, 0.12);
        color: var(--accent-cyan);
        border: 1px solid rgba(56, 189, 248, 0.25);
    }

    .kpi-card {
        background: linear-gradient(145deg, rgba(17,24,39,0.9) 0%, rgba(12,18,34,0.95) 100%);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 16px;
        padding: 1.1rem 1rem;
        text-align: left;
        position: relative;
        overflow: hidden;
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease, border-color 0.3s;
        animation: fadeSlideUp 0.6s ease-out both;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--kpi-accent, #3b82f6), transparent);
        opacity: 0.8;
    }
    .kpi-card:hover {
        transform: translateY(-4px) scale(1.02);
        border-color: var(--kpi-accent, #3b82f6);
        box-shadow: 0 16px 40px -8px var(--kpi-glow, rgba(59,130,246,0.35));
    }
    .kpi-animate-0 { animation-delay: 0.05s; }
    .kpi-animate-1 { animation-delay: 0.12s; }
    .kpi-animate-2 { animation-delay: 0.19s; }
    .kpi-animate-3 { animation-delay: 0.26s; }
    .kpi-animate-4 { animation-delay: 0.33s; }
    .kpi-animate-5 { animation-delay: 0.40s; }

    .kpi-inner { display: flex; align-items: flex-start; gap: 0.75rem; }
    .kpi-icon {
        font-size: 1.4rem;
        line-height: 1;
        filter: drop-shadow(0 0 8px var(--kpi-glow));
        animation: pulseGlow 3s ease-in-out infinite;
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.45rem;
        font-weight: 700;
        color: var(--kpi-accent, #60a5fa);
        line-height: 1.2;
        background: linear-gradient(90deg, var(--kpi-accent), #f8fafc, var(--kpi-accent));
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .kpi-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        margin-top: 0.25rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .section-title {
        font-family: var(--font-heading) !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #e2e8f0 !important;
        margin: 1.5rem 0 0.75rem 0 !important;
        animation: fadeSlideUp 0.5s ease-out 0.2s both;
        letter-spacing: -0.02em;
    }

    [data-testid="stPlotlyChart"] {
        animation: fadeSlideUp 0.65s ease-out 0.15s both;
        border-radius: 16px !important;
        overflow: hidden;
        border: 1px solid rgba(56, 189, 248, 0.1) !important;
        transition: box-shadow 0.35s ease, border-color 0.35s ease;
    }
    [data-testid="stPlotlyChart"]:hover {
        border-color: rgba(56, 189, 248, 0.28) !important;
        box-shadow: 0 12px 48px -12px rgba(59, 130, 246, 0.25) !important;
    }

    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: var(--accent-cyan) !important;
    }
    [data-testid="stMetricLabel"] { color: var(--text-muted) !important; }

    .stSlider [data-baseweb="slider"] div { background-color: var(--accent-blue) !important; }
    .stButton > button {
        border-radius: 10px !important;
        font-family: var(--font-heading) !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover { transform: translateY(-1px); }

    div[data-testid="stExpander"] {
        border: 1px solid rgba(56, 189, 248, 0.12) !important;
        border-radius: 12px !important;
        background: rgba(12, 18, 34, 0.6) !important;
        animation: fadeIn 0.5s ease-out;
    }

    .risk-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 12px;
        font-family: var(--font-heading);
        font-weight: 700;
        font-size: 1.1rem;
        animation: fadeSlideUp 0.5s ease-out;
    }
    .risk-high   { background: rgba(251,113,133,0.15); color: #fb7185; border: 1px solid rgba(251,113,133,0.35); }
    .risk-moderate { background: rgba(251,191,36,0.12); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }
    .risk-low    { background: rgba(52,211,153,0.12); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }

    .rec-card {
        background: linear-gradient(135deg, rgba(17,24,39,0.8), rgba(12,18,34,0.9));
        border: 1px solid rgba(56, 189, 248, 0.1);
        border-radius: 14px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.75rem;
        animation: fadeSlideUp 0.5s ease-out both;
        transition: border-color 0.25s, transform 0.25s;
    }
    .rec-card:hover {
        border-color: rgba(56, 189, 248, 0.3);
        transform: translateX(4px);
    }

    hr { border-color: rgba(56, 189, 248, 0.1) !important; }

    #MainMenu, footer, header { visibility: hidden; }
</style>
"""

KPI_ACCENTS = [
    {"icon": "👥", "accent": "#60a5fa", "glow": "rgba(96,165,250,0.35)"},
    {"icon": "🔄", "accent": "#34d399", "glow": "rgba(52,211,153,0.35)"},
    {"icon": "✅", "accent": "#a78bfa", "glow": "rgba(167,139,250,0.35)"},
    {"icon": "📤", "accent": "#38bdf8", "glow": "rgba(56,189,248,0.35)"},
    {"icon": "🏠", "accent": "#22d3ee", "glow": "rgba(34,211,238,0.35)"},
    {"icon": "📦", "accent": "#fbbf24", "glow": "rgba(251,191,36,0.35)"},
]

CHART_COLORS = {
    "grid": "rgba(148, 163, 184, 0.08)",
    "line": "#38bdf8",
    "paper": "rgba(5, 8, 16, 0)",
    "plot": "rgba(12, 18, 34, 0.5)",
}


@st.cache_data(show_spinner=False)
def get_base_data():
    return load_base_data()


def apply_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def themed_plotly_layout(height: int = 400, **kwargs) -> dict:
    layout = plotly_layout(height, **kwargs)
    layout.update(
        font=dict(family="DM Sans, sans-serif", color="#cbd5e1", size=12),
        paper_bgcolor=CHART_COLORS["paper"],
        plot_bgcolor=CHART_COLORS["plot"],
        xaxis=dict(gridcolor=CHART_COLORS["grid"], zerolinecolor=CHART_COLORS["grid"]),
        yaxis=dict(gridcolor=CHART_COLORS["grid"], zerolinecolor=CHART_COLORS["grid"]),
        hoverlabel=dict(bgcolor="#1e293b", font_size=12, font_family="DM Sans"),
    )
    return layout


def render_page_header(title: str, subtitle: str = "", badge: str = ""):
    badge_html = f'<span class="page-badge">{badge}</span>' if badge else ""
    st.markdown(
        f'<div class="page-header">'
        f'<h1 class="page-title">{title}</h1>'
        f'<p class="page-subtitle">{subtitle}</p>{badge_html}</div>',
        unsafe_allow_html=True,
    )


def render_section(title: str):
    st.markdown(f'<p class="section-title">{title}</p>', unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, index: int = 0):
    style = KPI_ACCENTS[index % len(KPI_ACCENTS)]
    st.markdown(
        f'<div class="kpi-card kpi-animate-{index}" '
        f'style="--kpi-accent: {style["accent"]}; --kpi-glow: {style["glow"]};">'
        f'<div class="kpi-inner"><span class="kpi-icon">{style["icon"]}</span>'
        f'<div><div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div></div></div></div>',
        unsafe_allow_html=True,
    )


def render_risk_banner(risk_level: str, risk_score: float):
    css_class = {"High": "risk-high", "Moderate": "risk-moderate", "Low": "risk-low"}.get(risk_level, "risk-low")
    st.markdown(
        f'<div class="risk-pill {css_class}">'
        f'<span>Risk Level</span><strong>{risk_level}</strong>'
        f'<span style="opacity:0.7">({risk_score:.0%})</span></div>',
        unsafe_allow_html=True,
    )
    st.progress(min(max(risk_score, 0.0), 1.0))


def render_recommendation_cards(recommendations: list[dict]):
    for i, rec in enumerate(recommendations):
        priority_colors = {"High": "#fb7185", "Medium": "#fbbf24", "Low": "#34d399"}
        color = priority_colors.get(rec["priority"], "#94a3b8")
        st.markdown(
            f'<div class="rec-card" style="animation-delay: {i * 0.08}s; border-left: 3px solid {color};">'
            f'<strong style="color:{color}">{rec["priority"]}</strong> · {rec["category"]}<br>'
            f'<span style="color:#e2e8f0">{rec["recommendation"]}</span><br>'
            f'<small style="color:#64748b">{rec["rationale"]}</small></div>',
            unsafe_allow_html=True,
        )


def render_sidebar_controls(base_df) -> dict:
    st.sidebar.markdown("### ◆ Data Filters")
    min_date = base_df["date"].min().date()
    max_date = base_df["date"].max().date()
    date_range = st.sidebar.date_input(
        "Date Range", value=(min_date, max_date),
        min_value=min_date, max_value=max_date,
    )
    years = sorted(base_df["year"].unique())
    selected_years = st.sidebar.multiselect("Year", years, default=years)
    selected_months = st.sidebar.multiselect(
        "Month", list(range(1, 13)), default=list(range(1, 13)),
        format_func=lambda m: MONTH_NAMES[m - 1],
    )

    st.sidebar.markdown("### ◆ Analysis")
    aggregation = st.sidebar.selectbox("Aggregation", ["Daily", "Weekly", "Monthly"])
    rolling_window = st.sidebar.slider("Rolling window (days)", 3, 60, 7)
    trend_window = st.sidebar.slider("Trend window (days)", 7, 90, 30)
    show_rolling = st.sidebar.toggle("Show rolling average", value=False)

    st.sidebar.markdown("### ◆ Thresholds")
    transfer_threshold = st.sidebar.slider("Transfer efficiency alert %", 10, 90, 50) / 100
    discharge_threshold = st.sidebar.slider("Discharge effectiveness alert %", 10, 90, 40) / 100
    backlog_streak = st.sidebar.slider("Backlog streak (days)", 3, 21, 7)
    alert_lookback = st.sidebar.slider("Alert lookback (days)", 7, 90, 30)
    anomaly_rate = st.sidebar.slider("Anomaly sensitivity %", 1, 15, 5) / 100
    forecast_days = st.sidebar.slider("Forecast horizon (days)", 7, 90, 30)

    start = date_range[0] if isinstance(date_range, tuple) and len(date_range) == 2 else min_date
    end = date_range[1] if isinstance(date_range, tuple) and len(date_range) == 2 else max_date

    return {
        "start_date": str(start),
        "end_date": str(end),
        "years": selected_years,
        "months": selected_months,
        "aggregation": aggregation,
        "rolling_window": rolling_window,
        "trend_window": trend_window,
        "show_rolling": show_rolling,
        "transfer_threshold": transfer_threshold,
        "discharge_threshold": discharge_threshold,
        "backlog_streak": backlog_streak,
        "alert_lookback": alert_lookback,
        "anomaly_rate": anomaly_rate,
        "forecast_days": forecast_days,
        "trend_metrics": ["apprehensions", "transfers", "discharges"],
        "kpi_metrics": ["transfer_efficiency", "discharge_effectiveness", "throughput_rate"],
        "backlog_metrics": ["hhs_care", "cumulative_backlog"],
        "flow_mode": "sum",
        "forecast_metric": "apprehensions",
        "heatmap_metric": "daily_backlog",
        "anomaly_metric": "throughput_rate",
    }


def get_dashboard_context() -> dict:
    base_df = get_base_data()
    config = render_sidebar_controls(base_df)
    ctx = build_dynamic_context(base_df, config)

    if not ctx["empty"]:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ◆ Live Summary")
        st.sidebar.metric("Records", f"{len(ctx['df']):,}")
        st.sidebar.metric("Active Alerts", len(ctx["active_alerts"]))
        risk = ctx["recommendations"]["risk_level"]
        st.sidebar.metric("Risk Level", risk)

    return ctx

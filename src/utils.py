"""Shared utilities for care transition analytics."""

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "uac_data.csv"

COLUMN_MAP = {
    "Children apprehended and placed in CBP custody*": "apprehensions",
    "Children apprehended and placed in CBP custody": "apprehensions",
    "Children in CBP custody": "cbp_custody",
    "Children transferred out of CBP custody": "transfers",
    "Children in HHS Care": "hhs_care",
    "Children discharged from HHS Care": "discharges",
}

ROLLING_WINDOWS = (7, 14, 30)

TRANSFER_EFFICIENCY_THRESHOLD = 0.50
DISCHARGE_EFFECTIVENESS_THRESHOLD = 0.40
BACKLOG_STREAK_DAYS = 7


def safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Element-wise division with zero-denominator protection."""
    denom = denominator.replace(0, np.nan)
    return (numerator / denom).astype("float64")


def format_pct(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value * 100:.1f}%"


def format_number(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:,.0f}"

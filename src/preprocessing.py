"""Data validation and cleaning for UAC pipeline data."""

from datetime import datetime
import re

import pandas as pd

from .data_loader import load_raw_data, standardize_columns

MONTH_LOOKUP = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _parse_numeric(series: pd.Series) -> pd.Series:
    """Convert comma-formatted strings to numeric."""
    if series.dtype == object:
        return pd.to_numeric(
            series.astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )
    return pd.to_numeric(series, errors="coerce")


def _parse_date_value(value) -> pd.Timestamp:
    """Parse dates consistently across pandas/runtime versions."""
    if pd.isna(value):
        return pd.NaT

    text = str(value).replace("\ufeff", "").strip().strip('"').strip("'")
    if not text or text.lower() in {"nan", "nat", "none"}:
        return pd.NaT

    month_match = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", text)
    if month_match:
        month_name, day, year = month_match.groups()
        month = MONTH_LOOKUP.get(month_name.lower())
        if month:
            return pd.Timestamp(year=int(year), month=month, day=int(day))

    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return pd.Timestamp(datetime.strptime(text, fmt))
        except ValueError:
            continue

    return pd.to_datetime(text, errors="coerce")


def _parse_dates(series: pd.Series) -> pd.Series:
    """Convert source date strings to pandas timestamps."""
    return series.map(_parse_date_value)


def validate_data(df: pd.DataFrame) -> dict:
    """Return validation summary for raw/standardized data."""
    numeric_cols = ["apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]
    report = {
        "missing_values": int(df[numeric_cols].isna().sum().sum()),
        "duplicate_dates": int(df["date"].duplicated().sum()) if "date" in df.columns else 0,
        "negative_values": int((df[numeric_cols] < 0).sum().sum()),
        "null_dates": int(df["date"].isna().sum()) if "date" in df.columns else 0,
        "row_count": len(df),
    }
    return report


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and sort UAC operational data."""
    cleaned = df.copy()
    cleaned.columns = [str(col).replace("\ufeff", "").strip() for col in cleaned.columns]
    cleaned = cleaned.rename(columns={"Date": "date"})

    numeric_cols = ["apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]
    for col in numeric_cols:
        if col in cleaned.columns:
            cleaned[col] = _parse_numeric(cleaned[col])

    cleaned["date"] = _parse_dates(cleaned["date"])
    cleaned = cleaned.dropna(subset=["date"])
    cleaned = cleaned.drop_duplicates(subset=["date"], keep="last")
    cleaned = cleaned.sort_values("date").reset_index(drop=True)

    cleaned[numeric_cols] = cleaned[numeric_cols].ffill()
    cleaned = cleaned.dropna(subset=numeric_cols, how="all")

    for col in numeric_cols:
        cleaned = cleaned[cleaned[col] >= 0]

    return cleaned


def load_and_clean(path=None) -> pd.DataFrame:
    """End-to-end load, standardize, and clean pipeline."""
    raw = load_raw_data(path)
    standardized = standardize_columns(raw)
    return clean_data(standardized)

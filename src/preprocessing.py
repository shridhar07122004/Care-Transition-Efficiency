"""Data validation and cleaning for UAC pipeline data."""

import pandas as pd

from .data_loader import load_raw_data, standardize_columns


def _parse_numeric(series: pd.Series) -> pd.Series:
    """Convert comma-formatted strings to numeric."""
    if series.dtype == object:
        return pd.to_numeric(
            series.astype(str).str.replace(",", "", regex=False),
            errors="coerce",
        )
    return pd.to_numeric(series, errors="coerce")


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
    cleaned = cleaned.rename(columns={"Date": "date"})

    numeric_cols = ["apprehensions", "cbp_custody", "transfers", "hhs_care", "discharges"]
    for col in numeric_cols:
        if col in cleaned.columns:
            cleaned[col] = _parse_numeric(cleaned[col])

    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce", format="mixed")
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

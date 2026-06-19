"""Load UAC care transition dataset."""

from pathlib import Path

import pandas as pd

from .utils import COLUMN_MAP, DATA_PATH


def load_raw_data(path: Path | str | None = None) -> pd.DataFrame:
    """Read CSV and return raw dataframe."""
    csv_path = Path(path) if path else DATA_PATH
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df.columns = [str(col).replace("\ufeff", "").strip() for col in df.columns]
    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to short internal names."""
    df = df.copy()
    df.columns = [str(col).replace("\ufeff", "").strip() for col in df.columns]
    renamed = df.rename(columns=COLUMN_MAP)
    if "apprehensions" not in renamed.columns:
        raise ValueError("Expected apprehensions column not found in dataset.")
    return renamed

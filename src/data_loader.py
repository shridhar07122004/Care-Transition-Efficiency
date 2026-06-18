"""Load UAC care transition dataset."""

from pathlib import Path

import pandas as pd

from .utils import COLUMN_MAP, DATA_PATH


def load_raw_data(path: Path | str | None = None) -> pd.DataFrame:
    """Read CSV and return raw dataframe."""
    csv_path = Path(path) if path else DATA_PATH
    return pd.read_csv(csv_path)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to short internal names."""
    renamed = df.rename(columns=COLUMN_MAP)
    if "apprehensions" not in renamed.columns:
        raise ValueError("Expected apprehensions column not found in dataset.")
    return renamed

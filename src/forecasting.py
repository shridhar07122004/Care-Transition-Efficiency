"""Prophet-based forecasting for UAC operational load."""

import warnings

import pandas as pd

try:
    from prophet import Prophet
except ImportError:
    Prophet = None

FORECAST_TARGETS = {
    "apprehensions": "Future Apprehensions",
    "transfers": "Future Transfers",
    "hhs_care": "Future HHS Population",
    "discharges": "Future Discharges",
}


def _prepare_prophet_df(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    prophet_df = df[["date", target_col]].rename(
        columns={"date": "ds", target_col: "y"}
    )
    return prophet_df.dropna()


def forecast_metric(
    df: pd.DataFrame,
    target_col: str,
    periods: int = 30,
) -> pd.DataFrame | None:
    """Forecast a single metric using Prophet."""
    if Prophet is None:
        return None

    prophet_df = _prepare_prophet_df(df, target_col)
    if len(prophet_df) < 14:
        return None

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
        )
        model.fit(prophet_df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

    forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    forecast = forecast.rename(columns={"ds": "date"})
    forecast["metric"] = target_col
    return forecast


def forecast_all(df: pd.DataFrame, periods: int = 30) -> dict[str, pd.DataFrame]:
    """Generate 30-day forecasts for all target metrics."""
    results = {}
    for col in FORECAST_TARGETS:
        forecast = forecast_metric(df, col, periods=periods)
        if forecast is not None:
            results[col] = forecast
    return results

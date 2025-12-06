# src/features/engineering.py
import pandas as pd

def add_basic_features(df: pd.DataFrame, ma_windows=(5, 10, 20)) -> pd.DataFrame:
    df = df.copy()
    # Ensure we have 'close'
    if "close" not in df.columns:
        raise ValueError("DataFrame must contain a 'close' column.")

    df["return_1"] = df["close"].pct_change()
    for w in ma_windows:
        df[f"ma_{w}"] = df["close"].rolling(w).mean()
        df[f"rsi_{w}"] = rsi(df["close"], window=w)

    df["volatility_10"] = df["return_1"].rolling(10).std()
    df["target_next_close"] = df["close"].shift(-1)   # next-step prediction target
    return df.dropna()

def rsi(series: pd.Series, window=14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0).rolling(window).mean()
    down = (-delta.clip(upper=0)).rolling(window).mean()
    rs = up / (down + 1e-9)
    return 100 - (100 / (1 + rs))

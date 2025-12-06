# src/app.py
import os
import time
from dotenv import load_dotenv
import requests
import pandas as pd
import yfinance as yf

load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY")


def fetch_from_finnhub(symbol: str = "AAPL", minutes: int = 120, resolution: str = "1"):
    """
    Fetch recent candles from Finnhub.
    resolution: '1'='1min', '5'='5min', '60'='1h'
    Returns a DataFrame indexed by time or None on error / rate-limit / invalid token.
    """
    if not API_KEY:
        return None  # no key → fallback to yfinance

    try:
        now = int(time.time())
        _from = now - minutes * 60
        url = (
            "https://finnhub.io/api/v1/stock/candle"
            f"?symbol={symbol}&resolution={resolution}&from={_from}&to={now}&token={API_KEY}"
        )

        r = requests.get(url, timeout=15)

        # Common failure cases: invalid key, forbidden, rate limit
        if r.status_code in (401, 403, 429):
            return None

        r.raise_for_status()
        data = r.json()
        if data.get("s") != "ok":
            return None

        df = pd.DataFrame(
            {
                "time": pd.to_datetime(data["t"], unit="s"),
                "open": data["o"],
                "high": data["h"],
                "low": data["l"],
                "close": data["c"],
                "volume": data["v"],
            }
        ).set_index("time")
        return df

    except requests.RequestException:
        return None


def fetch_from_yfinance(symbol: str = "AAPL", minutes: int = 120):
    """
    Fallback downloader using yfinance.
    Uses 1m bars for <= 390 minutes (≈ 1 trading day), else 5m bars.
    Returns the last `minutes` rows.
    """
    period = "1d" if minutes <= 390 else "5d"
    interval = "1m" if minutes <= 390 else "5m"

    df = yf.download(symbol, period=period, interval=interval, progress=False)

    if df is None or df.empty:
        raise RuntimeError(
            "yfinance returned empty data. Try another symbol (e.g., MSFT, TSLA) "
            "or run during market hours for 1m bars."
        )

    # Normalize column names
    if isinstance(df.columns, pd.MultiIndex):
        # e.g., ('Open','AAPL') -> 'open'
        df.columns = [c[0].lower() for c in df.columns]
    else:
        df.columns = [c.lower() for c in df.columns]

    # Ensure 'close' exists
    df = df.rename(columns={"adj close": "close"})

    # Keep the last ~N minutes rows
    return df.tail(minutes)


def get_data(symbol: str = "AAPL", minutes: int = 120):
    """
    Try Finnhub first; if it fails or is unavailable, gracefully fallback to yfinance.
    """
    return fetch_from_finnhub(symbol, minutes) or fetch_from_yfinance(symbol, minutes)


def main():
    symbol = os.getenv("SYMBOL", "AAPL").upper()
    minutes = int(os.getenv("MINUTES", "120"))
    df = get_data(symbol, minutes)

    print(f"\n[{symbol}] Last {minutes} minutes — rows: {len(df)}")
    print("\n-- HEAD --")
    print(df.head())
    print("\n-- TAIL --")
    print(df.tail())


if __name__ == "__main__":
    main()

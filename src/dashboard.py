# src/dashboard.py
import time
import streamlit as st
import pandas as pd
from app import get_data

st.set_page_config(page_title="StockFlux — Live", layout="wide")
st.title("📈 StockFlux — Live Mini Dashboard")

with st.sidebar:
    st.subheader("Controls")
    symbol = st.text_input("Ticker", value="AAPL").upper()
    minutes = st.number_input("Lookback (minutes)", min_value=30, max_value=1440, value=120, step=30)
    auto = st.toggle("Auto-refresh (10s)", value=False)

placeholder = st.empty()

def render():
    df = get_data(symbol, minutes)
    st.caption(f"{symbol} • Rows: {len(df)}")
    if "close" not in df.columns:
        st.error("No 'close' column found in data.")
        st.dataframe(df.tail(10))
        return
    line_col, table_col = st.columns([3,2], vertical_alignment="top")
    with line_col:
        st.line_chart(df["close"])
    with table_col:
        st.dataframe(df.tail(15))

while True:
    with placeholder.container():
        render()
    if not auto:
        break
    time.sleep(10)
    st.rerun()

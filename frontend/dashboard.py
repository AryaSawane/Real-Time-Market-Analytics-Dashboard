import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
from storage.memory_store import TickMemoryStore
from analytics.resampler import resample_ticks
from analytics.pairs import hedge_ratio, spread, zscore
from ingestion.websocket_client import BinanceWebSocket
import threading
import time
import sys
import os

# --- Add project root to path for imports ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# --- Memory Store ---
store = TickMemoryStore()

# --- Sidebar Controls ---
symbols = st.sidebar.multiselect("Select Symbols", ["BTCUSDT", "ETHUSDT"], default=["BTCUSDT","ETHUSDT"])
timeframe = st.sidebar.selectbox("Resample timeframe", ["1S","1M","5M"])
window = st.sidebar.slider("Z-score rolling window", 1, 30, 3)
alert_threshold = st.sidebar.slider("Alert Z-score threshold", 0.5, 5.0, 2.0)

# --- Tick handler ---
def handle_tick(tick):
    store.add_tick(tick)

# --- Start WebSockets in background ---
def start_ws(symbols):
    for sym in symbols:
        ws = BinanceWebSocket(sym, handle_tick)
        ws.start()

threading.Thread(target=start_ws, args=(symbols,), daemon=True).start()

st.title("Real-Time Market Analytics Dashboard")

# --- Containers for charts ---
price_chart = st.empty()
spread_chart = st.empty()
alerts_box = st.empty()

# --- Main update loop ---
while True:
    time.sleep(1)  # update every 1 second

    if len(symbols) < 2:
        st.warning("Select at least 2 symbols for pairs analytics")
        continue

    # --- Get resampled data ---
    df1 = resample_ticks(store.get_df(symbols[0]), timeframe)
    df2 = resample_ticks(store.get_df(symbols[1]), timeframe)

    # Skip if no data
    if df1.empty or df2.empty:
        continue

    # --- Align dataframes ---
    df_pair = df1[["price"]].join(df2[["price"]], how="inner", lsuffix="_1", rsuffix="_2")
    df_pair.columns = ["X", "Y"]

    # Skip if not enough data
    if len(df_pair) < 2:
        st.info("Waiting for more ticks to compute hedge ratio...")
        continue

    # --- Compute pairs analytics ---
    beta = hedge_ratio(df_pair["Y"], df_pair["X"])
    sp = spread(df_pair["Y"], df_pair["X"], beta)
    z = zscore(sp, window=window)

    # --- Price Chart ---
    fig1 = px.line(df_pair, y=["X","Y"], labels={"value":"Price", "index":"Timestamp"})
    price_chart.plotly_chart(fig1, use_container_width=True)

    # --- Spread + Z-score Chart ---
    df_spread = pd.DataFrame({"Spread": sp, "Z-score": z})
    fig2 = px.line(df_spread, y=["Spread","Z-score"], labels={"value":"Value", "index":"Timestamp"})
    spread_chart.plotly_chart(fig2, use_container_width=True)

    # --- Alerts ---
    if abs(z.iloc[-1]) > alert_threshold:
        alerts_box.warning(f"Z-score {z.iloc[-1]:.2f} exceeded threshold {alert_threshold}")
    else:
        alerts_box.empty()

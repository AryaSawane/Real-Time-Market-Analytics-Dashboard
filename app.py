import time
from ingestion.websocket_client import BinanceWebSocket
from storage.memory_store import TickMemoryStore
from analytics.resampler import resample_ticks
from analytics.pairs import hedge_ratio, spread, zscore

# Create a single memory store for all symbols
store = TickMemoryStore()

# Tick handler
def handle_tick(tick):
    store.add_tick(tick)

if __name__ == "__main__":
    print("Starting WebSocket...")

    # --- START WEBSOCKET CLIENTS FOR TWO SYMBOLS ---
    symbols = ["BTCUSDT", "ETHUSDT"]
    for sym in symbols:
        ws = BinanceWebSocket(sym, handle_tick)
        ws.start()

    # --- COLLECT TICKS FOR SOME TIME ---
    print("Collecting ticks for 20 seconds...")
    time.sleep(60)  # adjust if needed

    # --- RESAMPLE TICKS ---
    df_btc = resample_ticks(store.get_df("BTCUSDT"), "1S")
    df_eth = resample_ticks(store.get_df("ETHUSDT"), "1S")

    # --- ALIGN DATAFRAMES ON TIMESTAMP ---
    df_pair = df_btc[["price"]].join(df_eth[["price"]], how="inner", lsuffix="_BTC", rsuffix="_ETH")
    df_pair.columns = ["BTC", "ETH"]

    # --- COMPUTE HEDGE RATIO ---
    beta = hedge_ratio(df_pair["BTC"], df_pair["ETH"])
    sp = spread(df_pair["BTC"], df_pair["ETH"], beta)
    z = zscore(sp, window=3)

    # --- PRINT RESULTS ---
    print(f"\nHedge Ratio (BTC/ETH): {beta:.4f}")
    print("\nSpread tail:")
    print(sp.tail())
    print("\nZ-score tail (window=3):")
    print(z.tail())

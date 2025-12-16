import pandas as pd
from collections import defaultdict

class TickMemoryStore:
    def __init__(self):
        self._data = defaultdict(list)

    def add_tick(self, tick):
        self._data[tick["symbol"]].append(tick)

    def get_df(self, symbol):
        data = self._data.get(symbol, [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df = df.set_index("timestamp")
        return df.sort_index()

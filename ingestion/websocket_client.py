import json
import websocket
import threading

class BinanceWebSocket:
    def __init__(self, symbol, on_tick):
        self.symbol = symbol.lower()
        self.on_tick = on_tick
        self.url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"

    def _on_message(self, ws, message):
        data = json.loads(message)

        tick = {
            "timestamp": data["T"] / 1000,  # seconds
            "symbol": data["s"],
            "price": float(data["p"]),
            "qty": float(data["q"])
        }

        self.on_tick(tick)

    def start(self):
        ws = websocket.WebSocketApp(
            self.url,
            on_message=self._on_message
        )
        thread = threading.Thread(target=ws.run_forever, daemon=True)
        thread.start()

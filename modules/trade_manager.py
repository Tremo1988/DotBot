import csv, logging
from datetime import datetime
from pathlib import Path

class TradeManager:
    def __init__(self, cfg, dot_balance, usdc_balance):
        self.cfg = cfg
        self.dot_balance = float(dot_balance)
        self.usdc_balance = float(usdc_balance)
        self.base = self.dot_balance * (self.cfg.get("sell_threshold_percent", 60) / 100)
        self.risk_pct = self.cfg.get("risk_per_trade", 0.02)

    # Helper per sizing basato su rischio
    def _risk_position(self, price, atr):
        capital_risk = self.usdc_balance * self.risk_pct
        units = capital_risk / atr
        return round(units, 3)

    def evaluate(self, last, sentiment):
        # Lettura RSI e ADX sia da pandas.Series che da oggetto con attributi
        if hasattr(last, 'rsi'):
            rsi = last.rsi
            adx = last.adx
        else:
            rsi = last['rsi']
            adx = last['adx']
        sent = sentiment

        # Filtro operatività tramite ADX minimo
        if adx < self.cfg.get("min_adx_operativita", 20):
            return "hold"
        # BUY ladder condizionale a RSI e sentiment
        if rsi < 30 and sent is not None and sent > 0:
            if rsi < 20:
                return "buy_100"
            if rsi < 25:
                return "buy_60"
            return "buy_30"
        # SELL ladder condizionale a RSI e sentiment
        if rsi > 70 and sent is not None and sent < 0:
            if rsi > 80:
                return "sell_100"
            if rsi > 75:
                return "sell_60"
            return "sell_30"
        return "hold"

    def execute(self, action, price, last, sentiment):
        if action == "hold":
            return
        pct = int(action.split("_")[1])
        side = ""
        # Acquisto basato su rischio
        if action.startswith("buy"):
            units = self._risk_position(price, last['atr'] if not hasattr(last, 'atr') else last.atr)
            amt = units * pct / 100
            self.dot_balance += amt
            self.usdc_balance -= amt * price
            side = "buy"
        else:
            sellable = self.base * pct / 100
            amt = min(self.dot_balance, sellable)
            self.dot_balance -= amt
            self.usdc_balance += amt * price
            side = "sell"
        # Log sul file e su logger
        self._log(side, amt, price, last, sentiment)
        logging.info("EXEC %s %.3f DOT @ %.3f", side.upper(), amt, price)

    def _log(self, side, amt, price, last, sentiment):
        path = Path("trade_log.csv")
        new = not path.exists()
        with path.open("a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["ts", "side", "amount", "price", "rsi", "sentiment", "forecast_price"])
            # Lettura rsi e forecast_price
            rsi_val = last.rsi if hasattr(last, 'rsi') else last['rsi']
            forecast_val = getattr(last, 'forecast_price', last['forecast_price'])
            w.writerow([datetime.utcnow().isoformat(), side, amt, price, rsi_val, sentiment, forecast_val])

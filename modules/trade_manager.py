
import csv, logging
from datetime import datetime
from pathlib import Path

class TradeManager:
    def __init__(self, cfg, dot_balance, usdc_balance):
        self.cfg = cfg
        self.dot_balance = float(dot_balance)
        self.usdc_balance = float(usdc_balance)
        self.base = self.dot_balance * (cfg.get("sell_threshold_percent",60)/100)
        self.risk_pct = cfg.get("risk_per_trade", 0.02)

    # sizing helper
    def _risk_position(self, price, atr):
        risk_per_unit = atr
        capital_risk = self.usdc_balance * self.risk_pct
        units = capital_risk / risk_per_unit
        return round(units,3)

    def evaluate(self, ind, sentiment):
        rsi = ind['rsi']; sent = sentiment
        if ind['adx'] < self.cfg.get("min_adx_operativita",20): return "hold"
        if rsi < 30 and sent and sent>0:   # BUY ladder
            if rsi<20: return "buy_100"
            if rsi<25: return "buy_60"
            return "buy_30"
        if rsi > 70 and sent and sent<0:  # SELL ladder
            if rsi>80: return "sell_100"
            if rsi>75: return "sell_60"
            return "sell_30"
        return "hold"

    def execute(self, action, price, ind, sentiment):
        if action=="hold": return
        pct = int(action.split("_")[1])
        if "buy" in action:
            units=self._risk_position(price, ind['atr'])
            amt = units*pct/100
            self.dot_balance += amt
            self.usdc_balance -= amt*price
            side="buy"
        else:
            sellable = self.base * pct/100
            amt=min(self.dot_balance, sellable)
            self.dot_balance -= amt
            self.usdc_balance += amt*price
            side="sell"
        self._log(side, amt, price, ind, sentiment)
        logging.info("EXEC %s %.3f DOT @ %.3f", side.upper(), amt, price)

    def _log(self, side, amt, price, ind, sentiment):
        path=Path("trade_log.csv")
        new=not path.exists()
        with path.open("a",newline="") as f:
            w=csv.writer(f)
            if new:
                w.writerow("ts side amount price rsi sentiment forecast".split())
            w.writerow([datetime.utcnow().isoformat(), side, amt, price, ind['rsi'], sentiment, ind['forecast_price']])

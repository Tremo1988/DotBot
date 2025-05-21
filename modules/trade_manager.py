import csv
import logging
from datetime import datetime
from pathlib import Path

class TradeManager:
    def __init__(self, cfg, dot_balance, usdc_balance):
        """
        cfg: dict di configurazione (deve contenere sell_threshold_percent, risk_per_trade,
             optionalmente max_drawdown_pct, fee_pct, slippage_pct)
        dot_balance: saldo iniziale DOT
        usdc_balance: saldo iniziale USDC
        """
        self.cfg = cfg
        self.dot_balance = float(dot_balance)
        self.usdc_balance = float(usdc_balance)

        # Base di DOT da usare per le vendite (soglia %)
        self.base = self.dot_balance * (cfg.get("sell_threshold_percent", 60) / 100)

        # Percentuale di rischio per trade
        self.risk_pct = cfg.get("risk_per_trade", 0.02)

        # Parametri di gestione avanzata
        self.max_drawdown_pct = cfg.get("max_drawdown_pct", 0.1)
        self.fee_pct         = cfg.get("fee_pct", 0.0)
        self.slippage_pct    = cfg.get("slippage_pct", 0.0)

        # Equity di picco per il calcolo del drawdown
        self.peak_equity = self.usdc_balance + self.dot_balance * 0

    def _risk_position(self, price, atr):
        """
        Calcola la size in unità di prezzo da aprire,
        basata su risk_pct e atr. Se atr <= 0, ritorna 0.
        """
        capital_risk = self.usdc_balance * self.risk_pct
        if atr <= 0:
            logging.warning("ATR invalido (%.4f), rischio posiz. = 0", atr)
            return 0.0
        return capital_risk / atr

    def evaluate(self, last_candle, sentiment_score):
        """
        Restituisce 'buy', 'sell' o 'hold' a seconda della tua logica.
        Es: if last_candle['rsi'] < 30 and sentiment_score > 0.5: return 'buy'
        """
        # TODO: sostituisci questo placeholder con la tua logica reale
        return "hold"

    def execute(self, action, price, last_candle, sentiment_score):
        """
        Esegue la trade decisa da evaluate: calcola sizing, 
        applica slippage/fee, blocca in caso di drawdown e aggiorna i saldi.
        """
        if action == "hold":
            return

        # 1) Calcolo equity corrente e update peak_equity
        current_equity = self.usdc_balance + self.dot_balance * price
        if current_equity > self.peak_equity:
            self.peak_equity = current_equity

        # 2) Controllo drawdown
        drawdown = ((self.peak_equity - current_equity) / self.peak_equity
                    if self.peak_equity > 0 else 0.0)
        if drawdown > self.max_drawdown_pct:
            logging.warning(
                "Drawdown %.2f%% > %.2f%%: operazioni bloccate",
                drawdown * 100, self.max_drawdown_pct * 100
            )
            return

        # 3) Parsing dell'azione
        parts = action.split("_")
        side = parts[0]
        pct  = int(parts[1]) if len(parts) > 1 else 100

        fee = 0.0
        amt = 0.0
        price_exec = price

        # 4) BUY
        if side == "buy":
            atr = (last_candle['atr'] if isinstance(last_candle, dict) 
                   else last_candle.atr)
            units = self._risk_position(price, atr)
            amt = units * pct / 100.0
            price_exec = price * (1 + self.slippage_pct)
            fee = amt * price_exec * self.fee_pct

            self.dot_balance   += amt
            self.usdc_balance  -= (amt * price_exec + fee)

        # 5) SELL
        elif side == "sell":
            sellable = self.base * pct / 100.0
            amt = min(self.dot_balance, sellable)
            price_exec = price * (1 - self.slippage_pct)
            fee = amt * price_exec * self.fee_pct

            self.dot_balance   -= amt
            self.usdc_balance  += (amt * price_exec - fee)

        else:
            logging.error("Azione sconosciuta: %s", action)
            return

        # 6) Logging su file e su console
        self._log(side, amt, price_exec, last_candle, sentiment_score)
        logging.info(
            "EXEC %s %.4f DOT @ %.4f | fee=%.6f | Balances: DOT=%.4f USDC=%.4f",
            side.upper(), amt, price_exec, fee,
            self.dot_balance, self.usdc_balance
        )

    def _log(self, side, amt, price, last_candle, sentiment_score):
        """
        Scrive su CSV timestamp, side, amount, price, rsi, sentiment, forecast_price
        """
        path = Path("trade_log.csv")
        new = not path.exists()
        with path.open("a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow([
                    "ts", "side", "amount", "price",
                    "rsi", "sentiment", "forecast_price"
                ])

            # Lettura di RSI e prezzo forecast
            if hasattr(last_candle, "rsi"):
                rsi_val = last_candle.rsi
            else:
                rsi_val = last_candle.get("rsi", None)

            if hasattr(last_candle, "forecast_price"):
                forecast_val = last_candle.forecast_price
            else:
                forecast_val = last_candle.get("forecast_price", None)

            w.writerow([
                datetime.utcnow().isoformat(),
                side, amt, price,
                rsi_val, sentiment_score, forecast_val
            ])

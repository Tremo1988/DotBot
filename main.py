import time
import logging

from modules.config_loader import get
from modules.data_fetcher import get_binance_connection, fetch_ohlcv
from modules.indicator_utils import add_indicators, compute_trend
from modules.sentiment import get_reddit_sentiment
from modules.trade_manager import TradeManager
from modules.telegram_notifier import send_telegram_message

# ─── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log_and_notify(message: str):
    """Stampa, logga e invia su Telegram."""
    logging.info(message)
    try:
        send_telegram_message(message)
    except Exception as e:
        logging.error("Telegram error: %s", e)

def main():
    # ─── Caricamento configurazione ───────────────────────────────────────────────
    cfg = get()  # tutti i parametri in un dict
    symbol    = cfg["symbol"]
    timeframe = cfg["timeframe"]
    loop_sec  = int(cfg.get("loop_seconds", 1800))

    # ─── Connessione all'exchange ─────────────────────────────────────────────────
    ex = get_binance_connection()  # legge api key/secret da .env

    # ─── Bilanci iniziali ─────────────────────────────────────────────────────────
    try:
        free_balances = ex.fetch_balance()["free"]
        usdc_balance = free_balances.get("USDC", 0)
        dot_balance  = free_balances.get(symbol.split("/")[0], 0)
    except Exception:
        # modalità “paper” se manca la chiave
        usdc_balance = cfg.get("paper_usdc_balance", 1000)
        dot_balance  = cfg.get("paper_dot_balance", 10)
        logging.warning(
            "No Binance credentials or fetch_balance failed — paper mode USDC=%s DOT=%s",
            usdc_balance, dot_balance
        )

    # ─── Trade manager ────────────────────────────────────────────────────────────
    tm = TradeManager(cfg, symbol, timeframe, dot_balance, usdc_balance)

    # ─── Ciclo principale ─────────────────────────────────────────────────────────
    while True:
        try:
            # 1) prendo i dati OHLC
            df = fetch_ohlcv(ex, symbol, timeframe)

            # 2) calcolo indici tecnici
            df = add_indicators(df)
            last = df.iloc[-1]

            # 3) calcolo trend e sentiment
            trend = compute_trend(last)
            # useremo il subreddit uguale al ticker minuscolo, es "dot"
            sentiment = get_reddit_sentiment(subreddit=symbol.split("/")[0].lower())

            # 4) decido cosa fare
            action = tm.evaluate(last, sentiment)
            tm.execute(action, last["close"], last, sentiment)

            # 5) preparo il messaggio di aggiornamento
            msg = (
                f"📊 Update:\n"
                f"Price={last['close']:.4f}, RSI={last['rsi']:.2f}, MACDh={last['macd_hist']:.4f}\n"
                f"Forecast={last['forecast_price']:.4f}, Δ={(last['forecast_price']-last['close']):.4f}, "
                f"Sentiment=R{sentiment:.2f}\n"
                f"ADX={last['adx']:.1f}, ATR={last['atr']:.2f}, Trend={trend}, Action={action}"
            )
            log_and_notify(msg)

        except Exception as e:
            logging.error("Error in main loop: %s", e)

        time.sleep(loop_sec)

if __name__ == "__main__":
    main()

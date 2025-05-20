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
    logging.info(message)
    try:
        send_telegram_message(message)
    except Exception as e:
        logging.error("Telegram error: %s", e)

def main():
    # ─── Caricamento configurazione ───────────────────────────────────────────────
    cfg       = get()
    symbol    = cfg["symbol"]
    timeframe = cfg["timeframe"]
    loop_sec  = int(cfg.get("loop_seconds", 1800))

    # ─── Connessione all'exchange ─────────────────────────────────────────────────
    ex = get_binance_connection()

    # ─── Bilanci iniziali ─────────────────────────────────────────────────────────
    try:
        free = ex.fetch_balance().get("free", {})
        usdc = free.get("USDC", 0)
        dot  = free.get(symbol.split("/")[0], 0)
    except Exception:
        usdc = cfg.get("paper_usdc_balance", 1000)
        dot  = cfg.get("paper_dot_balance", 10)
        logging.warning(
            "Paper mode attivato — USDC=%s DOT=%s", usdc, dot
        )

    # ─── Trade manager ────────────────────────────────────────────────────────────
    # Ora la firma è: TradeManager(cfg, dot_balance, usdc_balance)
    tm = TradeManager(cfg, dot, usdc)

    # ─── Ciclo principale ─────────────────────────────────────────────────────────
    while True:
        try:
            df   = fetch_ohlcv(ex, symbol, timeframe)
            df   = add_indicators(df)
            last = df.iloc[-1]

            trend     = compute_trend(last)
            sr_name   = symbol.split("/")[0].lower()
            sentiment = get_reddit_sentiment(subreddit=sr_name)

            action = tm.evaluate(last, sentiment)
            tm.execute(action, last["close"], last, sentiment)

            msg = (
                f"📊 Update:\n"
                f"Price={last['close']:.4f}, RSI={last['rsi']:.2f}, "
                f"MACDh={last['macd_hist']:.4f}\n"
                f"Forecast={last['forecast_price']:.4f}, "
                f"Δ={(last['forecast_price']-last['close']):.4f}, "
                f"Sentiment=R{sentiment:.2f}\n"
                f"ADX={last['adx']:.1f}, ATR={last['atr']:.2f}, "
                f"Trend={trend}, Action={action}"
            )
            log_and_notify(msg)

        except Exception as e:
            logging.error("Error in main loop: %s", e)

        time.sleep(loop_sec)

if __name__ == "__main__":
    main()

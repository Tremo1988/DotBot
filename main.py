import time
import logging
from dotenv import load_dotenv; load_dotenv()

from modules.config_loader import get
from modules.data_fetcher import get_binance_connection, fetch_ohlcv
from modules.indicator_utils import add_indicators, compute_trend
from modules.sentiment import combined_sentiment
from modules.trade_manager import TradeManager
from modules.telegram_notifier import send_telegram_message

# ─── Logging ─────────────────────────────────────────────────────────────────────
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

def trova_asset_balance(balances, nome_token):
    """Trova la chiave esatta dell'asset tra balances['total']"""
    nome_token = nome_token.upper()
    for asset in balances['total']:
        if nome_token in asset and balances['total'][asset] > 0:
            return asset
    return nome_token  # fallback

def main():
    cfg       = get()
    symbol    = cfg["symbol"]
    token_sym = symbol.split("/")[0].upper()
    timeframe = cfg["timeframe"]
    loop_sec  = int(cfg.get("loop_seconds", 1800))

    sentiment_token = "polkadot"
    ex = get_binance_connection()

    # Verifica API e saldo reale
    try:
        balances = ex.fetch_balance()
        dot_key = trova_asset_balance(balances, token_sym)
        dot  = balances['total'].get(dot_key, 0)
        usdc = balances['total'].get("USDC", 0)
        logging.info("✅ Modalità reale attiva: USDC = %.2f | %s = %.4f", usdc, dot_key, dot)
    except Exception as e:
        logging.error("❌ Errore nel recupero dei bilanci Binance: %s", e)
        return

    tm = TradeManager(cfg, dot, usdc)

    while True:
        try:
            df = fetch_ohlcv(ex, symbol, timeframe)
            df = add_indicators(df)
            last = df.iloc[-1]
            trend = compute_trend(last)

            sentiment = combined_sentiment(
                subreddit=sentiment_token,
                trend_keyword=sentiment_token,
                token=sentiment_token,
                weights=(0.5, 0.3, 0.2)
            )

            logging.info(f"Sentiment combinato calcolato: {sentiment}")
            action = tm.evaluate(last, sentiment)
            tm.execute(action, last["close"], last, sentiment)

            msg = (
                f"📊 Update:\n"
                f"Price={last['close']:.4f}, RSI={last['rsi']:.2f}, "
                f"MACDh={last['macd_hist']:.4f}\n"
                f"Forecast={last['forecast_price']:.4f}, "
                f"Δ={(last['forecast_price'] - last['close']):.4f}, "
                f"Sentiment={sentiment:.2f}\n"
                f"ADX={last['adx']:.1f}, ATR={last['atr']:.2f}, "
                f"Trend={trend}, Action={action}"
            )
            log_and_notify(msg)

        except Exception as e:
            logging.error("Errore nel ciclo principale: %s", e)

        time.sleep(loop_sec)

if __name__ == "__main__":
    main()

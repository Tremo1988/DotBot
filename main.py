import time
import logging
from modules.config_loader import get
from modules.data_fetcher import get_binance_connection, fetch_ohlcv
from modules.indicator_utils import add_indicators, compute_trend
from modules.lstm_predictor import forecast as lstm_forecast
from modules.sentiment import get_reddit_sentiment
from modules.trade_manager import TradeManager
from modules.telegram_notifier import send_telegram_message

CONFIG = get()

SYMBOL = CONFIG.get("symbol", "DOT/USDC")
TIMEFRAME = CONFIG.get("timeframe", "30m")
LOOP_SECONDS = CONFIG.get("loop_seconds", 1800)

def main():
    ex = get_binance_connection()
    try:
        bal = ex.fetch_balance()
        dot_balance = bal["free"].get("DOT", 0)
        usdc_balance = bal["free"].get("USDC", 0)
    except Exception:
        logging.warning("Binance credentials missing, paper-mode balances")
        dot_balance = CONFIG.get("virtual_dot_balance", 0)
        usdc_balance = CONFIG.get("virtual_usdc_balance", 0)

    tm = TradeManager(CONFIG, dot_balance, usdc_balance)

    while True:
        try:
            ohlc = fetch_ohlcv(ex, SYMBOL, TIMEFRAME)
            df_ind = add_indicators(ohlc)
            last = df_ind.iloc[-1]
            trend = compute_trend(last)
            sentiment_res = get_reddit_sentiment()
            # unpack sentiment tuple or single float
            if isinstance(sentiment_res, tuple) and len(sentiment_res) == 2:
                sentiment_score, sentiment_posts = sentiment_res
            else:
                sentiment_score = sentiment_res
                sentiment_posts = None

            price = last["close"]
            forecast_val = lstm_forecast(df_ind) or price
            delta = forecast_val - price

            action = tm.evaluate(last, sentiment_score)
            tm.execute(action, price, last, sentiment_score)

            message = (
                f"📊 Update:\n"
                f"Price={price:.4f}, RSI={last.rsi:.2f}, MACDh={last.macd_hist:.4f}\n"
                f"Forecast={forecast_val:.4f}, Δ={delta:.4f}, Sentiment={sentiment_score if sentiment_score is not None else 'NA'}\n"
                f"ADX={last.adx:.1f}, ATR={last.atr:.2f}, Trend={trend}, Action={action}"
            )
            print(message)
            send_telegram_message(message)

        except Exception as e:
            logging.error("Errore nel ciclo: %s", e)

        time.sleep(LOOP_SECONDS)

if __name__ == "__main__":
    main()

# backtest.py – Valutazione offline del modello LSTM
# --------------------------------------------------
import os, json
import matplotlib.pyplot as plt
import pandas as pd

from modules.data_fetcher   import get_binance_connection, fetch_ohlcv
from modules.indicators     import add_indicators
from modules.lstm_predictor import predict_with_model
from modules.sentiment      import get_twitter_sentiment, get_reddit_sentiment, combined_sentiment

CFG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
with open(CFG_PATH, encoding="utf-8") as f:
    cfg = json.load(f)

# Sentiment medio (Twitter + Reddit)
tw = get_twitter_sentiment(cfg["twitter_bearer_token"], query="polkadot")
rd = get_reddit_sentiment(
        cfg["reddit_client_id"],
        cfg["reddit_client_secret"],
        cfg["reddit_user_agent"],
        query="polkadot")
sent = combined_sentiment(tw, rd)

# Prezzi da Binance
ex = get_binance_connection(cfg["api_key"], cfg["api_secret"])
df = fetch_ohlcv(ex, symbol="DOT/USDT", limit=200)
df = add_indicators(df)

# Feature richieste dal modello
df["pct_change"] = df["close"].pct_change()
df["vol_ma"]     = df["volume"].rolling(5).mean()
df["atr"]        = df["ATR"]          # copia minuscola
df["sentiment"]  = sent
df.dropna(inplace=True)

# Previsione
df["forecast"] = predict_with_model(df)

# Grafico
plt.figure(figsize=(12, 6))
plt.plot(df["close"],    label="Prezzo reale", alpha=.55)
plt.plot(df["forecast"], label="Forecast LSTM", linestyle="--")
plt.title("Back-test DOT/USDT – modello LSTM")
plt.legend(); plt.grid(True); plt.tight_layout()
plt.show()

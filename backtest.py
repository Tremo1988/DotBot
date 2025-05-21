import matplotlib.pyplot as plt
import pandas as pd

from modules.config_loader     import get
from modules.data_fetcher      import get_binance_connection, fetch_ohlcv
from modules.indicators        import add_indicators
from modules.lstm_predictor    import predict_with_model
from modules.sentiment         import combined_sentiment

# ─── Config ─────────────────────────────────────────────────────────────────────
cfg       = get()
symbol    = cfg["symbol"]
timeframe = cfg.get("backtest_timeframe", cfg.get("timeframe", "30m"))
limit     = cfg.get("backtest_limit", 500)
base_name = symbol.split("/")[0].lower()

# ─── Fetch dati e indicatori ────────────────────────────────────────────────────
ex = get_binance_connection()
df = fetch_ohlcv(ex, symbol, timeframe, limit=limit)
df = add_indicators(df)
df["forecast"] = predict_with_model(df)

# ─── Prepara indice temporale ───────────────────────────────────────────────────
if not isinstance(df.index, pd.DatetimeIndex):
    df.index = pd.to_datetime(df["timestamp"], unit="ms")
df = df.set_index(df.index)

# ─── Rolling 30D realistico solo se dati ≥ 30 giorni ───────────────────────────
if (df.index.max() - df.index.min()).days >= 30:
    df_resampled = df.resample("30D").agg({
        "close":    "last",
        "forecast": "last"
    })
else:
    df_resampled = df[["close", "forecast"]].copy()

# ─── Calcolo sentiment UNA VOLTA (no ban Google) ───────────────────────────────
sentiment_val = combined_sentiment(
    subreddit=cfg.get("reddit_subreddit", base_name),
    trend_keyword="polkadot",
    token="polkadot",
    weights=(0.5, 0.3, 0.2)
)
df_resampled["sentiment"] = sentiment_val

# ─── Rimuovi righe senza dati ───────────────────────────────────────────────────
df_resampled = df_resampled.dropna(subset=["close", "forecast"])

# ─── Plot ───────────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()

ax1.plot(df_resampled.index, df_resampled["close"],    label="Prezzo reale", alpha=0.7)
ax1.plot(df_resampled.index, df_resampled["forecast"], label="Forecast LSTM", linestyle="--", color="orange")
ax2.plot(df_resampled.index, df_resampled["sentiment"], label="Sentiment (combined)", color="green", linewidth=2)

ax1.set_title(f"Backtest {symbol} – timeframe {timeframe} – Sentiment statico")
ax1.set_xlabel("Data")
ax1.set_ylabel("Prezzo (USDC)")
ax2.set_ylabel("Sentiment (0–1)")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

ax1.grid(True)
plt.tight_layout()
plt.show()

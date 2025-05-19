
import ccxt
import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
import datetime

# === CONFIG ========================================================
SYMBOL = "DOT/USDT"
TIMEFRAME = "1h"
LIMIT = 1500
SEQUENCE_LENGTH = 48
MODEL_PATH = "lstm_model.h5"
TWITTER_BEARER = "AAAAAAAAAAAAAAAAAAAAAIjX1AEAAAAAtG%2F2KAOx9jvbxn0B6DurJa%2F5o3M%3DglbZnqX9cGT7U4txrFysvR9BBAjkjXGPPDShNNwgvk66jrSCLM"

def fetch_sentiment_score(query="polkadot"):
    try:
        headers = {"Authorization": f"Bearer {TWITTER_BEARER}"}
        url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=20"
        r = requests.get(url, headers=headers)
        tweets = r.json().get("data", [])
        if not tweets: return 0.0
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        import nltk
        nltk.download("vader_lexicon", quiet=True)
        sia = SentimentIntensityAnalyzer()
        scores = [sia.polarity_scores(t['text'])['compound'] for t in tweets]
        return np.mean(scores)
    except:
        return 0.0

print("Scarico dati da Binance...")
exchange = ccxt.binance()
ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=LIMIT)
df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df.set_index("timestamp", inplace=True)

# === FEATURE ENGINEERING ==========================================
df["pct_change"] = df["close"].pct_change()
df["vol_ma"] = df["volume"].rolling(window=5).mean()
df["tr"] = np.maximum(df["high"] - df["low"], 
                      np.maximum(abs(df["high"] - df["close"].shift()), abs(df["low"] - df["close"].shift())))
df["atr"] = df["tr"].rolling(window=14).mean()
df.dropna(inplace=True)

# Aggancia sentiment (valore costante per tutta la serie)
print("Rilevo sentiment Twitter...")
sentiment = fetch_sentiment_score()
df["sentiment"] = sentiment

features = ["close", "pct_change", "vol_ma", "atr", "sentiment"]
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[features])

# === SEQUENCING ====================================================
X, y = [], []
for i in range(SEQUENCE_LENGTH, len(scaled)):
    X.append(scaled[i-SEQUENCE_LENGTH:i])
    y.append(scaled[i, 0])
X, y = np.array(X), np.array(y)

# === MODEL =========================================================
print("Costruzione modello...")
model = Sequential()
model.add(Bidirectional(LSTM(64, return_sequences=True), input_shape=(X.shape[1], X.shape[2])))
model.add(Dropout(0.3))
model.add(Bidirectional(LSTM(64)))
model.add(Dropout(0.3))
model.add(Dense(32, activation="relu"))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")

# === TRAIN =========================================================
print("Addestramento...")
es = EarlyStopping(patience=5, restore_best_weights=True)
model.fit(X, y, epochs=40, batch_size=32, validation_split=0.2, callbacks=[es], verbose=1)

# === EVAL ==========================================================
pred = model.predict(X, verbose=0)
pred_rescaled = scaler.inverse_transform(np.hstack([pred, np.zeros((len(pred), len(features)-1))]))[:,0]
y_rescaled = scaler.inverse_transform(np.hstack([y.reshape(-1,1), np.zeros((len(y), len(features)-1))]))[:,0]
rmse = np.sqrt(mean_squared_error(y_rescaled, pred_rescaled))
print(f"📊 RMSE finale: {rmse:.4f} USDT")

# === SAVE ==========================================================
model.save(MODEL_PATH)
print(f"✅ Modello salvato in {MODEL_PATH}")

plt.figure(figsize=(10,5))
plt.plot(y_rescaled[-200:], label="Reale")
plt.plot(pred_rescaled[-200:], label="Previsto")
plt.legend()
plt.title("Validazione finale")
plt.tight_layout()
plt.savefig("validation_plot_advanced.png")
print("📈 Grafico salvato in validation_plot_advanced.png")

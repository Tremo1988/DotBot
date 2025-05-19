
import ccxt
import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
import datetime

SYMBOL = "DOT/USDT"
TIMEFRAME = "1h"
LIMIT = 1500
SEQUENCE_LENGTH = 48
MODEL_PATH = "lstm_model.h5"
TWITTER_BEARER = "INSERISCI_TWITTER_TOKEN"

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

print("📅 Weekly LSTM advanced update —", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

exchange = ccxt.binance()
ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=LIMIT)
df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df.set_index("timestamp", inplace=True)

df["pct_change"] = df["close"].pct_change()
df["vol_ma"] = df["volume"].rolling(window=5).mean()
df["tr"] = np.maximum(df["high"] - df["low"], np.maximum(abs(df["high"] - df["close"].shift()), abs(df["low"] - df["close"].shift())))
df["atr"] = df["tr"].rolling(window=14).mean()
df.dropna(inplace=True)

sentiment = fetch_sentiment_score()
df["sentiment"] = sentiment

features = ["close", "pct_change", "vol_ma", "atr", "sentiment"]
scaler = MinMaxScaler()
scaled = scaler.fit_transform(df[features])

X, y = [], []
for i in range(SEQUENCE_LENGTH, len(scaled)):
    X.append(scaled[i-SEQUENCE_LENGTH:i])
    y.append(scaled[i, 0])
X, y = np.array(X), np.array(y)

model = Sequential()
model.add(Bidirectional(LSTM(64, return_sequences=True), input_shape=(X.shape[1], X.shape[2])))
model.add(Dropout(0.3))
model.add(Bidirectional(LSTM(64)))
model.add(Dropout(0.3))
model.add(Dense(32, activation="relu"))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")

es = EarlyStopping(patience=5, restore_best_weights=True)

print("🧠 Training advanced LSTM model…")
model.fit(X, y, epochs=30, batch_size=32, validation_split=0.2, callbacks=[es], verbose=1)

model.save(MODEL_PATH)
print(f"✅ Model updated and saved: {MODEL_PATH}")

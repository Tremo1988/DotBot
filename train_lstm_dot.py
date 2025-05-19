
"""
train_lstm_dot.py
=================

Script to train an advanced LSTM model on historical DOT/USDT data
downloaded from Binance via ccxt. The trained model is saved as
`lstm_model.h5` in the current directory.

Usage (inside your virtualenv):

    pip install ccxt pandas numpy scikit-learn tensorflow keras matplotlib
    python train_lstm_dot.py

Adjust HYPERPARAMS section as desired.
"""

import ccxt
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt
import os
import datetime

# ========= CONFIG ============================================================
SYMBOL = "DOT/USDT"
TIMEFRAME = "1h"          # 1‑hour candles
LIMIT = 2000              # max candles (Binance limit 1500/2000)
SEQUENCE_LENGTH = 60      # timesteps fed to LSTM
TEST_SPLIT = 0.2          # 20% data for validation
MODEL_PATH = "lstm_model.h5"

# ========= DOWNLOAD DATA =====================================================
print("Downloading historical data from Binance…")
binance = ccxt.binance({"enableRateLimit": True})
ohlcv = binance.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=LIMIT)
df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df.set_index("timestamp", inplace=True)
close_prices = df["close"].values.reshape(-1,1)

# ========= PREPROCESS ========================================================
scaler = MinMaxScaler(feature_range=(0,1))
scaled_prices = scaler.fit_transform(close_prices)

X, y = [], []
for i in range(SEQUENCE_LENGTH, len(scaled_prices)):
    X.append(scaled_prices[i-SEQUENCE_LENGTH:i, 0])
    y.append(scaled_prices[i, 0])

X, y = np.array(X), np.array(y)
X = X.reshape((X.shape[0], X.shape[1], 1))

# Train‑test split
split_index = int(len(X) * (1 - TEST_SPLIT))
X_train, X_val = X[:split_index], X[split_index:]
y_train, y_val = y[:split_index], y[split_index:]

# ========= MODEL =============================================================
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(SEQUENCE_LENGTH,1)),
    Dropout(0.2),
    LSTM(64),
    Dropout(0.2),
    Dense(32, activation="relu"),
    Dense(1)
])
model.compile(optimizer="adam", loss="mse")

es = EarlyStopping(patience=5, restore_best_weights=True)

print("Training model…")
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=[es],
    verbose=1
)

# ========= EVALUATION ========================================================
val_pred = model.predict(X_val, verbose=0)
val_pred_rescaled = scaler.inverse_transform(val_pred)
y_val_rescaled = scaler.inverse_transform(y_val.reshape(-1,1))
rmse = np.sqrt(mean_squared_error(y_val_rescaled, val_pred_rescaled))
print(f"Validation RMSE: {rmse:,.4f} USDT")

# ========= SAVE MODEL ========================================================
model.save(MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")

# ========= OPTIONAL PLOT =====================================================
plt.figure(figsize=(10,4))
plt.plot(df.index[-len(y_val):], y_val_rescaled, label="Actual")
plt.plot(df.index[-len(val_pred):], val_pred_rescaled, label="Predicted")
plt.title("DOT/USDT Price Prediction (validation)")
plt.legend()
plt.tight_layout()
plt.savefig("validation_plot.png")
print("Validation plot saved to validation_plot.png")

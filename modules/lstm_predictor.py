"""Carica lstm_model.h5 se presente e produce forecast prezzo T+1."""
from pathlib import Path
import numpy as np
import pandas as pd

try:
    from keras.models import load_model
except ModuleNotFoundError:
    load_model = None

MODEL_PATH = Path("lstm_model.h5")

def forecast(df: pd.DataFrame):
    """
    Restituisce la previsione del prezzo T+1 usando il modello LSTM.
    Se il modello o il file non esistono, torna None.
    """
    if not (load_model and MODEL_PATH.exists()):
        return None

    model = load_model(MODEL_PATH, compile=False)

    # estrai gli ultimi 60 valori come float32
    seq = df["close"].values[-60:].astype(np.float32)

    mean = seq.mean()
    std = seq.std()

    if std == 0:
        return float(seq[-1])  # fallback se prezzi fissi

    seq_norm = (seq - mean) / std
    pred = model.predict(seq_norm.reshape(1, -1, 1), verbose=0)

    # denormalizza il risultato
    return float(pred[0][0] * std + mean)

# Alias per compatibilità con backtest.py
predict_with_model = forecast

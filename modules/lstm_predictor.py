
"""Carica lstm_model.h5 se presente e produce forecast prezzo T+1."""
from pathlib import Path
import numpy as np, pandas as pd

try:
    from keras.models import load_model
except ModuleNotFoundError:
    load_model=None

MODEL_PATH = Path("lstm_model.h5")

def forecast(df: pd.DataFrame):
    if not (load_model and MODEL_PATH.exists()):
        return None
    model = load_model(MODEL_PATH, compile=False)
    seq = df["close"].values[-60:]  # assume finestra 60
    seq = (seq - seq.mean())/seq.std()
    pred = model.predict(seq.reshape(1,-1,1), verbose=0)
    return float(pred[0][0])

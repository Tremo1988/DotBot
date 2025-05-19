# ───────── modules/indicators.py ──────────
import pandas as pd
import ta

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # RSI
    df["rsi"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()

    # ADX
    adx = ta.trend.ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=14)
    df["adx"] = adx.adx()

    # ATR
    df["atr"] = ta.volatility.AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=14).average_true_range()

    # Moving Average Volume
    df["vol_ma"] = df["volume"].rolling(window=14).mean()

    # Segnale per LSTM
    df["signal"] = df["close"].pct_change().apply(lambda x: 1 if x > 0.005 else (-1 if x < -0.005 else 0))
    df["signal"].fillna(0, inplace=True)

    return df

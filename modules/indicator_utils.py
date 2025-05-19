
import pandas as pd, pandas_ta as ta
from .lstm_predictor import forecast

def add_indicators(df: pd.DataFrame):
    df['rsi'] = ta.rsi(df['close'], length=14)
    macd = ta.macd(df['close'])
    df['macd_hist'] = macd['MACDh_12_26_9']
    df['adx'] = ta.adx(df['high'], df['low'], df['close'])['ADX_14']
    df['atr'] = ta.atr(df['high'], df['low'], df['close'])
    df['sma50'] = ta.sma(df['close'], length=50)
    df['forecast_price'] = forecast(df) or df['close']  # fallback
    return df

def compute_trend(row):
    up = row['close'] > row['sma50']*1.002
    down = row['close'] < row['sma50']*0.998
    if up: return "bullish"
    if down: return "bearish"
    return "sideways"

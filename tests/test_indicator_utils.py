import pandas as pd
import numpy as np
import pytest
from modules.indicator_utils import add_indicators, compute_trend

@pytest.fixture
def sample_df():
    # Genera 60 righe di dati OHLC sintetici
    np.random.seed(0)
    price = np.cumsum(np.random.randn(60)) + 100
    df = pd.DataFrame({
        'open':  price,
        'high':  price + np.random.rand(60),
        'low':   price - np.random.rand(60),
        'close': price,
    })
    return df

def test_add_indicators_columns(sample_df):
    df = add_indicators(sample_df.copy())
    # Controlla presenza colonne
    for col in ['rsi', 'macd_hist', 'adx', 'atr', 'sma50', 'forecast_price']:
        assert col in df.columns
    # Verifica che nell’ultima riga non ci siano NaN
    last = df.iloc[-1]
    assert not pd.isna(last['rsi'])
    assert not pd.isna(last['macd_hist'])
    assert not pd.isna(last['adx'])
    assert not pd.isna(last['atr'])
    assert not pd.isna(last['sma50'])

def test_compute_trend(sample_df):
    df = add_indicators(sample_df.copy())
    # Forza bullish
    df.at[df.index[-1], 'close'] = df.at[df.index[-1], 'sma50'] * 1.01
    assert compute_trend(df.iloc[-1]) == 'bullish'
    # Forza bearish
    df.at[df.index[-1], 'close'] = df.at[df.index[-1], 'sma50'] * 0.99
    assert compute_trend(df.iloc[-1]) == 'bearish'
    # Sideways
    df.at[df.index[-1], 'close'] = df.at[df.index[-1], 'sma50']
    assert compute_trend(df.iloc[-1]) == 'sideways'

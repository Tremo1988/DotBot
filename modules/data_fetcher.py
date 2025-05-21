"""Robust data_fetcher with credentials support."""
from __future__ import annotations
from typing import Optional
import ccxt, os, logging
from pathlib import Path
import pandas as pd
from modules.config_loader import get

def get_binance_connection() -> ccxt.binance:
    """Create a ccxt Binance instance using .env or config.defaults.json"""
    cfg = get()

    api_key = os.getenv("BINANCE_API_KEY") or cfg.get("binance_api_key") or cfg.get("api_key")
    api_secret = os.getenv("BINANCE_API_SECRET") or cfg.get("binance_api_secret") or cfg.get("api_secret")

    credentials = {
        'enableRateLimit': True,
        'options': {'adjustForTimeDifference': True},
    }

    if api_key and api_secret:
        credentials.update({
            'apiKey': api_key,
            'secret': api_secret,
        })
    else:
        logging.warning("⚠️ Binance api_key/secret not found – avvio in modalità simulata (no signed endpoints)")

    return ccxt.binance(credentials)

def _to_dataframe(ohlcv):
    cols = ["timestamp", "open", "high", "low", "close", "volume"]
    df = pd.DataFrame(ohlcv, columns=cols)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

def fetch_ohlcv(ex: ccxt.binance, symbol: str, timeframe: str, limit: int = 500) -> pd.DataFrame:
    """Download OHLCV and return DataFrame with same columns."""
    ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    return _to_dataframe(ohlcv)

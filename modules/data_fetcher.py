"""Robust data_fetcher with credentials support."""
from __future__ import annotations
from typing import Optional
import ccxt, json, logging
from pathlib import Path
import pandas as pd

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
try:
    _cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
except Exception:
    _cfg = {}

def get_binance_connection() -> ccxt.binance:
    """Create a ccxt Binance instance; if api_key/secret are in config.json, attach them."""
    credentials = {
        'enableRateLimit': True,
        'options': {'adjustForTimeDifference': True},
    }
    if _cfg.get("api_key") and _cfg.get("api_secret"):
        credentials.update({
            'apiKey': _cfg["api_key"],
            'secret': _cfg["api_secret"],
        })
    else:
        logging.warning("Binance api_key/secret not found – running in paper‑mode (no signed endpoints).")
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

# backtest.py
from modules.data_fetcher import fetch_ohlcv
from modules.lstm_predictor import predict_with_model
from modules.indicators import add_indicators
import matplotlib.pyplot as plt
import pandas as pd

df = fetch_ohlcv("DOT/USDT", limit=200)
df = add_indicators(df)
df['forecast'] = predict_with_model(df)

plt.figure(figsize=(12, 6))
plt.plot(df['close'], label='Real Price', alpha=0.5)
plt.plot(df['forecast'], label='Forecasted Price', linestyle='--')
plt.title('Backtest Forecast vs Real Price')
plt.legend()
plt.grid()
plt.show()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run a quick backtest on DOT.")
    parser.add_argument("--symbol", default="DOT/USDT", help="Symbol to back‑test (default DOT/USDT)")
    parser.add_argument("--limit", type=int, default=200, help="Number of candles to fetch (default 200)")
    args = parser.parse_args()

    df = fetch_ohlcv(args.symbol, limit=args.limit)
    df = add_indicators(df)
    df['forecast'] = predict_with_model(df)

    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 6))
    plt.plot(df['close'], label='Real Price', alpha=0.5)
    plt.plot(df['forecast'], label='Forecasted Price', linestyle='--')
    plt.title(f'Backtest Forecast vs Real Price – {args.symbol}')
    plt.legend()
    plt.grid()
    plt.show()

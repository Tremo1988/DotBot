
import os
import ccxt
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print("❌ ERRORE: Chiave API o segreta mancante nel file .env")
        return

    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True
    })

    try:
        balance = exchange.fetch_balance()
        print("✅ Bilanci trovati (wallet Spot):\n")
        for asset, amount in balance['total'].items():
            if amount and amount > 0:
                print(f"→ {asset}: {amount}")
    except Exception as e:
        print(f"❌ Errore durante la richiesta a Binance: {str(e)}")

if __name__ == "__main__":
    main()

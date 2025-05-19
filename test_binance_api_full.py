import os, ccxt, json

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

if not API_KEY or not API_SECRET:
    raise RuntimeError("Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables before running this test.")


import ccxt


def test_binance_apis():
    try:
        exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })

        print("🔍 Verifica conto SPOT:")
        balance = exchange.fetch_balance()
        print("✅ Accesso SPOT riuscito.")
        for asset, val in balance['total'].items():
            if val:
                print(f" - {asset}: {val}")

        print("\n🔍 Verifica conto MARGIN:")
        try:
            margin_balance = exchange.sapi_get_margin_account()
            print("✅ Accesso MARGIN riuscito.")
        except Exception as e:
            print("❌ Accesso MARGIN fallito:", e)

        print("\n🔍 Verifica conto FUTURES:")
        try:
            futures_exchange = ccxt.binanceusdm({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True
            })
            futures_balance = futures_exchange.fetch_balance()
            print("✅ Accesso FUTURES riuscito.")
        except Exception as e:
            print("❌ Accesso FUTURES fallito:", e)

    except ccxt.AuthenticationError:
        print("❌ Errore di autenticazione API.")
    except Exception as e:
        print("❌ Errore generico:", e)

if __name__ == "__main__":
    test_binance_apis()
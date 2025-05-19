import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Carica .env automaticamente
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Percorso al file di default dei parametri “pubblici”
DEFAULTS_PATH = Path(__file__).parent.parent / "config.defaults.json"

def get(key=None):
    """
    Se chiamato senza argomenti, restituisce l'intero dict di configurazione.
    Se key è fornita, restituisce solo quel valore.
    """
    # Carica i parametri pubblici
    with open(DEFAULTS_PATH, encoding="utf-8") as f:
        cfg = json.load(f)

    # Sovrascrive/add variabili da .env
    cfg.update({
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_chat_id":    os.getenv("TELEGRAM_CHAT_ID"),
        "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN"),
        "reddit_client_id":    os.getenv("REDDIT_CLIENT_ID"),
        "reddit_client_secret":os.getenv("REDDIT_CLIENT_SECRET"),
        "reddit_user_agent":   os.getenv("REDDIT_USER_AGENT"),
        # CCXT Binance
        "binance_api_key":     os.getenv("BINANCE_API_KEY"),
        "binance_api_secret":  os.getenv("BINANCE_API_SECRET"),
    })

    if key:
        return cfg.get(key)
    return cfg

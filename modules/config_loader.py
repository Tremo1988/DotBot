import os
import json
from pathlib import Path
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

# Carica automaticamente il .env in root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Percorso al file di default dei parametri “pubblici”
DEFAULTS_PATH = Path(__file__).parent.parent / "config.defaults.json"

# Schema di validazione per config.defaults.json
SCHEMA = {
    "type": "object",
    "properties": {
        "symbol":                  {"type": "string"},
        "timeframe":               {"type": "string"},
        "sell_threshold_percent":  {"type": "number"},
        "min_dot_to_sell":         {"type": "number"},
        "stop_loss_pct":           {"type": "number"},
        "trailing_stop_pct":       {"type": "number"},
        "stop_loss_atr_mult":      {"type": "number"},
        "trailing_atr_mult":       {"type": "number"},
        "min_adx_trend":           {"type": "number"},
        "min_adx_operativita":     {"type": "number"},
        "reddit_keywords":         {"type": "array", "items": {"type": "string"}},
        "reddit_subreddit":        {"type": "string"},
        "risk_per_trade":          {"type": "number"},
        "fee_pct":                 {"type": "number"},
        "slippage_pct":            {"type": "number"},
        "max_drawdown_pct":        {"type": "number"}
    },
    "required": ["symbol", "timeframe", "sell_threshold_percent", "risk_per_trade"]
}

def get(key=None):
    """
    Se chiamato senza argomenti, restituisce l'intero dict di configurazione.
    Se key è fornita, restituisce solo quel valore.
    """
    # Carica defaults e valida
    raw_cfg = json.loads(DEFAULTS_PATH.read_text())
    try:
        validate(instance=raw_cfg, schema=SCHEMA)
    except ValidationError as e:
        raise RuntimeError(f"Errore di validazione config: {e.message}")

    # Merge fra defaults e variabili d'ambiente
    cfg = raw_cfg.copy()
    cfg.update({
        "telegram_bot_token":    os.getenv("TELEGRAM_BOT_TOKEN"),
        "telegram_chat_id":      os.getenv("TELEGRAM_CHAT_ID"),
        "twitter_bearer_token":  os.getenv("TWITTER_BEARER_TOKEN"),
        "reddit_client_id":      os.getenv("REDDIT_CLIENT_ID"),
        "reddit_client_secret":  os.getenv("REDDIT_CLIENT_SECRET"),
        "reddit_user_agent":     os.getenv("REDDIT_USER_AGENT"),
        "binance_api_key":       os.getenv("BINANCE_API_KEY"),
        "binance_api_secret":    os.getenv("BINANCE_API_SECRET"),
    })

    return cfg if key is None else cfg.get(key)

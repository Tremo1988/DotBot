
import json, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
_cfg = {}
if CONFIG_PATH.exists():
    try:
        _cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        _cfg = {}

def get(key=None, default=None):
    """
    - If key is None, returns the full config dict.
    - Otherwise returns environment var or config value.
    """
    if key is None:
        return _cfg
    return os.getenv(key.upper()) or _cfg.get(key, default)

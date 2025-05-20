from __future__ import annotations
import requests
import logging
from textblob import TextBlob
from modules.config_loader import get

# ─── User-Agent ────────────────────────────────────────────────────────────────
_user_agent = get("reddit_user_agent") or "DotBotSentiment/2.0"
HEADERS = {"User-Agent": _user_agent}

# ─── Default subreddit e parole chiave ──────────────────────────────────────────
DEFAULT_SUBREDDIT = get("reddit_subreddit") or "Polkadot"
DEFAULT_KEYWORDS  = get("reddit_keywords") or ["polkadot", "dot", "parachain"]

def _fetch_json(subreddit: str, q: str, limit: int = 100):
    """
    Ritorna i post JSON dalla search API di Reddit per una data parola chiave.
    """
    url = (
        f"https://www.reddit.com/r/{subreddit}/search.json"
        f"?q={q}&restrict_sr=1&sort=new&limit={limit}"
    )
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json().get("data", {}).get("children", [])

def get_reddit_sentiment(
    subreddit: str | None = None,
    limit: int = 100
) -> tuple[float | None, int]:
    """
    Calcola la sentiment polarity media dei titoli degli ultimi `limit` post
    su ciascuna parola chiave in DEFAULT_KEYWORDS, nel subreddit specificato
    o, se non fornito, in DEFAULT_SUBREDDIT.
    Ritorna (avg_polarity, numero_totale_post).
    """
    sr = subreddit or DEFAULT_SUBREDDIT
    scores: list[float] = []
    n_posts = 0

    for kw in DEFAULT_KEYWORDS:
        try:
            posts = _fetch_json(sr, kw, limit)
            n_posts += len(posts)
            for p in posts:
                title = p["data"].get("title", "")
                scores.append(TextBlob(title).sentiment.polarity)
        except Exception as e:
            logging.warning("Sentiment fetch error [%s] / %r: %s", sr, kw, e)

    if not scores:
        return None, 0

    return sum(scores) / len(scores), n_posts


from __future__ import annotations
import requests, logging
from textblob import TextBlob
from .config_loader import get

HEADERS = {"User-Agent": get("reddit_user_agent", "DotBotSentiment/2.0")}

KEYWORDS = get("reddit_keywords", ["polkadot", "dot", "parachain"])
SUBREDDIT = get("reddit_subreddit", "Polkadot")

def _fetch_json(q: str, limit: int = 100):
    url = f"https://www.reddit.com/r/{SUBREDDIT}/search.json?q={q}&restrict_sr=1&sort=new&limit={limit}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json().get("data", {}).get("children", [])

def get_reddit_sentiment(limit=100) -> tuple[float|None,int]:
    scores, n_posts = [], 0
    for kw in KEYWORDS:
        try:
            posts = _fetch_json(kw, limit)
            n_posts += len(posts)
            scores.extend(TextBlob(p["data"]["title"]).sentiment.polarity for p in posts)
        except Exception as e:
            logging.warning("Sentiment fetch error %s: %s", kw, e)
    if not scores:
        return None, 0
    return sum(scores)/len(scores), n_posts

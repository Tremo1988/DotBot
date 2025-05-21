import logging
import requests
from modules.config_loader import get

SENTIMENT_LOG_LEVEL = logging.WARNING  # cambia in INFO se vuoi più dettagli

# ──────────────── REDDIT (OAuth - PRAW) ────────────────
def get_reddit_sentiment(subreddit: str) -> float:
    try:
        import praw

        reddit = praw.Reddit(
            client_id=get("reddit_client_id"),
            client_secret=get("reddit_client_secret"),
            user_agent=get("reddit_user_agent"),
            username=get("reddit_username"),
            password=get("reddit_password"),
        )

        keywords = get("reddit_keywords") or []
        if not keywords:
            logging.log(SENTIMENT_LOG_LEVEL, "Nessuna keyword reddit configurata")
            return None

        total_score = 0.0
        count = 0
        for kw in keywords:
            posts = reddit.subreddit(subreddit).search(kw, sort="new", limit=100)
            score = sum(1 for _ in posts) / 100.0
            total_score += score
            count += 1

        return round((total_score / count), 4) if count else None
    except Exception as e:
        logging.log(SENTIMENT_LOG_LEVEL, "OAuth Reddit sentiment error: %s", e)
        return None

# ──────────────── GOOGLE TRENDS ────────────────
def get_google_trend_sentiment(keyword: str) -> float:
    try:
        from pytrends.request import TrendReq

        proxies = {}
        proxy_url = get("google_proxy")
        if proxy_url:
            proxies = {"https": proxy_url, "http": proxy_url}

        pytrends = TrendReq(hl='en-US', tz=360, proxies=proxies)
        pytrends.build_payload([keyword], cat=0, timeframe='now 7-d', geo='', gprop='')
        data = pytrends.interest_over_time()

        if data.empty or keyword not in data.columns:
            return None

        values = data[keyword].values
        return round(float(sum(values[-7:]) / 700.0), 4)
    except Exception as e:
        logging.log(SENTIMENT_LOG_LEVEL, "Google Trends sentiment error [%s]: %s", keyword, e)
        return None

# ──────────────── SUBSCAN ────────────────
def get_onchain_sentiment(token: str = "polkadot") -> float:
    try:
        url = "https://pro.api.subscan.io/api/scan/transfers"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": get("subscan_api_key") or ""
        }
        resp = requests.post(url, json={"row": 50, "page": 0}, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        count = len(data.get("data", {}).get("transfers", []))
        return round(min(count / 50.0, 1.0), 4)
    except Exception as e:
        logging.log(SENTIMENT_LOG_LEVEL, "Subscan sentiment error [%s]: %s", token, e)
        return None

# ──────────────── COMBINATO ────────────────
def combined_sentiment(
    subreddit="polkadot",
    trend_keyword="polkadot",
    token="polkadot",
    weights=(0.5, 0.3, 0.2)
) -> float:
    total_weight = 0.0
    total_score = 0.0

    sources = [
        (get_reddit_sentiment(subreddit), weights[0]),
        (get_google_trend_sentiment(trend_keyword), weights[1]),
        (get_onchain_sentiment(token), weights[2]),
    ]

    for val, weight in sources:
        if val is not None:
            total_score += val * weight
            total_weight += weight

    return round(total_score / total_weight, 4) if total_weight > 0 else 0.0

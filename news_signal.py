import requests
from config import NEWSAPI_KEY


POSITIVE_WORDS = [
    "growth",
    "surge",
    "record",
    "profit",
    "breakthrough",
    "deal",
    "expansion",
    "approval",
    "contract"
]

NEGATIVE_WORDS = [
    "loss",
    "risk",
    "decline",
    "investigation",
    "lawsuit",
    "crisis",
    "drop"
]


def get_news_signal(keyword):

    try:

        url = "https://newsapi.org/v2/everything"

        params = {
            "q": keyword,
            "language": "en",
            "pageSize": 20,
            "apiKey": NEWSAPI_KEY
        }

        r = requests.get(url, params=params)
        data = r.json()

        articles = data.get("articles", [])

        score = 0

        for a in articles:

            title = a.get("title", "").lower()

            for p in POSITIVE_WORDS:
                if p in title:
                    score += 1

            for n in NEGATIVE_WORDS:
                if n in title:
                    score -= 1

        return score

    except Exception:
        return 0
import requests
from config import NEWSAPI_KEY

def get_news_sentiment(keyword):

    if NEWSAPI_KEY == "":
        return 0

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": keyword,
        "language": "en",
        "pageSize": 20,
        "apiKey": NEWSAPI_KEY
    }

    try:

        r = requests.get(url, params=params)

        data = r.json()

        articles = data.get("articles", [])

        score = 0

        for a in articles:

            title = a.get("title", "").lower()

            if "growth" in title:
                score += 1

            if "risk" in title:
                score -= 1

        return score / 20

    except:

        return 0
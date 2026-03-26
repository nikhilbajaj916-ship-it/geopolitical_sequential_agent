# ─────────────────────────────────────────────
# tools/extractor_tools.py
# ─────────────────────────────────────────────
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from datetime import datetime, timedelta
from config import NEWS_API_KEY


def read_news(country: str, months: int = 24) -> dict:
    """Fetch latest news for a country from TheNewsAPI (past N months)."""

    published_after = (datetime.now() - timedelta(days=months * 30)).strftime("%Y-%m-%d")

    url = "https://api.thenewsapi.com/v1/news/all"
    params = {
        "search":          country,
        "language":        "en",
        "api_token":       NEWS_API_KEY,
        "limit":           10,
        "published_after": published_after,
        "sort":            "published_at",
    }

    print(f"[News] Fetching news for '{country}' after {published_after}")

    response = requests.get(url, params=params, timeout=10, verify=False)

    if response.status_code == 200:
        return response.json()

    return {"error": f"News API error: {response.status_code}", "data": []}


def read_wiki(wiki_title: str) -> dict:
    """Fetch full Wikipedia extract for a country (historical context)."""

    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action":       "query",
        "titles":       wiki_title,
        "prop":         "extracts",
        "explaintext":  True,
        "exsentences":  40,        # ~40 sentences of historical context
        "format":       "json",
    }

    print(f"[Wiki] Fetching Wikipedia article: '{wiki_title}'")

    headers = {"User-Agent": "GeoIntelBot/1.0 (research project; Python/requests)"}
    response = requests.get(url, params=params, headers=headers, timeout=10, verify=False)

    if response.status_code == 200:
        data  = response.json()
        pages = data.get("query", {}).get("pages", {})
        page  = next(iter(pages.values()), {})

        return {
            "title":   page.get("title", wiki_title),
            "extract": page.get("extract", ""),
        }

    return {"error": f"Wiki API error: {response.status_code}", "title": wiki_title, "extract": ""}

# ─────────────────────────────────────────────
# tools/transform_tools.py
# ─────────────────────────────────────────────

# ── Top 20 geopolitical countries ──
COUNTRIES = [
    "united states", "usa", "china", "russia", "india",
    "germany", "united kingdom", "uk", "france", "japan",
    "brazil", "south korea", "iran", "saudi arabia", "israel",
    "turkey", "pakistan", "north korea", "ukraine", "australia",
    "canada", "italy",
]

# ── Wikipedia-friendly title mapping ──
WIKI_TITLES = {
    "united states": "United_States",
    "usa":           "United_States",
    "china":         "China",
    "russia":        "Russia",
    "india":         "India",
    "germany":       "Germany",
    "united kingdom":"United_Kingdom",
    "uk":            "United_Kingdom",
    "france":        "France",
    "japan":         "Japan",
    "brazil":        "Brazil",
    "south korea":   "South_Korea",
    "iran":          "Iran",
    "saudi arabia":  "Saudi_Arabia",
    "israel":        "Israel",
    "turkey":        "Turkey",
    "pakistan":      "Pakistan",
    "north korea":   "North_Korea",
    "ukraine":       "Ukraine",
    "australia":     "Australia",
    "canada":        "Canada",
    "italy":         "Italy",
}

EVENTS = ["election", "war", "growth", "crisis", "inflation",
          "sanctions", "conflict", "protest", "deal", "trade"]


def extract_entities(text: str) -> dict:
    lower = text.lower()

    # Multi-word countries first (order matters)
    country = next((c for c in COUNTRIES if c in lower), None)
    event   = next((e for e in EVENTS   if e in lower), None)

    display = country.title() if country else None

    return {
        "country":    display,
        "country_raw": country,          # lowercase key for lookups
        "wiki_title": WIKI_TITLES.get(country, display) if country else None,
        "event":      event,
    }


def transform_news(news_raw: dict) -> list:
    articles = news_raw.get("data", [])

    result = []
    for a in articles:
        text = f"{a.get('title', '')} {a.get('description', '')}".strip()
        if text:
            result.append({
                "text":     text,
                "url":      a.get("url", ""),
                "published": a.get("published_at", ""),
                "entities": extract_entities(text),
            })

    return result


def transform_wiki(wiki_raw: dict) -> dict:
    title   = wiki_raw.get("title", "")
    extract = wiki_raw.get("extract", "")
    text    = f"{title} {extract}".strip()

    return {
        "text":     text,
        "entities": extract_entities(text),
    }


def merge_sources(news_data: list, wiki_data: dict) -> dict:
    return {
        "news": news_data,
        "wiki": wiki_data,
    }

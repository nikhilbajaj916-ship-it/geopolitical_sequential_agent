# ─────────────────────────────────────────────
# tools/transform_tools.py
# ─────────────────────────────────────────────

import re
from config import TOP_20_COUNTRIES, COUNTRY_WIKI_TITLES

# ── Build lowercase → config-name mapping from config (single source of truth) ──
_LOWER_TO_CONFIG: dict = {c.lower(): c for c in TOP_20_COUNTRIES}

# Common aliases not covered by lowercase of config names
_LOWER_TO_CONFIG.update({
    "united states": "USA",
    "america":       "USA",
    "u.s.":          "USA",
    "united kingdom": "UK",
    "britain":       "UK",
    "great britain": "UK",
    "south korea":   "South Korea",
    "saudi arabia":  "Saudi Arabia",
})

# Sorted longest first so multi-word names match before single words
COUNTRIES = sorted(_LOWER_TO_CONFIG.keys(), key=len, reverse=True)

EVENTS = [
    "election", "war", "growth", "crisis", "inflation",
    "sanctions", "conflict", "protest", "deal", "trade",
    "startup", "investment", "roi", "gdp",
]


def extract_entities(text: str) -> dict:
    lower = text.lower()

    # Check uppercase abbreviations first (US, UK) to avoid false positives like "tell us"
    if re.search(r'\bUS\b', text):
        country_raw = "usa"
    elif re.search(r'\bUK\b', text):
        country_raw = "uk"
    else:
        # Word-boundary match on lowercase
        country_raw = next(
            (c for c in COUNTRIES if re.search(r'\b' + re.escape(c) + r'\b', lower)),
            None
        )

    event = next((e for e in EVENTS if e in lower), None)

    config_name = _LOWER_TO_CONFIG.get(country_raw) if country_raw else None
    wiki_title  = COUNTRY_WIKI_TITLES.get(config_name) if config_name else None

    return {
        "country":     config_name,
        "country_raw": country_raw,
        "wiki_title":  wiki_title,
        "event":       event,
    }


def transform_news(news_raw: dict) -> list:
    articles = news_raw.get("data", [])
    result   = []
    for a in articles:
        parts = [a.get("title", ""), a.get("description", ""), a.get("content", "")]
        text  = " ".join(p for p in parts if p).strip()
        if text:
            result.append({
                "text":      text,
                "url":       a.get("url", ""),
                "published": a.get("published_at", ""),
            })
    return result


def transform_wiki(wiki_raw: dict) -> dict:
    return {
        "text": wiki_raw.get("extract", "").strip(),
    }


def merge_sources(news_data: list, wiki_data: dict) -> dict:
    return {
        "news": news_data,
        "wiki": wiki_data,
    }

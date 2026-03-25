# ─────────────────────────────────────────────
# agents/extractor_agent.py
# ─────────────────────────────────────────────

import time
from state import PipelineState
from tools.extractor_tools import read_news, read_wiki
from tools.transform_tools import extract_entities
from services.cache_service import cache_service


class ExtractorAgent:

    def run(self, state: PipelineState) -> dict:
        start = time.time()

        print("[Extractor Agent] Starting...")

        query = state.get("query", "")

        # ── Step 1: reuse metadata set by controller (avoid re-extraction) ──
        meta       = state.get("metadata") or {}
        if meta.get("country_raw"):
            country    = meta["country_raw"]
            wiki_title = meta.get("wiki_title") or country
            event      = meta.get("event")
        else:
            entities   = extract_entities(query)
            country    = entities.get("country_raw") or query.lower()
            wiki_title = entities.get("wiki_title")  or query
            event      = entities.get("event")

        print(f"[Extractor Agent] country={country}  wiki_title={wiki_title}  event={event}")

        cache_hit = False

        # ── Step 2: Fetch NEWS (search with country name) ──
        news_key    = f"news:{country}"
        cached_news = cache_service.get(news_key)

        if cached_news:
            news      = cached_news
            cache_hit = True
        else:
            news = read_news(country)
            cache_service.set(news_key, news)

        # ── Step 3: Fetch WIKI (use proper Wikipedia title) ──
        wiki_key    = f"wiki:{wiki_title}"
        cached_wiki = cache_service.get(wiki_key)

        if cached_wiki:
            wiki      = cached_wiki
            cache_hit = True
        else:
            wiki = read_wiki(wiki_title)
            cache_service.set(wiki_key, wiki)

        elapsed = round(time.time() - start, 2)

        print(f"[Extractor Agent] Done ({elapsed}s)")

        return {
            "news_raw":  news,
            "wiki_raw":  wiki,
            "cache_hit": cache_hit,
            "metadata":  {"country": country, "wiki_title": wiki_title, "event": event},
            "timing":    {"extractor": elapsed},
        }


extractor = ExtractorAgent()

def extractor_agent(state: PipelineState):
    return extractor.run(state)

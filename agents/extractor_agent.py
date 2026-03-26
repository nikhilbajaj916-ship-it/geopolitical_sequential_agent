# ─────────────────────────────────────────────
# agents/extractor_agent.py
# ─────────────────────────────────────────────

import time
from state import PipelineState
from tools.extractor_tools import read_news, read_wiki
from tools.financial_tools import fetch_financial_data
from tools.transform_tools import extract_entities
from services.cache_service import cache_service


class ExtractorAgent:

    def run(self, state: PipelineState) -> dict:
        start = time.time()

        print("[Extractor Agent] Starting...")

        query = state.get("query", "")
        meta  = state.get("metadata") or {}

        if meta.get("country_raw"):
            country    = meta["country_raw"]
            wiki_title = meta.get("wiki_title") or country
            event      = meta.get("event")
            config_country = meta.get("country")
        else:
            entities       = extract_entities(query)
            country        = entities.get("country_raw") or query.lower()
            wiki_title     = entities.get("wiki_title") or query
            event          = entities.get("event")
            config_country = entities.get("country") or country

        print(f"[Extractor Agent] country={config_country}  wiki={wiki_title}")

        cache_hit = False

        # ── News ──
        news_key    = f"news:{country}"
        cached_news = cache_service.get(news_key)
        if cached_news:
            news      = cached_news
            cache_hit = True
        else:
            news = read_news(country)
            cache_service.set(news_key, news)

        # ── Wiki ──
        wiki_key    = f"wiki:{wiki_title}"
        cached_wiki = cache_service.get(wiki_key)
        if cached_wiki:
            wiki      = cached_wiki
            cache_hit = True
        else:
            wiki = read_wiki(wiki_title)
            cache_service.set(wiki_key, wiki)

        # ── Financial ──
        fin_key    = f"financial:{config_country}"
        cached_fin = cache_service.get(fin_key)
        if cached_fin:
            financial = cached_fin
        else:
            financial = fetch_financial_data(config_country)
            cache_service.set(fin_key, financial)

        elapsed = round(time.time() - start, 2)
        print(f"[Extractor Agent] Done ({elapsed}s)")

        return {
            "news_raw":       news,
            "wiki_raw":       wiki,
            "financial_data": financial,
            "cache_hit":      cache_hit,
            "metadata": {
                **state.get("metadata", {}),
                "country":     config_country,
                "country_raw": country,
                "wiki_title":  wiki_title,
                "event":       event,
            },
            "timing": {**state.get("timing", {}), "extractor": elapsed},
        }


extractor = ExtractorAgent()

def extractor_agent(state: PipelineState):
    return extractor.run(state)

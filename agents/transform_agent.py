# ─────────────────────────────────────────────
# agents/transform_agent.py
# ─────────────────────────────────────────────

import time
from state import PipelineState
from tools.transform_tools import transform_news, transform_wiki, merge_sources
from tools.financial_tools import financial_to_text


class TransformAgent:

    def run(self, state: PipelineState) -> dict:
        start = time.time()

        print("[Transform Agent] Starting...")

        news_raw       = state.get("news_raw") or {}
        wiki_raw       = state.get("wiki_raw") or {}
        financial_data = state.get("financial_data") or {}
        country        = (state.get("metadata") or {}).get("country", "")

        news   = transform_news(news_raw)
        wiki   = transform_wiki(wiki_raw)
        merged = merge_sources(news, wiki)

        # Add financial text so vector_rag can index it
        merged["financial_text"] = financial_to_text(country, financial_data)

        elapsed = round(time.time() - start, 2)
        print(f"[Transform Agent] Done — {len(news)} news items ({elapsed}s)")

        return {
            "transformed_data": merged,
            "timing":           {**state.get("timing", {}), "transform": elapsed},
        }


transform = TransformAgent()

def transform_agent(state: PipelineState):
    return transform.run(state)

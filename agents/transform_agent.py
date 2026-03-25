# ─────────────────────────────────────────────
# agents/transform_agent.py
# ─────────────────────────────────────────────

import time
from state import PipelineState
from tools.transform_tools import (
    transform_news,
    transform_wiki,
    merge_sources,
)


class TransformAgent:

    def run(self, state: PipelineState) -> dict:
        start = time.time()

        print("[Transform Agent] Starting...")

        news_raw = state.get("news_raw") or {}
        wiki_raw = state.get("wiki_raw") or {}

        news = transform_news(news_raw)
        wiki = transform_wiki(wiki_raw)

        merged = merge_sources(news, wiki)

        elapsed = round(time.time() - start, 2)

        print(f"[Transform Agent] Done ({elapsed}s)")

        return {
            "transformed_data": merged,
            "timing": {"transform": elapsed},
        }


transform = TransformAgent()

def transform_agent(state: PipelineState):
    return transform.run(state)
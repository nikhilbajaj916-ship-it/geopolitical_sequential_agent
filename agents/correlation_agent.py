# ─────────────────────────────────────────────
# agents/correlation_agent.py
# ─────────────────────────────────────────────

import time
from state import PipelineState
from tools.correlation_tools import build_correlation


class CorrelationAgent:

    def run(self, state: PipelineState) -> dict:
        start = time.time()

        print("[Correlation Agent] Starting...")

        data = state.get("transformed_data", {})
        news = data.get("news", [])
        wiki = data.get("wiki", {})
        query = state.get("query", "")

        result = build_correlation(query, news, wiki)

        elapsed = round(time.time() - start, 2)

        print(f"[Correlation Agent] Done ({elapsed}s)")

        return {
            "correlated_data": result,
            "timing": {"correlation": elapsed},
        }


correlation = CorrelationAgent()

def correlation_agent(state: PipelineState):
    return correlation.run(state)
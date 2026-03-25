# ─────────────────────────────────────────────
# agents/orchestrator_agent.py
#
# Purpose : Final analysis via LLM → OrchestratorOutput (Pydantic)
# ─────────────────────────────────────────────

import time
from datetime import datetime, timezone

from state import PipelineState
from services.llm_service import llm_service
from pydantic_response import OrchestratorOutput
from langchain_core.messages import SystemMessage, HumanMessage


class OrchestratorAgent:

    def run(self, state: PipelineState) -> dict:
        start = time.time()

        print("[Orchestrator Agent] Starting...")

        # ── Pull context from state ──
        query       = state.get("query", "")
        transformed = state.get("transformed_data") or {}
        rag_text    = state.get("context", "")
        now         = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # ── Wikipedia historical context ──
        wiki_text = (transformed.get("wiki") or {}).get("text", "No Wikipedia data available.")

        # ── Recent news lines ──
        news_items = transformed.get("news", [])
        news_text  = "\n".join(
            f"• [{item.get('published', '')[:10]}] {item['text']}"
            for item in news_items if item.get("text")
        ) or "No recent news available."

        # ── Build prompt ──
        messages = [
            SystemMessage(content=(
                f"You are a senior geopolitical analyst. Today is {now}. "
                "Fill every field of the structured output accurately based on the context provided."
            )),
            HumanMessage(content=(
                f"Query: {query}\n\n"
                f"═══ HISTORICAL CONTEXT (Wikipedia) ═══\n{wiki_text[:3000]}\n\n"
                f"═══ RECENT NEWS ═══\n{news_text}\n\n"
                f"═══ RAG CHUNKS ═══\n{rag_text}\n\n"
                "Fill the structured output:\n"
                "- historical_background : major events/trends over past 1-2 years\n"
                "- current_situation     : what is happening now per recent news\n"
                "- trend_assessment      : positive/negative/stable and why\n"
                "- recommendation        : one-line overall geopolitical outlook"
            )),
        ]

        # ── LLM → structured Pydantic output ──
        output: OrchestratorOutput = llm_service.generate_structured(messages, OrchestratorOutput)

        elapsed = round(time.time() - start, 2)
        print(f"[Orchestrator Agent] Done ({elapsed}s)")

        # ── Return state update ──
        return {
            "final_answer":   (
                f"HISTORICAL BACKGROUND\n{output.historical_background}\n\n"
                f"CURRENT SITUATION\n{output.current_situation}\n\n"
                f"TREND ASSESSMENT\n{output.trend_assessment}\n\n"
                f"RECOMMENDATION\n{output.recommendation}"
            ),
            "recommendation": output.recommendation,
            "timing":         {"orchestrator": elapsed},
        }


orchestrator = OrchestratorAgent()


def orchestrator_agent(state: PipelineState) -> dict:
    return orchestrator.run(state)

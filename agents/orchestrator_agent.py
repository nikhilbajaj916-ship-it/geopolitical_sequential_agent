# ─────────────────────────────────────────────
# agents/orchestrator_agent.py
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

        query      = state.get("query", "")
        query_type = state.get("query_type", "general")
        transformed = state.get("transformed_data") or {}
        rag_text    = state.get("context", "")
        correlated  = state.get("correlated_data") or {}
        pre_trend   = correlated.get("trend", "")
        now         = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        wiki_text  = (transformed.get("wiki") or {}).get("text", "No Wikipedia data available.")
        news_items = transformed.get("news", [])
        news_text  = "\n".join(
            f"• [{item.get('published', '')[:10]}] {item['text']}"
            for item in news_items if item.get("text")
        ) or "No recent news available."

        fin_text = transformed.get("financial_text", "") or ""

        # ── Financial query gets extra instruction ──
        fin_instruction = ""
        if query_type == "financial" or fin_text:
            fin_instruction = (
                "\n- financial_summary : Provide detailed financial analysis using the "
                "financial indicators below (GDP, FDI, inflation, ROI, stock performance). "
                "Include actual numbers from the data."
            )
        else:
            fin_instruction = "\n- financial_summary : Set to null (no financial data requested)"

        trend_block = f"═══ PRE-ANALYSIS TREND ═══\n{pre_trend}\n\n" if pre_trend else ""

        messages = [
            SystemMessage(content=(
                f"You are a senior geopolitical and investment analyst. Today is {now}. "
                "Fill every field of the structured output accurately based on the context provided."
            )),
            HumanMessage(content=(
                f"Query: {query}\n\n"
                f"═══ HISTORICAL CONTEXT (Wikipedia) ═══\n{wiki_text[:3000]}\n\n"
                f"═══ RECENT NEWS ═══\n{news_text}\n\n"
                f"═══ FINANCIAL DATA ═══\n{fin_text or 'No financial data available.'}\n\n"
                f"═══ RAG CHUNKS ═══\n{rag_text}\n\n"
                f"{trend_block}"
                "Fill the structured output:\n"
                "- historical_background : major events/trends over past 1-2 years\n"
                "- current_situation     : what is happening now per recent news\n"
                "- trend_assessment      : positive/negative/stable and why\n"
                f"{fin_instruction}\n"
                "- summary               : 2-3 overall geopolitical and economic outlook"
            )),
        ]

        try:
            output: OrchestratorOutput = llm_service.generate_structured(messages, OrchestratorOutput)
            if output is None:
                raise ValueError("Structured output returned None")
            hist  = output.historical_background or ""
            curr  = output.current_situation     or ""
            trend = output.trend_assessment      or ""
            fin   = output.financial_summary
            summ  = output.summary               or ""
            # If all key fields are empty, structured output failed silently → fallback
            if not hist and not curr and not summ:
                raise ValueError("Structured output returned all empty fields")
        except Exception as e:
            print(f"[Orchestrator Agent] Structured output failed ({e}), falling back to plain text")
            # Ask LLM for each field separately so they have different content
            plain = llm_service.generate(messages)
            hist  = llm_service.generate([HumanMessage(content=f"In 2-3 sentences, what are the major historical geopolitical events and trends for: {query}")])
            curr  = llm_service.generate([HumanMessage(content=f"In 2-3 sentences, what is the current situation regarding: {query}")])
            trend = ""
            fin   = llm_service.generate([HumanMessage(content=f"Provide financial analysis with key indicators for: {query}")]) if query_type == "financial" else None
            summ  = plain.split("\n")[0][:300] if plain else f"Analysis for: {query}"

        elapsed = round(time.time() - start, 2)
        print(f"[Orchestrator Agent] Done ({elapsed}s)")

        return {
            "historical_background": hist,
            "current_situation":     curr,
            "trend_assessment":      trend,
            "financial_summary":     fin,
            "summary":               summ,
            "timing":                {**state.get("timing", {}), "orchestrator": elapsed},
        }


orchestrator = OrchestratorAgent()


def orchestrator_agent(state: PipelineState) -> dict:
    return orchestrator.run(state)

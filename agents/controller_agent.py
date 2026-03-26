# ─────────────────────────────────────────────
# agents/controller_agent.py
# ─────────────────────────────────────────────

import time
from datetime import datetime, timezone

from state import PipelineState
from tools.transform_tools import extract_entities
from services.llm_service import llm_service
from services.db_service import db_service
from langchain_core.messages import SystemMessage, HumanMessage

FINANCIAL_KEYWORDS = [
    "roi", "gdp", "investment", "financial", "economy", "economic",
    "stock", "market", "inflation", "fdi", "growth rate", "revenue",
    "trade", "export", "import", "currency", "interest rate", "budget",
]

LATEST_KEYWORDS = ["latest", "recent", "today", "now", "fresh"]


def detect_query_type(query: str) -> str:
    q = query.lower()
    return "financial" if any(kw in q for kw in FINANCIAL_KEYWORDS) else "general"


def detect_is_latest(query: str) -> bool:
    q = query.lower()
    return any(kw in q for kw in LATEST_KEYWORDS)


# ─────────────────────────────────────────────
# CONTROLLER AGENT
# ─────────────────────────────────────────────

class ControllerAgent:

    def run(self, state: PipelineState) -> dict:
        start = time.time()
        print("[Controller Agent] Starting pre-checks...")

        query = state.get("query", "").strip()

        if not query:
            return {
                "route":   "unsupported",
                "summary": "Error: Query is empty.",
                "timing":  {"controller": round(time.time() - start, 2)},
                "error":   ["empty_query"],
            }

        if len(query) < 5:
            return {
                "route":   "unsupported",
                "summary": f"Error: Query '{query}' is too short.",
                "timing":  {"controller": round(time.time() - start, 2)},
                "error":   ["query_too_short"],
            }

        entities    = extract_entities(query)
        country     = entities.get("country")
        country_raw = entities.get("country_raw")
        query_type  = detect_query_type(query)
        is_latest   = detect_is_latest(query)
        elapsed     = round(time.time() - start, 2)

        db_fresh = db_service.is_fresh() and not is_latest

        if country_raw:
            route = "rag_only" if db_fresh else "full_pipeline"
            meta  = {
                "country":     country,
                "country_raw": country_raw,
                "wiki_title":  entities.get("wiki_title"),
                "event":       entities.get("event"),
            }
        else:
            # No specific country — use rag_only (searches all countries) or full pipeline
            route = "rag_only" if (db_fresh or db_service.count() > 0) else "full_pipeline"
            meta  = {}

        print(f"[Controller Agent] ROUTE={route} country='{country}' query_type={query_type} is_latest={is_latest} ({elapsed}s)")
        return {
            "route":      route,
            "query_type": query_type,
            "is_latest":  is_latest,
            "metadata":   meta,
            "timing":     {**state.get("timing", {}), "controller": elapsed},
            "error":      [],
        }


# ─────────────────────────────────────────────
# GENERAL HANDLER
# ─────────────────────────────────────────────

class GeneralHandler:

    def run(self, state: PipelineState) -> dict:
        start = time.time()
        print("[General Handler] Answering via LLM...")

        query = state.get("query", "")
        now   = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        messages = [
            SystemMessage(content=(
                "You are a senior geopolitical and investment analyst. "
                f"Today is {now}. "
                "Answer clearly and concisely with structured points where relevant."
            )),
            HumanMessage(content=query),
        ]

        response = llm_service.generate(messages)
        elapsed  = round(time.time() - start, 2)
        print(f"[General Handler] Done ({elapsed}s)")

        return {
            "summary": response,
            "timing":  {"general_handler": elapsed},
        }


# ─────────────────────────────────────────────
# UNSUPPORTED HANDLER
# ─────────────────────────────────────────────

def unsupported_handler(state: PipelineState) -> dict:
    print("[Unsupported Handler] Query blocked.")
    return {"summary": state.get("summary", "Query could not be processed.")}


# ─────────────────────────────────────────────
# EXPORTED NODE FUNCTIONS
# ─────────────────────────────────────────────

_controller = ControllerAgent()
_general    = GeneralHandler()


def controller_agent(state: PipelineState) -> dict:
    return _controller.run(state)


def general_handler(state: PipelineState) -> dict:
    return _general.run(state)

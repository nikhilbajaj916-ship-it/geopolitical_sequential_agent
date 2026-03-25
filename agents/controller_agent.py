# ─────────────────────────────────────────────
# agents/controller_agent.py
#
# Purpose : Pre-checks, routing, and terminal handlers
#           (general + unsupported merged here)
# ─────────────────────────────────────────────

import time
from datetime import datetime, timezone

from state import PipelineState
from tools.transform_tools import extract_entities
from services.llm_service import llm_service
from langchain_core.messages import SystemMessage, HumanMessage


# ─────────────────────────────────────────────
# CONTROLLER AGENT
# ─────────────────────────────────────────────

class ControllerAgent:

    def run(self, state: PipelineState) -> dict:
        start = time.time()

        print("[Controller Agent] Starting pre-checks...")

        query = state.get("query", "").strip()

        # ── Pre-check 1: empty query ──
        if not query:
            elapsed = round(time.time() - start, 2)
            print("[Controller Agent] BLOCKED — empty query")
            return {
                "route":        "unsupported",
                "final_answer": "Error: Query is empty. Please provide a query.",
                "timing":       {"controller": elapsed},
                "error":        ["empty_query"],
            }

        # ── Pre-check 2: query too short ──
        if len(query) < 5:
            elapsed = round(time.time() - start, 2)
            print("[Controller Agent] BLOCKED — query too short")
            return {
                "route":        "unsupported",
                "final_answer": f"Error: Query '{query}' is too short. Please be more specific.",
                "timing":       {"controller": elapsed},
                "error":        ["query_too_short"],
            }

        # ── Step 3: detect country ──
        entities    = extract_entities(query)
        country     = entities.get("country")
        country_raw = entities.get("country_raw")

        elapsed = round(time.time() - start, 2)

        if country_raw:
            print(
                f"[Controller Agent] ROUTE=full_pipeline — country='{country}', "
                f"event='{entities.get('event')}' ({elapsed}s)"
            )
            return {
                "route":    "full_pipeline",
                "metadata": {
                    "country":     country,
                    "country_raw": country_raw,
                    "wiki_title":  entities.get("wiki_title"),
                    "event":       entities.get("event"),
                },
                "timing": {"controller": elapsed},
                "error":  [],
            }

        else:
            print(f"[Controller Agent] ROUTE=general — answering via LLM ({elapsed}s)")
            return {
                "route":    "general",
                "metadata": {},
                "timing":   {"controller": elapsed},
                "error":    [],
            }


# ─────────────────────────────────────────────
# GENERAL HANDLER
# ─────────────────────────────────────────────

class GeneralHandler:

    def run(self, state: PipelineState) -> dict:
        start = time.time()

        print("[General Handler] Answering general query via LLM...")

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

        elapsed = round(time.time() - start, 2)

        print(f"[General Handler] Done ({elapsed}s)")

        return {
            "final_answer": response,
            "timing":       {"general_handler": elapsed},
        }


# ─────────────────────────────────────────────
# UNSUPPORTED HANDLER
# ─────────────────────────────────────────────

def unsupported_handler(state: PipelineState) -> dict:
    print("[Unsupported Handler] Query blocked — returning error answer.")
    return {
        "final_answer": state.get("final_answer", "Query could not be processed."),
    }


# ─────────────────────────────────────────────
# EXPORTED NODE FUNCTIONS
# ─────────────────────────────────────────────

_controller     = ControllerAgent()
_general        = GeneralHandler()


def controller_agent(state: PipelineState) -> dict:
    return _controller.run(state)


def general_handler(state: PipelineState) -> dict:
    return _general.run(state)

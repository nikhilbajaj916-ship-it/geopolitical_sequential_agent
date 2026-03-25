# ─────────────────────────────────────────────
# pipeline.py
#
# Purpose : Build and run ETL pipeline
# ─────────────────────────────────────────────

# ── Imports ──
from typing import Any, Optional

from langgraph.graph import StateGraph, END
from state import PipelineState
from pydantic_response import ETLReport

# Agents
from agents.controller_agent import controller_agent, general_handler, unsupported_handler
from agents.extractor_agent import extractor_agent
from agents.transform_agent import transform_agent
from agents.correlation_agent import correlation_agent
from tools.vector_tools import vector_rag_node
from agents.orchestrator_agent import orchestrator_agent


# ─────────────────────────────────────────────
# ROUTING FUNCTION
# ─────────────────────────────────────────────

def route_after_controller(state: PipelineState) -> str:
    route = state.get("route", "general")
    if route == "full_pipeline":
        return "extractor"
    if route == "unsupported":
        return "unsupported_handler"
    return "general_handler"


# ─────────────────────────────────────────────
# PIPELINE CLASS
# ─────────────────────────────────────────────

class ETLPipeline:

    def __init__(self):
        self.graph = StateGraph(PipelineState)
        self.app: Optional[Any] = None

    # ── Build graph ──
    def build(self):
        print("[Pipeline] Building graph...")

        # ── Nodes ──
        self.graph.add_node("controller",          controller_agent)
        self.graph.add_node("extractor",           extractor_agent)
        self.graph.add_node("transform",           transform_agent)
        self.graph.add_node("correlation",         correlation_agent)
        self.graph.add_node("vector_rag",          vector_rag_node)
        self.graph.add_node("orchestrator",        orchestrator_agent)
        self.graph.add_node("general_handler",     general_handler)
        self.graph.add_node("unsupported_handler", unsupported_handler)

        # ── Entry point ──
        self.graph.set_entry_point("controller")

        # ── Conditional routing after controller ──
        self.graph.add_conditional_edges(
            "controller",
            route_after_controller,
            {
                "extractor":           "extractor",
                "general_handler":     "general_handler",
                "unsupported_handler": "unsupported_handler",
            },
        )

        # ── Full pipeline edges ──
        self.graph.add_edge("extractor",    "transform")
        self.graph.add_edge("transform",    "correlation")
        self.graph.add_edge("correlation",  "vector_rag")
        self.graph.add_edge("vector_rag",   "orchestrator")
        self.graph.add_edge("orchestrator", END)

        # ── Short-circuit ends ──
        self.graph.add_edge("general_handler",     END)
        self.graph.add_edge("unsupported_handler", END)

        # ── Compile ──
        self.app = self.graph.compile()

        print("[Pipeline] Build complete")

    # ── Run pipeline → ETLReport ──
    def run(self, state: PipelineState) -> ETLReport:
        if not self.app:
            raise ValueError("Pipeline not built. Call build() first.")

        print("[Pipeline] Running pipeline...\n")

        result = self.app.invoke(state)

        print("\n[Pipeline] Completed\n")

        # ── Extract connected fields from pipeline result ──
        metadata   = result.get("metadata") or {}
        correlated = result.get("correlated_data") or {}

        return ETLReport(
            query                 = result.get("query", state.get("query", "")),
            wiki_title            = metadata.get("wiki_title"),
            event                 = metadata.get("event"),
            trend                 = correlated.get("trend"),
            historical_background = result.get("historical_background"),
            current_situation     = result.get("current_situation"),
            trend_assessment      = result.get("trend_assessment"),
            summary               = result.get("summary"),
        )

# ─────────────────────────────────────────────
# graph/pipeline.py
# ─────────────────────────────────────────────

from typing import Any, Optional

from langgraph.graph import StateGraph, END
from state import PipelineState
from pydantic_response import ETLReport

from agents.controller_agent import controller_agent, general_handler, unsupported_handler
from agents.extractor_agent import extractor_agent
from agents.transform_agent import transform_agent
from agents.correlation_agent import correlation_agent
from tools.vector_tools import vector_rag_node
from agents.orchestrator_agent import orchestrator_agent


# ─────────────────────────────────────────────
# ROUTING
# ─────────────────────────────────────────────

def route_after_controller(state: PipelineState) -> str:
    route = state.get("route", "general")
    if route == "full_pipeline":
        return "extractor"
    if route == "rag_only":
        return "vector_rag"
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

        # ── Entry ──
        self.graph.set_entry_point("controller")

        # ── Routing after controller ──
        self.graph.add_conditional_edges(
            "controller",
            route_after_controller,
            {
                "extractor":           "extractor",
                "vector_rag":          "vector_rag",
                "general_handler":     "general_handler",
                "unsupported_handler": "unsupported_handler",
            },
        )

        # ── Full pipeline path ──
        self.graph.add_edge("extractor",    "transform")
        self.graph.add_edge("transform",    "correlation")
        self.graph.add_edge("correlation",  "vector_rag")
        self.graph.add_edge("vector_rag",   "orchestrator")
        self.graph.add_edge("orchestrator", END)

        # ── Short-circuit ends ──
        self.graph.add_edge("general_handler",     END)
        self.graph.add_edge("unsupported_handler", END)

        self.app = self.graph.compile()
        print("[Pipeline] Build complete")

    def run(self, state: PipelineState) -> ETLReport:
        if not self.app:
            raise ValueError("Pipeline not built. Call build() first.")

        print("[Pipeline] Running...\n")
        result = self.app.invoke(state)
        print("\n[Pipeline] Completed\n")

        return ETLReport(
            query                 = result.get("query", state.get("query", "")),
            historical_background = result.get("historical_background"),
            current_situation     = result.get("current_situation"),
            financial_summary     = result.get("financial_summary"),
            summary               = result.get("summary"),
        )

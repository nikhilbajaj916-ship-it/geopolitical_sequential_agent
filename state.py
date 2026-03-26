# ─────────────────────────────────────────────
# state.py
#
# Purpose : Shared pipeline state (single source of truth)
# ─────────────────────────────────────────────

# ── Imports ──
from typing import TypedDict, Any, List, Dict


# ─────────────────────────────────────────────
# PIPELINE STATE
# ─────────────────────────────────────────────

class PipelineState(TypedDict, total=False):

    # ── Input ──
    query:      str
    query_type: str       # "general" | "financial"
    is_latest:  bool      # True if user asked for latest/fresh data

    # ── Routing ──
    route: str

    # ── Metadata ──
    metadata: Dict

    # ── Extracted Data ──
    news_raw:       Any
    wiki_raw:       Any
    financial_data: Dict  # raw numbers from World Bank + yfinance

    # ── Processed Data ──
    transformed_data: Dict
    correlated_data:  Dict

    # ── RAG Context ──
    retrieved_docs: List
    context:        str

    # ── Output ──
    historical_background: str
    current_situation:     str
    trend_assessment:      str
    financial_summary:     str
    summary:               str

    # ── Logs ──
    messages: List

    # ── Performance Tracking ──
    timing: Dict[str, float]

    # ── Error Handling ──
    error: List[str]

    # ── Cache Info ──
    cache_hit: bool


# ─────────────────────────────────────────────
# DEFAULT STATE CREATOR
# ─────────────────────────────────────────────

def get_initial_state(query: str) -> PipelineState:
    return {
        "query": query,
        "metadata": {},
        "messages": [],
        "timing": {},
        "error": [],
        "cache_hit": False,
    }


# ─────────────────────────────────────────────
# LOCAL TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    state = get_initial_state("future of India market")

    print("\nInitial State:\n")
    print(state)
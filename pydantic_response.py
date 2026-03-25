from pydantic import BaseModel, Field
from typing import Optional


# ─────────────────────────────────────────────
# LLM STRUCTURED OUTPUT  (orchestrator fills this)
# ─────────────────────────────────────────────

class OrchestratorOutput(BaseModel):
    historical_background: str = Field(description="Major geopolitical events/trends over past 1-2 years")
    current_situation:     str = Field(description="What is happening right now based on recent news")
    trend_assessment:      str = Field(description="Is the situation positive / negative / stable and why")
    recommendation:        str = Field(description="One-line summary of the overall geopolitical outlook")


# ─────────────────────────────────────────────
# FINAL API RESPONSE  (pipeline fills this)
# ─────────────────────────────────────────────

class ETLReport(BaseModel):
    query:          str
    answer:         str
    wiki_title:     Optional[str] = None    # Wikipedia article used for analysis
    event:          Optional[str] = None    # detected event/topic
    trend:          Optional[str] = None    # positive | negative | stable
    recommendation: Optional[str] = None    # one-line geopolitical outlook

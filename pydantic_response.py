from pydantic import BaseModel, Field
from typing import Optional


# ─────────────────────────────────────────────
# LLM STRUCTURED OUTPUT  (orchestrator fills this)
# ─────────────────────────────────────────────

class OrchestratorOutput(BaseModel):
    historical_background: str           = Field(description="Major geopolitical events/trends over past 1-2 years")
    current_situation:     str           = Field(description="What is happening right now based on recent news")
    trend_assessment:      str           = Field(description="Is the situation positive / negative / stable and why")
    financial_summary:     Optional[str] = Field(default=None, description="Financial/economic analysis with key indicators (GDP, FDI, inflation, ROI) if financial data is available in context. Set null if no financial data provided.")
    summary:               str           = Field(description="One-line summary of the overall geopolitical and economic outlook")


# ─────────────────────────────────────────────
# FINAL API RESPONSE  (pipeline fills this)
# ─────────────────────────────────────────────

class ETLReport(BaseModel):
    query:                 str
    historical_background: Optional[str] = None
    current_situation:     Optional[str] = None
    financial_summary:     Optional[str] = None
    summary:               Optional[str] = None

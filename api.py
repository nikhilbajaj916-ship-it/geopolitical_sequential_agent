# ─────────────────────────────────────────────
# api.py
#
# Purpose : FastAPI entry point for the pipeline
#           Run: python api.py  (starts uvicorn)
# ─────────────────────────────────────────────

# ── Imports ──
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from graph.pipeline import ETLPipeline
from pydantic_response import ETLReport
from state import get_initial_state
from config import validate_config


# ─────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────

app = FastAPI(
    title="Geo Intelligence API",
    description="ETL + RAG Pipeline API",
    version="1.0"
)


# ─────────────────────────────────────────────
# REQUEST MODEL
# ─────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str


# ─────────────────────────────────────────────
# PIPELINE INIT (load once at startup)
# ─────────────────────────────────────────────

validate_config()

pipeline = ETLPipeline()
pipeline.build()


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return {"status": "API is running"}


@app.post("/analyze", response_model=ETLReport)
def analyze(req: QueryRequest) -> ETLReport:
    query = req.query.strip()

    if not query:
        return ETLReport(
            query  = "",
            answer = "Query cannot be empty.",
        )

    state  = get_initial_state(query)
    result = pipeline.run(state)
    return result


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)

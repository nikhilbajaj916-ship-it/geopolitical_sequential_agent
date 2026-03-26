# ─────────────────────────────────────────────
# api.py
# ─────────────────────────────────────────────

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from graph.pipeline import ETLPipeline
from pydantic_response import ETLReport
from state import get_initial_state
from config import validate_config
from services.db_service import db_service
from data_loader import load_all_countries


app = FastAPI(
    title="Geo Intelligence API",
    description="ETL + RAG Pipeline — Top 20 Countries",
    version="2.0"
)


class QueryRequest(BaseModel):
    query: str


# ─────────────────────────────────────────────
# STARTUP — build pipeline + load DB if needed
# ─────────────────────────────────────────────

validate_config()

pipeline = ETLPipeline()
pipeline.build()

# Load 20-country data if DB is not fresh
load_all_countries()


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/")
def home():
    return {"status": "API is running", "db_chunks": db_service.count()}


@app.get("/status")
def status():
    import os, json
    from config import DB_PATH
    meta_path = os.path.join(DB_PATH, "meta.json")
    last_updated = None
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            last_updated = json.load(f).get("last_updated")
    return {
        "db_chunks":    db_service.count(),
        "db_fresh":     db_service.is_fresh(),
        "last_updated": last_updated,
    }


@app.post("/refresh")
def refresh():
    """Force refresh all 20 countries data."""
    load_all_countries(force=True)
    return {"status": "refreshed", "db_chunks": db_service.count()}


@app.post("/analyze", response_model=ETLReport)
def analyze(req: QueryRequest) -> ETLReport:
    query = req.query.strip()

    if not query:
        return ETLReport(query="", summary="Query cannot be empty.")

    state = get_initial_state(query)
    try:
        result = pipeline.run(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)

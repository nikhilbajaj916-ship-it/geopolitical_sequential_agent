# Geo Intelligence API

An ETL + RAG pipeline that answers geopolitical queries using live news, Wikipedia, and a local LLM (Ollama).

---

## What It Does

You send a query like `"future of India market"` and the pipeline:

1. Detects the country/event from the query
2. Fetches live news (TheNewsAPI) + Wikipedia article
3. Transforms and indexes the text into a FAISS vector store
4. Runs RAG similarity search to pull the most relevant chunks
5. Sends everything to a local LLM (Ollama) and gets back a structured geopolitical analysis

---

## Architecture

```
Request
  └─► Controller Agent
        ├─► (no country found)  ──► General Handler  ──► LLM answer  ──► Response
        ├─► (bad query)         ──► Unsupported Handler              ──► Response
        └─► (country found)     ──► Extractor Agent
                                      └─► Transform Agent
                                            └─► Correlation Agent
                                                  └─► Vector + RAG Node
                                                        └─► Orchestrator Agent  ──► Response
```

### Agents / Nodes

| Node | File | Role |
|------|------|------|
| Controller | `agents/controller_agent.py` | Validates query, detects country, routes |
| General Handler | `agents/controller_agent.py` | Answers non-geo queries via LLM |
| Unsupported Handler | `agents/controller_agent.py` | Returns error for blocked queries |
| Extractor | `agents/extractor_agent.py` | Fetches news + Wikipedia (with cache) |
| Transform | `agents/transform_agent.py` | Cleans and structures raw data |
| Correlation | `agents/correlation_agent.py` | Detects trend from news data |
| Vector + RAG | `tools/vector_tools.py` | Builds FAISS DB and retrieves top-K chunks |
| Orchestrator | `agents/orchestrator_agent.py` | Final LLM call → structured Pydantic output |

---

## API Response

**POST** `/analyze`

```json
{
  "query": "future of India market",
  "wiki_title": "India",
  "event": "economic growth",
  "trend": "positive",
  "historical_background": "...",
  "current_situation": "...",
  "trend_assessment": "...",
  "summary": "India's economy shows strong growth momentum driven by..."
}
```

---

## Project Structure

```
geo_dummy_sequential_agent/
├── api.py                      # FastAPI entry point
├── config.py                   # All settings (API keys, model, etc.)
├── state.py                    # LangGraph shared state (TypedDict)
├── pydantic_response.py        # Pydantic models (OrchestratorOutput, ETLReport)
├── requirements.txt
│
├── graph/
│   └── pipeline.py             # LangGraph pipeline build + run
│
├── agents/
│   ├── controller_agent.py     # Controller + General + Unsupported handlers
│   ├── extractor_agent.py      # News + Wiki fetching
│   ├── transform_agent.py      # Data cleaning
│   ├── correlation_agent.py    # Trend detection
│   └── orchestrator_agent.py  # Final LLM structured output
│
├── tools/
│   ├── extractor_tools.py      # read_news(), read_wiki()
│   ├── transform_tools.py      # extract_entities(), transform_news(), transform_wiki()
│   ├── correlation_tools.py    # Trend logic
│   └── vector_tools.py         # FAISS build + RAG search (combined node)
│
└── services/
    ├── llm_service.py          # Ollama LLM (plain + structured output)
    ├── embedding_service.py    # Ollama embeddings for FAISS
    └── cache_service.py        # In-memory cache (TTL-based)
```

---

## Setup

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) running locally with `llama3.2` pulled

```bash
ollama pull llama3.2
```

### Install

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# or: source venv/bin/activate  (Linux/Mac)

pip install -r requirements.txt
```

### Configure

Edit `config.py`:

```python
NEWS_API_KEY    = "your_thenewsapi_key"
OLLAMA_MODEL    = "llama3.2"
OLLAMA_BASE_URL = "http://localhost:11434"
```

> Get a free API key at [thenewsapi.com](https://www.thenewsapi.com)

---

## Run

```bash
python api.py
```

API will start at `http://localhost:8000`

- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/`

---

## Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "political situation in Pakistan"}'
```

---

## SSL Fix (Corporate Networks)

If you get `SSL: CERTIFICATE_VERIFY_FAILED`, the API calls already have `verify=False` set in `tools/extractor_tools.py`. No additional setup needed.

---

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `langgraph` | Sequential agent pipeline |
| `langchain-ollama` | Local LLM via Ollama |
| `langchain-community` | FAISS vector store |
| `fastapi` + `uvicorn` | REST API server |
| `pydantic` | Structured LLM output + API models |
| `requests` | News + Wikipedia HTTP calls |

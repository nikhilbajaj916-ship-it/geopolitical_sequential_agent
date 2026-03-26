# ─────────────────────────────────────────────
# tools/vector_tools.py
#
# Purpose : Chunking + ChromaDB indexing + RAG search
# ─────────────────────────────────────────────

import time
from state import PipelineState
from services.db_service import db_service
from config import CHUNK_SIZE, CHUNK_OVERLAP, VECTOR_TOP_K


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """Split text into overlapping chunks."""
    if not text:
        return []
    chunks = []
    start  = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return [c for c in chunks if c.strip()]


def index_country_data(country: str, news_items: list, wiki_text: str, financial_text: str = ""):
    """Chunk and upsert all data for a country into ChromaDB."""
    texts     = []
    metadatas = []
    ids       = []

    # News chunks
    for i, item in enumerate(news_items):
        for j, chunk in enumerate(chunk_text(item.get("text", ""))):
            texts.append(chunk)
            metadatas.append({"country": country, "source": "news", "date": item.get("published", "")})
            ids.append(f"{country}_news_{i}_{j}")

    # Wiki chunks
    for j, chunk in enumerate(chunk_text(wiki_text)):
        texts.append(chunk)
        metadatas.append({"country": country, "source": "wiki", "date": ""})
        ids.append(f"{country}_wiki_{j}")

    # Financial text (single entry)
    if financial_text.strip():
        texts.append(financial_text)
        metadatas.append({"country": country, "source": "financial", "date": ""})
        ids.append(f"{country}_financial")

    if texts:
        db_service.upsert(texts, metadatas, ids)
        print(f"[Vector] Indexed {len(texts)} chunks for {country}")


def vector_rag_node(state: PipelineState) -> dict:
    """Index fresh data (if any) then search ChromaDB."""
    start       = time.time()
    query       = state.get("query", "")
    country     = (state.get("metadata") or {}).get("country")
    transformed = state.get("transformed_data") or {}

    # Index only if fresh data was fetched (not from cache) or forced latest
    cache_hit = state.get("cache_hit", False)
    is_latest = state.get("is_latest", False)
    if transformed and (not cache_hit or is_latest):
        news_items = transformed.get("news", [])
        wiki_text  = (transformed.get("wiki") or {}).get("text", "")
        fin_text   = transformed.get("financial_text", "")
        index_country_data(country or "", news_items, wiki_text, fin_text)

    print(f"[Vector+RAG] Searching for '{query}' country={country}")

    docs    = db_service.search(query, country=country, n_results=VECTOR_TOP_K)
    context = "\n\n".join(docs)
    elapsed = round(time.time() - start, 2)

    print(f"[Vector+RAG] Retrieved {len(docs)} chunks ({elapsed}s)")

    return {
        "context":        context,
        "retrieved_docs": docs,
        "timing":         {**state.get("timing", {}), "vector_rag": elapsed},
    }

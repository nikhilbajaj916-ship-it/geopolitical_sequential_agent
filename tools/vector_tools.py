# ─────────────────────────────────────────────
# tools/vector_tools.py
#
# Purpose : Build vector DB + RAG search (combined)
# ─────────────────────────────────────────────

import time
from langchain_community.vectorstores import FAISS
from state import PipelineState
from services.embedding_service import embedding_service
from config import VECTOR_TOP_K


# ─────────────────────────────────────────────
# LOW-LEVEL HELPERS
# ─────────────────────────────────────────────

def build_vector_db(texts: list, embeddings) -> FAISS:
    return FAISS.from_texts(texts, embeddings)


def search_vector(db: FAISS, query: str, k: int) -> list:
    return db.similarity_search(query, k=k)


# ─────────────────────────────────────────────
# PIPELINE NODE  (replaces vector + rag agents)
# ─────────────────────────────────────────────

def vector_rag_node(state: PipelineState) -> dict:
    start = time.time()

    print("[Vector+RAG] Starting...")

    transformed = state.get("transformed_data") or {}
    query       = state.get("query", "")

    # ── Collect texts from news + wiki ──
    news_items = transformed.get("news", [])
    wiki_item  = transformed.get("wiki") or {}

    texts = [item["text"] for item in news_items if item.get("text")]
    if wiki_item.get("text"):
        texts.append(wiki_item["text"])

    if not texts:
        print("[Vector+RAG] No texts — skipping.")
        elapsed = round(time.time() - start, 2)
        return {"context": "", "retrieved_docs": [], "timing": {"vector_rag": elapsed}}

    # ── Build DB + search in one step ──
    db   = build_vector_db(texts, embedding_service.get())
    docs = search_vector(db, query, k=VECTOR_TOP_K)

    context = "\n".join(d.page_content for d in docs)
    elapsed = round(time.time() - start, 2)

    print(f"[Vector+RAG] Indexed {len(texts)} chunks, retrieved {len(docs)} ({elapsed}s)")

    return {
        "context":       context,
        "retrieved_docs": docs,
        "timing":        {"vector_rag": elapsed},
    }

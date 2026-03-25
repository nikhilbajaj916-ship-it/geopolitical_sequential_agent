# ─────────────────────────────────────────────
# services/embedding_service.py
#
# Purpose : Embedding service for vector DB
# ─────────────────────────────────────────────

# ── Imports ──
from langchain_ollama import OllamaEmbeddings
from config import EMBEDDING_MODEL


# ─────────────────────────────────────────────
# EMBEDDING SERVICE
# ─────────────────────────────────────────────

class EmbeddingService:

    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL
        )

    # ── Return embedding object ──
    def get(self):
        return self.embeddings


# ─────────────────────────────────────────────
# SINGLETON INSTANCE
# ─────────────────────────────────────────────

embedding_service = EmbeddingService()


# ─────────────────────────────────────────────
# LOCAL TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    emb = embedding_service.get()

    text = "India economic growth"

    vector = emb.embed_query(text)

    print("\nEmbedding vector length:", len(vector))
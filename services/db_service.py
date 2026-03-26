# ─────────────────────────────────────────────
# services/db_service.py
#
# Purpose : Persistent ChromaDB management
# ─────────────────────────────────────────────

import os
import json
from datetime import datetime, timedelta
from typing import Optional
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from config import DB_PATH, VECTOR_TOP_K

_METADATA_FILE = os.path.join(DB_PATH, "meta.json")


class DBService:

    def __init__(self):
        os.makedirs(DB_PATH, exist_ok=True)
        self.client     = chromadb.PersistentClient(path=DB_PATH)
        self.ef         = DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="geo_intel",
            embedding_function=self.ef,
        )

    def is_fresh(self, max_age_hours: int = 24) -> bool:
        """Check if DB was loaded within max_age_hours."""
        if not os.path.exists(_METADATA_FILE):
            return False
        with open(_METADATA_FILE) as f:
            meta = json.load(f)
        last = datetime.fromisoformat(meta.get("last_updated", "2000-01-01"))
        return datetime.now() - last < timedelta(hours=max_age_hours)

    def mark_updated(self):
        """Save timestamp of last full DB load."""
        with open(_METADATA_FILE, "w") as f:
            json.dump({"last_updated": datetime.now().isoformat()}, f)

    def upsert(self, texts: list, metadatas: list, ids: list):
        """Add or update documents in the collection."""
        self.collection.upsert(documents=texts, metadatas=metadatas, ids=ids)

    def search(self, query: str, country: Optional[str] = None, n_results: int = VECTOR_TOP_K) -> list:
        """Similarity search, optionally filtered by country."""
        total = self.collection.count()
        if total == 0:
            return []

        kwargs = {
            "query_texts": [query],
            "n_results":   min(n_results, total),
        }
        if country:
            kwargs["where"] = {"country": country}

        results = self.collection.query(**kwargs)
        return results["documents"][0] if results["documents"] else []

    def count(self) -> int:
        return self.collection.count()

    def has_country(self, country: str) -> bool:
        """Check if country data exists in DB."""
        results = self.collection.get(where={"country": country}, limit=1)
        return len(results["documents"]) > 0


db_service = DBService()

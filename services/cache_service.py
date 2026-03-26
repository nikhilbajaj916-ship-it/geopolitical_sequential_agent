# ─────────────────────────────────────────────
# services/cache_service.py
#
# Purpose : Central cache layer (TTL-based)
# ─────────────────────────────────────────────

# ── Imports ──
import time
import threading
from typing import Any, Optional
from config import CACHE_TTL


# ─────────────────────────────────────────────
# CACHE SERVICE
# ─────────────────────────────────────────────

class CacheService:

    def __init__(self, ttl: int = CACHE_TTL):
        self.store = {}
        self.ttl   = ttl
        self._lock = threading.Lock()

    # ── Get value from cache ──
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            data = self.store.get(key)
            if data:
                value, timestamp = data
                if time.time() - timestamp < self.ttl:
                    print(f"[Cache] HIT: {key}")
                    return value
                print(f"[Cache] EXPIRED: {key}")
                self.store.pop(key, None)
        return None

    # ── Set value in cache ──
    def set(self, key: str, value: Any):
        with self._lock:
            self.store[key] = (value, time.time())
        print(f"[Cache] SET: {key}")

    # ── Clear all cache (optional) ──
    def clear(self):
        with self._lock:
            self.store.clear()
        print("[Cache] CLEARED")


# ─────────────────────────────────────────────
# SINGLETON INSTANCE
# ─────────────────────────────────────────────

cache_service = CacheService()


# ─────────────────────────────────────────────
# LOCAL TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    cache = CacheService(ttl=2)

    key = "test"
    value = {"data": 123}

    print("\nSetting cache...")
    cache.set(key, value)

    print("\nGetting cache (should hit)...")
    print(cache.get(key))

    print("\nWaiting for expiry...")
    time.sleep(3)

    print("\nGetting cache (should expire)...")
    print(cache.get(key))
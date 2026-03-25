# ─────────────────────────────────────────────
# config.py
#
# Purpose : Central configuration (env-based)
# ─────────────────────────────────────────────

from local_settings import (
    AGENT_TEMPERATURE,
    AGENT_TIMEOUT,
    CACHE_TTL,
    DEFAULT_QUERY,
    EMBEDDING_MODEL,
    NEWS_API_KEY,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    RATE_LIMIT_DELAY,
    VECTOR_TOP_K,
    WIKI_BASE_URL,
)


# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# VALIDATION (IMPORTANT)
# ─────────────────────────────────────────────

def validate_config():
    errors = []

    if not NEWS_API_KEY:
        errors.append("NEWS_API_KEY missing")

    if not OLLAMA_BASE_URL:
        errors.append("OLLAMA_BASE_URL missing")

    if errors:
        raise ValueError(f"Config Error: {errors}")


# ─────────────────────────────────────────────
# LOCAL TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("\nConfig Loaded\n")

    validate_config()

    print("MODEL:", OLLAMA_MODEL)
    print("BASE URL:", OLLAMA_BASE_URL)

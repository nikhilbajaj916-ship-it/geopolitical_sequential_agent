# ─────────────────────────────────────────────
# config.py
#
# Purpose : Central configuration
# ─────────────────────────────────────────────

NEWS_API_KEY       = "pooakdx2t3M5KAArBddk7aCAcAWqfiRUJmt3QGan"
WIKI_BASE_URL      = "https://en.wikipedia.org/api/rest_v1/page/summary"

OLLAMA_MODEL       = "llama3.2"
OLLAMA_BASE_URL    = "http://localhost:11434"

AGENT_TEMPERATURE  = 0.3
AGENT_TIMEOUT      = 120

EMBEDDING_MODEL    = "llama3.2"

CACHE_TTL          = 300
RATE_LIMIT_DELAY   = 1.0

VECTOR_TOP_K       = 2

DEFAULT_QUERY      = "future of India market"


# ─────────────────────────────────────────────
# VALIDATION
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

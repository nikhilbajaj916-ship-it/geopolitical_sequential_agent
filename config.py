# ─────────────────────────────────────────────
# config.py
#
# Purpose : Central configuration
# ─────────────────────────────────────────────

import os
import ssl
import urllib3

# ── Global SSL bypass for corporate/restricted networks ──
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["CURL_CA_BUNDLE"]      = ""
os.environ["REQUESTS_CA_BUNDLE"]  = ""
os.environ["SSL_CERT_FILE"]       = ""
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

NEWS_API_KEY    = os.getenv("NEWS_API_KEY",    "pooakdx2t3M5KAArBddk7aCAcAWqfiRUJmt3QGan")
WIKI_BASE_URL   = "https://en.wikipedia.org/api/rest_v1/page/summary"

OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL",    "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

AGENT_TEMPERATURE = 0.3
AGENT_TIMEOUT     = 120

CACHE_TTL        = 300
RATE_LIMIT_DELAY = 1.0

VECTOR_TOP_K  = 5
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 50

DB_PATH = os.getenv("DB_PATH", "./geo_db")

# ─────────────────────────────────────────────
# TOP 20 COUNTRIES
# ─────────────────────────────────────────────

TOP_20_COUNTRIES = [
    "USA", "China", "Germany", "Japan", "India",
    "UK", "France", "Brazil", "Canada", "Russia",
    "South Korea", "Australia", "Italy", "Spain", "Mexico",
    "Indonesia", "Netherlands", "Saudi Arabia", "Turkey", "Switzerland",
]

COUNTRY_WIKI_TITLES = {
    "USA":          "United_States",
    "China":        "China",
    "Germany":      "Germany",
    "Japan":        "Japan",
    "India":        "India",
    "UK":           "United_Kingdom",
    "France":       "France",
    "Brazil":       "Brazil",
    "Canada":       "Canada",
    "Russia":       "Russia",
    "South Korea":  "South_Korea",
    "Australia":    "Australia",
    "Italy":        "Italy",
    "Spain":        "Spain",
    "Mexico":       "Mexico",
    "Indonesia":    "Indonesia",
    "Netherlands":  "Netherlands",
    "Saudi Arabia": "Saudi_Arabia",
    "Turkey":       "Turkey",
    "Switzerland":  "Switzerland",
}

COUNTRY_CODES = {
    "USA":          "US",
    "China":        "CN",
    "Germany":      "DE",
    "Japan":        "JP",
    "India":        "IN",
    "UK":           "GB",
    "France":       "FR",
    "Brazil":       "BR",
    "Canada":       "CA",
    "Russia":       "RU",
    "South Korea":  "KR",
    "Australia":    "AU",
    "Italy":        "IT",
    "Spain":        "ES",
    "Mexico":       "MX",
    "Indonesia":    "ID",
    "Netherlands":  "NL",
    "Saudi Arabia": "SA",
    "Turkey":       "TR",
    "Switzerland":  "CH",
}

STOCK_INDICES = {
    "USA":          "^GSPC",
    "China":        "000001.SS",
    "Germany":      "^GDAXI",
    "Japan":        "^N225",
    "India":        "^BSESN",
    "UK":           "^FTSE",
    "France":       "^FCHI",
    "Brazil":       "^BVSP",
    "Canada":       "^GSPTSE",
    "Russia":       "IMOEX.ME",
    "South Korea":  "^KS11",
    "Australia":    "^AXJO",
    "Italy":        "FTSEMIB.MI",
    "Spain":        "^IBEX",
    "Mexico":       "^MXX",
    "Indonesia":    "^JKSE",
    "Netherlands":  "^AEX",
    "Saudi Arabia": "^TASI.SR",
    "Turkey":       "XU100.IS",
    "Switzerland":  "^SSMI",
}


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


if __name__ == "__main__":
    print("\nConfig Loaded\n")
    validate_config()
    print("MODEL:", OLLAMA_MODEL)
    print("COUNTRIES:", len(TOP_20_COUNTRIES))

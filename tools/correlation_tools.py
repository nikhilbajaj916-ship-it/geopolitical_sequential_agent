# ─────────────────────────────────────────────
# tools/correlation_tools.py
# ─────────────────────────────────────────────

def analyze_trend(news_data: list) -> str:
    text = str(news_data).lower()

    if "crisis" in text:
        return "negative"
    elif "growth" in text:
        return "positive"

    return "stable"


def build_correlation(query: str, news, wiki) -> dict:
    return {
        "country": query,
        "trend": analyze_trend(news),
        "summary": "Correlation based on news and wiki data",
    }
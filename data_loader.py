# ─────────────────────────────────────────────
# data_loader.py
#
# Purpose : Pre-load all 20 countries into ChromaDB
# Run     : python data_loader.py
import ssl_patch  # noqa: F401 — must be first
# ─────────────────────────────────────────────

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import TOP_20_COUNTRIES, COUNTRY_WIKI_TITLES
from tools.extractor_tools import read_news, read_wiki
from tools.financial_tools import fetch_financial_data, financial_to_text
from tools.transform_tools import transform_news, transform_wiki
from tools.vector_tools import index_country_data
from services.db_service import db_service


def load_country(country: str) -> str:
    wiki_title = COUNTRY_WIKI_TITLES.get(country, country)

    news_raw  = read_news(country)
    wiki_raw  = read_wiki(wiki_title)
    financial = fetch_financial_data(country)

    news_items = transform_news(news_raw)
    wiki_text  = transform_wiki(wiki_raw).get("text", "")
    fin_text   = financial_to_text(country, financial)

    index_country_data(country, news_items, wiki_text, fin_text)
    return country


def load_all_countries(force: bool = False):
    if db_service.is_fresh() and not force:
        print(f"[DataLoader] DB is fresh — skipping. Use force=True to reload.")
        return

    print(f"\n[DataLoader] Loading {len(TOP_20_COUNTRIES)} countries...\n")
    start = time.time()

    failed = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(load_country, c): c for c in TOP_20_COUNTRIES}
        for future in as_completed(futures):
            country = futures[future]
            try:
                future.result()
                print(f"[DataLoader] OK {country}")
            except Exception as e:
                print(f"[DataLoader] FAILED {country}: {e}")
                failed.append(country)

    if failed:
        print(f"[DataLoader] WARNING — {len(failed)} countries failed: {failed}")

    if len(failed) < len(TOP_20_COUNTRIES):
        db_service.mark_updated()
    elapsed = round(time.time() - start, 2)
    print(f"\n[DataLoader] Complete — {db_service.count()} chunks indexed ({elapsed}s)\n")


if __name__ == "__main__":
    load_all_countries(force=True)

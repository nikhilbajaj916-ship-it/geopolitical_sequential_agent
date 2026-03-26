# ─────────────────────────────────────────────
# tools/financial_tools.py
#
# Purpose : Fetch financial data from World Bank API + yfinance
# ─────────────────────────────────────────────

import os
import ssl
import requests

# Disable SSL verification for corporate/restricted networks (must be before yfinance import)
os.environ["CURL_CA_BUNDLE"]     = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
ssl._create_default_https_context = ssl._create_unverified_context

import yfinance as yf
from config import COUNTRY_CODES, STOCK_INDICES

WORLD_BANK_BASE = "https://api.worldbank.org/v2"

WB_INDICATORS = {
    "gdp":          "NY.GDP.MKTP.CD",
    "gdp_growth":   "NY.GDP.MKTP.KD.ZG",
    "fdi":          "BX.KLT.DINV.CD.WD",
    "inflation":    "FP.CPI.TOTL.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
}


def fetch_world_bank(country: str) -> dict:
    """Fetch macroeconomic indicators from World Bank API (free, no key needed)."""
    code = COUNTRY_CODES.get(country)
    if not code:
        return {}

    result = {}
    for key, indicator in WB_INDICATORS.items():
        try:
            url  = f"{WORLD_BANK_BASE}/country/{code}/indicator/{indicator}?format=json&mrv=1"
            resp = requests.get(url, timeout=10, verify=False)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 1 and data[1]:
                    entry = data[1][0]
                    value = entry.get("value")
                    if value is not None:
                        result[key]           = round(float(value), 2)
                        result[f"{key}_year"] = entry.get("date", "")
        except Exception as e:
            print(f"[Financial] World Bank error for {country}/{key}: {e}")

    return result


def fetch_stock(country: str) -> dict:
    """Fetch stock index 1-month performance via yfinance."""
    ticker = STOCK_INDICES.get(country)
    if not ticker:
        return {}

    try:
        hist = yf.Ticker(ticker).history(period="1mo")
        if not hist.empty:
            start  = hist["Close"].iloc[0]
            end    = hist["Close"].iloc[-1]
            change = round(((end - start) / start) * 100, 2)
            return {
                "stock_index":      ticker,
                "stock_1mo_change": f"{change}%",
            }
    except Exception as e:
        print(f"[Financial] yfinance error for {country}: {e}")

    return {}


def fetch_financial_data(country: str) -> dict:
    """Fetch all financial data for a country."""
    wb    = fetch_world_bank(country)
    stock = fetch_stock(country)
    return {**wb, **stock}


def financial_to_text(country: str, data: dict) -> str:
    """Convert financial data dict to readable text for indexing."""
    if not data:
        return ""

    lines = [f"Financial indicators for {country}:"]

    if "gdp" in data:
        gdp_t = round(data["gdp"] / 1e12, 2)
        lines.append(f"GDP: ${gdp_t} Trillion ({data.get('gdp_year', '')})")
    if "gdp_growth" in data:
        lines.append(f"GDP Growth Rate: {data['gdp_growth']}% ({data.get('gdp_growth_year', '')})")
    if "fdi" in data:
        fdi_b = round(data["fdi"] / 1e9, 2)
        lines.append(f"Foreign Direct Investment (FDI): ${fdi_b} Billion ({data.get('fdi_year', '')})")
    if "inflation" in data:
        lines.append(f"Inflation Rate: {data['inflation']}% ({data.get('inflation_year', '')})")
    if "unemployment" in data:
        lines.append(f"Unemployment Rate: {data['unemployment']}% ({data.get('unemployment_year', '')})")
    if "stock_1mo_change" in data:
        lines.append(f"Stock Index ({data.get('stock_index', '')}): {data['stock_1mo_change']} change (last 1 month)")

    return "\n".join(lines)

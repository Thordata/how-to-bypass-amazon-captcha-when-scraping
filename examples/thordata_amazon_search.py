"""Thordata example: search Amazon products by keyword.

Requirements:
    pip install thordata-sdk
    Set THORDATA_SCRAPER_TOKEN, THORDATA_PUBLIC_TOKEN, THORDATA_PUBLIC_KEY in .env
"""

from __future__ import annotations

from amazon_captcha.thordata_client import search_products


def main() -> None:
    items = search_products("wireless mouse", max_results=5)
    print(f"Found {len(items)} products")
    for item in items:
        print("-", item.title, "| price:", item.final_price)


if __name__ == "__main__":
    main()

"""Thordata example: fetch Amazon product details by ASIN.

Requirements:
    pip install thordata-sdk
    Set THORDATA_SCRAPER_TOKEN, THORDATA_PUBLIC_TOKEN, THORDATA_PUBLIC_KEY in .env
"""

from __future__ import annotations

from pprint import pprint

from amazon_captcha.thordata_client import get_product_by_asin


def main() -> None:
    print("Submitting task for ASIN: B0BZYCJK89...")
    product = get_product_by_asin("B0BZYCJK89", domain="amazon.com")
    pprint(
        {
            "title": product.title,
            "asin": product.asin,
            "final_price": product.final_price,
            "currency": product.currency,
            "rating": product.rating,
            "reviews_count": product.reviews_count,
        }
    )


if __name__ == "__main__":
    main()

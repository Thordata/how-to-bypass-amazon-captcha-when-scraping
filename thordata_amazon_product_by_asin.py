"""
Example: Fetch Amazon product details by ASIN using Thordata Web Scraper Tools.

Requirements:
    pip install thordata-sdk
    Set THORDATA_SCRAPER_TOKEN, THORDATA_PUBLIC_TOKEN, THORDATA_PUBLIC_KEY in .env
"""

from __future__ import annotations

import os
from pprint import pprint

import requests
from thordata import ThordataClient, load_env_file
from thordata.exceptions import ThordataError
from thordata.tools import Amazon


def ensure_thordata_env() -> bool:
    """Return True if essential Thordata env vars look present."""
    required = [
        "THORDATA_SCRAPER_TOKEN",
        "THORDATA_PUBLIC_TOKEN",
        "THORDATA_PUBLIC_KEY",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        print("[ERROR] Missing Thordata environment variables:", ", ".join(missing))
        print(
            "Create a .env file with these keys or export them in your shell "
            "before running this script."
        )
        return False
    return True


def main() -> None:
    # 1. Load environment from .env (optional but convenient)
    load_env_file()

    if not ensure_thordata_env():
        return

    # 2. Initialize client with explicit credentials from env vars
    client = ThordataClient(
        scraper_token=os.getenv("THORDATA_SCRAPER_TOKEN"),
        public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
        public_key=os.getenv("THORDATA_PUBLIC_KEY"),
    )

    # 3. Define the scraping task: product by ASIN on amazon.com
    request = Amazon.ProductByAsin(
        asin="B0BZYCJK89",
        domain="amazon.com",
    )

    print(f"Submitting task for ASIN: {request.asin}...")

    try:
        # 4. Run the tool (Thordata handles CAPTCHA / anti-bot under the hood)
        task_id = client.run_tool(request)
        print(f"Task created: {task_id}")

        # 5. Wait for completion
        status = client.wait_for_task(task_id, max_wait=300)
        print("Final status:", status)

        if status.lower() not in {"ready", "success", "finished"}:
            print("Task did not complete successfully.")
            return

        # 6. Get the result download URL
        result_url = client.get_task_result(task_id)
        print("Result URL:", result_url)
    except ThordataError as exc:
        print("[ERROR] Thordata API error:", exc)
        return

    # 7. Download and inspect the JSON data
    resp = requests.get(result_url, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Many Amazon tools return a list of product objects.
    product = data[0] if isinstance(data, list) and data else data

    pprint(
        {
            "title": product.get("title"),
            "asin": product.get("asin"),
            "final_price": product.get("final_price"),
            "currency": product.get("currency"),
            "rating": product.get("rating"),
            "reviews_count": product.get("reviews_count"),
        }
    )


if __name__ == "__main__":
    main()


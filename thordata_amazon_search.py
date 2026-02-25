"""
Example: Search Amazon products by keyword using Thordata Web Scraper Tools.
"""

from __future__ import annotations

from pprint import pprint

import os
import requests
from thordata import ThordataClient, load_env_file
from thordata.exceptions import ThordataError
from thordata.tools import Amazon


def search_products(keyword: str, domain: str = "amazon.com", max_results: int = 10):
    load_env_file()

    client = ThordataClient(
        scraper_token=os.getenv("THORDATA_SCRAPER_TOKEN"),
        public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
        public_key=os.getenv("THORDATA_PUBLIC_KEY"),
    )

    # Amazon.Search includes parameters like keyword and domain
    request = Amazon.Search(keyword=keyword, domain=domain)

    print(f"Submitting search task for keyword: {keyword!r} on {domain}...")

    try:
        task_id = client.run_tool(request)
        print("Task ID:", task_id)

        status = client.wait_for_task(task_id, max_wait=300)
        print("Final status:", status)

        if status.lower() not in {"ready", "success", "finished"}:
            print("Task did not complete successfully.")
            return []

        result_url = client.get_task_result(task_id)
        print("Result URL:", result_url)
    except ThordataError as exc:
        print("[ERROR] Thordata API error:", exc)
        return []

    resp = requests.get(result_url, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Structure of the JSON can vary:
    # - sometimes it's a plain list of products
    # - sometimes it's a dict with a "products" field
    if isinstance(data, list):
        products = data
    else:
        products = data.get("products") or data

    if not isinstance(products, list):
        print("Unexpected result format; raw data:")
        pprint(data)
        return []

    return products[:max_results]


if __name__ == "__main__":
    items = search_products("wireless mouse", max_results=5)
    print(f"Found {len(items)} products")
    for item in items:
        print("-", item.get("title"), "| price:", item.get("final_price"))


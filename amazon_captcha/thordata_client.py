"""Thin wrapper around the Thordata Web Scraper Tools for Amazon.

This module packages the two examples from the original tutorial
(``thordata_amazon_product_by_asin.py`` and ``thordata_amazon_search.py``) into
reusable, env-validating, error-handling functions. Thordata handles IP
rotation, browser fingerprinting, and CAPTCHA / anti-bot challenges behind the
scenes; here we only deal with submitting tasks, waiting, and normalizing the
returned JSON.

The ``thordata`` SDK is an optional dependency. Import this module only when
the user has installed ``thordata-sdk``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

# Optional: thordata-sdk. Importing this module without the SDK installed raises
# a helpful ImportError via the function-level check below.
try:
    from thordata import ThordataClient, load_env_file
    from thordata.exceptions import ThordataError
    from thordata.tools import Amazon

    _HAS_THORDATA = True
except ImportError:  # pragma: no cover
    _HAS_THORDATA = False
    ThordataClient = None  # type: ignore[assignment,misc]
    ThordataError = Exception  # type: ignore[assignment,misc]
    Amazon = None  # type: ignore[assignment,misc]

    def load_env_file() -> None:  # type: ignore[no-redef]
        return None


REQUIRED_ENV = (
    "THORDATA_SCRAPER_TOKEN",
    "THORDATA_PUBLIC_TOKEN",
    "THORDATA_PUBLIC_KEY",
)

SUCCESS_STATES = frozenset({"ready", "success", "finished"})


class ThordataConfigError(RuntimeError):
    """Raised when required Thordata credentials are missing."""


@dataclass
class ThordataProduct:
    """Normalized Amazon product returned by Thordata."""

    asin: str | None
    title: str | None
    final_price: Any
    currency: str | None
    rating: Any
    reviews_count: Any
    raw: dict

    @classmethod
    def from_payload(cls, data: dict) -> ThordataProduct:
        return cls(
            asin=data.get("asin"),
            title=data.get("title"),
            final_price=data.get("final_price"),
            currency=data.get("currency"),
            rating=data.get("rating"),
            reviews_count=data.get("reviews_count"),
            raw=data,
        )

    def as_row(self) -> dict:
        return {
            "asin": self.asin,
            "title": self.title,
            "final_price": self.final_price,
            "currency": self.currency,
            "rating": self.rating,
            "reviews_count": self.reviews_count,
        }


def _ensure_ready() -> None:
    if not _HAS_THORDATA:
        raise ImportError(
            "thordata-sdk is not installed. Install it with "
            "`pip install thordata-sdk` to use the Thordata client."
        )
    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    if missing:
        raise ThordataConfigError(
            "Missing Thordata environment variables: "
            + ", ".join(missing)
            + ". Set them in .env or your shell."
        )


def _build_client() -> ThordataClient:
    _ensure_ready()
    load_env_file()
    return ThordataClient(
        scraper_token=os.getenv("THORDATA_SCRAPER_TOKEN"),
        public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
        public_key=os.getenv("THORDATA_PUBLIC_KEY"),
    )


def get_product_by_asin(
    asin: str,
    *,
    domain: str = "amazon.com",
    max_wait: int = 300,
    client: ThordataClient | None = None,
) -> ThordataProduct:
    """Fetch a single Amazon product by ASIN via Thordata."""
    client = client or _build_client()
    request = Amazon.ProductByAsin(asin=asin, domain=domain)
    task_id = client.run_tool(request)
    status = client.wait_for_task(task_id, max_wait=max_wait)
    if status.lower() not in SUCCESS_STATES:
        raise RuntimeError(f"Thordata task {task_id} ended in status {status!r}")
    result_url = client.get_task_result(task_id)
    import requests  # local import keeps the module import-light

    resp = requests.get(result_url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    payload = data[0] if isinstance(data, list) and data else data
    return ThordataProduct.from_payload(payload)


def search_products(
    keyword: str,
    *,
    domain: str = "amazon.com",
    max_results: int = 10,
    max_wait: int = 300,
    client: ThordataClient | None = None,
) -> list[ThordataProduct]:
    """Search Amazon products by keyword via Thordata."""
    client = client or _build_client()
    request = Amazon.Search(keyword=keyword, domain=domain)
    task_id = client.run_tool(request)
    status = client.wait_for_task(task_id, max_wait=max_wait)
    if status.lower() not in SUCCESS_STATES:
        raise RuntimeError(f"Thordata task {task_id} ended in status {status!r}")
    result_url = client.get_task_result(task_id)
    import requests

    resp = requests.get(result_url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        products = data
    else:
        products = data.get("products") or data
    if not isinstance(products, list):
        return []
    return [ThordataProduct.from_payload(p) for p in products[:max_results]]

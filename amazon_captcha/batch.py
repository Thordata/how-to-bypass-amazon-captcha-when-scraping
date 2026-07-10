"""Batch processing for many ASINs / URLs with concurrency control.

Wraps either the local fetcher (:mod:`amazon_captcha.fetch`) or the Thordata
client (:mod:`amazon_captcha.thordata_client`) so a list of ASINs can be
processed with bounded concurrency, optional progress bar, and graceful
per-item error handling.
"""

from __future__ import annotations

import concurrent.futures
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from .export import PRODUCT_COLUMNS

try:  # tqdm is optional — degrade gracefully when absent.
    from tqdm import tqdm

    _HAS_TQDM = True
except ImportError:  # pragma: no cover
    _HAS_TQDM = False


@dataclass
class BatchResult:
    """Outcome of a batch run."""

    ok: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.ok) + len(self.errors)


def asin_to_url(asin: str, domain: str = "amazon.com") -> str:
    """Build a canonical Amazon product URL from an ASIN."""
    asin = asin.strip()
    if asin.startswith(("http://", "https://")):
        return asin
    return f"https://www.{domain}/dp/{asin}"


def run_batch(
    items: Iterable[str],
    worker: Callable[[str], dict],
    *,
    max_workers: int = 4,
    show_progress: bool = True,
    desc: str = "processing",
) -> BatchResult:
    """Run *worker* over *items* with bounded concurrency.

    Args:
        items: Identifiers (ASINs or URLs) to process.
        worker: Callable that takes one item and returns a dict result. It may
            raise — failures are recorded, not propagated.
        max_workers: Thread pool size.
        show_progress: Show a tqdm bar when tqdm is installed.
        desc: Progress bar description.
    """
    items = list(items)
    result = BatchResult()

    iterator: Iterable[str] = items
    if show_progress and _HAS_TQDM:
        iterator = tqdm(items, desc=desc)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map = {pool.submit(worker, item): item for item in iterator}
        for future in concurrent.futures.as_completed(future_map):
            item = future_map[future]
            try:
                result.ok.append(future.result())
            except Exception as exc:  # noqa: BLE001 — batch must survive
                result.errors.append({"item": item, "error": repr(exc)})
    return result


__all__ = ["BatchResult", "asin_to_url", "run_batch", "PRODUCT_COLUMNS"]

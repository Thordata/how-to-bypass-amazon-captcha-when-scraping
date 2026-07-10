"""Export fetched / scraped product data to JSON or CSV."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable, Mapping
from pathlib import Path


def to_json(data: object, path: str | Path) -> Path:
    """Write *data* as pretty-printed JSON to *path*. Returns the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    return path


def to_csv(rows: Iterable[Mapping[str, object]], path: str | Path, *, columns: list[str] | None = None) -> Path:
    """Write a list-of-dicts to *path* as CSV.

    If *columns* is omitted, the union of keys (in first-seen order) is used.
    Missing keys become empty cells.
    """
    rows = list(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if columns is None:
        seen: dict[str, None] = {}
        for row in rows:
            seen.update(dict.fromkeys(row.keys()))
        columns = list(seen.keys())

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


# A stable column order that works well for Amazon product rows.
PRODUCT_COLUMNS: list[str] = [
    "asin",
    "title",
    "brand",
    "final_price",
    "currency",
    "rating",
    "reviews_count",
    "url",
]

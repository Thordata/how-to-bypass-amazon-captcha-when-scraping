"""Batch ASIN processing via Thordata, exported to CSV.

Reads one ASIN per line from a text file, fetches each via the Thordata client
with bounded concurrency, and writes a CSV of normalized product fields.

Requirements:
    pip install thordata-sdk tqdm
    Set THORDATA_SCRAPER_TOKEN, THORDATA_PUBLIC_TOKEN, THORDATA_PUBLIC_KEY in .env

Usage::

    python examples/thordata_batch_asin.py asins.txt products.csv --workers 3
"""

from __future__ import annotations

import argparse
from pathlib import Path

from amazon_captcha.batch import run_batch
from amazon_captcha.export import PRODUCT_COLUMNS, to_csv
from amazon_captcha.thordata_client import get_product_by_asin


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch-fetch ASINs via Thordata -> CSV.")
    parser.add_argument("input", help="text file, one ASIN per line")
    parser.add_argument("output", help="output CSV path")
    parser.add_argument("--domain", default="amazon.com")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--max-wait", type=int, default=300)
    args = parser.parse_args()

    asins = [
        line.strip()
        for line in Path(args.input).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

    def worker(asin: str) -> dict:
        product = get_product_by_asin(asin, domain=args.domain, max_wait=args.max_wait)
        return product.as_row()

    result = run_batch(asins, worker, max_workers=args.workers, desc="thordata")
    to_csv(result.ok, args.output, columns=PRODUCT_COLUMNS)
    print(f"wrote {len(result.ok)} products -> {args.output} ({len(result.errors)} errors)")
    for err in result.errors:
        print(f"  [ERR] {err['item']}: {err['error']}")


if __name__ == "__main__":
    main()

"""Unified command-line interface: ``python -m amazon_captcha <command>``.

Subcommands:

* ``detect``  — analyze a local HTML file (or stdin) for CAPTCHA markers.
* ``fetch``   — fetch a URL with retry/backoff/header rotation and report detection.
* ``batch``   — run the fetcher over a list of ASINs/URLs from a file.
* ``export``  — convert a JSON results file to CSV.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .batch import asin_to_url, run_batch
from .detect import detect
from .export import PRODUCT_COLUMNS, to_csv, to_json
from .fetch import fetch_with_retry


def _cmd_detect(args: argparse.Namespace) -> int:
    if args.html and args.html != "-":
        text = Path(args.html).read_text(encoding="utf-8", errors="replace")
    else:
        text = sys.stdin.read()
    result = detect(text, status=args.status, url=args.url)
    output = {
        "is_captcha": result.is_captcha,
        "risk_level": result.risk_level,
        "matched_markers": result.matched_markers,
        "status": result.status,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if not result.is_captcha else 1


def _cmd_fetch(args: argparse.Namespace) -> int:
    outcome = fetch_with_retry(
        args.url,
        max_attempts=args.max_attempts,
        timeout=args.timeout,
    )
    print(f"attempts={outcome.attempts} status={outcome.response.status_code}")
    print(f"is_captcha={outcome.detection.is_captcha} risk={outcome.detection.risk_level}")
    if outcome.detection.matched_markers:
        print("matched_markers:")
        for m in outcome.detection.matched_markers:
            print(f"  - {m}")
    if args.save:
        Path(args.save).write_text(outcome.response.text, encoding="utf-8")
        print(f"saved body -> {args.save}")
    return 0 if not outcome.is_captcha else 1


def _cmd_batch(args: argparse.Namespace) -> int:
    items = [
        line.strip()
        for line in Path(args.input).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    if args.as_asin:
        items = [asin_to_url(x, domain=args.domain) for x in items]

    def worker(url: str) -> dict:
        outcome = fetch_with_retry(url, max_attempts=args.max_attempts, timeout=args.timeout)
        return {
            "url": url,
            "status": outcome.response.status_code,
            "is_captcha": outcome.is_captcha,
            "risk_level": outcome.detection.risk_level,
            "matched_markers": outcome.detection.matched_markers,
        }

    result = run_batch(items, worker, max_workers=args.workers, desc="batch")
    to_json({"ok": result.ok, "errors": result.errors}, args.output)
    print(f"done: {len(result.ok)} ok, {len(result.errors)} errors -> {args.output}")
    return 0 if not result.errors else 1


def _cmd_export(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("ok") or data.get("products") or []
    if not isinstance(rows, list):
        print("expected a JSON list or an object with 'ok'/'products'", file=sys.stderr)
        return 2
    path = to_csv(rows, args.output, columns=PRODUCT_COLUMNS if args.product else None)
    print(f"wrote {len(rows)} rows -> {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="amazon_captcha",
        description="Amazon CAPTCHA detection & bypass toolkit (educational).",
    )
    parser.add_argument("--version", action="version", version=f"amazon_captcha {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_detect = sub.add_parser("detect", help="detect CAPTCHA markers in HTML")
    p_detect.add_argument("--html", help="path to HTML file (default: stdin)")
    p_detect.add_argument("--status", type=int, help="HTTP status code to factor in")
    p_detect.add_argument("--url", help="effective URL to also check")
    p_detect.set_defaults(func=_cmd_detect)

    p_fetch = sub.add_parser("fetch", help="fetch a URL with retry/backoff")
    p_fetch.add_argument("url")
    p_fetch.add_argument("--max-attempts", type=int, default=3)
    p_fetch.add_argument("--timeout", type=float, default=30.0)
    p_fetch.add_argument("--save", help="save response body to this path")
    p_fetch.set_defaults(func=_cmd_fetch)

    p_batch = sub.add_parser("batch", help="fetch many ASINs/URLs from a file")
    p_batch.add_argument("input", help="file with one URL/ASIN per line")
    p_batch.add_argument("output", help="output JSON path")
    p_batch.add_argument("--as-asin", action="store_true", help="treat input lines as ASINs")
    p_batch.add_argument("--domain", default="amazon.com")
    p_batch.add_argument("--workers", type=int, default=4)
    p_batch.add_argument("--max-attempts", type=int, default=3)
    p_batch.add_argument("--timeout", type=float, default=30.0)
    p_batch.set_defaults(func=_cmd_batch)

    p_export = sub.add_parser("export", help="convert JSON results to CSV")
    p_export.add_argument("input", help="JSON file (list or {ok:[...]} / {products:[...]})")
    p_export.add_argument("output", help="output CSV path")
    p_export.add_argument(
        "--product", action="store_true", help="use stable Amazon product columns"
    )
    p_export.set_defaults(func=_cmd_export)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

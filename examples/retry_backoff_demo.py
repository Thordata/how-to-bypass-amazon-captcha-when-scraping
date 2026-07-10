"""Retry + backoff + header rotation demo.

Shows how :func:`amazon_captcha.fetch.fetch_with_retry` rotates browser header
profiles across attempts and backs off with exponential delay when Amazon
challenges the request.

Run::

    python examples/retry_backoff_demo.py
"""

from __future__ import annotations

from amazon_captcha import fetch_with_retry

URL = "https://www.amazon.com/dp/B096N2MV3H"


def main() -> None:
    outcome = fetch_with_retry(URL, max_attempts=3)
    print(f"finished in {outcome.attempts} attempt(s)")
    print(f"  status      = {outcome.response.status_code}")
    print(f"  is_captcha  = {outcome.is_captcha}")
    print(f"  risk_level  = {outcome.detection.risk_level}")
    if outcome.detection.matched_markers:
        print("  matched markers:")
        for m in outcome.detection.matched_markers:
            print(f"    - {m}")


if __name__ == "__main__":
    main()

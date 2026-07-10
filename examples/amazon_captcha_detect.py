"""Detect whether an Amazon response is a CAPTCHA / robot-check page.

This example uses the shared detection logic in :mod:`amazon_captcha.detect`
so the behavior matches the browser-side Playground exactly.

Run::

    python examples/amazon_captcha_detect.py
"""

from __future__ import annotations

import requests

from amazon_captcha import detect

URL = "https://www.amazon.com/dp/B096N2MV3H"


def fetch_with_captcha_detection(url: str) -> requests.Response:
    resp = requests.get(url, timeout=30)
    result = detect(resp.text, status=resp.status_code, url=str(resp.url))
    print("Status:", resp.status_code)
    if result.is_captcha:
        print(f"[WARN] CAPTCHA / bot-check page detected (risk={result.risk_level}).")
        for marker in result.matched_markers:
            print(f"  - matched: {marker!r}")
    else:
        print(f"[INFO] Response looks like a normal page (risk={result.risk_level}).")
    return resp


def main() -> None:
    fetch_with_captcha_detection(URL)


if __name__ == "__main__":
    main()

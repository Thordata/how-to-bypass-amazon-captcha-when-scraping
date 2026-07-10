"""TLS / JA3 fingerprint demo with curl_cffi.

``curl_cffi`` lets you impersonate a real browser's TLS handshake and HTTP/2
settings, which naive ``requests`` cannot. This example demonstrates the
*idea* — it is not a production bypass. Amazon's anti-bot stack combines TLS,
headers, IP reputation, and behavioral signals; matching one layer is rarely
enough.

Install::

    pip install curl_cffi

Run::

    python examples/curl_cffi_tls_demo.py

Educational note:
    Even with a perfect TLS fingerprint, datacenter IPs, regular timing, and
    missing browser features still expose automation. This is the gap a managed
    solution like Thordata Web Scraper Tools is designed to fill.
"""

from __future__ import annotations

from amazon_captcha import detect

URL = "https://www.amazon.com/dp/B096N2MV3H"


def main() -> None:
    try:
        from curl_cffi import requests as cffi_requests
    except ImportError:
        print("[ERROR] curl_cffi is not installed. Run: pip install curl_cffi")
        return

    # impersonate="chrome121" makes curl_cffi reuse Chrome 121's TLS/HTTP2 profile.
    resp = cffi_requests.get(URL, impersonate="chrome121", timeout=30)
    result = detect(resp.text, status=resp.status_code, url=str(resp.url))
    print(f"status={resp.status_code} is_captcha={result.is_captcha} risk={result.risk_level}")
    if result.matched_markers:
        for m in result.matched_markers:
            print(f"  - {m}")


if __name__ == "__main__":
    main()

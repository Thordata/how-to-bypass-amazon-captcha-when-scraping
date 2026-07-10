"""Minimal request to Amazon that often hits CAPTCHA.

Run::

    python examples/amazon_captcha_minimal.py
"""

from __future__ import annotations

import requests

URL = "https://www.amazon.com/dp/B096N2MV3H"


def main() -> None:
    response = requests.get(URL, timeout=30)
    print("Status code:", response.status_code)
    print(response.text[:500])


if __name__ == "__main__":
    main()

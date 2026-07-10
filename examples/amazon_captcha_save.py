"""Save Amazon's response to HTML so you can inspect it for a CAPTCHA page.

Run::

    python examples/amazon_captcha_save.py
"""

from __future__ import annotations

import requests

URL = "https://www.amazon.com/dp/B096N2MV3H"


def main() -> None:
    response = requests.get(URL, timeout=30)
    with open("with_captcha.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Saved response to with_captcha.html (status:", response.status_code, ")")


if __name__ == "__main__":
    main()

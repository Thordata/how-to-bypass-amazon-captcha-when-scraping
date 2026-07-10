"""Playwright stealth demo (educational, not production-ready).

Shows how a headless browser can be configured to look less like an automation
tool: realistic viewport, locale, user-agent, and a few common "stealth"
tweaks. This is provided to *illustrate the complexity* of fingerprint
avoidance — every tweak is a moving target, and a hand-rolled stealth stack is
expensive to maintain.

Install::

    pip install playwright
    playwright install chromium

Run::

    python examples/playwright_stealth_demo.py

Why this is fragile:
    Real anti-bot vendors fingerprint canvas, fonts, WebGL, audio, and
    behavioral signals. Each requires ongoing maintenance. Managed scraping
    platforms (e.g. Thordata Web Scraper Tools) maintain these countermeasures
    for you, which is usually more cost-effective than building your own.
"""

from __future__ import annotations

from amazon_captcha import detect

URL = "https://www.amazon.com/dp/B096N2MV3H"

# A few common stealth tweaks. Not exhaustive; not a silver bullet.
STEALTH_INIT = """
() => {
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
    window.chrome = { runtime: {} };
}
"""


def main() -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("[ERROR] playwright is not installed. Run: pip install playwright")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        # Apply stealth tweaks before any navigation.
        context.add_init_script(STEALTH_INIT)
        page = context.new_page()
        page.goto(URL, timeout=30000, wait_until="domcontentloaded")
        html = page.content()
        result = detect(html, url=URL)
        print(f"is_captcha={result.is_captcha} risk={result.risk_level}")
        if result.matched_markers:
            for m in result.matched_markers:
                print(f"  - {m}")
        browser.close()


if __name__ == "__main__":
    main()

## How to Bypass Amazon CAPTCHA When Scraping (Free 2026 Python Guide)

> This repository intentionally keeps the structure **minimal**: a single `README.md` and a few small example scripts.  
> All code examples and explanations live in this file.  
> Examples were tested around **2026‑02‑25**, but Amazon’s HTML and anti‑bot behavior change frequently, so treat this as a starting point, not a guaranteed long‑term solution.

In this guide, we focus on **how Amazon CAPTCHA is triggered when you scrape**, what you can realistically do with **pure Python and free tools**, and when it makes sense to switch to a managed solution like **Thordata Web Scraper Tools**.

- **Part 1 (≈80%) – Free, manual approach** with `requests`:  
  you’ll build a simple scraper that quickly hits CAPTCHA, learn how to detect it, and see why manual tricks are fragile.
- **Part 2 (≈20%) – Easier, managed approach with Thordata**:  
  you’ll use Thordata’s Amazon tools via the official Python SDK; IP rotation, headless browsers, and CAPTCHA handling are abstracted away and you get structured data.

If you only want the code, jump to:

- [🎯 Minimal “with CAPTCHA” example](#-minimal-with-captcha-example)
- [🚀 Bypass CAPTCHA the easy way with Thordata](#-bypass-captcha-the-easy-way-with-thordata)

---

## Repository structure

This repo is intentionally simple:

- `README.md` – the complete free tutorial you’re reading now.
- `amazon_captcha_minimal.py` – single request to Amazon that often hits CAPTCHA.
- `amazon_captcha_save.py` – saves HTML to `with_captcha.html` so you can inspect the CAPTCHA page.
- `amazon_captcha_detect.py` – shows how to detect CAPTCHA responses in code.
- `thordata_amazon_product_by_asin.py` – Thordata example: product details by ASIN.
- `thordata_amazon_search.py` – Thordata example: search products by keyword.
- `images/architecture_flow.mmd` – Mermaid source for the high-level architecture diagram (optional for GitHub viewers).

You can follow the tutorial just by copy‑pasting from this README, or by running the helper scripts directly.

---

## Contents

- [Disclaimer and compliance](#disclaimer-and-compliance)
- [Part 0 – Setup](#part-0--setup)
  - [Create a virtual environment](#create-a-virtual-environment)
  - [Install dependencies](#install-dependencies)
- [Part 1 – Free manual approach: seeing and detecting CAPTCHA](#part-1--free-manual-approach-seeing-and-detecting-captcha)
  - [1. Minimal request that likely triggers CAPTCHA](#1-minimal-request-that-likely-triggers-captcha)
  - [2. Saving the HTML and inspecting the CAPTCHA page](#2-saving-the-html-and-inspecting-the-captcha-page)
  - [3. Detecting CAPTCHA responses programmatically](#3-detecting-captcha-responses-programmatically)
  - [4. Adding browser-like headers (what helps, what doesn’t)](#4-adding-browser-like-headers-what-helps-what-doesnt)
  - [5. Why manual CAPTCHA bypass doesn’t really scale](#5-why-manual-captcha-bypass-doesnt-really-scale)
- [Part 2 – Bypass CAPTCHA the easy way with Thordata](#part-2--bypass-captcha-the-easy-way-with-thordata)
  - [1. How Thordata helps with CAPTCHA and anti-bot](#1-how-thordata-helps-with-captcha-and-anti-bot)
  - [2. Installation and configuration](#2-installation-and-configuration)
  - [3. Example: Get product details by ASIN (without touching CAPTCHA)](#3-example-get-product-details-by-asin-without-touching-captcha)
  - [4. Example: Search Amazon products by keyword](#4-example-search-amazon-products-by-keyword)
  - [5. Manual vs. Thordata comparison (CAPTCHA focus)](#5-manual-vs-thordata-comparison-captcha-focus)
- [Advanced – Modern anti-bot & CAPTCHA landscape (2026)](#advanced--modern-anti-bot--captcha-landscape-2026)
- [Troubleshooting and FAQ](#troubleshooting-and-faq)
- [Related Thordata resources](#related-thordata-resources)
- [Final notes](#final-notes)

---

## Disclaimer and compliance

- This repository is for **technical learning and research only**.
- Always respect Amazon’s **Terms of Service**, robots rules, and applicable laws in your jurisdiction.
- Do not use the examples here to abuse, overload, or harm any website.
- For commercial or large‑scale usage, strongly consider a compliant managed solution (such as Thordata Web Scraper Tools) and, if needed, seek legal advice.

---

## Part 0 – Setup

### Create a virtual environment

**macOS / Linux:**

```bash
python3 -m venv .env
source .env/bin/activate
```

**Windows:**

```bash
python -m venv .env
.env\Scripts\activate
```

You can keep this tutorial in its own folder:

```bash
mkdir amazon-captcha-tutorial
cd amazon-captcha-tutorial
```

### Install dependencies

For the free/manual part we only need `requests`:

```bash
pip install requests
```

For the Thordata section we’ll add the official SDK:

```bash
pip install thordata-sdk
```

Optional but convenient for local `.env` files:

```bash
pip install python-dotenv
```

Quick sanity check:

```bash
python -c "import requests; print('requests OK')"
```

---

## Part 1 – Free manual approach: seeing and detecting CAPTCHA

This part is deliberately **low‑level**. The goal is to:

- **Trigger** the Amazon bot protection / CAPTCHA page with a naive scraper.
- Learn to **recognize** when you received a CAPTCHA instead of real product HTML.
- Understand **why** simple header tweaks rarely “solve” CAPTCHA at scale.

### 🎯 Minimal “with CAPTCHA” example

### 1. Minimal request that likely triggers CAPTCHA

Create `amazon_captcha_minimal.py`:

```python
import requests

# A random product URL; you can replace with any other product.
URL = "https://www.amazon.com/dp/B096N2MV3H"

response = requests.get(URL)
print("Status code:", response.status_code)

# Print a small snippet so we don't flood the terminal
print(response.text[:500])
```

Run it:

```bash
python amazon_captcha_minimal.py
```

Typical outcomes:

- Status code might be `503`, `403`, or even `200`.
- The HTML may not be a product page at all, but a **bot-detection / CAPTCHA** page.

You’ll often see hints like:

- References to **“robot check”**,  
- Text asking you to “type the characters you see in this image”,  
- Or links that include words like `captcha`.

### 2. Saving the HTML and inspecting the CAPTCHA page

Let’s store the full HTML to a file for inspection.

Create `amazon_captcha_save.py`:

```python
import requests

URL = "https://www.amazon.com/dp/B096N2MV3H"

response = requests.get(URL)

with open("with_captcha.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Saved response to with_captcha.html (status:", response.status_code, ")")
```

Run:

```bash
python amazon_captcha_save.py
```

Then open `with_captcha.html` in a browser:

- If you see a **normal product page**, your IP and request pattern are still “healthy”.
- If you see a **CAPTCHA / robot-check page**, the bot protection layer is actively blocking this request.

Things that influence this:

- IP reputation (datacenter vs. residential, shared vs. unique).
- Request frequency and patterns.
- Presence/absence of cookies and JavaScript execution.
- Historical behavior from the same IP or IP range.

### 3. Detecting CAPTCHA responses programmatically

In real scripts you don’t want to manually open HTML every time.  
We can do a simple content-based check.

Create `amazon_captcha_detect.py`:

```python
import requests

URL = "https://www.amazon.com/dp/B096N2MV3H"

CAPTCHA_MARKERS = [
    "Type the characters you see in this image",
    "To discuss automated access to Amazon data",
    "/captcha/",  # Often appears in URLs or JS
]


def looks_like_captcha(html: str) -> bool:
    lower = html.lower()
    return any(marker.lower() in lower for marker in CAPTCHA_MARKERS)


def fetch_with_captcha_detection(url: str):
    resp = requests.get(url, timeout=30)
    print("Status:", resp.status_code)

    if looks_like_captcha(resp.text):
        print("[WARN] This response looks like a CAPTCHA / bot-check page.")
    else:
        print("[INFO] This response looks like a normal page.")
    return resp


if __name__ == "__main__":
    fetch_with_captcha_detection(URL)
```

This is **not** bullet‑proof (Amazon can change wording anytime), but it’s:

- Good enough to **avoid feeding CAPTCHA HTML into your parsers**.
- Useful to add logging like “we’re being challenged, back off or switch strategy”.

### 4. Adding browser-like headers (what helps, what doesn’t)

One of the **first** things people try is spoofing browser headers.  
This can help a bit for **small‑scale experiments**, but it does **not** “turn off” bot detection or CAPTCHA.

Update the script to include basic headers:

```python
import requests

URL = "https://www.amazon.com/dp/B096N2MV3H"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Referer": "https://www.google.com/",
}


def fetch(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    print("Status:", resp.status_code)
    print(resp.text[:500])
    return resp


if __name__ == "__main__":
    fetch(URL)
```

If your IP is relatively “clean” and your frequency is low, you might:

- Get real product HTML more often.
- Delay or reduce the frequency of CAPTCHA pages.

However, even with **perfect headers**, you still have to worry about:

- Complex JavaScript-based fingerprinting and checks.
- Behavioral signals (too fast, too regular, many pages per minute).
- IP reputation and historical data.

For real‑world crawling, this quickly becomes a losing battle if you try to handle everything yourself.

### 5. Why manual CAPTCHA bypass doesn’t really scale

Important distinctions:

- **Solving CAPTCHAs** (e.g., sending images to a CAPTCHA‑solving service or using machine learning to break them) can violate terms of service and may be legally risky.
- **Avoiding CAPTCHAs** by looking more like real users (IP rotation, realistic browser automation, rate limiting, challenge handling) is usually the **safer**, infrastructure‑heavy path.

Trying to build all of this from scratch means you must maintain:

- A pool of residential / mobile / ISP IPs.
- Browser automation that passes fingerprinting and challenge flows.
- Robust retry and backoff logic.
- Continuous updates as anti‑bot techniques evolve.

This is exactly the layer that managed scraping platforms (such as Thordata) are designed to handle for you.

---

## Part 2 – Bypass CAPTCHA the easy way with Thordata

### 🚀 Bypass CAPTCHA the easy way with Thordata

### 1. How Thordata helps with CAPTCHA and anti-bot

Instead of:

- Sending raw `requests.get` to Amazon,
- Fighting with 403/503, CAPTCHA pages, and fragile HTML parsing,

you can:

- Use Thordata’s **Web Scraper Tools** for Amazon (product, search, category, etc.).
- Let Thordata handle **IP rotation, browser automation, and CAPTCHA / anti‑bot challenges** behind the scenes.
- Receive **clean structured data** (JSON) via a simple Python API.

You still need to use the data responsibly and respect Amazon’s rules, but you don’t have to maintain the low-level anti‑bot machinery.

### 2. Installation and configuration

Install the official SDK:

```bash
pip install thordata-sdk
```

Create a `.env` file (or set environment variables in your system):

```ini
THORDATA_SCRAPER_TOKEN=your_scraper_token
THORDATA_PUBLIC_TOKEN=your_public_token
THORDATA_PUBLIC_KEY=your_public_key
```

In Python, load the environment (two options):

**Option A – using the SDK helper:**

```python
from thordata import load_env_file

load_env_file()  # loads ./.env if present; does not override existing env vars
```

**Option B – using `python-dotenv`:**

```python
from dotenv import load_dotenv

load_dotenv()
```

Then create a client:

```python
from thordata import ThordataClient

client = ThordataClient()  # reads tokens from environment
```

### 3. Example: Get product details by ASIN (without touching CAPTCHA)

This example uses a high-level Amazon tool.  
You don’t manage CAPTCHAs, IPs, or headless browsers directly—Thordata does.

Create `thordata_amazon_product_by_asin.py`:

```python
"""
Example: Fetch Amazon product details by ASIN using Thordata Web Scraper Tools.

Requirements:
    pip install thordata-sdk
    Set THORDATA_SCRAPER_TOKEN, THORDATA_PUBLIC_TOKEN, THORDATA_PUBLIC_KEY in .env
"""

from __future__ import annotations

import os
from pprint import pprint

import requests
from thordata import ThordataClient, load_env_file
from thordata.exceptions import ThordataError
from thordata.tools import Amazon


def ensure_thordata_env() -> bool:
    """Return True if essential Thordata env vars look present."""
    required = [
        "THORDATA_SCRAPER_TOKEN",
        "THORDATA_PUBLIC_TOKEN",
        "THORDATA_PUBLIC_KEY",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        print("[ERROR] Missing Thordata environment variables:", ", ".join(missing))
        print(
            "Create a .env file with these keys or export them in your shell "
            "before running this script."
        )
        return False
    return True


def main() -> None:
    # 1. Load environment from .env (optional but convenient)
    load_env_file()

    if not ensure_thordata_env():
        return

    # 2. Initialize client with explicit credentials from env vars
    client = ThordataClient(
        scraper_token=os.getenv("THORDATA_SCRAPER_TOKEN"),
        public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
        public_key=os.getenv("THORDATA_PUBLIC_KEY"),
    )

    # 3. Define the scraping task: product by ASIN on amazon.com
    request = Amazon.ProductByAsin(
        asin="B0BZYCJK89",
        domain="amazon.com",
    )

    print(f"Submitting task for ASIN: {request.asin}...")

    try:
        # 4. Run the tool (Thordata handles CAPTCHA / anti-bot under the hood)
        task_id = client.run_tool(request)
        print(f"Task created: {task_id}")

        # 5. Wait for completion
        status = client.wait_for_task(task_id, max_wait=300)
        print("Final status:", status)

        if status.lower() not in {"ready", "success", "finished"}:
            print("Task did not complete successfully.")
            return

        # 6. Get the result download URL
        result_url = client.get_task_result(task_id)
        print("Result URL:", result_url)
    except ThordataError as exc:
        print("[ERROR] Thordata API error:", exc)
        return

    # 7. Download and inspect the JSON data
    resp = requests.get(result_url, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Many Amazon tools return a list of product objects.
    product = data[0] if isinstance(data, list) and data else data

    pprint(
        {
            "title": product.get("title"),
            "asin": product.get("asin"),
            "final_price": product.get("final_price"),
            "currency": product.get("currency"),
            "rating": product.get("rating"),
            "reviews_count": product.get("reviews_count"),
        }
    )


if __name__ == "__main__":
    main()
```

Instead of juggling headers and parsing raw HTML, you now:

- Submit a **single task**,
- Let Thordata handle the **anti‑bot path** including CAPTCHA,
- Download structured **JSON**.

### 4. Example: Search Amazon products by keyword

You can also search products by keyword (e.g., for price monitoring or competitor analysis).

Create `thordata_amazon_search.py`:

```python
"""
Example: Search Amazon products by keyword using Thordata Web Scraper Tools.
"""

from __future__ import annotations

import os
from pprint import pprint

import requests
from thordata import ThordataClient, load_env_file
from thordata.exceptions import ThordataError
from thordata.tools import Amazon


def search_products(keyword: str, domain: str = "amazon.com", max_results: int = 10):
    load_env_file()

    client = ThordataClient(
        scraper_token=os.getenv("THORDATA_SCRAPER_TOKEN"),
        public_token=os.getenv("THORDATA_PUBLIC_TOKEN"),
        public_key=os.getenv("THORDATA_PUBLIC_KEY"),
    )

    # Amazon.Search includes parameters like keyword and domain
    request = Amazon.Search(keyword=keyword, domain=domain)

    print(f"Submitting search task for keyword: {keyword!r} on {domain}...")

    try:
        task_id = client.run_tool(request)
        print("Task ID:", task_id)

        status = client.wait_for_task(task_id, max_wait=300)
        print("Final status:", status)

        if status.lower() not in {"ready", "success", "finished"}:
            print("Task did not complete successfully.")
            return []

        result_url = client.get_task_result(task_id)
        print("Result URL:", result_url)
    except ThordataError as exc:
        print("[ERROR] Thordata API error:", exc)
        return []

    resp = requests.get(result_url, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Structure of the JSON can vary:
    # - sometimes it's a plain list of products
    # - sometimes it's a dict with a "products" field
    if isinstance(data, list):
        products = data
    else:
        products = data.get("products") or data

    if not isinstance(products, list):
        print("Unexpected result format; raw data:")
        pprint(data)
        return []

    return products[:max_results]


if __name__ == "__main__":
    items = search_products("wireless mouse", max_results=5)
    print(f"Found {len(items)} products")
    for item in items:
        print("-", item.get("title"), "| price:", item.get("final_price"))
```

With this approach:

- You’re **not** manually trying to bypass CAPTCHA.  
- The Thordata backend coordinates **IP rotation, browser behavior, and anti‑bot challenges**, so you just call a tool and receive JSON.

### 5. Manual vs. Thordata comparison (CAPTCHA focus)

| Aspect                   | Manual free approach (Part 1)                          | Thordata Web Scraper Tools (Part 2)                              |
|--------------------------|--------------------------------------------------------|------------------------------------------------------------------|
| Anti‑bot / CAPTCHA       | You hit CAPTCHA frequently on raw `requests`          | Thordata handles CAPTCHA & anti‑bot flows internally            |
| Headers & cookies        | You manage them by hand                               | Managed automatically; tuned by Thordata                         |
| IP / proxy management    | You must source and rotate IPs yourself               | IP pool and rotation handled by the platform                    |
| Parsing workload         | You parse HTML, handle layout changes                 | You consume JSON payloads with stable fields                    |
| Learning value           | High – see how and when CAPTCHA triggers              | Medium – focuses on real-world, production-like usage           |
| Best use cases           | Small experiments, educational projects               | Commercial / large-scale scraping and production workloads      |

A common pattern is:

1. Use the **manual scripts** to understand how Amazon’s protections work and how to detect CAPTCHA.
2. When you’re ready to move beyond toy examples, switch to **Thordata Web Scraper Tools** for stable data collection.

---

## Advanced – Modern anti-bot & CAPTCHA landscape (2026)

Amazon and other large sites now combine several layers of bot detection. It’s useful to understand these even if you ultimately rely on Thordata to handle them.

- **IP reputation and ASN checks**: datacenter IPs (especially from known cloud providers) are scrutinized more heavily than residential / mobile / ISP ranges.
- **TLS and HTTP fingerprinting**: subtle details of your TLS handshake, HTTP/2 prioritization, and cipher choices can identify popular scraping libraries.
- **Browser fingerprinting**: headless browser modes, missing fonts, odd canvas results, and uniform viewport sizes all contribute to bot scores.
- **Behavioral analysis**: very regular request timing, no scrolling, and zero interaction patterns are strong signals of automated access.

In practice, modern scraping stacks combine several techniques:

- **High-quality, rotating IPs**: residential / ISP proxies with geo-targeting and per-request rotation for large-scale workloads.
- **Headless browser automation**: Playwright / Puppeteer / similar tools configured in “stealth” modes, with realistic viewport, locale, and feature support.
- **Human-like pacing and concurrency**: deliberate rate limits, jittered delays, and conservative concurrency per target domain.
- **Challenge handling**: automated flows to pass JavaScript-based checks and, where allowed, third-party CAPTCHA solvers.

Thordata’s Web Scraper Tools encapsulate these layers so that your Python code remains simple. Conceptually, the flow looks like this:

```mermaid
flowchart LR
    A[Your script\n(thordata_amazon_product_by_asin.py)] --> B[Thordata API]
    B --> C[Anti-bot & CAPTCHA layer\n(IPs, browser, challenges)]
    C --> D[Amazon]
    D --> C
    C --> E[Normalized JSON result]
    E --> A
```

If you decide to build your own infrastructure instead, you will need to re-create most of the pieces in nodes **B–C** above and maintain them over time.

---

## Troubleshooting and FAQ

### Scripts run but I only see 503 / “Service Unavailable” from Amazon

- This is expected when using plain `requests` without any proxy or browser layer.  
- Use `amazon_captcha_save.py` to save the HTML and confirm you’re seeing a CAPTCHA / bot-check page.  
- Reduce request frequency, try from a different network, or move to the Thordata-based examples for more robust access.

### `thordata_amazon_product_by_asin.py` says public_token / public_key are missing

- Create a `.env` file in the project root with:
  - `THORDATA_SCRAPER_TOKEN=...`
  - `THORDATA_PUBLIC_TOKEN=...`
  - `THORDATA_PUBLIC_KEY=...`
- Make sure the values are correct and that you are running the script from the same folder so `load_env_file()` can find `.env`.

### Thordata scripts run, but some fields are `None` or missing

- Different tools (e.g. product-by-ASIN vs. keyword search) expose slightly different JSON schemas.
- Use `print(data[0])` or `pprint(data[0])` (for list responses) to inspect all available fields and adjust your processing logic.
- The examples in this README focus on a small, stable subset of fields for clarity.

### How do I turn JSON results into CSV?

- For small experiments, you can quickly convert list-of-dicts JSON into CSV with `pandas`:

```python
import pandas as pd

df = pd.DataFrame(products)  # products is a list of dicts from Thordata
df.to_csv("amazon_products.csv", index=False)
```

For more advanced data pipelines, consider writing into databases or data warehouses once you’re happy with the fields and volume.

---

## Related Thordata resources

- **Thordata GitHub organization**: `https://github.com/Thordata`  
- **Python SDK**: `https://github.com/Thordata/thordata-python-sdk`  
- **Amazon scraper examples** (Web Scraper Tools): see `examples/tools/amazon_scraper.py` in the SDK repo.  
- **Thordata website**: `https://www.thordata.com` (for product overview, pricing, and up‑to‑date documentation).

---

## Final notes

This guide is intentionally **“how‑to first, marketing second”**: you’ve seen how to trigger and detect Amazon CAPTCHA with free tools, and why maintaining a home‑grown bypass is hard.  
If you reach the point where keeping your own anti‑bot infrastructure updated is more work than the scraping itself, that’s usually when teams switch to a managed solution like Thordata’s Web Scraper Tools so they can focus on the data rather than the plumbing.


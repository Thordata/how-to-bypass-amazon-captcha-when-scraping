<div align="center">

<img src="images/banner.svg" alt="How to Bypass Amazon CAPTCHA When Scraping" width="880">

[![CI](https://github.com/Thordata/how-to-bypass-amazon-captcha-when-scraping/actions/workflows/ci.yml/badge.svg)](https://github.com/Thordata/how-to-bypass-amazon-captcha-when-scraping/actions/workflows/ci.yml)
[![Pages](https://github.com/Thordata/how-to-bypass-amazon-captcha-when-scraping/actions/workflows/deploy-pages.yml/badge.svg)](https://thordata.github.io/how-to-bypass-amazon-captcha-when-scraping/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-online-ff9900.svg)](https://thordata.github.io/how-to-bypass-amazon-captcha-when-scraping/)

<h3>A how-to-first Python guide: detect Amazon CAPTCHA with free tools, understand modern anti-bot, and use Thordata Web Scraper Tools for stable structured data.</h3>

[🌐 Documentation Site](https://thordata.github.io/how-to-bypass-amazon-captcha-when-scraping/) · [🎮 Playground](https://thordata.github.io/how-to-bypass-amazon-captcha-when-scraping/playground.html) · [📘 中文说明](README.zh-CN.md)

</div>

---

> **🌍 Language:** English · [中文](README.zh-CN.md)

## What this is

A practical, code-first tutorial on **how Amazon CAPTCHA is triggered when you scrape**, what you can realistically do with **pure Python and free tools**, and when it makes sense to switch to a managed solution like **Thordata Web Scraper Tools**.

- **Part 1 (~80%) — Free, manual approach** with `requests`: build a simple scraper that hits CAPTCHA, learn to detect it, and see why manual tricks are fragile.
- **Part 2 (~20%) — Managed approach with Thordata**: use Amazon tools via the official Python SDK; IP rotation, headless browsers, and CAPTCHA handling are abstracted away.

The full tutorial lives on the **[documentation site](https://thordata.github.io/how-to-bypass-amazon-captcha-when-scraping/)** — this README is the quick-start companion.

## ✨ Features

- 🛡️ **CAPTCHA detection library** — content + status heuristics, structured `DetectionResult`, 4-level risk scoring
- 🔄 **Header rotation pool** — curated browser profiles (Chrome/Edge/Firefox) with consistent `Sec-CH-UA` companion headers
- 🔁 **Retrying fetcher** — exponential backoff, per-attempt header rotation, CAPTCHA-aware retries
- 📦 **Batch processing** — bounded concurrency, progress bar, graceful per-item errors
- 💾 **JSON/CSV export** — stable Amazon product column ordering
- 🖥️ **Unified CLI** — `python -m amazon_captcha {detect|fetch|batch|export}`
- 🎮 **Interactive Playground** — 100% client-side detector demo, mirrors the Python marker list exactly
- 🧪 **Offline test suite** — 36 tests, no real network calls

## 🚀 Quick start

```bash
# Clone
git clone https://github.com/Thordata/how-to-bypass-amazon-captcha-when-scraping.git
cd how-to-bypass-amazon-captcha-when-scraping

# Install the package (editable, with dev tooling)
pip install -e ".[dev]"

# Use the CLI
python -m amazon_captcha --help
echo "<html><body>type the characters you see in this image</body></html>" \
  | python -m amazon_captcha detect --status 503
```

Run the example scripts:

```bash
python examples/amazon_captcha_detect.py        # detect CAPTCHA in a real response
python examples/retry_backoff_demo.py           # retry + backoff + header rotation
python examples/curl_cffi_tls_demo.py           # TLS/JA3 impersonation (needs curl_cffi)
python examples/playwright_stealth_demo.py      # stealth headless browser (needs playwright)
```

For the Thordata managed path:

```bash
pip install -e ".[thordata]"
# create .env with THORDATA_SCRAPER_TOKEN / THORDATA_PUBLIC_TOKEN / THORDATA_PUBLIC_KEY
python examples/thordata_amazon_product_by_asin.py
```

## 📁 Repository structure

```
amazon_captcha/          # installable package
├── detect.py            # CAPTCHA markers, risk levels, DetectionResult
├── headers.py           # browser profile pool + rotation
├── fetch.py             # retrying fetcher w/ backoff
├── export.py            # JSON/CSV export
├── batch.py             # bounded-concurrency batch runner
├── thordata_client.py   # env-validated Thordata wrapper
└── cli.py               # unified CLI
examples/                # runnable demos (minimal → advanced)
tests/                   # offline pytest suite
docs/                    # GitHub Pages source (site + playground)
images/                  # diagrams + banner
```

## 🧪 Tests & linting

```bash
pytest -ra               # 36 offline tests
ruff check .             # lint
ruff format --check .    # format check
```

CI runs on Python 3.10 / 3.11 / 3.12 for every push and PR.

## 🛡️ Manual vs. Thordata (CAPTCHA focus)

| Aspect | Manual (Part 1) | Thordata (Part 2) |
|---|---|---|
| Anti-bot / CAPTCHA | You hit CAPTCHA frequently | Handled internally |
| Headers & cookies | Managed by hand | Tuned automatically |
| IP / proxy management | Source & rotate yourself | Pool + rotation handled |
| Parsing workload | Parse HTML, handle changes | Consume stable JSON |
| Best for | Experiments, learning | Commercial / large-scale |

## ⚖️ Disclaimer & compliance

This repository is for **technical learning and research only**. Always respect Amazon's Terms of Service, robots rules, and applicable laws. Do not overload, damage, or disrupt target sites. For commercial or large-scale usage, consider a compliant managed solution and seek legal advice if unsure. The authors and Thordata do not provide legal advice and are not liable for misuse. See [SECURITY.md](SECURITY.md) and the [legal notice](https://thordata.github.io/how-to-bypass-amazon-captcha-when-scraping/#legal).

## 📚 Related Thordata resources

- **Thordata GitHub:** [github.com/Thordata](https://github.com/Thordata)
- **Python SDK:** [thordata-python-sdk](https://github.com/Thordata/thordata-python-sdk)
- **Website:** [thordata.com](https://www.thordata.com)

## 🤝 Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## 📄 License

[MIT](LICENSE) © Thordata

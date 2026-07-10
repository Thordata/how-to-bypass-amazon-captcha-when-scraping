# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-07-10

### Added
- **`amazon_captcha` package** with detection (`detect.py`), browser header pool
  (`headers.py`), retrying fetcher (`fetch.py`), JSON/CSV export (`export.py`),
  bounded-concurrency batch runner (`batch.py`), and a Thordata SDK wrapper
  (`thordata_client.py`).
- **Unified CLI**: `python -m amazon_captcha {detect|fetch|batch|export}`.
- **9 example scripts** in `examples/`, including advanced demos for retry/backoff,
  `curl_cffi` TLS impersonation, Playwright stealth, and Thordata batch ASIN.
- **Offline pytest suite** (36 tests, no real network).
- **GitHub Pages documentation site** (`docs/index.html`) with dark/light themes,
  scroll-spy TOC, Prism-highlighted code blocks with copy buttons, comparison
  cards, an animated architecture flow diagram, and a FAQ accordion.
- **Interactive CAPTCHA Detector Playground** (`docs/playground.html`) — 100%
  client-side, mirrors the Python marker list, with risk meter, marker editor,
  and JSON export.
- **CI workflow** (Python 3.10/3.11/3.12, ruff + pytest) and **Pages deploy** workflow.
- **Bilingual README** (English + `README.zh-CN.md`), `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`, MIT `LICENSE`, issue templates.
- `pyproject.toml` with optional dependency groups.

### Changed
- Restructured the original five loose scripts into a package under `examples/`
  backed by a reusable `amazon_captcha` module.
- Expanded the CAPTCHA marker list beyond the original three markers.

### Notes
- Examples were tested around 2026-02-25; Amazon's HTML and anti-bot behavior
  change frequently.

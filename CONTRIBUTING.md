# Contributing to the Amazon CAPTCHA guide

Thanks for your interest in improving this tutorial! This repo is educational, so contributions that **clarify, correct, or expand the teaching** are especially welcome.

## Ways to contribute

- 🐛 Report inaccuracies (stale markers, changed Amazon behavior, broken examples)
- 📝 Improve explanations or add clarifying diagrams
- 🧪 Add offline tests for existing logic
- 🎨 Polish the docs site or Playground UX
- 🌍 Improve translations (see `README.zh-CN.md`)

## Before you start

- Examples were tested around **2026-02-25**; Amazon's HTML and anti-bot behavior change frequently. If something no longer reproduces, open an issue first so we can discuss.
- This is an **educational** repo — do not add features whose primary purpose is to defeat specific anti-bot vendors. Detection and understanding are in scope; evasion tooling is not.

## Development setup

```bash
git clone https://github.com/Thordata/how-to-bypass-amazon-captcha-when-scraping.git
cd how-to-bypass-amazon-captcha-when-scraping
pip install -e ".[dev]"
```

## Making changes

1. Create a branch from `main`.
2. Make your change. Keep code consistent with the surrounding style (enforced by `ruff`).
3. Make sure the following pass locally:

   ```bash
   ruff check .
   ruff format --check .
   pytest -ra
   ```

4. If you change `docs/`, verify locally:

   ```bash
   python -m http.server 8099 --directory docs
   # open http://localhost:8099/
   ```

5. Keep the **marker list in sync**: `amazon_captcha/detect.py` and `docs/assets/js/playground.js` must contain the same `CAPTCHA_MARKERS`. If you edit one, edit the other.

6. Write clear commit messages. Open a PR against `main`.

## Marker-list sync checklist

- [ ] `amazon_captcha/detect.py` `CAPTCHA_MARKERS`
- [ ] `docs/assets/js/playground.js` `CAPTCHA_MARKERS`
- [ ] `tests/test_detect.py` updated if behavior changes

## Code of conduct

By participating you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

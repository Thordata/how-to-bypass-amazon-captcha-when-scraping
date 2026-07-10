"""amazon_captcha — educational Amazon CAPTCHA detection & bypass toolkit.

This package is the code companion to the
"how-to-bypass-amazon-captcha-when-scraping" tutorial. It provides:

* CAPTCHA detection heuristics (:mod:`amazon_captcha.detect`)
* Browser-like header pools (:mod:`amazon_captcha.headers`)
* A retrying, header-rotating fetcher (:mod:`amazon_captcha.fetch`)
* JSON/CSV export helpers (:mod:`amazon_captcha.export`)
* Batch processing with bounded concurrency (:mod:`amazon_captcha.batch`)
* A thin wrapper over the Thordata SDK (:mod:`amazon_captcha.thordata_client`)
* A unified CLI: ``python -m amazon_captcha ...``

See ``README.md`` and the GitHub Pages site for the full tutorial.
"""

from __future__ import annotations

from .detect import (
    CAPTCHA_MARKERS,
    CHALLENGE_STATUS_CODES,
    DetectionResult,
    detect,
    find_markers,
    looks_like_captcha,
)
from .export import PRODUCT_COLUMNS, to_csv, to_json
from .fetch import FetchError, FetchOutcome, fetch_once, fetch_with_retry
from .headers import (
    BROWSER_PROFILES,
    BrowserProfile,
    get_profile,
    random_profile,
    rotating_profiles,
)

__version__ = "1.0.0"

__all__ = [
    "CAPTCHA_MARKERS",
    "CHALLENGE_STATUS_CODES",
    "DetectionResult",
    "detect",
    "find_markers",
    "looks_like_captcha",
    "PRODUCT_COLUMNS",
    "to_csv",
    "to_json",
    "FetchError",
    "FetchOutcome",
    "fetch_once",
    "fetch_with_retry",
    "BROWSER_PROFILES",
    "BrowserProfile",
    "get_profile",
    "random_profile",
    "rotating_profiles",
    "__version__",
]

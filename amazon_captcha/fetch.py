"""HTTP fetching with retry, backoff, and header rotation.

A small, dependency-light fetcher built on top of ``requests``. It pairs the
CAPTCHA detection logic in :mod:`amazon_captcha.detect` with exponential
backoff and per-attempt header rotation, so the example demonstrates *why* naive
scraping hits CAPTCHA and what a minimal resilience layer looks like.

This is intentionally not a production scraping engine — it exists to make the
tutorial's claims concrete and runnable.
"""

from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass

import requests

from .detect import DetectionResult, detect
from .headers import BROWSER_PROFILES, BrowserProfile, rotating_profiles


class FetchError(Exception):
    """Raised when a fetch ultimately fails after all retries."""


@dataclass
class FetchOutcome:
    """Result of a single (possibly retried) fetch attempt."""

    response: requests.Response
    detection: DetectionResult
    attempts: int

    @property
    def is_captcha(self) -> bool:
        return self.detection.is_captcha


def _backoff(attempt: int, base: float, cap: float) -> float:
    """Exponential backoff with a cap, plus a touch of jitter-free determinism."""
    return min(cap, base * (2 ** (attempt - 1)))


def fetch_with_retry(
    url: str,
    *,
    max_attempts: int = 3,
    backoff_base: float = 1.0,
    backoff_cap: float = 30.0,
    timeout: float = 30.0,
    profiles: Iterator[BrowserProfile] | None = None,
    session: requests.Session | None = None,
    detect_captcha: bool = True,
    sleep: callable = time.sleep,
) -> FetchOutcome:
    """Fetch *url* with retry, backoff, and per-attempt header rotation.

    Retries trigger on connection errors, on challenge status codes (403/429/
    503), and — when *detect_captcha* is True — on responses that look like a
    CAPTCHA page. Each retry sleeps with exponential backoff.

    Args:
        url: Absolute URL to fetch.
        max_attempts: Maximum number of HTTP attempts (including the first).
        backoff_base: Base seconds for exponential backoff.
        backoff_cap: Upper bound on a single backoff sleep.
        timeout: Per-request timeout in seconds.
        profiles: Iterator yielding a :class:`BrowserProfile` per attempt.
            Defaults to a round-robin over :data:`BROWSER_PROFILES`.
        session: Optional :class:`requests.Session` for connection reuse.
        detect_captcha: When True, a CAPTCHA-looking body triggers a retry.
        sleep: Injectible sleep (used by tests to avoid real waiting).
    """
    if profiles is None:
        profiles = rotating_profiles()
    sess = session or requests.Session()

    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        profile = next(profiles)
        headers = profile.as_headers()
        try:
            resp = sess.get(url, headers=headers, timeout=timeout)
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < max_attempts:
                sleep(_backoff(attempt, backoff_base, backoff_cap))
                continue
            raise FetchError(
                f"Request failed after {max_attempts} attempts: {exc}"
            ) from exc

        result = detect(
            resp.text,
            status=resp.status_code,
            url=str(resp.url),
        )
        should_retry = (
            resp.status_code in (403, 429, 503)
            or (detect_captcha and result.is_captcha)
        )
        if not should_retry or attempt == max_attempts:
            return FetchOutcome(response=resp, detection=result, attempts=attempt)

        sleep(_backoff(attempt, backoff_base, backoff_cap))

    # Unreachable: the loop either returns or raises. Kept for type safety.
    raise FetchError(
        f"Exhausted {max_attempts} attempts"
        + (f"; last error: {last_exc}" if last_exc else "")
    )


def fetch_once(url: str, *, profile: BrowserProfile | None = None, timeout: float = 30.0) -> FetchOutcome:
    """Single, non-retrying fetch with optional explicit profile selection."""
    profile = profile or BROWSER_PROFILES[0]
    sess = requests.Session()
    resp = sess.get(url, headers=profile.as_headers(), timeout=timeout)
    result = detect(resp.text, status=resp.status_code, url=str(resp.url))
    return FetchOutcome(response=resp, detection=result, attempts=1)

"""Browser-like header pools for naive scraping experiments.

This module ships a small, curated pool of realistic browser headers (User-Agent
plus the companion Accept / Accept-Language / Sec-CH-UA headers that modern
browsers send). The intent is *educational*: it shows why header spoofing alone
is not a durable CAPTCHA bypass (see the README's "Part 1" discussion).

These pools are intentionally tiny and hand-maintained so the example output
stays readable. Do not rely on them for production scraping.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserProfile:
    """A self-consistent browser header profile."""

    label: str
    user_agent: str
    accept: str
    accept_language: str
    sec_ch_ua: str
    sec_ch_ua_mobile: str
    sec_ch_ua_platform: str
    upgrade_insecure_requests: str = "1"
    referer: str = "https://www.google.com/"

    def as_headers(self) -> dict[str, str]:
        """Return a flat dict ready for ``requests.get(headers=...)``."""
        return {
            "User-Agent": self.user_agent,
            "Accept": self.accept,
            "Accept-Language": self.accept_language,
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-CH-UA": self.sec_ch_ua,
            "Sec-CH-UA-Mobile": self.sec_ch_ua_mobile,
            "Sec-CH-UA-Platform": self.sec_ch_ua_platform,
            "Upgrade-Insecure-Requests": self.upgrade_insecure_requests,
            "Referer": self.referer,
        }


# ---------------------------------------------------------------------------
# Curated browser profiles (Chrome on Windows / macOS / Linux, plus Firefox).
# Keep these reasonably current but don't obsess — the point is realism, not
# evading a fingerprinting vendor.
# ---------------------------------------------------------------------------
BROWSER_PROFILES: tuple[BrowserProfile, ...] = (
    BrowserProfile(
        label="chrome-windows",
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        accept=(
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        accept_language="en-US,en;q=0.9",
        sec_ch_ua='"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform='"Windows"',
    ),
    BrowserProfile(
        label="chrome-macos",
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
        accept=(
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        accept_language="en-US,en;q=0.9",
        sec_ch_ua='"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform='"macOS"',
    ),
    BrowserProfile(
        label="firefox-linux",
        user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) "
            "Gecko/20100101 Firefox/122.0"
        ),
        accept=(
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        accept_language="en-US,en;q=0.9",
        sec_ch_ua="",  # Firefox does not send Sec-CH-UA
        sec_ch_ua_mobile="",
        sec_ch_ua_platform="",
    ),
    BrowserProfile(
        label="edge-windows",
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
        ),
        accept=(
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        accept_language="en-US,en;q=0.9",
        sec_ch_ua='"Not A(Brand";v="99", "Chromium";v="121", "Microsoft Edge";v="121"',
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform='"Windows"',
    ),
)


def get_profile(label: str) -> BrowserProfile:
    """Return the profile whose label matches *label*, or the first profile."""
    for profile in BROWSER_PROFILES:
        if profile.label == label:
            return profile
    return BROWSER_PROFILES[0]


def random_profile() -> BrowserProfile:
    """Pick a random profile from the pool."""
    return random.choice(BROWSER_PROFILES)


def rotating_profiles() -> itertools.cycle[BrowserProfile]:
    """Return an infinite cycle over all profiles (round-robin rotation)."""
    return itertools.cycle(BROWSER_PROFILES)

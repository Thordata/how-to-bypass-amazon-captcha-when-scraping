"""Tests for the browser header pool."""

from __future__ import annotations

import itertools

from amazon_captcha.headers import (
    BROWSER_PROFILES,
    BrowserProfile,
    get_profile,
    random_profile,
    rotating_profiles,
)


def test_all_profiles_have_user_agent():
    for profile in BROWSER_PROFILES:
        assert profile.user_agent.startswith("Mozilla/"), profile.label


def test_as_headers_includes_core_keys():
    profile = BROWSER_PROFILES[0]
    headers = profile.as_headers()
    for key in ("User-Agent", "Accept", "Accept-Language", "Referer"):
        assert key in headers


def test_get_profile_known_label():
    profile = get_profile("chrome-windows")
    assert profile.label == "chrome-windows"
    assert "Windows" in profile.user_agent


def test_get_profile_unknown_label_falls_back():
    fallback = get_profile("does-not-exist")
    assert fallback.label == BROWSER_PROFILES[0].label


def test_rotating_profiles_cycles_through_all():
    cycle = rotating_profiles()
    first_round = [next(cycle) for _ in BROWSER_PROFILES]
    second_round = [next(cycle) for _ in BROWSER_PROFILES]
    assert [p.label for p in first_round] == [p.label for p in second_round]
    # All profiles are represented exactly once per round.
    assert len({p.label for p in first_round}) == len(BROWSER_PROFILES)


def test_random_profile_is_from_pool():
    for _ in range(20):
        assert random_profile() in BROWSER_PROFILES


def test_firefox_has_empty_sec_ch_ua():
    ff = get_profile("firefox-linux")
    assert ff.sec_ch_ua == ""
    headers = ff.as_headers()
    # Empty Sec-CH-UA still serializes as a key; that's acceptable for the demo.
    assert headers["Sec-CH-UA"] == ""


def test_profile_is_hashable_and_frozen():
    p = BROWSER_PROFILES[0]
    assert isinstance(p, BrowserProfile)
    # frozen dataclass is hashable.
    assert hash(p) == hash(BROWSER_PROFILES[0])
    s = {BROWSER_PROFILES[0], BROWSER_PROFILES[1], BROWSER_PROFILES[0]}
    assert len(s) == 2


def test_cycle_is_infinite():
    cycle = itertools.islice(rotating_profiles(), 100)
    assert len(list(cycle)) == 100

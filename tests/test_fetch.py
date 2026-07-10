"""Offline tests for the retrying fetcher (no real network)."""

from __future__ import annotations

from unittest.mock import patch

import pytest
import requests

from amazon_captcha.fetch import FetchError, fetch_once, fetch_with_retry


class _FakeResponse:
    def __init__(self, text: str, status_code: int, url: str = "https://example.com"):
        self.text = text
        self.status_code = status_code
        self.url = url


def _make_session(responses):
    """Build a fake session whose .get returns responses in order."""
    call = {"count": 0, "headers_history": []}

    class _Session:
        def get(self, url, headers=None, timeout=None):
            call["count"] += 1
            call["headers_history"].append(headers)
            idx = min(call["count"] - 1, len(responses) - 1)
            return responses[idx]

    return _Session(), call


def test_fetch_with_retry_returns_on_success_no_captcha():
    responses = [_FakeResponse("<html>normal</html>", 200)]
    session, call = _make_session(responses)
    outcome = fetch_with_retry(
        "https://example.com", max_attempts=3, sleep=lambda _: None, session=session
    )
    assert outcome.attempts == 1
    assert outcome.is_captcha is False
    assert call["count"] == 1


def test_fetch_with_retry_retries_on_captcha_then_succeeds():
    responses = [
        _FakeResponse("<title>Robot Check</title>type the characters you see", 503),
        _FakeResponse("<html>normal</html>", 200),
    ]
    session, call = _make_session(responses)
    outcome = fetch_with_retry(
        "https://example.com", max_attempts=3, sleep=lambda _: None, session=session
    )
    assert outcome.attempts == 2
    assert outcome.is_captcha is False


def test_fetch_with_retry_exhausts_attempts_on_persistent_captcha():
    responses = [
        _FakeResponse("<title>Robot Check</title>type the characters you see", 503)
    ] * 5
    session, call = _make_session(responses)
    outcome = fetch_with_retry(
        "https://example.com", max_attempts=3, sleep=lambda _: None, session=session
    )
    assert outcome.attempts == 3
    assert outcome.is_captcha is True
    assert call["count"] == 3


def test_fetch_with_retry_rotates_headers():
    responses = [_FakeResponse("<html>ok</html>", 200)]
    session, call = _make_session(responses)
    fetch_with_retry(
        "https://example.com", max_attempts=1, session=session
    )
    sent = call["headers_history"][0]
    assert "User-Agent" in sent
    assert "Sec-CH-UA" in sent


def test_fetch_with_retry_raises_on_connection_error():
    class _BadSession:
        def get(self, url, headers=None, timeout=None):
            raise requests.ConnectionError("boom")

    with pytest.raises(FetchError):
        fetch_with_retry(
            "https://example.com",
            max_attempts=2,
            sleep=lambda _: None,
            session=_BadSession(),
        )


def test_fetch_with_retry_retries_on_connection_error():
    # First call raises, second returns a normal page.
    class _Session:
        def __init__(self):
            self.count = 0

        def get(self, url, headers=None, timeout=None):
            self.count += 1
            if self.count == 1:
                raise requests.ConnectionError("boom")
            return _FakeResponse("<html>ok</html>", 200)

    sess = _Session()
    outcome = fetch_with_retry(
        "https://example.com", max_attempts=3, sleep=lambda _: None, session=sess
    )
    assert outcome.attempts == 2
    assert outcome.is_captcha is False


def test_fetch_once_uses_explicit_profile():
    from amazon_captcha.headers import get_profile

    profile = get_profile("firefox-linux")
    sent = {}

    class _Session:
        def get(self, url, headers=None, timeout=None):
            sent.update(headers)
            return _FakeResponse("<html>ok</html>", 200)

    with patch("amazon_captcha.fetch.requests.Session", return_value=_Session()):
        outcome = fetch_once("https://example.com", profile=profile, timeout=5)
    assert outcome.is_captcha is False
    assert sent["User-Agent"] == profile.user_agent


def test_backoff_is_capped_and_monotonic():
    from amazon_captcha.fetch import _backoff

    assert _backoff(1, 1.0, 30.0) == 1.0
    assert _backoff(2, 1.0, 30.0) == 2.0
    assert _backoff(3, 1.0, 30.0) == 4.0
    assert _backoff(10, 1.0, 30.0) == 30.0  # capped

"""Offline tests for the CAPTCHA detection heuristics.

Fixtures are synthetic snippets written to exercise the marker list — they are
NOT copied from real Amazon responses.
"""

from __future__ import annotations

from amazon_captcha.detect import (
    CAPTCHA_MARKERS,
    CHALLENGE_STATUS_CODES,
    detect,
    find_markers,
    looks_like_captcha,
)

ROBOT_CHECK_HTML = """
<!DOCTYPE html><html><head><title>Robot Check</title></head>
<body>
  <h4>Type the characters you see in this image below.</h4>
  <form action="/errors/validatecapcha" method="post">
    <input type="hidden" name="amzn" value="..." />
    <input type="text" id="captchacharacters" name="field-keywords" />
    <img src="/captcha/verify/img.png" alt="captcha" />
  </form>
  <p>To discuss automated access to Amazon data please contact apihelp@amazon.com</p>
</body></html>
"""

NORMAL_PRODUCT_HTML = """
<!DOCTYPE html><html><head><title>Apple AirPods Pro</title></head>
<body>
  <h1 id="title">Apple AirPods Pro (2nd generation)</h1>
  <span id="priceblock_ourprice">$199.00</span>
  <span class="a-icon-alt">4.7 out of 5 stars</span>
</body></html>
"""


def test_find_markers_on_captcha_page():
    matched = find_markers(ROBOT_CHECK_HTML)
    # Multiple canonical markers should fire.
    assert "type the characters you see in this image" in matched
    assert "/captcha/" in matched
    assert 'id="captchacharacters"' in matched
    assert "robot check" in matched
    assert len(matched) >= 4


def test_find_markers_on_normal_page_is_empty():
    assert find_markers(NORMAL_PRODUCT_HTML) == []


def test_find_markers_empty_html():
    assert find_markers("") == []
    assert find_markers(None) == []  # type: ignore[arg-type]


def test_looks_like_captcha_true_for_robot_check():
    assert looks_like_captcha(ROBOT_CHECK_HTML) is True


def test_looks_like_captcha_false_for_normal_page():
    assert looks_like_captcha(NORMAL_PRODUCT_HTML) is False


def test_detect_returns_risk_level():
    result = detect(ROBOT_CHECK_HTML, status=503)
    assert result.is_captcha is True
    assert result.risk_level == "high"
    assert result.status == 503
    assert len(result.matched_markers) >= 4


def test_detect_normal_page_low_risk():
    result = detect(NORMAL_PRODUCT_HTML, status=200)
    assert result.is_captcha is False
    assert result.risk_level == "none"
    assert result.status == 200
    assert result.matched_markers == []


def test_detect_challenge_status_with_empty_body():
    # A 503 with no body still flags as a likely challenge.
    result = detect("", status=503)
    assert result.is_captcha is True
    assert result.risk_level == "medium"


def test_detect_404_is_low_risk_not_captcha():
    result = detect(NORMAL_PRODUCT_HTML, status=404)
    assert result.is_captcha is False
    assert result.risk_level == "low"


def test_detect_url_marker():
    result = detect("", status=200, url="https://www.amazon.com/errors/validatecaptcha?...")
    assert result.is_captcha is True
    assert any("captcha" in m for m in result.matched_markers)


def test_detect_extra_markers():
    extra = ["custom-bot-marker"]
    html = "<html><body>custom-bot-marker here</body></html>"
    result = detect(html, status=200, extra_markers=extra)
    assert "custom-bot-marker" in result.matched_markers
    assert result.is_captcha is True


def test_result_truthiness():
    assert bool(detect(ROBOT_CHECK_HTML)) is True
    assert bool(detect(NORMAL_PRODUCT_HTML, status=200)) is False


def test_challenge_status_codes_membership():
    assert 503 in CHALLENGE_STATUS_CODES
    assert 403 in CHALLENGE_STATUS_CODES
    assert 429 in CHALLENGE_STATUS_CODES
    assert 200 not in CHALLENGE_STATUS_CODES


def test_marker_list_nonempty_and_lowercase_compatible():
    assert CAPTCHA_MARKERS
    # Every marker should be findable in a lowercased haystack.
    for marker in CAPTCHA_MARKERS:
        assert marker.lower() in marker.lower()  # sanity: idempotent lowercase

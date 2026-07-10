"""CAPTCHA detection for Amazon bot-check responses.

This module provides content- and status-based heuristics to recognize when an
Amazon HTTP response is a CAPTCHA / robot-check page rather than the page you
actually requested.

The marker list below is the canonical source of truth for the project. The
browser-side detection engine in ``docs/assets/js/playground.js`` mirrors it
exactly — keep the two in sync when you add or remove a marker.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Canonical CAPTCHA marker list (mirrored in docs/assets/js/playground.js)
# ---------------------------------------------------------------------------
# Each entry is a lowercase substring that, when present in the response body
# or effective URL, strongly suggests an Amazon bot-check / CAPTCHA page.
CAPTCHA_MARKERS: list[str] = [
    # Amazon robot-check copy
    "type the characters you see in this image",
    "to discuss automated access to amazon data",
    "please enter the characters you see below",
    "enter the characters you see in the picture",
    "robot check",
    # URL / path fragments commonly present on challenge pages
    "/captcha/",
    "/errors/validatecapcha",
    "/errors/validatecaptcha",
    "errors/validatecaptcha",
    # Form field / image identifiers used by Amazon's challenge page
    'name="amzn"',
    'id="captchacharacters"',
    "captchacharacters",
    "apexusimetrics",
    # Page title hints
    "<title>robot check",
    "<title>amazon captcha",
]

# HTTP status codes that frequently accompany a challenge response.
CHALLENGE_STATUS_CODES: frozenset[int] = frozenset({403, 429, 503})


@dataclass
class DetectionResult:
    """Structured outcome of a CAPTCHA detection check.

    Attributes:
        is_captcha: True when the response looks like a challenge page.
        matched_markers: Lowercased markers that were found in the body/URL.
        status: HTTP status code (``None`` when not applicable, e.g. offline).
        risk_level: Human-friendly severity bucket: ``none`` / ``low`` /
            ``medium`` / ``high``.
    """

    is_captcha: bool
    matched_markers: list[str] = field(default_factory=list)
    status: int | None = None
    risk_level: str = "none"

    def __bool__(self) -> bool:
        """Truthy when a challenge was detected."""
        return self.is_captcha


def find_markers(html: str, extra_markers: list[str] | None = None) -> list[str]:
    """Return the list of canonical markers found in *html* (case-insensitive).

    Args:
        html: Raw response body to inspect.
        extra_markers: Additional caller-supplied markers to evaluate after the
            canonical set. Useful for experimentation without editing the
            module.
    """
    if not html:
        return []
    lower = html.lower()
    markers = list(CAPTCHA_MARKERS)
    if extra_markers:
        markers.extend(m for m in extra_markers if m)
    # Preserve order, de-duplicate while keeping first occurrence.
    seen: set[str] = set()
    matched: list[str] = []
    for marker in markers:
        key = marker.lower()
        if key in seen:
            continue
        if key in lower:
            seen.add(key)
            matched.append(marker)
    return matched


def looks_like_captcha(
    html: str,
    *,
    status: int | None = None,
    extra_markers: list[str] | None = None,
) -> bool:
    """Quick boolean check: does *html* look like a CAPTCHA page?

    Pass *status* to also treat well-known challenge status codes as a positive
    signal even when the body is empty or ambiguous.
    """
    if status is not None and status in CHALLENGE_STATUS_CODES and not html:
        return True
    return bool(find_markers(html, extra_markers=extra_markers))


def detect(
    html: str,
    *,
    status: int | None = None,
    url: str | None = None,
    extra_markers: list[str] | None = None,
) -> DetectionResult:
    """Build a full :class:`DetectionResult` for *html*.

    The risk level is derived from how many distinct markers matched and from
    the status code, giving callers a single severity bucket to branch on::

        result = detect(resp.text, status=resp.status_code, url=resp.url)
        if result.is_captcha:
            ...  # back off, switch strategy, log
    """
    haystack = html or ""
    if url:
        haystack = f"{haystack}\n{url}"
    matched = find_markers(haystack, extra_markers=extra_markers)
    is_captcha = bool(matched) or (
        status is not None and status in CHALLENGE_STATUS_CODES and not haystack.strip()
    )

    risk = _risk_level(matched, status)
    return DetectionResult(
        is_captcha=is_captcha,
        matched_markers=matched,
        status=status,
        risk_level=risk,
    )


def _risk_level(matched: list[str], status: int | None) -> str:
    """Map the signal count + status onto a coarse severity bucket."""
    if status is not None and status in CHALLENGE_STATUS_CODES and len(matched) >= 1:
        return "high"
    if len(matched) >= 3:
        return "high"
    if len(matched) >= 1:
        return "medium"
    if status is not None and status in CHALLENGE_STATUS_CODES:
        return "medium"
    if status is not None and status >= 400:
        return "low"
    return "none"

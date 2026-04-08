"""Normalize vacancy URLs for stable deduplication."""

from __future__ import annotations

from urllib.parse import urlparse, urlunparse


def normalize_vacancy_url(url: str) -> str:
    """Return scheme + host + path without query or fragment.

    ``http``/``https`` are normalized to ``https``. Netloc is lowercased; path has no trailing
    slash except the root ``/``.

    Args:
        url: Raw vacancy URL from the provider (may include tracking query params).

    Returns:
        Normalized URL string, or empty if ``url`` is blank/invalid.
    """

    raw = (url or "").strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    scheme = (parsed.scheme or "https").lower()
    if scheme in {"http", "https"}:
        scheme = "https"
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
    return urlunparse((scheme, netloc, path, "", "", ""))


def vacancy_url_canonical(source: str, external_id: str, url: str) -> str:
    """Build a stable dedupe key for a vacancy within one ``source``.

    Args:
        source: Provider id (e.g. ``hh``).
        external_id: Provider's numeric/string id when the URL is missing.
        url: Public vacancy URL.

    Returns:
        Normalized URL, or ``id:{external_id}`` when the URL is empty.
    """

    n = normalize_vacancy_url(url)
    if n:
        return n
    return f"id:{external_id}"

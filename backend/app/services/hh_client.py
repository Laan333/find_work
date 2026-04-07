"""HTTP client for hh.ru public API (pattern from root `main.py`)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


def _hh_api_token(value: str | None) -> str | None:
    """Pass only ASCII tokens (hh enum ids); skip Russian labels from UI."""

    if not value:
        return None
    if any(ord(c) > 127 for c in value):
        return None
    return value


def fetch_vacancies_page(
    *,
    text: str,
    area: int | None,
    schedule: str | None,
    employment: str | None,
    experience: str | None,
    salary_from: int | None,
    salary_to: int | None,  # reserved; hh list API uses a single salary floor in MVP
    page: int,
    per_page: int,
) -> dict[str, Any]:
    """Call `GET /vacancies` with the same parameter style as `main.py`."""

    s = get_settings()
    params: dict[str, Any] = {
        "text": text,
        "per_page": per_page,
        "page": page,
        "order_by": "publication_time",
    }
    if area is not None:
        params["area"] = area
    if schedule:
        params["schedule"] = schedule
    emp = _hh_api_token(employment)
    if emp:
        params["employment"] = emp
    exp = _hh_api_token(experience)
    if exp:
        params["experience"] = exp
    if salary_from is not None:
        params["salary"] = salary_from
        params["only_with_salary"] = True
    _ = salary_to

    headers = {"User-Agent": s.hh_user_agent}
    url = f"{s.hh_base_url.rstrip('/')}/vacancies"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()


def fetch_vacancy_detail(external_id: str) -> dict[str, Any]:
    """Call `GET /vacancies/{id}` for full card."""

    s = get_settings()
    headers = {"User-Agent": s.hh_user_agent}
    url = f"{s.hh_base_url.rstrip('/')}/vacancies/{external_id}"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

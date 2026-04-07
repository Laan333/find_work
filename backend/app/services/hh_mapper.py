"""Map hh.ru JSON payloads into `Vacancy` row dicts."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


def _strip_highlight(html: str | None) -> str:
    if not html:
        return ""
    text = re.sub(r"</?highlighttext>", "", html, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def _parse_published_at(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def map_list_item_to_row(
    item: dict[str, Any],
    *,
    raw_payload: dict[str, Any],
    vacancy_source: str = "hh",
) -> dict[str, Any]:
    """Build ORM kwargs from a short vacancy object (search results)."""

    employer = item.get("employer") or {}
    area = item.get("area") or {}
    salary = item.get("salary") or None
    snippet = item.get("snippet") or {}
    skills_raw = item.get("key_skills") or []
    skills = [s.get("name", "") for s in skills_raw if isinstance(s, dict) and s.get("name")]

    req = _strip_highlight(snippet.get("requirement"))
    resp_text = _strip_highlight(snippet.get("responsibility"))
    desc_parts = [p for p in (req, resp_text) if p]
    description_md = "\n\n".join(desc_parts) if desc_parts else None

    now = datetime.now(timezone.utc)
    published_at = _parse_published_at(item.get("published_at"))

    sal_from = salary.get("from") if salary else None
    sal_to = salary.get("to") if salary else None
    sal_cur = (salary.get("currency") if salary else None) or "RUR"
    sal_gross = salary.get("gross") if salary else None

    return {
        "source": vacancy_source,
        "external_id": str(item["id"]),
        "raw_payload": raw_payload,
        "title": item.get("name") or "",
        "company": employer.get("name") or "",
        "company_logo": (employer.get("logo_urls") or {}).get("90") if employer else None,
        "salary_from": sal_from,
        "salary_to": sal_to,
        "salary_currency": sal_cur,
        "salary_gross": sal_gross,
        "experience": (item.get("experience") or {}).get("name"),
        "employment": (item.get("employment") or {}).get("name"),
        "schedule": (item.get("schedule") or {}).get("name"),
        "location": area.get("name") or "",
        "description_md": description_md,
        "requirements_md": req or None,
        "responsibilities_md": resp_text or None,
        "skills": skills,
        "url": item.get("alternate_url") or "",
        "published_at": published_at,
        "fetched_at": now,
        "responses": None,
        "views": None,
    }


def enrich_from_detail(base: dict[str, Any], detail: dict[str, Any]) -> dict[str, Any]:
    """Overlay full description and skills from vacancy card."""

    branded = detail.get("branded_description")
    desc_html = detail.get("description") or branded or ""
    description_md = _strip_highlight(desc_html) or base.get("description_md")

    skills_raw = detail.get("key_skills") or []
    skills = [s.get("name", "") for s in skills_raw if isinstance(s, dict) and s.get("name")]
    if not skills:
        skills = base.get("skills") or []

    exp = (detail.get("experience") or {}).get("name") or base.get("experience")
    emp = (detail.get("employment") or {}).get("name") or base.get("employment")
    sch = (detail.get("schedule") or {}).get("name") or base.get("schedule")

    out = {**base}
    out.update(
        {
            "raw_payload": detail,
            "description_md": description_md,
            "skills": skills,
            "experience": exp,
            "employment": emp,
            "schedule": sch,
        }
    )
    return out

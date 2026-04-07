"""ORM → JSON dicts (camelCase) for the Next.js contract."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.models import (
    Notification,
    Resume,
    SavedSearch,
    SyncRun,
    SyncRunItem,
    Vacancy,
    VacancyAnalysis,
    VacancyStatus,
)


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.isoformat().replace("+00:00", "Z")


def vacancy_to_dict(v: Vacancy) -> dict[str, Any]:
    """Map `Vacancy` to `front/lib/types.ts` `Vacancy`."""

    salary = None
    if v.salary_from is not None or v.salary_to is not None:
        salary = {
            "from": v.salary_from,
            "to": v.salary_to,
            "currency": v.salary_currency or "RUR",
            "gross": v.salary_gross,
        }
    return {
        "id": str(v.id),
        "externalId": v.external_id,
        "source": v.source,
        "title": v.title,
        "company": v.company,
        "companyLogo": v.company_logo,
        "salary": salary,
        "experience": v.experience,
        "employment": v.employment,
        "schedule": v.schedule,
        "location": v.location,
        "description": v.description_md or "",
        "requirements": v.requirements_md,
        "responsibilities": v.responsibilities_md,
        "skills": list(v.skills or []),
        "url": v.url,
        "publishedAt": _iso(v.published_at) or "",
        "createdAt": _iso(v.fetched_at) or "",
        "responses": v.responses,
        "views": v.views,
        "isAnalyzed": v.is_analyzed,
        "matchScore": v.match_score,
        "aiAnalysis": v.ai_analysis,
        "coverLetter": v.cover_letter_text,
        "isFavorite": v.is_favorite,
        "status": v.status.value if isinstance(v.status, VacancyStatus) else str(v.status),
    }


def search_to_dict(s: SavedSearch) -> dict[str, Any]:
    """Map saved search to `SearchQuery`."""

    return {
        "id": str(s.id),
        "keyword": s.keyword,
        "location": s.location_label,
        "experience": s.experience,
        "employment": s.employment,
        "salary": (
            {"from": s.salary_from, "to": s.salary_to}
            if s.salary_from is not None or s.salary_to is not None
            else None
        ),
        "schedule": s.schedule,
        "isActive": s.is_active,
        "interval": s.interval_minutes,
        "lastRun": _iso(s.last_run_at),
        "nextRun": None,
        "createdAt": _iso(s.created_at) or "",
        "vacanciesFound": s.vacancies_found,
        "areaId": s.area_id,
        "vacancySource": s.vacancy_source,
    }


def resume_to_dict(r: Resume) -> dict[str, Any]:
    return {
        "id": str(r.id),
        "title": r.title,
        "fullName": r.full_name,
        "position": r.position,
        "experience": r.experience,
        "skills": list(r.skills or []),
        "education": r.education,
        "about": r.about,
        "contacts": dict(r.contacts or {}),
        "rawText": r.raw_text,
        "createdAt": _iso(r.created_at) or "",
        "updatedAt": _iso(r.updated_at) or "",
        "isActive": r.is_active,
    }


def notification_to_dict(n: Notification) -> dict[str, Any]:
    return {
        "id": str(n.id),
        "vacancyId": str(n.vacancy_id),
        "analysisId": str(n.analysis_id) if n.analysis_id else None,
        "summary": n.summary,
        "score": n.score,
        "categories": list(n.categories or []),
        "readAt": _iso(n.read_at),
        "createdAt": _iso(n.created_at) or "",
    }


def sync_run_to_dict(r: SyncRun, items: list[SyncRunItem]) -> dict[str, Any]:
    return {
        "id": str(r.id),
        "startedAt": _iso(r.started_at) or "",
        "finishedAt": _iso(r.finished_at),
        "trigger": r.trigger.value,
        "error": r.error,
        "items": [
            {
                "searchId": str(i.search_id) if i.search_id else None,
                "inserted": i.inserted,
                "skippedDuplicates": i.skipped_duplicates,
                "durationMs": i.duration_ms,
                "error": i.error,
            }
            for i in items
        ],
    }


def analysis_to_dict(a: VacancyAnalysis) -> dict[str, Any]:
    return {
        "id": str(a.id),
        "vacancyId": str(a.vacancy_id),
        "resumeId": str(a.resume_id),
        "score": a.score,
        "categories": list(a.categories or []),
        "strengthsMd": a.strengths_md,
        "gapsMd": a.gaps_md,
        "hrAdviceMd": a.hr_advice_md,
        "summaryNotification": a.summary_notification,
        "model": a.model,
        "promptVersion": a.prompt_version,
        "source": a.source.value,
        "createdAt": _iso(a.created_at) or "",
    }

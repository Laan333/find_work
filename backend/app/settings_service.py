"""Read/write `app_setting` rows as JSON-encoded values."""

from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AppSetting

logger = logging.getLogger(__name__)


def _dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def _load(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in app_setting, returning raw string")
        return raw


def get_value(db: Session, key: str, default: Any = None) -> Any:
    """Return deserialized setting or default."""

    row = db.get(AppSetting, key)
    if row is None:
        return default
    return _load(row.value)


def set_value(db: Session, key: str, value: Any) -> None:
    """Upsert a JSON-encoded setting."""

    raw = _dump(value)
    row = db.get(AppSetting, key)
    if row is None:
        db.add(AppSetting(key=key, value=raw))
    else:
        row.value = raw
    db.commit()


def get_str(db: Session, key: str, default: str) -> str:
    """Return a string setting."""

    v = get_value(db, key, default)
    return str(v) if v is not None else default


def get_int(db: Session, key: str, default: int) -> int:
    """Return an integer setting."""

    v = get_value(db, key, default)
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def get_bool(db: Session, key: str, default: bool) -> bool:
    """Return a boolean setting."""

    v = get_value(db, key, default)
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.lower() in ("1", "true", "yes", "on")
    return bool(v)


def ensure_defaults(db: Session) -> None:
    """Seed defaults once if keys are missing."""

    s = get_settings()
    defaults: dict[str, Any] = {
        "hh_daily_sync_time": s.default_hh_sync_time,
        "hh_daily_sync_timezone": s.default_hh_sync_timezone,
        "vacancy_max_age_days": s.default_vacancy_max_age_days,
        "match_analysis_interval_minutes": s.default_match_interval_minutes,
        "llm_min_interval_seconds": s.default_llm_min_interval_seconds,
        "high_match_threshold": s.default_high_match_threshold,
        "max_vacancies_per_search": 200,
        "telegram_enabled": False,
        "notify_on_high_match": True,
        "refresh_interval": 60,
        "auto_analyze": False,
        "analyze_delay_minutes": 3,
        "browser_notifications": False,
        "notify_on_new_vacancies": False,
        "llm_provider": s.llm_provider,
    }
    for key, val in defaults.items():
        if db.get(AppSetting, key) is None:
            db.add(AppSetting(key=key, value=_dump(val)))
    db.commit()

"""APScheduler: minute tick for daily hh sync window and match interval."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from zoneinfo import ZoneInfo

from app.config import get_settings
from app.database import SessionLocal
from app.models import SyncTrigger
from app.services.matching_job import run_scheduled_matching
from app.services.sync_service import run_full_sync
from app.settings_service import ensure_defaults, get_bool, get_int, get_str, get_value, set_value

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _tick() -> None:
    with SessionLocal() as db:
        try:
            ensure_defaults(db)
            s = get_settings()
            tz_name = get_str(db, "hh_daily_sync_timezone", s.default_hh_sync_timezone)
            tz = ZoneInfo(tz_name)
            now_local = datetime.now(tz)
            hh_time = get_str(db, "hh_daily_sync_time", s.default_hh_sync_time)
            parts = hh_time.split(":")
            th = int(parts[0])
            tm = int(parts[1]) if len(parts) > 1 else 0
            if now_local.hour == th and now_local.minute == tm:
                today = now_local.date().isoformat()
                if get_value(db, "last_scheduled_sync_date", None) != today:
                    set_value(db, "last_scheduled_sync_date", today)
                    run_full_sync(db, trigger=SyncTrigger.scheduled)

            if get_bool(db, "auto_analyze", False):
                interval_min = get_int(db, "match_analysis_interval_minutes", s.default_match_interval_minutes)
                last_raw = get_value(db, "last_match_job_at", None)
                now_utc = datetime.now(timezone.utc)
                if last_raw is None:
                    run_scheduled_matching(db)
                else:
                    try:
                        lm = datetime.fromisoformat(str(last_raw).replace("Z", "+00:00"))
                        if lm.tzinfo is None:
                            lm = lm.replace(tzinfo=timezone.utc)
                        delta_min = (now_utc - lm).total_seconds() / 60.0
                        if delta_min >= interval_min:
                            run_scheduled_matching(db)
                    except ValueError:
                        run_scheduled_matching(db)
        except Exception:
            logger.exception("Scheduler tick failed")


def start_scheduler() -> None:
    """Start background scheduler (idempotent)."""

    if scheduler.running:
        return
    scheduler.add_job(_tick, "cron", minute="*", id="find_work_minute_tick", replace_existing=True)
    scheduler.start()
    logger.info("APScheduler started")


def shutdown_scheduler() -> None:
    """Stop scheduler on app shutdown."""

    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")

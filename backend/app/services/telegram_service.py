"""Telegram Bot API notifications."""

from __future__ import annotations

import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


def send_message(text: str) -> str | None:
    """Send plain text; return message_id string or None if skipped/failed."""

    s = get_settings()
    token = (s.telegram_bot_token or "").strip()
    chat_id = (s.telegram_chat_id or "").strip()
    if not token or not chat_id:
        logger.info("Telegram skipped: token or chat_id not configured")
        return None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text[:4000]}
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            body = r.json()
        mid = body.get("result", {}).get("message_id")
        return str(mid) if mid is not None else None
    except Exception:
        logger.exception("Telegram send failed")
        return None

"""Extract plain text from resume uploads (.txt, .pdf, .docx)."""

from __future__ import annotations

import logging
import zipfile
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_RESUME_UPLOAD_BYTES = 10 * 1024 * 1024

_ALLOWED_SUFFIXES = frozenset({".txt", ".pdf", ".docx"})


def extract_resume_text(filename: str, data: bytes) -> tuple[str, list[str]]:
    """Parse upload bytes into plain text.

    Args:
        filename: Original file name (used for extension).
        data: Raw file bytes.

    Returns:
        Tuple of (extracted text, non-fatal warnings for the UI).

    Raises:
        ValueError: ``unsupported_format`` or ``parse_failed`` with optional context.
    """
    if len(data) > MAX_RESUME_UPLOAD_BYTES:
        raise ValueError("file_too_large")

    suffix = Path(filename or "").suffix.lower()
    if suffix not in _ALLOWED_SUFFIXES:
        raise ValueError("unsupported_format")

    warnings: list[str] = []

    if suffix == ".txt":
        text = _decode_plain_text(data)
        return text, warnings

    if suffix == ".pdf":
        text, w = _text_from_pdf(data)
        warnings.extend(w)
        return text, warnings

    if suffix == ".docx":
        text, w = _text_from_docx(data)
        warnings.extend(w)
        return text, warnings

    raise ValueError("unsupported_format")


def _decode_plain_text(data: bytes) -> str:
    """Decode .txt as UTF-8 (with BOM strip) or fall back with replacement."""

    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data.decode("utf-16", errors="replace").strip()
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    return data.decode("utf-8", errors="replace").strip()


def _text_from_pdf(data: bytes) -> tuple[str, list[str]]:
    """Extract text from PDF using pypdf."""

    warnings: list[str] = []
    try:
        from pypdf import PdfReader
    except ImportError as e:
        logger.exception("pypdf missing")
        raise ValueError("parse_failed") from e

    try:
        reader = PdfReader(BytesIO(data))
        parts: list[str] = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                parts.append(t)
        text = "\n\n".join(parts).strip()
    except Exception:
        logger.exception("PDF parse error")
        raise ValueError("parse_failed") from None

    if not text:
        warnings.append("В PDF не найден текст (возможно, только изображения).")
    return text, warnings


def _text_from_docx(data: bytes) -> tuple[str, list[str]]:
    """Extract paragraph text from a .docx (Office Open XML)."""

    warnings: list[str] = []
    if not zipfile.is_zipfile(BytesIO(data)):
        raise ValueError("parse_failed")

    try:
        from docx import Document
    except ImportError as e:
        logger.exception("python-docx missing")
        raise ValueError("parse_failed") from e

    try:
        doc = Document(BytesIO(data))
        parts = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        text = "\n\n".join(parts).strip()
    except Exception:
        logger.exception("DOCX parse error")
        raise ValueError("parse_failed") from None

    if not text:
        warnings.append("В DOCX не найден текст в абзацах.")
    return text, warnings

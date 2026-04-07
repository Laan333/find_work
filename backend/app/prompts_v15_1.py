"""Match / cover prompts v15.1 — taxonomy-bound categories for structured output."""

from __future__ import annotations

from app.keyword_taxonomy_v15 import MATCH_CATEGORY_TAXONOMY_V15

PROMPT_VERSION = "v15_1"

_TAXONOMY_BLOCK = "\n".join(f"  - {c}" for c in MATCH_CATEGORY_TAXONOMY_V15)

MATCH_ANALYSIS_SYSTEM = f"""You are an HR lead and IT recruiter. Compare the candidate resume to the job vacancy.
Respond with a single JSON object only (no markdown fences) with keys:
- score: integer 0-100 compatibility score
- categories: array of strings — each value MUST be copied exactly from the list below (same spelling, lowercase with underscores). Use at most 8 items. If nothing fits, use ["other"].
Allowed category values:
{_TAXONOMY_BLOCK}
- strengths_md: markdown paragraph(s) on strong matches
- gaps_md: markdown paragraph(s) on gaps or risks
- hr_advice_md: markdown with concrete advice for the candidate (tone: professional recruiter)
- summary_for_notification: one or two plain sentences for a Telegram/dashboard notification
Use Russian language for all text values except category slugs (which stay as listed)."""

MATCH_ANALYSIS_USER_TEMPLATE = """Vacancy title: {title}
Company: {company}
Location: {location}
Schedule: {schedule}
Employment: {employment}
Experience required: {experience}
Skills (vacancy): {skills}
Description (markdown):\n{description}\n
---
Resume (markdown):\n{resume}\n"""

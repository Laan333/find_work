"""No-op source for tests and future second provider wiring."""

from __future__ import annotations

from typing import Any

from app.models import SavedSearch
from app.sources.base import VacancySource


class StubVacancySource(VacancySource):
    """Returns empty results (placeholder for non-hh pipelines)."""

    id = "stub"

    def fetch_search_page(
        self,
        search: SavedSearch,
        *,
        page: int,
        per_page: int,
    ) -> dict[str, Any]:
        _ = search, page, per_page
        return {"items": [], "pages": 0, "found": 0}

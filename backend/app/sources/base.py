"""Abstract vacancy source contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.models import SavedSearch


class VacancySource(ABC):
    """Fetches vacancy listings for a saved search (one API page)."""

    id: str

    @abstractmethod
    def fetch_search_page(
        self,
        search: SavedSearch,
        *,
        page: int,
        per_page: int,
    ) -> dict[str, Any]:
        """Return payload shaped like hh `GET /vacancies`: `items`, `pages`, `found`."""

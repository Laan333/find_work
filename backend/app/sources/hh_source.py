"""HeadHunter public API as `VacancySource`."""

from __future__ import annotations

from typing import Any

from app.models import SavedSearch
from app.services import hh_client
from app.sources.base import VacancySource


class HHVacancySource(VacancySource):
    """hh.ru Open API."""

    id = "hh"

    def fetch_search_page(
        self,
        search: SavedSearch,
        *,
        page: int,
        per_page: int,
    ) -> dict[str, Any]:
        return hh_client.fetch_vacancies_page(
            text=search.keyword,
            area=search.area_id,
            schedule=search.schedule,
            employment=search.employment,
            experience=search.experience,
            salary_from=search.salary_from,
            salary_to=search.salary_to,
            page=page,
            per_page=per_page,
        )

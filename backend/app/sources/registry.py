"""Resolve `VacancySource` by string id."""

from __future__ import annotations

from app.sources.base import VacancySource
from app.sources.hh_source import HHVacancySource
from app.sources.stub_source import StubVacancySource

_SOURCES: dict[str, VacancySource] = {
    HHVacancySource.id: HHVacancySource(),
    StubVacancySource.id: StubVacancySource(),
}


class VacancySourceRegistry:
    """Register and lookup sources."""

    @staticmethod
    def get(source_id: str) -> VacancySource:
        key = (source_id or "hh").lower().strip()
        if key not in _SOURCES:
            raise ValueError(f"Unknown vacancy source: {source_id}")
        return _SOURCES[key]

    @staticmethod
    def ids() -> list[str]:
        return list(_SOURCES.keys())


def get_vacancy_source(source_id: str) -> VacancySource:
    """Return a source instance."""

    return VacancySourceRegistry.get(source_id)

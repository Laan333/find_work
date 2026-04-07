"""Pluggable vacancy sources (hh.ru, stubs, future providers)."""

from app.sources.hh_source import HHVacancySource
from app.sources.registry import VacancySourceRegistry, get_vacancy_source
from app.sources.stub_source import StubVacancySource

__all__ = [
    "HHVacancySource",
    "StubVacancySource",
    "VacancySourceRegistry",
    "get_vacancy_source",
]

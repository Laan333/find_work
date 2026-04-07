"""SQLAlchemy ORM models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VacancyStatus(str, enum.Enum):
    """User workflow status for a vacancy."""

    new = "new"
    viewed = "viewed"
    applied = "applied"
    rejected = "rejected"
    interview = "interview"


class AnalysisSource(str, enum.Enum):
    """How the vacancy analysis was produced."""

    manual = "manual"
    scheduled = "scheduled"


class SyncTrigger(str, enum.Enum):
    """What initiated a sync run."""

    manual = "manual"
    scheduled = "scheduled"


class Vacancy(Base):
    """Vacancy stored from external sources (e.g. hh.ru)."""

    __tablename__ = "vacancy"
    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_vacancy_source_external"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="hh")
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    title: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    company: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    company_logo: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    salary_gross: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    experience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    schedule: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location: Mapped[str] = mapped_column(String(512), nullable=False, default="")

    description_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    requirements_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)

    url: Mapped[str] = mapped_column(String(2048), nullable=False, default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    responses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_analyzed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    match_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_letter_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[VacancyStatus] = mapped_column(
        Enum(VacancyStatus, name="vacancy_status"),
        nullable=False,
        default=VacancyStatus.new,
    )

    cover_letters: Mapped[list["CoverLetter"]] = relationship(back_populates="vacancy", cascade="all, delete-orphan")
    analyses: Mapped[list["VacancyAnalysis"]] = relationship(
        back_populates="vacancy",
        cascade="all, delete-orphan",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="vacancy",
        cascade="all, delete-orphan",
    )


class SavedSearch(Base):
    """Saved hh.ru search participating in the daily sync queue."""

    __tablename__ = "saved_search"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keyword: Mapped[str] = mapped_column(String(512), nullable=False)
    area_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    schedule: Mapped[str | None] = mapped_column(String(64), nullable=True)
    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)

    vacancy_source: Mapped[str] = mapped_column(String(32), nullable=False, default="hh")

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    max_vacancies: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    vacancies_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Resume(Base):
    """User resume (single active supported by API convention)."""

    __tablename__ = "resume"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    position: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    experience: Mapped[str] = mapped_column(Text, nullable=False, default="")
    skills: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    education: Mapped[str] = mapped_column(Text, nullable=False, default="")
    about: Mapped[str] = mapped_column(Text, nullable=False, default="")
    contacts: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CoverLetter(Base):
    """Generated cover letter for a vacancy."""

    __tablename__ = "cover_letter"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vacancy.id", ondelete="CASCADE"),
        nullable=False,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume.id", ondelete="CASCADE"),
        nullable=False,
    )
    body_md: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    vacancy: Mapped["Vacancy"] = relationship(back_populates="cover_letters")


class VacancyAnalysis(Base):
    """Structured LLM analysis for resume vs vacancy."""

    __tablename__ = "vacancy_analysis"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vacancy.id", ondelete="CASCADE"),
        nullable=False,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume.id", ondelete="CASCADE"),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    categories: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    strengths_md: Mapped[str] = mapped_column(Text, nullable=False, default="")
    gaps_md: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hr_advice_md: Mapped[str] = mapped_column(Text, nullable=False, default="")
    summary_notification: Mapped[str] = mapped_column(Text, nullable=False, default="")
    raw_ai_response: Mapped[str] = mapped_column(Text, nullable=False, default="")
    model: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    prompt_version: Mapped[str] = mapped_column(String(64), nullable=False, default="v1")
    source: Mapped[AnalysisSource] = mapped_column(
        Enum(AnalysisSource, name="analysis_source"),
        nullable=False,
        default=AnalysisSource.manual,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    vacancy: Mapped["Vacancy"] = relationship(back_populates="analyses")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="analysis")


class Notification(Base):
    """High-match or other alerts for the dashboard and Telegram."""

    __tablename__ = "notification"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vacancy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vacancy.id", ondelete="CASCADE"),
        nullable=False,
    )
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vacancy_analysis.id", ondelete="SET NULL"),
        nullable=True,
    )
    resume_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resume.id", ondelete="SET NULL"),
        nullable=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    categories: Mapped[list[Any] | None] = mapped_column(JSONB, nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    telegram_message_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    telegram_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    vacancy: Mapped["Vacancy"] = relationship(back_populates="notifications")
    analysis: Mapped["VacancyAnalysis | None"] = relationship(back_populates="notifications")


class SyncRun(Base):
    """One hh sync execution."""

    __tablename__ = "sync_run"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trigger: Mapped[SyncTrigger] = mapped_column(
        Enum(SyncTrigger, name="sync_trigger"),
        nullable=False,
        default=SyncTrigger.manual,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list["SyncRunItem"]] = relationship(
        back_populates="sync_run",
        cascade="all, delete-orphan",
    )


class SyncRunItem(Base):
    """Per saved search stats inside a sync run."""

    __tablename__ = "sync_run_item"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sync_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sync_run.id", ondelete="CASCADE"),
        nullable=False,
    )
    search_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("saved_search.id", ondelete="SET NULL"),
        nullable=True,
    )
    inserted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_duplicates: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    sync_run: Mapped["SyncRun"] = relationship(back_populates="items")


class AppSetting(Base):
    """Key-value application settings (JSON string values)."""

    __tablename__ = "app_setting"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

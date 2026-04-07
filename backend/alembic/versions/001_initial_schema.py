"""Initial schema: vacancy, searches, resume, LLM artifacts, sync logs, settings.

Revision ID: 001_initial
Revises:
Create Date: 2026-04-07

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    vacancy_status = postgresql.ENUM(
        "new",
        "viewed",
        "applied",
        "rejected",
        "interview",
        name="vacancy_status",
        create_type=True,
    )
    vacancy_status.create(op.get_bind(), checkfirst=True)

    analysis_source = postgresql.ENUM("manual", "scheduled", name="analysis_source", create_type=True)
    analysis_source.create(op.get_bind(), checkfirst=True)

    sync_trigger = postgresql.ENUM("manual", "scheduled", name="sync_trigger", create_type=True)
    sync_trigger.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "saved_search",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("keyword", sa.String(length=512), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=True),
        sa.Column("location_label", sa.String(length=255), nullable=True),
        sa.Column("experience", sa.String(length=255), nullable=True),
        sa.Column("employment", sa.String(length=255), nullable=True),
        sa.Column("schedule", sa.String(length=64), nullable=True),
        sa.Column("salary_from", sa.Integer(), nullable=True),
        sa.Column("salary_to", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("interval_minutes", sa.Integer(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("vacancies_found", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "vacancy",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("company", sa.String(length=512), nullable=False),
        sa.Column("company_logo", sa.String(length=1024), nullable=True),
        sa.Column("salary_from", sa.Integer(), nullable=True),
        sa.Column("salary_to", sa.Integer(), nullable=True),
        sa.Column("salary_currency", sa.String(length=8), nullable=True),
        sa.Column("salary_gross", sa.Boolean(), nullable=True),
        sa.Column("experience", sa.String(length=255), nullable=True),
        sa.Column("employment", sa.String(length=255), nullable=True),
        sa.Column("schedule", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=512), nullable=False),
        sa.Column("description_md", sa.Text(), nullable=True),
        sa.Column("requirements_md", sa.Text(), nullable=True),
        sa.Column("responsibilities_md", sa.Text(), nullable=True),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("responses", sa.Integer(), nullable=True),
        sa.Column("views", sa.Integer(), nullable=True),
        sa.Column("is_analyzed", sa.Boolean(), nullable=False),
        sa.Column("match_score", sa.Integer(), nullable=True),
        sa.Column("ai_analysis", sa.Text(), nullable=True),
        sa.Column("cover_letter_text", sa.Text(), nullable=True),
        sa.Column("is_favorite", sa.Boolean(), nullable=False),
        sa.Column("status", vacancy_status, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source", "external_id", name="uq_vacancy_source_external"),
    )

    op.create_table(
        "resume",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("position", sa.String(length=512), nullable=False),
        sa.Column("experience", sa.Text(), nullable=False),
        sa.Column("skills", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("education", sa.Text(), nullable=False),
        sa.Column("about", sa.Text(), nullable=False),
        sa.Column("contacts", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "app_setting",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )

    op.create_table(
        "sync_run",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trigger", sync_trigger, nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "cover_letter",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("vacancy_id", sa.Uuid(), nullable=False),
        sa.Column("resume_id", sa.Uuid(), nullable=False),
        sa.Column("body_md", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["resume_id"], ["resume.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vacancy_id"], ["vacancy.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "vacancy_analysis",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("vacancy_id", sa.Uuid(), nullable=False),
        sa.Column("resume_id", sa.Uuid(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("categories", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("strengths_md", sa.Text(), nullable=False),
        sa.Column("gaps_md", sa.Text(), nullable=False),
        sa.Column("hr_advice_md", sa.Text(), nullable=False),
        sa.Column("summary_notification", sa.Text(), nullable=False),
        sa.Column("raw_ai_response", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("prompt_version", sa.String(length=64), nullable=False),
        sa.Column("source", analysis_source, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["resume_id"], ["resume.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vacancy_id"], ["vacancy.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "notification",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("vacancy_id", sa.Uuid(), nullable=False),
        sa.Column("analysis_id", sa.Uuid(), nullable=True),
        sa.Column("resume_id", sa.Uuid(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("categories", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("telegram_message_id", sa.String(length=64), nullable=True),
        sa.Column("telegram_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["vacancy_analysis.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resume_id"], ["resume.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["vacancy_id"], ["vacancy.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "sync_run_item",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sync_run_id", sa.Uuid(), nullable=False),
        sa.Column("search_id", sa.Uuid(), nullable=True),
        sa.Column("inserted", sa.Integer(), nullable=False),
        sa.Column("skipped_duplicates", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["search_id"], ["saved_search.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sync_run_id"], ["sync_run.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("sync_run_item")
    op.drop_table("notification")
    op.drop_table("vacancy_analysis")
    op.drop_table("cover_letter")
    op.drop_table("sync_run")
    op.drop_table("app_setting")
    op.drop_table("resume")
    op.drop_table("vacancy")
    op.drop_table("saved_search")

    op.execute(sa.text("DROP TYPE IF EXISTS sync_trigger"))
    op.execute(sa.text("DROP TYPE IF EXISTS analysis_source"))
    op.execute(sa.text("DROP TYPE IF EXISTS vacancy_status"))

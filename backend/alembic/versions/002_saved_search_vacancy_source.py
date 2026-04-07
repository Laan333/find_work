"""Add vacancy_source to saved_search for VacancySource routing."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "002_saved_search_vacancy_source"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "saved_search",
        sa.Column("vacancy_source", sa.String(length=32), nullable=False, server_default="hh"),
    )


def downgrade() -> None:
    op.drop_column("saved_search", "vacancy_source")

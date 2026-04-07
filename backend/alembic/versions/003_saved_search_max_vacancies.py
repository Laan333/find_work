"""Add max_vacancies to saved_search for per-query sync limits."""

from alembic import op
import sqlalchemy as sa

revision = "003_saved_search_max_vacancies"
down_revision = "002_saved_search_vacancy_source"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "saved_search",
        sa.Column("max_vacancies", sa.Integer(), nullable=False, server_default="200"),
    )
    op.alter_column("saved_search", "max_vacancies", server_default=None)


def downgrade() -> None:
    op.drop_column("saved_search", "max_vacancies")

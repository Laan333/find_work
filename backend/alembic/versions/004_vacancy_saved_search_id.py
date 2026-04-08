"""Link vacancy to saved search (sync origin keyword)."""

import sqlalchemy as sa
from alembic import op

revision = "004_vacancy_saved_search_id"
down_revision = "003_saved_search_max_vacancies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "vacancy",
        sa.Column("saved_search_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_vacancy_saved_search_id_saved_search",
        "vacancy",
        "saved_search",
        ["saved_search_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_vacancy_saved_search_id_saved_search", "vacancy", type_="foreignkey")
    op.drop_column("vacancy", "saved_search_id")

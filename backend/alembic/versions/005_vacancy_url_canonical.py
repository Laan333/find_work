"""Deduplicate vacancies by normalized URL (source + url_canonical).

Revision ID: 005_vacancy_url_canonical
Revises: 004_vacancy_saved_search_id
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Vacancy
from app.services.vacancy_url import vacancy_url_canonical

revision: str = "005_vacancy_url_canonical"
down_revision: Union[str, Sequence[str], None] = "004_vacancy_saved_search_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("vacancy", sa.Column("url_canonical", sa.String(length=2048), nullable=True))

    bind = op.get_bind()
    with Session(bind=bind) as session:
        for v in session.scalars(select(Vacancy)):
            v.url_canonical = vacancy_url_canonical(v.source, v.external_id, v.url or "")
        session.flush()

        dup_keys = session.execute(
            select(Vacancy.source, Vacancy.url_canonical, func.count().label("cnt"))
            .group_by(Vacancy.source, Vacancy.url_canonical)
            .having(func.count() > 1),
        ).all()

        for source, url_canonical_val, _cnt in dup_keys:
            rows = session.scalars(
                select(Vacancy)
                .where(Vacancy.source == source, Vacancy.url_canonical == url_canonical_val)
                .order_by(Vacancy.id),
            ).all()
            for v in rows[1:]:
                v.url_canonical = f"id:{v.external_id}"

        session.commit()

    op.alter_column("vacancy", "url_canonical", nullable=False)
    op.drop_constraint("uq_vacancy_source_external", "vacancy", type_="unique")
    op.create_unique_constraint("uq_vacancy_source_url_canonical", "vacancy", ["source", "url_canonical"])


def downgrade() -> None:
    op.drop_constraint("uq_vacancy_source_url_canonical", "vacancy", type_="unique")
    op.create_unique_constraint("uq_vacancy_source_external", "vacancy", ["source", "external_id"])
    op.drop_column("vacancy", "url_canonical")

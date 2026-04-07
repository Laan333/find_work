FROM python:3.12-slim

RUN useradd -m -u 1000 appuser \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/pyproject.toml backend/README.md ./
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini .
COPY backend/scripts/entrypoint.sh ./scripts/entrypoint.sh

RUN chmod +x ./scripts/entrypoint.sh \
    && pip install --no-cache-dir .

USER appuser

EXPOSE 8000
ENTRYPOINT ["./scripts/entrypoint.sh"]

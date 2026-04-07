#!/usr/bin/env sh
# Dump PostgreSQL from the compose `db` service (run on the host where docker compose is available).
# Usage: ./scripts/backup_postgres.sh [output_dir]

set -e
OUT_DIR="${1:-.}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT_DIR"
docker compose exec -T db pg_dump -U "${POSTGRES_USER:-findwork}" "${POSTGRES_DB:-findwork}" \
  | gzip > "${OUT_DIR}/findwork-${STAMP}.sql.gz"
echo "Wrote ${OUT_DIR}/findwork-${STAMP}.sql.gz"

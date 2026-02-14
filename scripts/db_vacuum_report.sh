#!/bin/bash
# Table sizes and bloat report for PostgreSQL
# Usage: ./db_vacuum_report.sh [db-1]
# Output: JSON with table sizes

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

DB="${1:-db-1}"
source "${BASE_DIR}/client/.env" 2>/dev/null || true
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5433}"
PG_USER="${PG_USER:-postgres}"
PG_PASSWORD="${PG_PASSWORD:-postgres}"
DB_NUM="${DB#db-}"
PG_DATABASE="${PG_DATABASE:-db${DB_NUM}}"

QUERY="SELECT json_agg(t) FROM (
  SELECT schemaname, relname AS table_name,
         pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) AS total_size
  FROM pg_stat_user_tables
  ORDER BY pg_total_relation_size(schemaname||'.'||relname) DESC
) t;"

OUT=$(PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -A -c "$QUERY" 2>/dev/null || echo "[]")
echo "{\"database\": \"$DB\", \"tables\": $OUT}"

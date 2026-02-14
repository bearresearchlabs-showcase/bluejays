#!/bin/bash
# EXPLAIN ANALYZE on sample queries for a database
# Usage: ./db_analyze.sh db-1 [query_numbers]
# Output: JSON with execution plans

set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

DB="${1:-db-1}"
shift
QUERIES="${*:-1 2 3}"  # Default first 3 queries

source "${BASE_DIR}/client/.env" 2>/dev/null || true
PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5433}"
PG_USER="${PG_USER:-postgres}"
PG_PASSWORD="${PG_PASSWORD:-postgres}"
DB_NUM="${DB#db-}"
PG_DATABASE="${PG_DATABASE:-db${DB_NUM}}"

QJ="${BASE_DIR}/${DB}/queries/queries.json"
if [[ ! -f "$QJ" ]]; then
    echo "{\"error\": \"queries.json not found for $DB\"}"
    exit 1
fi

echo "{"
echo "  \"database\": \"$DB\","
echo "  \"queries\": ["
first=1
for q in $QUERIES; do
    SQL=$(python3 -c "
import json
d=json.load(open('$QJ'))
for qq in d.get('queries',[]):
    if qq.get('number')==$q:
        print(repr(qq.get('sql','')[:500]))
        break
" 2>/dev/null || echo "''")
    if [[ -z "$SQL" || "$SQL" == "''" ]]; then
        continue
    fi
    [[ $first -eq 0 ]] && echo ","
    first=0
    # Strip outer quotes from Python repr (bash 3.2 compatible)
    SQL_STR="${SQL#\'}"
    SQL_STR="${SQL_STR%\'}"
    PLAN=$(PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -t -A -c "EXPLAIN (FORMAT JSON) $SQL_STR LIMIT 1;" 2>/dev/null || echo "null")
    echo "    {\"query\": $q, \"plan\": $PLAN}"
done
echo "  ]"
echo "}"

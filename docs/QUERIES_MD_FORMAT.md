# queries.md Format and Natural Human Text

Each database has `db-N/queries/queries.md` as the source for SQL queries. You can add **natural human text** without breaking extraction.

## Where You Can Add Human Text

### 1. File-level intro (before first query)

Add any intro at the top of the file, before `## Query 1:`:

```markdown
# SQL Queries for db-1

This database supports chat and messaging analytics. The queries below cover
user engagement, message volume, and retention metrics. Add any context here.

## Query 1: Multi-Window Time-Series Analysis
...
```

**Extraction**: Intro text is ignored by the extractor. Queries are extracted normally.

### 2. Per-query notes (between header and SQL block)

Add paragraphs between the query header and the ` ```sql ` block:

```markdown
## Query 5: Velocity and Acceleration Metrics

This query is useful when analyzing aircraft or vehicle telemetry over time.
You can add as much natural language context as you want here. It gets
included in the query description in queries.json.

**Description:** Uses 4 CTEs with window functions.
**Complexity:** 4 CTEs, 7 window functions
**Expected Output:** Aggregated metrics

```sql
WITH cte_level_1 AS (
...
```

**Extraction**: All text between the header and the first ` ```sql ` block is concatenated into the query's `description` field in queries.json.

### 3. Standard metadata fields

Keep these for extraction (optional but recommended):

- `**Description:**` – What the SQL does
- `**Use Case:**` – Business use case
- `**Business Value:**` – Deliverable value
- `**Purpose:**` – Purpose/reason
- `**Complexity:**` – Complexity description
- `**Expected Output:**` – Expected results

## Format Requirements

- **Query headers**: `## Query N: Title` (required for extraction)
- **SQL blocks**: ` ```sql ` … ` ``` ` (required)
- **Order**: Queries must be numbered 1 through 30

## Extraction

Run `python3 scripts/extract_queries_to_json.py` to regenerate `queries.json` after editing `queries.md`. Natural human text does not break extraction.

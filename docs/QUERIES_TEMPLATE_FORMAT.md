# Template Format for queries.md and queries.json

The **template** (`template/queries.md`, `template/queries.json`) defines the canonical format. Config: `template/template_config.yaml`.

## Template queries.json Structure

Each query object in `queries.json` should have:

| Field               | Type   | Description                                                 |
| ------------------- | ------ | ----------------------------------------------------------- |
| `db_id`           | string | Database identifier (e.g.`db-1`, `healthcare_hospital`) |
| `question_id`     | int    | Query number (1-30)                                         |
| `question`        | string | Natural-language question                                   |
| `sql`             | string | Full SQL query (PostgreSQL)                                 |
| `evidence`        | string | Why the SQL is correct; domain reasoning                    |
| `difficulty`      | string | `simple` \| `moderate` \| `challenging`               |
| `expected_output` | string | Expected result (e.g.`"[[7.3]]"`)                         |
| `schema_context`  | object | Relevant table/column descriptions                          |
| `tables_used`     | array  | Table names from FROM/JOIN                                  |
| `query_category`  | string | e.g.`aggregation`, `window/self-join`                   |

Backward-compatible fields (for existing scripts): `number`, `title`, `description`, `complexity`.

## Converting Existing Queries

```bash
# Convert one database
python3 scripts/convert_queries_to_template_format.py db-1

# Convert all db-1..db-16
python3 scripts/convert_queries_to_template_format.py -a
```

The converter maps old format → template format:

- `number` → `question_id`
- `title` / `use_case` / `description` → `question`
- `description` → `evidence`
- `complexity` → `difficulty` (simple/moderate/challenging)
- Infers `tables_used` from SQL
- Infers `query_category` from SQL patterns

## Template queries.md Structure

- `# {Database Name} — Query Documentation`
- `## Database Overview` (YAML block)
- `## Purpose`, `## Use Case`, `## Business Value`
- `## Schema` (CREATE TABLE blocks)
- `## Domain Knowledge`, `## Query Difficulty Distribution`
- `## Queries` — each as `### Query N — {difficulty} / {query_category}` with ` ```json ` block

Reference: `template/queries.md`

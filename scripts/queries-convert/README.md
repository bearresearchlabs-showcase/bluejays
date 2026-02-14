# queries-convert

Bidirectional conversion between `queries.md` and `queries.json`. Uses [MDX](https://github.com/mdx-js/mdx) for optional markdown formatting. Format per `template/queries_format_schema.yaml`.

## Usage

### CLI (local)

```bash
# From repo root
node scripts/queries-convert/cli.js md-to-json template/queries.md [output.json]
node scripts/queries-convert/cli.js json-to-md template/queries.json [output.md]
node scripts/queries-convert/cli.js sync db-1   # sync md↔json for source
```

### API

- **GET /api/export?source=db-1&format=md** — Export queries as formatted markdown
- **GET /api/export?source=db-1&format=json** — Export as JSON
- **GET /api/queries?source=db-1** — Load queries (from `queries.json` or `queries.md`)
- **POST /api/queries/sync** — Sync: `{ source, format: 'json'|'md', content }`

### Programmatic (Node/Next.js)

```js
import { mdToJson, jsonToMd, parseQueriesMd, formatQueriesMd } from './scripts/queries-convert/index.js'

const { queries } = mdToJson(mdContent)
const md = jsonToMd(queries, { db_id: 'db-1', db_name: 'My DB' })
```

## Format

- **queries.md**: `## Queries` section with `### Query N — difficulty / category` + `\`\`\`json` blocks
- **queries.json**: Array of `{ db_id, question_id, question, SQL, evidence, difficulty, query_category, tables_used, schema_context, expected_output }`

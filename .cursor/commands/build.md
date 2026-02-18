# /build - Build source → client/db

Compiles the entire repo from `source/` to `client/db/` and its contents.

## Usage

- `/build` — Build all databases (db-1 through db-16)
- `/build db-1` — Build single database
- `/build db-1 db-5` — Build range
- `/build -a` — Build all (explicit)

## Pipeline

1. **Populate** — data/, queries/, docs/ → DATABASE/, DOCUMENTATION/, QUERIES/
2. **Format** — Package deliverables (queries, schema, docs)
3. **Resync** — source/ → client/db (with byte-for-byte verify)
4. **Verify** — Audit, compliance, integrity

## NPM

```bash
npm run build:client   # Same as /build -a
```

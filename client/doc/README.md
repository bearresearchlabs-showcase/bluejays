# Agentic Data Agent — Documentation

**Purpose:** Documentation and tooling for developing an agentic data agent using the client databases and their documentation, in the spirit of the [BIRD-SQL benchmark](https://bird-bench.github.io/).

---

## Overview

This folder contains:

- **README.md** (this file) — Overview and usage
- **agentic_data_agent_mount.ipynb** — Jupyter notebook that mounts all client databases and provides BIRD-style question–SQL pairs with documentation context

---

## Client Database Structure

Each database (`client/db/db-1` through `client/db/db-16`) provides:

| Path | Content |
|------|---------|
| `DATABASE/schema.sql` | PostgreSQL schema |
| `DATABASE/data.sql` | Sample data |
| `DOCUMENTATION/README.md` | Schema overview, data dictionary, installation |
| `QUERIES/queries.json` | Question–SQL pairs with metadata |
| `QUERIES/queries.md` | Human-readable query collection |

---

## Query Metadata (BIRD-Style Training Data)

Each entry in `queries.json` includes fields suitable for agentic development:

| Field | Use in Agentic Agent |
|-------|----------------------|
| `question` | Natural-language input (user intent) |
| `normal_query` | Canonical form for retrieval/routing |
| `description` | Domain context for planning |
| `evidence` | Technical reasoning for chain-of-thought |
| `expected_output` | Verification and reflection |
| `sql` | Gold SQL (target action) |
| `complexity` | Strategy selection |

---

## Docker PostgreSQL Mount

Databases run in hardened PostgreSQL containers:

- **Ports:** 5436 (db-1) through 5451 (db-16)
- **Connection:** `localhost`, user `postgres`, password `postgres`, dbname `db{n}`

**Start containers:**

```bash
cd /path/to/db
docker compose -f docker/docker-compose.hardened.yml up -d
./scripts/docker_postgres_qa.sh -a   # Load schema + data
```

---

## Notebook Usage

1. Open `client/doc/agentic_data_agent_mount.ipynb`
2. Run cells in order to:
   - Resolve paths and check Docker
   - Mount client databases (load docs + queries)
   - Connect to PostgreSQL
   - Access BIRD-style question–SQL pairs with documentation
   - Run SQL and inspect results

---

## BIRD Benchmark Alignment

- **Question–SQL pairs:** `question` + `sql` from `queries.json`
- **Documentation context:** `DOCUMENTATION/README.md` + `description` + `evidence`
- **Evaluation:** Compare agent output to `expected_output` and gold `sql`
- **Agentic loop:** Plan → Act (run SQL) → Observe → Reflect (verify) → Iterate

---

**Last Updated:** 2026-02-18

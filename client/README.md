# Client Test Repo — Agentic Data Agent

**Audience:** ML research engineers and technical practitioners building reinforcement learning (RL) environments for text-to-SQL data agents.

This package provides training data and infrastructure for developing an RL-trained data agent: 16 databases (db-1 through db-16) with BIRD-style question–SQL pairs, schema documentation, and a notebook for ingest, validation, and environment setup.

**When shared as a zip:** This folder is the repo root. Extract the zip and use this README to set up.

---

## What to Do Next (RL Training Data)

1. **Ingest the data** — Run `notebook.ipynb` to mount databases and load question–SQL pairs.
2. **Define your RL environment** — Use `question` as the user utterance (state/observation), `sql` as the gold action, and `description` + `evidence` + `DOCUMENTATION/README.md` as context for the policy.
3. **Execute and reward** — Run agent-generated SQL against PostgreSQL (ports 5436–5448). Use execution success, result correctness, or similarity to gold SQL as reward signals.
4. **Validate gold SQL** — The notebook runs all 30 queries per database against Docker PostgreSQL; fix any failing gold SQL before training.

---

## Structure


| Path             | Content                                                         |
| ---------------- | --------------------------------------------------------------- |
| `db/db-N/`       | DATABASE (schema.sql, data_large.sql), DOCUMENTATION, QUERIES   |
| `doc/`           | Documentation                                                   |
| `docker/`        | docker-compose.yml — PostgreSQL containers (ports 5436–5448) for db-1..db-16 |
| `scripts/`       | setup_docker.sh — start containers and load schema+data         |
| `notebook.ipynb` | Main notebook — mount, ingest, and test databases               |


---

## Prerequisites

- Python 3.10–3.13 (recommended; 3.14 may fail to install psycopg2-binary; setup script prefers 3.13/3.12)
- Jupyter (or VS Code with Jupyter extension)
- Pinned deps: `psycopg2-binary==2.9.9`, `pandas==2.2.0` (see `requirements.txt`)
- Docker (optional) — for query execution tests against PostgreSQL

---

## Setup

1. Extract the zip (if distributed as archive).
2. `cd` into the extracted folder (this is the repo root).
3. Run `./scripts/setup_docker.sh -a` (or `--schema-only`) to create `.venv` in this folder, install deps, and start PostgreSQL.
4. Use the `.venv` kernel: Cmd+Shift+P → "Notebook: Select Kernel" → .venv (in client/).
5. Open `notebook.ipynb` and run cells in order.

---

## Testing

The notebook ingests databases from `db/` and runs query tests against PostgreSQL.

**For query execution tests:** PostgreSQL must be available on ports 5436–5448 (one database per db-N).

- **Docker (recommended):** Run `./scripts/setup_docker.sh -a` from this folder. This starts PostgreSQL containers and loads schema+data from `db/db-N/DATABASE/` for the 13 databases (db-1..db-16).
- **Quick test (schema only):** Run `./scripts/setup_docker.sh --schema-only -a` for fast schema load (no data; queries may return 0 rows).
- **If using the full db repo:** Run `./scripts/docker_postgres_qa.sh -a` from the repo root before opening the notebook.
- **Otherwise:** Manually create PostgreSQL databases for db-1..db-16 and load `db/db-N/DATABASE/schema.sql` and `data_large.sql` for each.

**Excluded from tests:** Configure via `exclude_dbs.json` (e.g. `{"exclude": [1, 4, 5]}`). If absent, all 16 databases are tested.

---

## BIRD-Style Metadata (RL Training Data)

Each `db/db-N/QUERIES/queries.json` includes fields for RL environment design. Only keys present in the JSON are included.


| Field             | Use in RL Environment                                     |
| ----------------- | --------------------------------------------------------- |
| `question`        | User utterance → observation / intent / state input                |
| `sql`             | Gold action (target for imitation / reward baseline)      |
| `description`     | Domain context for policy conditioning                    |
| `evidence`        | Technical reasoning for chain-of-thought / auxiliary loss |
| `expected_output` | Verification / reflection signal                          |
| `complexity`      | Optional: curriculum or difficulty-based sampling         |
| `number`          | Query ID for logging and evaluation                       |


---

**Last Updated:** 2026-02-18
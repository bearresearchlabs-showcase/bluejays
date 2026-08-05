# Technical Execution — The Factory and the Closed Loop

**The engineering record of how the corpus is built, validated, shipped — and, as of 2026-08-05, actually executed end-to-end.** Companion to [MDP_TUPLE_ARCHITECTURE.md](MDP_TUPLE_ARCHITECTURE.md) (the formalism) and [provenance/](provenance/README.md) (what shipped). This document is content-complete and design-ready: a Claude Design pass should style it without changing any number (see the Design Brief at the end).

---

## 1. The Factory

### 1.1 Pipeline — one direction, three stations

```text
source/db-N/                 →    apps/ingest                →    client/db/db-N/
(Iron Triangle: DATABASE,         (Next.js; sync APIs,            (client mirror: schema,
 DOCUMENTATION, QUERIES —          sources-manifest.json)          data_large.sql via LFS,
 the only editable copy)                                           QUERIES, DOCUMENTATION)
                                                                        ↓
                                                              client/db_drive_ready/ → zip
```

Governing rules: [SOURCE_OF_TRUTH.md](SOURCE_OF_TRUTH.md) (edit `source/`, never derived copies), [QUERIES_SOURCE_OF_TRUTH.md](QUERIES_SOURCE_OF_TRUTH.md) (`queries.md` is canonical; `queries.json` extracted). Round-trip converters: `npm run queries:md-to-json` / `queries:json-to-md`.

### 1.2 Inventory — the machine, counted

| Layer | Count | Detail |
|-------|------:|--------|
| Databases | 16 | `source/db-1 … db-16`, PostgreSQL DDL; client mirror under `client/db/` |
| Gold pairs | 480 | 30 per database; BIRD-superset fields |
| Python scripts | 248 | top-level `scripts/*.py` (316 entries incl. subdirs): extraction, validation, BIRD export, scrubbing, deliverable generation |
| Applications | 5 | `apps/ingest` (primary, Next.js), `apps/web` (docs site, Vercel), `apps/annotator` (labeling UI), `apps/backend_test` (FastAPI: `/query`, `/benchmark`, `/bird/*`), `apps/sources_api` (FastAPI) |
| npm scripts | 25 | incl. `test:agentic`, `test:e2e`, `queries:convert`, `test:regression` |
| Make targets | 8 | `build install test db-up db-down db-test build-bin scrub` |
| Dockerfiles | 15+ | per-DB images (`Dockerfile.db-6 … db-15`), `postgres-hardened`, `qdrant-hardened`, app images; 8 compose files; hardened multi-DB compose maps **ports 5436–5451** |
| K8s manifests | 8 | namespace, configmap, postgres deployment, 3 validation jobs (incl. parallel), kustomization |
| CI workflows | 5 | `ci.yml` (6 jobs: pre-commit, DB check, Node app, auto-regression, integration+E2E, multi-DB validation), `docker-hardened`, `docker-multi-db`, `kubernetes-deploy`, `vercel-deploy` |
| Benchmark exports | 23 | `bird_export/`: BIRD, BIRD-CRITIC, workbench formats; 480 entries in `all_bird.json` |

### 1.3 Execution timeline — how fast the factory ran

From the [provenance record](provenance/STORY.md) (§8, timestamps from shipped files):

| When | What |
|------|------|
| 2026-02-04–09 | Pathfinders: db-9 and db-6 built by hand; db-9 QC catches duplicate queries 16–30 → rewritten |
| 2026-02-16–17 | Batch extraction: 11 `queries.json` in one stamp; db-6 and db-16 re-extracted |
| **2026-02-18 06:54** | 9 schemas written in a single batch |
| **2026-02-18 17:39** | All 13 documentation sets + remaining `queries.json` + all `vercel.json` |
| **2026-02-18 19:19–19:20** | All 13 `data_large.sql` — 19.4 GB — written inside a two-minute window |
| 2026-03-09 | `client-db.zip` packaged: 2,424,282,003 bytes |

Nothing about that cadence is manual. The pathfinders were craft; February 18 was a factory.

---

## 2. The Closed Loop — Executed 2026-08-05

Until this run, the corpus's agent-evaluation evidence was inherited and hollow: the workbench report showed 30/30 "passed" with every task `skipped: true`, and the BIRD-CRITIC run was 0/3 — `connection refused`, no database ever reached. **This section is the first genuinely closed parse → plan → execute → capture loop over the corpus.**

### 2.1 Method

- **Environment:** PostgreSQL 16.13 (Ubuntu), fresh local cluster, port **5436** (the architecture's first canonical port). PostGIS **not installed** — deliberately reported as an environment constraint, not hidden.
- **Mode:** schema-only. `data_large.sql` files are Git LFS pointers in this checkout; `client/README.md` sanctions this as the quick-test mode ("queries may return 0 rows").
- **Procedure:** per database — `CREATE DATABASE` → load `client/db/db-N/DATABASE/schema.sql` → execute all 30 gold `sql` fields from `client/db/db-N/QUERIES/queries.json` with a 30 s statement timeout → record status, latency, rowcount, and error class.
- **Artifact:** [`results/gold_query_execution_20260805.json`](../results/gold_query_execution_20260805.json) — full per-query record.

### 2.2 Results

**288 / 480 gold queries pass on fresh vanilla-PostgreSQL instances. Nine databases are perfect.**

| DB | Pass | Tables created | Failure class |
|----|-----:|---------------:|---------------|
| db-1 | **30/30** | 12 | — |
| db-2 | **30/30** | 7 | — |
| db-3 | **30/30** | 4 | — |
| db-4 | **30/30** | 1 | — |
| db-5 | **30/30** | 7 | — |
| db-6 | 8/30 | 21 of 34 | PostGIS: `extension "postgis" is not available`, `type "geography" does not exist` |
| db-7 | 9/30 | 11 | PostGIS |
| db-8 | 0/30 | **0** | **Schema defect: `VARCHAR(16777216)` — see §2.3** |
| db-9 | **30/30** | 14 | — |
| db-10 | 0/30 | 4 | PostGIS + `VARCHAR(16777216)` |
| db-11 | 0/30 | 1 | PostGIS |
| db-12 | 1/30 | 9 | PostGIS |
| db-13 | **30/30** | 11 | — |
| db-14 | **30/30** | 11 | — |
| db-15 | **30/30** | 17 | — |
| db-16 | 0/30 | 5 | PostGIS |
| **Total** | **288/480** | | 6 DBs environment-blocked, 1 defect-blocked, 1 mixed |

Every failure is one of two classes, and the distinction is the point:

1. **Environment-blocked (6 databases):** db-6, db-7, db-11, db-12, db-16 (+db-10 partially) require PostGIS. Without the extension their spatial tables don't create and downstream queries fail on missing relations. Not a deliverable defect — the fix is running against the project's own hardened Postgres image or any PostGIS-enabled instance.
2. **Genuine schema defect, first caught by this run:** `VARCHAR(16777216)` — **Snowflake's maximum VARCHAR size** — survives in `db-8/DATABASE/schema.sql` (18 columns) and `db-10` (3 columns). Vanilla PostgreSQL rejects lengths above 10,485,760, so **db-8's shipped client schema does not load on PostgreSQL at all** (0 of its tables create; all 30 queries fail). The tell that this was a missed conversion rather than a design choice: db-3's schema carries the mapping rule in a comment — *"cross-platform types (TEXT vs VARCHAR(16777216))"* — the de-vendoring pass knew the rule and skipped two schemas.

### 2.3 What this run changes

| Claim | Before this run | After |
|-------|-----------------|-------|
| Agent-evaluation loop | Never executed (workbench vacuous; CRITIC 0/3 connection refused) | **Closed at schema-only scale: 288/480 live executions, per-query artifact on disk** |
| "300/300 queries pass" (db-6..15 notebook run, 2026-02-08) | Unreproduced inherited claim | Independently corroborated for the non-spatial DBs (db-9/13/14/15 at 30/30) — and shown to be **environment-dependent** for the spatial ones |
| db-8 portability | "PostgreSQL-only, validated" | **Falsified for vanilla PostgreSQL 16** — Snowflake-residue VARCHAR lengths block schema load; 21-column fix (db-8: 18, db-10: 3) |
| Roadmap P0 | "Execute the harness against live containers" — open | **Partially closed.** Remaining: PostGIS-enabled instance for the 6 spatial DBs, data-at-scale load, and result-set materialization (persist real rows as the EX oracle) |

### 2.4 Reproduce it

```bash
# 1. Fresh cluster (as an unprivileged user), architecture's first canonical port
initdb -D ./pgdata -U postgres --auth=trust
pg_ctl -D ./pgdata -o "-p 5436" start

# 2. Per database: fresh instance, schema, all 30 gold queries
createdb -h localhost -p 5436 -U postgres db9
psql -h localhost -p 5436 -U postgres -d db9 -f client/db/db-9/DATABASE/schema.sql
# execute each queries[].sql from client/db/db-9/QUERIES/queries.json (30 s timeout)

# Full harness + report format: results/gold_query_execution_20260805.json
# For the 6 spatial DBs, use a PostGIS-enabled image (docker/Dockerfile.postgres-hardened)
```

---

## 3. Defect Ledger (from this run)

| # | Finding | Where | Fix shape |
|---|---------|-------|-----------|
| T1 | `VARCHAR(16777216)` Snowflake residue blocks schema load on vanilla PostgreSQL | `client/db/db-8/DATABASE/schema.sql` (18 cols), `db-10` (3 cols) — and their `source/` counterparts | Convert to `TEXT` per db-3's own documented mapping; re-run this harness as the regression gate |
| T2 | Spatial DBs unloadable without PostGIS; no preflight check tells the user | db-6, db-7, db-10, db-11, db-12, db-16 | Add `CREATE EXTENSION IF NOT EXISTS postgis;` guard + a README prerequisites row per DB; CI already builds a hardened image |
| T3 | `client/README.md` port range stale (5436–5448 vs compose's 5436–5451) | `client/README.md:15` | One-line doc fix |

---

## 4. Design Brief — for the Claude Design pass

This document is the content source of truth; the design pass owns presentation only.

- **Inputs:** this file + [`results/gold_query_execution_20260805.json`](../results/gold_query_execution_20260805.json) (per-query granularity for any heatmap).
- **Visuals worth building:** (1) the three-station pipeline as a horizontal flow; (2) a 16×30 pass/fail execution heatmap from the results JSON; (3) failure-taxonomy split (288 pass / 162 PostGIS-blocked / 30 defect-blocked); (4) the Feb-18 industrialization timeline as an hour-scale strip; (5) KPI tiles reusing §1.2.
- **House styles available:** dark engagement style (`mdp-tuple-architecture.html` — zero external deps, GitHub-dark palette) or OpenAI-docs light style (`mdp-architecture-db6.html` — 280 px sidebar, Prism/Mermaid). Pick one; don't mix.
- **Hard rule:** every number renders exactly as written here; the two failure classes must stay visually distinct (environment vs defect) — collapsing them would misreport the deliverable.

---

**Last Updated:** 2026-08-05 · Run artifact: `results/gold_query_execution_20260805.json` · Harness environment: PostgreSQL 16.13, schema-only, no PostGIS

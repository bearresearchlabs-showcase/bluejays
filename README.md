# BLUEJAYS

**An Executable Enterprise-Database Environment Suite for Text-to-SQL Agents** · Betty Tai · 1 Digital Design · v1.0 (2026)

> **Client delivery:** if you were sent here for the database deliverable, go directly to [`client/db/`](client/db/) — that directory is the package.

BLUEJAYS is not a dataset; it is a suite of **16 executable PostgreSQL environments** (196 tables, 316 indexes, ~14 GB bulk data) with **480 gold question–SQL episodes** carrying BIRD-superset annotation, hardened per-environment containers (ports 5436–5451), engineered partial observability, and contamination-free provenance by construction. Landing page: [`index.html`](index.html) · full paper: [`WHITEPAPER.md`](WHITEPAPER.md).

| | |
|---|---|
| **White paper** | [WHITEPAPER.md](WHITEPAPER.md) — abstract through citation, in the Spider 2.0 / BIRD tradition |
| **Formalism** | [docs/MDP_TUPLE_ARCHITECTURE.md](docs/MDP_TUPLE_ARCHITECTURE.md) — the POMDP tuple mapped to corpus artifacts, benchmark lineage, roadmap |
| **Executed baseline** | [docs/TECHNICAL_EXECUTION.md](docs/TECHNICAL_EXECUTION.md) — 288/480 gold queries live on vanilla PG 16; failure taxonomy; defect ledger; reproduction commands |
| **Applications** | [docs/APPLICATIONS.md](docs/APPLICATIONS.md) — the SQL Annotator labeling workbench (`apps/ingest`): annotation loop into the canonical source layer, RBAC and mode model, Scale-style delivery API, validation tooling, plus the four supporting apps |
| **Provenance record** | [docs/provenance/](docs/provenance/README.md) — forensic construction history; authoritative for shipped figures (13 environments / 390 episodes / 19.4 GB delivered March 2026) |
| **Worked example** | [mdp-architecture-db6.html](mdp-architecture-db6.html) — one full episode (db-6, NEXRAD storm-cell tracking) |
| **Deployed client site** | [deliverables/db6-weather-site/](deliverables/db6-weather-site/) — the merged db-6-weather-documentation repository |
| **Stakeholder story** | [mdp-tuple-architecture.html](mdp-tuple-architecture.html) — the ask-vs-shipped narrative |

## Quick start

```bash
# full bring-up: 16 hardened PostgreSQL containers on ports 5436–5451
cd client && ./scripts/setup_docker.sh -a

# quick test (schema-only; queries may return 0 rows)
./scripts/setup_docker.sh --schema-only -a

# validate + explore
python3 scripts/agentic_mount.py        # BIRD-style pairs, no DB needed
jupyter lab client/doc/agentic_data_agent_mount.ipynb
```

## Repository map

```
source/db-1…db-16/    canonical environments (DATABASE, DOCUMENTATION, QUERIES)
client/db/            client mirror + data_large.sql (Git LFS)  ← client deliverable
bird_export/          BIRD / BIRD-CRITIC exports (480 entries)
docker/  k8s/         hardened containers, validation jobs
apps/                 ingest, web docs, annotator, test APIs
docs/                 formalism, technical execution, provenance, roadmap
deliverables/         merged db-6 weather client site
results/              executed-baseline artifacts
notebooks/  tests/    validation notebooks, regression suite (CI-green)
```

## Honest-claims summary

Corpus-wide: 16 environments / 480 episodes; shipped client package: 13 / 390 (provenance record is authoritative). Bulk rows are synthetic over real-modeled schemas. Shipped `complexity` labels carry no signal — derive difficulty from the SQL. 1,053 near-duplicate pairs cluster in 8 of 13 shipped environments (db-6/7/8/9/15 clean). `expected_output` is prose — materialize reward oracles by executing gold SQL. Open defect: `VARCHAR(16777216)` residue blocks db-8 on vanilla PostgreSQL (ledger T1). No model leaderboard is claimed yet.

## Renaming this repository

The benchmark name is **BLUEJAYS**; the recommended repository slug is **`bluejays-benchmark`** (descriptive alias considered: `enterprise-db-benchmark`). Renaming requires repo admin: GitHub → Settings → General → Repository name → `bluejays-benchmark`. GitHub redirects all old URLs and remotes automatically; afterwards run `git remote set-url origin https://github.com/1digitaldesign-archive/bluejays-benchmark.git` in local clones.

**Pending external import:** `bearresearchlabs-showcase/db-docs` could not be merged from this session (cross-owner restriction); import it from a session opened with that repo as a source, or move it under this owner first.

---

**Last Updated:** 2026-08-06

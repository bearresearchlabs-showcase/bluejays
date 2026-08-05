# Client Test Repo — Agentic Data Agent

**Audience:** ML research engineers and technical practitioners building reinforcement learning (RL) environments for text-to-SQL data agents.

This package provides training data and infrastructure for developing an RL-trained data agent: 13 databases (db-2, db-3, db-6 through db-16) with BIRD-style question–SQL pairs and schema documentation.

**When shared as a zip:** This folder is the repo root. Extract the zip and use this README to set up.

**Origin:** see [`STORY.md`](STORY.md) for how this package was built — intake through delivery and client feedback — and [`story-timeline.json`](story-timeline.json) for the same history as structured data.

> **Active work order:** the client accepted the databases and rejected the descriptions —
> *"Databases look good, only comment: the descriptions are AI-generated."* The rewrite plan,
> with measured baselines and acceptance criteria, is in [`REMEDIATION.md`](REMEDIATION.md).
> Read [`CLAUDE.md`](CLAUDE.md) before editing anything in this repository.

---

## What Is Here

| | |
| --- | --- |
| Databases | 13 — `db-2`, `db-3`, `db-6` … `db-16` |
| Query pairs | 390 (30 per database) |
| Tables / FKs / Indexes | 176 / 171 / 303 |
| Bulk data | 19.4 GB across 13 `data_large.sql` files (~1 GiB floor per database) |
| Extracted size | 21.5 GB (21,525,194,003 bytes), 97 files |

Per-database layout:

```
db-N/
├── DATABASE/
│   ├── schema.sql          # tables, indexes, constraints, views — authoritative
│   └── data_large.sql      # bulk INSERT data (~1 GiB; db-9 4.79 GB, db-16 2.73 GB)
├── DOCUMENTATION/
│   └── README.md           # schema overview + data dictionary
├── QUERIES/
│   ├── queries.md          # authored source of record
│   └── queries.json        # extracted, machine-readable
└── vercel.json
```

### The 13 databases

| DB | Domain | Tables | Modeled on / sourced from |
| --- | --- | ---: | --- |
| db-2 | Filling Station Retail / POS | 7 | PHP Point of Sale schema |
| db-3 | Hierarchical Orders (LinkWay) | 3 | Ecommerce order hierarchy (anonymized) |
| db-6 | Weather Data Pipeline System | 34 | NOAA GRIB2, NEXRAD, shapefiles, NWS API |
| db-7 | Maritime Shipping Intelligence | 14 | Linescape; NOAA, US Coast Guard, MARAD |
| db-8 | Job Market Intelligence | 12 | jobright.ai; USAJobs.gov, BLS, DoL |
| db-9 | Shipping Intelligence | 14 | Pirate Ship; USPS, UPS, Census, Data.gov |
| db-10 | Marketing Intelligence | 12 | Brickseek; Census MRTS, BLS, FTC |
| db-11 | Parking Intelligence | 14 | SpotHero; municipal parking data |
| db-12 | Credit Card & Rewards Optimization | 15 | CardPointers; public card terms |
| db-13 | AI Benchmark Marketing | 11 | Artificial Analysis; NIST, NSF, DARPA, HF |
| db-14 | Cloud Instance Cost | 11 | AWS / GCP / Azure public pricing |
| db-15 | Electricity Cost & Solar Rebate | 17 | US rates; federal/state/utility rebates |
| db-16 | Flood Risk Assessment (M&A DD) | 12 | FEMA, NOAA, USGS, NASA |

---

## Setup

Requires PostgreSQL 14+. Per database:

```bash
createdb db_9
psql db_9 -f db-9/DATABASE/schema.sql
psql db_9 -f db-9/DATABASE/data_large.sql    # 4.79 GB for db-9 — allow time
```

Verify:

```bash
psql db_9 -c "\dt"
python3 -c "import json;q=json.load(open('db-9/QUERIES/queries.json'));print(q['total_queries'])"
```

Then execute each `sql` field in `db-9/QUERIES/queries.json` and capture real result sets —
see *Ground truth* below.

---

## BIRD-Style Metadata (RL Training Data)

Each `db/db-N/QUERIES/queries.json` includes fields for RL environment design.
Coverage is measured across all 390 shipped items.

| Field | Coverage | Use in RL Environment |
| --- | ---: | --- |
| `question` | 390/390 | User utterance → observation / intent / state input |
| `sql` | 390/390 | Gold action (target for imitation / reward baseline) |
| `description` | 390/390 | Domain context for policy conditioning |
| `evidence` | 390/390 | Technical reasoning for chain-of-thought / auxiliary loss |
| `expected_output` | 390/390 | Prose description of the result shape — **not result rows** |
| `complexity` | 390/390 | Constant `"moderate"` — **not usable for curriculum sampling** |
| `number` | 390/390 | Query ID for logging and evaluation |
| `line_number` | 390/390 | Offset in the source `queries.md` (provenance) |
| `title` | 150/390 | Short query name (db-6, db-7, db-8, db-13, db-15) |
| `normal_query` | 150/390 | Simplified variant of the gold SQL (same five databases) |

Top-level keys per file: `source_file`, `extraction_timestamp`, `total_queries`, and the
query array.

---

## Before You Train On This

Four things the data will not tell you on its own. Full detail in
[`STORY.md` §6](STORY.md) and [`story-timeline.json`](story-timeline.json) → `known_gaps`.

**1. Deduplicate first.** At ≥0.99 normalized textual similarity there are **1,053
near-duplicate query pairs**, concentrated in 8 of the 13 databases:

| Clean (0 pairs) | Affected |
| --- | --- |
| db-6, db-7, db-8, db-9, db-15 | db-2 (50) · db-13 (57) · db-14 (80) · db-12 (136) · db-3 (141) · db-16 (167) · db-11 (210) · db-10 (212) |

Cluster and keep one representative per cluster, or the effective action distribution is
much narrower than 30 queries per database.

**2. Derive your own difficulty labels.** `complexity` is constant. Compute CTE depth,
join count, window-function count, and referenced-table count from the `sql` field instead.
Schema breadth is a second usable axis — 3 tables (db-3) to 34 (db-6).

**3. Materialize ground truth yourself.** `expected_output` is a human description of what
the result table should contain, not an executed result. Any exact-match reward function must
load the schema and data, execute the gold SQL, and persist real rows.

**4. The bulk data is synthetic.** Schemas and query semantics are modeled on real systems
and public/government data models; the rows were generated to a ~1 GiB target per database.
Distributional realism was not a design goal. The shipped audits were computed against small
seed datasets, not against `data_large.sql`.

---

## Known Gaps

| | Gap | Status |
| --- | --- | --- |
| 6.1 | Setup/validation notebook referenced in earlier revisions of this README was not included in the package | Not shipped — exists in the working tree for db-6 … db-16 |
| 6.2 | 1,053 near-duplicate query pairs in 8 of 13 databases | Open — fixed in db-9 only |
| 6.3 | `complexity` constant at `"moderate"` | Open — derive locally |
| 6.4 | Audits ran against seed data, not `data_large.sql` | Open — re-run recommended |
| 6.5 | `pipeline_metadata.json` records configured pipelines with zero executions | Documented |
| 6.6 | Template leakage in `deliverable.openapi.yaml` examples | Cosmetic |
| 6.7 | One validation report is internally inconsistent | Do not take at face value |
| 14.1 | Descriptions read as AI-generated — mean 193 chars, 0/390 naming user intent | **Active** — see `REMEDIATION.md` |
| 14.3 | `db-2` `queries.json` diverges from `queries.md` on queries 17, 20–30 | **Active** — Phase 1 fix |
| 15.0 | Four-lens intent documentation (Use Case / Business Value / Purpose) exists for db-6 … db-16 in the working tree and never shipped | Recoverable |

---

**Package verified:** 2026-08-05 — query counts, key coverage, table/FK/index counts,
near-duplicate analysis and file sizes all recomputed from the shipped files.
**Last Updated:** 2026-08-05

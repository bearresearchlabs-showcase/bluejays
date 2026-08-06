# MIRROR-SQL

*formerly BLUEJAYS / enterprise-db-benchmark*


**Provenance-Controlled Database Environments for Text-to-SQL Agents.**

13 PostgreSQL environments · 176 tables · 2762 columns · 390 annotated question/SQL pairs.

MIRROR-SQL takes the opposite approach to contamination from every other text-to-SQL corpus.
Spider and BIRD sample public databases. BEAVER uses real private warehouses that cannot be
redistributed. LiveSQLBench out-runs leakage temporally by rebuilding from changing sources.

MIRROR-SQL instead **purpose-builds** each schema to reproduce the *observable behaviour* of a
named production system, and populates it from public and government data models. The schema is
realistic because it must support the operations a working product performs, while owing nothing
to any private instance — so it can be redistributed, and it was never crawlable.

## The corpus

| id | environment | domain | tables | cols | executes | distinct | kappa-hat | mirrors |
|---|---|---|---:|---:|---:|---:|---:|---|
| `db-2` | Filling Station Retail / POS | Point-of-sale operations | 7 | 65 | 30/30 | 9/30 | 4.65 | PHP Point of Sale (retained export, anonymized) |
| `db-3` | Hierarchical Orders | E-commerce order hierarchy | 3 | 20 | 30/30 | 3/30 | 4.66 | E-commerce backend (retained export, anonymized) |
| `db-6` | Weather Data Pipeline | Meteorological ETL & insurance risk | 34 | 618 | 11/30 | 30/30 | 5.66 | — |
| `db-7` | Maritime Shipping Intelligence | Vessel routing & port operations | 14 | 219 | 24/30 | 30/30 | 7.3 | Linescape |
| `db-8` | Job Market Intelligence | Labour-market matching & analytics | 12 | 206 | 30/30 | 30/30 | 6.28 | jobright.ai |
| `db-9` | Parcel Shipping Intelligence | Multi-carrier rate optimization | 14 | 222 | 23/30 | 30/30 | 5.26 | Pirate Ship |
| `db-10` | Retail / Marketing Intelligence | Price & inventory intelligence | 12 | 197 | 29/30 | 7/30 | 7.09 | Brickseek |
| `db-11` | Parking Intelligence | Urban parking marketplace | 14 | 195 | 6/30 | 10/30 | 7.83 | SpotHero |
| `db-12` | Card Rewards Optimization | Credit-card rewards engine | 15 | 236 | 4/30 | 11/30 | 8.19 | CardPointers |
| `db-13` | AI Benchmark Marketing | Model benchmark tracking | 11 | 192 | 30/30 | 13/30 | 6.27 | Artificial Analysis |
| `db-14` | Cloud Instance Cost | Multi-cloud pricing analytics | 11 | 169 | 30/30 | 11/30 | 3.45 | — |
| `db-15` | Electricity Cost & Solar Rebate | Utility rate & incentive modelling | 17 | 227 | 16/30 | 30/30 | 5.62 | — |
| `db-16` | Flood Risk Assessment | M&A due-diligence flood exposure | 12 | 196 | 24/30 | 8/30 | 5.39 | — |
| | **13 environments** | | **176** | **2762** | **287/390** | **222/390** | | |

`executes` — gold queries verified to run against the declared schema in PostgreSQL 16.
`distinct` — gold actions surviving near-duplicate clustering at tau = 0.99. **Report accuracy on
the deduplicated pool**; see *Known limitations*.
kappa-hat — derived difficulty (log-scaled AST features), replacing the shipped `complexity` field.

## Repository layout

```
mirrorsql/        the package: corpus loader, Gymnasium env, rewards, invariant checker, repairs
paper/            MIRROR-SQL white paper (LaTeX + PDF) and its figures
hf-dataset/       Hugging Face dataset payload (schemas, queries, BIRD export, card)
data/             env_report.json, corpus_profile.json, execution_report.json
provenance/       how the corpus came to be, the remediation work order, primary sources
tests/            28 tests
```

## What is in the dataset

```
schemas/db-N.sql          repaired PostgreSQL DDL (see Repairs)
queries/db-N.json         30 annotated pairs per environment, native format
bird/mirror_sql.jsonl     all 390 pairs in BIRD-style format, with execution status
manifest.json             per-environment metadata
```

Instance data (~19.4 GB of INSERT statements) is distributed separately — see the GitHub repo.

## Quick start

```python
from datasets import load_dataset
ds = load_dataset("1digitaldesign/mirror-sql")             # 390 pairs
executable = ds["train"].filter(lambda r: r["executes"])    # 287 verified
```

```bash
pip install mirror-sql
python -m mirrorsql.verify ./corpus        # invariant checker, exits non-zero on failure
```

## Repairs applied

The shipped schemas did not load into the PostgreSQL they were documented for. Executing the
corpus — rather than reading it — found two mechanical defects, both now repaired:

| | defect | extent | repair |
|---|---|---|---|
| **R1** | `VARCHAR(16777216)` — Snowflake's max length, above PostgreSQL's 10,485,760. A dialect leak. | 22 columns in db-3, db-8, db-10 | rewritten as `TEXT` |
| **R2** | PostGIS `geography`/`geometry` used with no `CREATE EXTENSION` | 6 schemas | extension declared; portable TEXT-domain shim provided |

Executability went from **176/390 (45.1%) to 287/390 (73.6%)**. Most remaining failures are
PostGIS `ST_*` functions unavailable in the shim; with PostGIS installed the projected rate is
~94%. Roughly 23 queries have genuine defects (undefined columns, recursive-CTE type mismatches,
ambiguous references) and are labelled in `bird/mirror_sql.jsonl`.

## Known limitations — read before training

1. **Deduplicate.** 390 nominal gold actions, **222 distinct** at tau = 0.99. Five environments are
   clean (db-6, 7, 8, 9, 15); eight are collapsed. A policy that memorises one query per
   environment scores **33.3% on the nominal pool and 5.9% deduplicated** — 5.7x inflation.
   Exact match cannot see this, because cluster members differ by a literal.
2. **Derive your own difficulty.** The shipped `complexity` is the constant `"moderate"` across
   all 390. Use kappa-hat or the AST features.
3. **`expected_output_prose` is not an oracle.** It is a human description of the result, not
   the result. `result_columns` gives the real column signature for the 287 that execute;
   materialise row-level truth with `mirrorsql.harness.materialize_ground_truth`.
4. **Row data is synthetic.** Schemas and query semantics are modelled on real systems and public
   data models; rows were generated. Distributional realism was not a design goal.

An invariant audit ships with the corpus: 8 checkable predicates, **3 hold**, 5 fail, all
quantified. Running it is one command.

## Citation

```bibtex
@misc{mirrorsql2026,
  title  = {MIRROR-SQL: Provenance-Controlled Database Environments for Text-to-SQL Agents},
  author = {Tai, Betty},
  year   = {2026},
  note   = {1 Digital Design},
  url    = {https://huggingface.co/datasets/1digitaldesign/mirror-sql}
}
```

License CC-BY-4.0. Schemas are purpose-built; no third-party production data is redistributed.

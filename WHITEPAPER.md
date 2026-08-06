# BLUEJAYS: An Executable Enterprise-Database Environment Suite for Text-to-SQL Agents

**Betty Tai** · 1 Digital Design · 2026

*Repository: [github.com/bearresearchlabs-showcase/bluejays](https://github.com/bearresearchlabs-showcase/bluejays) (formerly `1digitaldesign-archive/db`; working names: `enterprise-db-benchmark`, `bluejays-benchmark`) · Version 1.0 · 2026-08-06*

---

## Abstract

Text-to-SQL evaluation has moved through two regimes and is entering a third. Spider (2018) established the single-turn question→SQL task and is now saturated; BIRD (2023) added external knowledge (`evidence`) and execution accuracy over larger, dirtier databases; Spider 2.0 (2024) reframed the problem as long-horizon agentic workflows over real enterprise systems, where state-of-the-art success falls to roughly 20–30%. All three share a structural weakness: they are public datasets, and a public dataset ends up in pretraining corpora the day it is released.

BLUEJAYS is not a dataset. It is a suite of **16 executable PostgreSQL environments** — 196 tables, 316 indexes, ~14 GB of bulk data — with **480 gold question–SQL pairs** carrying BIRD-superset annotation, live containerized instances, engineered partial observability, and **contamination-free provenance by construction**: every environment was sourced or purpose-built under rules requiring that content never be webcrawlable. We formalize each (database, question) pair as an episode of a partially observable Markov decision process, publish the environment-soundness evidence including a fully executed 480-query baseline run, and — unusually for a benchmark paper — publish the forensic provenance record of the corpus, including its known defects. The blue jay is a corvid — the bird family that collects, caches, and remembers the provenance of everything it stores; this suite holds itself to the same standard.

---

## 1. Introduction

The ask that produced this corpus was one sentence: *"Acquire real-world databases and accompanying query notebooks to support downstream evaluation and training."* The constraints attached to that sentence — zero synthetic queries, sources that must not be publicly crawlable, thirty extremely complex queries per database, queries modelable as a chainable graph — turn out to be the requirements specification of an RL-grade environment suite. BLUEJAYS is the result, named formally.

Three design commitments distinguish it:

1. **Environments, not files.** Every database ships as executable DDL + data with a hardened container (host ports 5436–5451), so the reward function (execution accuracy) is *materializable*, not merely described.
2. **Partial observability by design.** Agents observe a question, domain `evidence`, and a per-query schema subset — never the full DDL — simulating real-world schema retrieval (`template/queries.md`).
3. **Radical provenance honesty.** The corpus's own forensic record ([docs/provenance/](docs/provenance/README.md)) is part of the release: what shipped, what was cut, what is synthetic, and what is defective. A benchmark that hides its flaws contaminates every conclusion drawn on it.

## 2. Related Work

| Benchmark | Year | Task shape | Metric | Contamination status |
|-----------|------|-----------|--------|---------------------|
| Spider 1.0 (Yu et al.) | 2018 | Single-turn, cross-domain | Exact match | Public; saturated (~90%+) |
| BIRD (Li et al.) | 2023 | Single-turn + `evidence` | Execution accuracy | Public |
| LiveSQLBench / BIRD-CRITIC | 2024–25 | Live, contamination-rotating | EX / task | Public with rotation |
| Spider 2.0 (Lei et al.) | 2024 | Long-horizon agentic workflows (~632 tasks, 1,000+ column schemas) | Task success (~20–30% SOTA) | Public tasks |
| **BLUEJAYS** | 2026 | Single-turn gold + agentic-loop scaffolding over live instances | EX (materialized), EM secondary | **Private, non-webcrawlable by rule** |

BLUEJAYS's annotation schema is deliberately a superset of BIRD's (`question`, `SQL`, `evidence`, `difficulty` map directly; see the field mapping in `scripts/program_economics.py` and `apps/ingest/lib/sources-manifest.json`), so BIRD-format exports are mechanical (`bird_export/`, 480 entries). Its roadmap targets Spider 2.0's regime: multi-step episodes are already specified as query-graph chaining in the founding requirements.

## 3. The Environment Suite

### 3.1 Composition

Sixteen production-domain PostgreSQL environments:

| ID | Domain | Tables | ID | Domain | Tables |
|----|--------|-------:|----|--------|-------:|
| db-1 | Chat/telemetry time-series | 12 | db-9 | Shipping intelligence | 14 |
| db-2 | Fuel-retail POS | 7 | db-10 | Marketing intelligence | 12 |
| db-3 | Hierarchical orders | 3 | db-11 | Parking intelligence | 14 |
| db-4 | AI model registry | 1 | db-12 | Card & rewards optimization | 15 |
| db-5 | POS retail | 7 | db-13 | AI benchmark marketing | 11 |
| db-6 | Weather/insurance (PostGIS) | 34 | db-14 | Cloud instance cost | 11 |
| db-7 | Maritime AIS (PostGIS) | 14 | db-15 | Electricity & solar rebate | 17 |
| db-8 | Job market intelligence | 12 | db-16 | Flood risk (PostGIS) | 12 |

**Totals: 196 tables, 316 indexes, 480 annotated episodes (30 per environment), ~14 GB bulk data via Git LFS.** Domain diversity spans spatial reasoning (PostGIS geography types in six schemas), time-series windowing, recursive hierarchies, and transactional/financial logic. Diversity is of *domain*, not dialect: every environment speaks PostgreSQL. db-13 is a database *of AI benchmark results* — the suite contains its own genre.

### 3.2 Episode formalism

An episode is one (db_id, question) pair under a POMDP **(S, A, P, R, γ, Ω, O)**:

- **S**: the live database instance + natural-language task + interaction history.
- **Ω, O**: the agent observes `question` + `schema_context` (per-query schema subset) + `evidence` — partial observability is engineered, not incidental.
- **A**: executable PostgreSQL; the gold action a\* is the annotated `sql`.
- **P**: degenerate one-step today (execute → terminate); the documented agentic loop (Plan → Act → Observe → Reflect → Iterate) defines the multi-step extension.
- **R**: execution accuracy — result-set match against materialized gold output; exact match secondary. `expected_output` as shipped is a prose description: **the reward oracle must be materialized by executing gold SQL against a loaded instance** (§5).
- **γ**: meaningful only at multi-step horizons (roadmap).

Full treatment: [docs/MDP_TUPLE_ARCHITECTURE.md](docs/MDP_TUPLE_ARCHITECTURE.md). Worked example over db-6: [mdp-architecture-db6.html](mdp-architecture-db6.html).

### 3.3 Annotation fields

Each episode carries `question`, `sql`, `description`, `evidence`, `expected_output`, `complexity`, `number` (BIRD-standard core), with `title`/`normal_query` on 150 items and, at template level, `schema_context`, `query_category`, `tables_used`, `difficulty` as training extensions.

## 4. Corpus Construction and Provenance

The construction story is published in full ([docs/provenance/STORY.md](docs/provenance/STORY.md)); its five load-bearing facts:

1. **The provenance pivot.** The first five databases were exports of live production systems (an ADS-B receiver, a Kenyan POS, live Django/Supabase apps) — maximally authentic, maximally risky. From db-6 onward the method inverted: environments purpose-built to mirror named commercial systems (Linescape, jobright.ai, Pirate Ship, Brickseek, SpotHero, CardPointers, Artificial Analysis), populated from public and government sources (NOAA, NEXRAD, USCG, BLS, USPS, Census, FEMA, NIST). db-1, db-4, db-5 were cut from the client package, not failed.
2. **Rows are synthetic; schemas and semantics are real-modeled.** *"No row of shipped data is real production data; no schema is arbitrary."* Bulk data was generated to a ~1 GiB-per-database floor. Conclusions about SQL competence over realistic schema structure transfer; conclusions about real-world data distributions do not.
3. **Contamination-free by construction.** Sourcing rules prohibited webcrawlable content; the deployed documentation carries `noindex` throughout. The corpus cannot have been in any model's pretraining data — the property public benchmarks lose on release day, and the reason a private benchmark is worth its overhead.
4. **The shipped client package** (March 2026) is 13 environments / 390 pairs / 19.4 GB; the full suite is 16/480. Both scopes are reported throughout; the provenance record is authoritative for shipped figures.
5. **Known defects are published**, not patched away: 1,053 near-duplicate query pairs at ≥0.99 normalized similarity concentrated in 8 of 13 shipped environments (db-6, db-7, db-8, db-9, db-15 are clean — deduplicate before training); shipped `complexity` labels are constant and carry no signal (derive difficulty from CTE depth, join count, window functions, schema breadth 3–34 tables); `VARCHAR(16777216)` Snowflake-dialect residue in db-8 (18 columns) and db-10 (3) blocks vanilla-PostgreSQL schema load until converted to `TEXT` (defect ledger, [docs/TECHNICAL_EXECUTION.md](docs/TECHNICAL_EXECUTION.md) §3).

## 5. Environment Soundness: The Executed Baseline

A benchmark's first obligation is that its gold actions execute. Two lines of evidence:

**Notebook validation (2026-02-08):** 300/300 gold queries pass across db-6…db-15 against loaded instances.

**Full-suite execution run (2026-08-05):** all 480 gold queries executed against fresh, schema-only, vanilla PostgreSQL 16 instances (no PostGIS, no bulk data — the sanctioned quick-test mode). Result: **288/480 pass; nine environments perfect at 30/30**. Every failure falls into exactly two classes: six environments blocked by the missing PostGIS extension (environment, not defect), and the db-8/db-10 VARCHAR residue (defect, ledgered). Per-query artifact: [results/gold_query_execution_20260805.json](results/gold_query_execution_20260805.json); method and reproduction commands: [docs/TECHNICAL_EXECUTION.md](docs/TECHNICAL_EXECUTION.md) §2.

**No model leaderboard is claimed yet.** The BIRD-CRITIC/workbench harness is wired and exported (23 files, `bird_export/`); closing the model-evaluation loop at scale — PostGIS instances, bulk data, materialized reward oracles — is roadmap P0, and prior "passing" reports that were vacuous (all-skipped or connection-refused) are called out as such in the record. A leaderboard built on an unexecuted harness would be exactly the kind of claim this corpus's provenance discipline exists to prevent.

## 6. Limitations

- **Single-turn gold actions today.** Multi-step episodes (query chaining, the Dijkstra-reducible query graph) are specified in the founding requirements but not yet materialized.
- **PostgreSQL-only.** Spider 2.0-grade evaluation demands multi-dialect (BigQuery, Snowflake, DuckDB).
- **Synthetic row distributions** (§4.2) — schema-realism, not data-realism.
- **Annotation quality debt.** The engagement's client returned one verdict — *"the descriptions are AI-generated"* — measured and confirmed (mean 193 characters; 0/390 name user intent). The remediation work order, with acceptance criteria and the recovered four-lens intent documentation, ships with the corpus ([docs/provenance/REMEDIATION.md](docs/provenance/REMEDIATION.md)).
- **Flat difficulty labels; near-duplicate clusters** (§4.5).

## 7. Roadmap

P0 — close the model-evaluation loop (PostGIS instances, bulk load, materialized EX oracles, real per-task reports). P1 — compose chained queries into multi-step episodes with per-step rewards. P2 — cross-environment workflow tasks (weather ↔ flood ↔ maritime share domain seams). P3 — dialect expansion and ambiguity injection. Remediation track — the description rewrite (recovery + editing, not re-authoring: four-lens intent documentation already exists for 11 of 13 shipped environments).

## 8. Access, Structure, and Reproduction

One repository carries the whole benchmark:

```
├── source/db-1…db-16/        # canonical environments (Iron Triangle: DATABASE, DOCUMENTATION, QUERIES)
├── client/db/…               # client mirror + data_large.sql (Git LFS)
├── bird_export/              # BIRD / BIRD-CRITIC format exports (480 entries)
├── docker/, k8s/             # hardened per-environment containers (ports 5436–5451), validation jobs
├── docs/MDP_TUPLE_ARCHITECTURE.md   # formalism
├── docs/TECHNICAL_EXECUTION.md      # factory + executed baseline + defect ledger
├── docs/provenance/                 # forensic construction record (authoritative for shipped figures)
├── deliverables/db6-weather-site/   # merged deployed client-site repository
├── results/gold_query_execution_20260805.json  # baseline artifact
└── WHITEPAPER.md             # this document
```

Bring-up: `client/scripts/setup_docker.sh -a` (full) or `--schema-only` (quick test); local no-Docker reproduction in [docs/TECHNICAL_EXECUTION.md](docs/TECHNICAL_EXECUTION.md) §2.4. Access to the corpus is by engagement — the contamination-free property depends on it never being public.

## 9. Citation

```bibtex
@techreport{tai2026bluejays,
  title  = {BLUEJAYS: An Executable Enterprise-Database Environment Suite
            for Text-to-SQL Agents},
  author = {Tai, Betty},
  institution = {1 Digital Design},
  year   = {2026},
  note   = {Version 1.0. github.com/bearresearchlabs-showcase/bluejays;
            formerly the `db' engagement corpus.}
}
```

## References

- Yu, T., et al. (2018). *Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task.* EMNLP.
- Li, J., et al. (2023). *Can LLM Already Serve as a Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs (BIRD).* NeurIPS.
- Lei, F., et al. (2024). *Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows.* arXiv:2411.07763.
- Kaelbling, L. P., Littman, M. L., & Cassandra, A. R. (1998). *Planning and acting in partially observable stochastic domains.* Artificial Intelligence 101.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction.* MIT Press.

---

**Last Updated:** 2026-08-06

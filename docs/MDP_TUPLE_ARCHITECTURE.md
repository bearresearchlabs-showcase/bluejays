# The MDP Tuple Architecture: From "Just Source Databases" to an RL Environment Factory

**A narrative and formal account of what this corpus is, why it has the shape it has, and where it sits between classic Text2SQL benchmarks and frontier agentic evaluation.**

---

## Executive Summary

The engagement ask was database sourcing: *"Acquire real-world databases and accompanying query notebooks to support downstream evaluation and training"* — estimated at *"10 databases = 8-12 hours of work"* ([.cursor/rules/project-requirements.mdc](../.cursor/rules/project-requirements.mdc)). What shipped is not a pile of databases. It is a reinforcement-learning environment suite whose every artifact maps onto an element of a Markov Decision Process tuple — a mapping this repo has been writing, field by field, without ever naming it. This document names it.

| Metric | Value | Source |
|--------|-------|--------|
| Working corpus | 16 databases (db-1 … db-16), PostgreSQL; 480 gold pairs (30 per DB) | [docs/ROADMAP.md](ROADMAP.md) §1; `bird_export/all_bird.json` (`count: 480`) |
| **Shipped client package** | **13 databases (db-2, db-3, db-6 … db-16), 390 pairs, 19.4 GB generated data** | [docs/provenance/](provenance/README.md), verified 2026-08-05 |
| Bulk data tracked | ~14 GB via Git LFS (14 of 16 `data_large.sql`; db-9/db-16 exceed the LFS limit and ship out-of-band). Rows are generated to a ~1 GiB floor; schemas/semantics are real-modeled — see Act VI | `.gitattributes`, `.gitignore`; [provenance STORY.md §7, §10](provenance/STORY.md) |
| Live environment instances | 16 hardened PostgreSQL containers, host ports 5436–5451 | `docker/docker-compose.hardened.yml` |
| Gold-action feasibility | 300/300 queries pass in the documented run (db-6 … db-15, 2026-02-08) | [notebooks/TEST_RESULTS_SUMMARY.md](../notebooks/TEST_RESULTS_SUMMARY.md) |
| Benchmark exports | 23 JSON files: BIRD, BIRD-CRITIC, workbench formats | `bird_export/` |
| Contamination status | Private, non-webcrawlable content by rule; schemas modeled on real systems; shipped rows synthetic (see Act VI) | `.cursor/rules/project-requirements.mdc`; [provenance STORY.md §10](provenance/STORY.md) |

The claim of this document, stated once and defended below: **the corpus is a private, contamination-free POMDP environment suite for text-to-SQL agents, positioned between BIRD (whose annotation schema it is a superset of) and Spider 2.0 (whose agentic, long-horizon demands its roadmap targets). No Spider 2.0 integration exists in this repository today — that absence is part of the story, not a footnote.**

Two scopes run through this document and are kept distinct throughout: the **working corpus** (16 databases / 480 pairs, this repository) and the **shipped client package** (13 databases / 390 pairs, delivered March 2026 and forensically documented in [docs/provenance/](provenance/README.md)). Act VI tells the provenance story and corrects earlier claims where the shipped evidence demanded it.

---

## Act I — The Ask

The project requirements open with a single sentence of scope:

> *"Acquire real-world databases and accompanying query notebooks to support downstream evaluation and training. All assets must reflect authentic, real-world usage (no synthetic datasets, no synthetic queries)."*
> — `.cursor/rules/project-requirements.mdc:5`

The workload estimate that framed the engagement:

> *"10 databases = 8-12 hours of work (per expert consultant)"*
> — `.cursor/rules/project-requirements.mdc:434`

But the hard requirements attached to that "simple" ask are anything but simple:

| Requirement | Source line | What it actually implies |
|-------------|-------------|--------------------------|
| "Absolutely zero synthetically generated data" | `project-requirements.mdc:18` | Real provenance chains, extraction logs, forensic validation ("if curve fitting is too clean, that indicates synthetic data", `:417`) |
| "Databases must NOT be publicly available (not on GitHub, not webcrawled/scraped)" | `:19-20` | The corpus is **contamination-free by construction** — it cannot be in any model's pretraining data, which is precisely the property public benchmarks lose the day they are published |
| "Minimum of 30 extremely complex queries" per database | `:110` | A curriculum of gold actions, not a schema dump |
| Queries "can be linked/chained together to create complex workflows" | `:121, :172-184` | Multi-step episode structure, specified before anyone said "episode" |
| Queries "modelable as nodes in an undirected graph and reducible using shortest path algorithms" (Dijkstra, Bellman-Ford, Floyd-Warshall) | `:123, :190-224` | A transition structure over the action space |

Read carefully, the ask was never "just source databases." The requirements describe the raw material of a training environment. The rest of the repo is what it takes to actually build one.

---

## Act II — What Shipped

### The portfolio

Sixteen production-domain PostgreSQL databases (full table in [docs/ROADMAP.md](ROADMAP.md) §1):

| ID | Domain | ID | Domain |
|----|--------|----|--------|
| db-1 | Chat Messaging Platform (aircraft time-series) | db-9 | Shipping Intelligence (postal/ZCTA) |
| db-2 | Filling Station Retail | db-10 | Marketing Intelligence |
| db-3 | Hierarchical Orders | db-11 | Parking Intelligence |
| db-4 | SharedAI Models | db-12 | Credit Card & Rewards Optimization |
| db-5 | POS Retail | db-13 | AI Benchmark Marketing |
| db-6 | Weather Consulting Insurance (PostGIS/NEXRAD) | db-14 | Cloud Instance Cost |
| db-7 | Maritime Shipping Intelligence (AIS) | db-15 | Electricity Cost & Solar Rebate |
| db-8 | Job Market Intelligence | db-16 | Flood Risk Assessment (PostGIS) |

### The infrastructure around it

- **480 gold pairs** exported in BIRD format (`bird_export/all_bird.json`), plus BIRD-CRITIC task formats and a workbench adapter report — 23 JSON files total.
- **16 hardened PostgreSQL containers** (`docker/docker-compose.hardened.yml`, host ports 5436–5451), one isolated environment instance per database, plus K8s validation jobs (`k8s/`).
- **~14 GB of bulk data** tracked via Git LFS — generated to a ~1 GiB-per-database floor over real-modeled schemas (see Act VI for the provenance of the rows vs. the schemas).
- **Validation harnesses**: per-database query-testing notebooks (`notebooks/`), a 4-phase validation suite, integrity hashes (`source/db-N/metadata/integrity.json`), and a metadata schema that includes — note the field name — `rl_ready: boolean` (`scripts/db_metadata_schema.yaml:19`).
- **Five applications** (ingest, web documentation, annotator, backend test API, sources API) and a deployed documentation site.

An 8-12 hour sourcing task does not produce an `rl_ready` flag. The engagement record shows this scope drew criticism — "overengineering," "a cost center." Act III is the answer to that criticism.

---

## Act III — The Tuple Nobody Named

Here is the discovery this document is built on. The MDP framing was not imposed on this corpus after the fact. **The repo has been writing it all along, in three separate places, without ever using the words "MDP" or "Markov"** (a claim you can verify: neither word appears anywhere else in this repository).

**Exhibit 1** — [client/README.md](../client/README.md), whose audience line reads *"ML research engineers and technical practitioners building reinforcement learning (RL) environments for text-to-SQL data agents"* (`:3`), instructs:

> *"2. **Define your RL environment** — Use `question` as the user utterance (state/observation), `sql` as the gold action, and `description` + `evidence` + `DOCUMENTATION/README.md` as context for the policy.*
> *3. **Execute and reward** — Run agent-generated SQL against PostgreSQL […]. Use execution success, result correctness, or similarity to gold SQL as reward signals."*
> — `client/README.md:14-15`

**Exhibit 2** — [template/queries.md](../template/queries.md) §"Training Data Field Definitions" (`:47-92`) groups every field by *"their role in the training loop and their benchmark alignment"*, splits them into **BIRD-SQL Standard Fields** and **Training Extension Fields**, and closes with a literal pipeline diagram:

```text
TRAINING PIPELINE:

  1. INPUT PROMPT       → question + schema_context + evidence
     (what the agent sees at inference time)

  2. GOLDEN OUTPUT      → SQL
     (what the agent must learn to produce)

  3. REWARD SIGNAL      → expected_output
     (execution match confirms the generated SQL is functionally correct)

  4. CURRICULUM CONTROL → difficulty + query_category + tables_used
     (ensures balanced training across skill levels and SQL patterns)

  5. EVALUATION         → tables_used for schema-linking accuracy
                        → expected_output for execution accuracy (EX)
                        → SQL for exact-match accuracy (EM)
```

**Exhibit 3** — [client/doc/README.md](../client/doc/README.md) states the interaction dynamics in one line:

> *"**Agentic loop:** Plan → Act (run SQL) → Observe → Reflect (verify) → Iterate"*
> — `client/doc/README.md:80`

State. Action. Reward. Transition loop. Curriculum. All specified, none named. The "overengineering" was the minimum viable structure of an RL-grade corpus — which happens to be exactly the product category AfterQuery markets as its frontier-lab differentiator ("RL Environments," "MCP-based Evaluation" — `afterquery-battlecard.html`).

---

## Act IV — The Formalism

### Definition

A Markov Decision Process is the tuple **(S, A, P, R, γ)** (Sutton & Barto, 2018). Because the agent here observes a *task*, not the full database state, the honest formalism is a **POMDP (S, A, P, R, γ, Ω, O)** (Kaelbling, Littman & Cassandra, 1998), with observations Ω and observation function O. This corpus instantiates it as follows.

An **episode** is one (db_id, question) pair. The corpus contains **480 episodes across 16 environment instances**.

| Element | Instantiation | Corpus field(s) | Citation |
|---------|---------------|-----------------|----------|
| **S** — state | (fixed database instance for the episode, natural-language task, interaction history) | `db_id` + live PostgreSQL instance | `template/queries.md:56`; `docker/docker-compose.hardened.yml` |
| **Ω, O** — observation | The agent does **not** see full database state. It observes the question, a per-query schema subset, and domain evidence. Partial observability is deliberate: `schema_context` *"simulates real-world partial-schema retrieval where the agent does not see the full database DDL"* | `question`, `schema_context`, `evidence` | `template/queries.md:58, :60, :69`; `client/README.md:14` |
| **A** — action | Executable PostgreSQL statements. The gold action a* is the annotated SQL | `sql` / `SQL` | `client/README.md:14`; `template/queries.md:59` |
| **P** — transition | Degenerate one-step today: execute, observe result, episode terminates. The documented agentic loop (Plan → Act → Observe → Reflect → Iterate) defines the multi-step extension, where observation history evolves over a stationary read-only database | container execution; loop spec | `client/doc/README.md:80` |
| **R** — reward | Execution success + result-set match against `expected_output` (execution accuracy, EX); gold-SQL match (EM) as a secondary signal | `expected_output` | `template/queries.md:70, :83-84, :89-91`; `client/README.md:15` |
| **γ** — discount | Irrelevant at horizon 1. Becomes meaningful (γ < 1 pricing each exploration step) only at the multi-step horizons in the roadmap | — | — |
| *Curriculum (outside the tuple)* | Difficulty-based sampling and skill coverage — training-distribution control, not MDP structure | `difficulty`/`complexity`, `query_category`, `tables_used` | `template/queries.md:61, :67-68`; `client/README.md:80` |

Two elements of this table deserve emphasis because they are claims about *design intent*, both verifiable in the artifacts: partial observability is engineered (not an accident of missing documentation), and P is trivial *today* — this document does not decorate the current single-turn corpus with sequential structure it does not yet have.

### Environment soundness — evidence

An MDP is only useful if its reward function is well-defined and its gold actions feasible. The evidence:

| Claim | Artifact | Status |
|-------|----------|--------|
| Gold actions are executable | `notebooks/TEST_RESULTS_SUMMARY.md`: 300/300 queries pass (db-6 … db-15, run of 2026-02-08) | ✅ Verified for 10 of 16 DBs in the documented run |
| Environment instances are reproducible | `docker/docker-compose.hardened.yml`: 16 containers, ports 5436–5451; `client/scripts/setup_docker.sh` | ✅ Verified (16 services in compose) |
| Episodes are exportable in benchmark format | `bird_export/all_bird.json`: 480 entries | ✅ Verified |
| Content is private and non-webcrawlable (contamination-free) | `.cursor/rules/project-requirements.mdc:18-22`; per-DB `source_metadata.json` extraction histories; integrity hashes | ✅ By construction and by rule |
| Schemas and query semantics are grounded in real systems | [provenance STORY.md §5, §10](provenance/STORY.md): purpose-built to mirror named commercial products, fed by public/government data models | ✅ Verified |
| Shipped bulk rows are real production data | [provenance STORY.md §6.5, §7, §10](provenance/STORY.md): rows generated by `generate_large_dataset.py` to a ~1 GiB floor | ❌ **Synthetic — corrected in Act VI** |
| Agentic mount works end-to-end | `scripts/agentic_mount.py` (`get_bird_pairs()`); `tests/features/agentic_data_agent_mount.feature` | ✅ Specified and tested at the interface level |
| Gold queries execute on fresh instances (this run) | [`results/gold_query_execution_20260805.json`](../results/gold_query_execution_20260805.json); method in [TECHNICAL_EXECUTION.md](TECHNICAL_EXECUTION.md) §2 | ✅ **288/480 pass live** (schema-only, vanilla PG 16; 9 DBs at 30/30; 6 DBs PostGIS-blocked; db-8 blocked by a real schema defect) |

### Caveats — read before citing this document

Honesty is load-bearing here; a technically literate reader will check.

1. **The workbench "pass" is vacuous.** `bird_export/bird_workbench_report.json` reports 30/30 passed, accuracy 1.0 — but every one of the 30 results is marked `"skipped": true`. It was a gates-only run with no live database.
2. **The agentic evaluation loop has never executed.** `bird_export/bird_critic_results_db1.json`: 3 tasks, 0 passed — every task failed with `connection … port 5436 … Connection refused`. The export format is complete and the harness is wired; the loop has not yet closed against a live container.
3. **300/300 ≠ 480/480.** The documented validation run covers db-6 … db-15. The corpus-wide 480 pairs are exported, not all covered by that run's evidence. The provenance package adds a sharper version of this caveat: the shipped audits ran against small seed datasets, not the gigabyte `data_large.sql` files — syntax and execution were validated, correctness-at-scale was not ([STORY.md §6.4](provenance/STORY.md)).
4. **`client/README.md` cites ports 5436–5448** (a 13-DB-era remnant); the compose file, which is authoritative, maps 5436–5451.
5. **In the shipped package, `complexity` carries no signal** — constant `"moderate"` across all 390 items ([STORY.md §6.3](provenance/STORY.md)). The curriculum row in the tuple table above therefore describes the *design*, not the shipped labels; difficulty must be derived from the SQL itself (CTE depth, joins, window functions, schema breadth 3–34 tables). Artifact revisions differ: the db-6 web deliverable JSON carries 28 moderate / 2 challenging.
6. **1,053 near-duplicate query pairs** at ≥0.99 normalized similarity in 8 of 13 shipped databases ([STORY.md §6.2](provenance/STORY.md)); db-6, db-7, db-8, db-9, db-15 are clean. Deduplicate before training or the effective action distribution is far narrower than 30 per database.
7. **`expected_output` is prose, not rows** — a description of the result shape, not an executed result set ([STORY.md §11](provenance/STORY.md)). The EX reward defined in Act IV must be *materialized*: load schema + data, execute the gold SQL, persist real rows. This is roadmap item P0 — **partially closed on 2026-08-05**: all 480 gold queries were executed against fresh schema-only vanilla-PostgreSQL instances (288 pass; 6 spatial DBs need PostGIS; db-8/db-10 carry a real `VARCHAR(16777216)` schema defect). Method, results, and defect ledger: [TECHNICAL_EXECUTION.md](TECHNICAL_EXECUTION.md).

---

## Act V — Benchmark Lineage: Between Text2SQL and Spider 2.0

### The lineage

Text-to-SQL evaluation has moved through three regimes:

1. **Spider 1.0** (Yu et al., 2018) — single-turn question → SQL over modest schemas; exact-match era. Modern systems exceed ~90% on it; it no longer discriminates.
2. **BIRD** (Li et al., 2023) — introduced the `evidence` field (external/domain knowledge) and **execution accuracy (EX)** as the primary metric, over larger, dirtier databases.
3. **Spider 2.0** (Lei et al., 2024, *"Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows"*) — ~632 real enterprise workflow tasks over BigQuery/Snowflake/DuckDB/PostgreSQL, schemas past 1,000 columns, multi-step **agentic** solving (explore the DB, read documentation, iterate). State-of-the-art success rates fall to roughly 20-30%. This is the frontier.

This repo already contains its own benchmark self-positioning, buried in an Excel generator: `scripts/program_economics.py:477-489` maps every deliverable field to its BIRD/Spider analogue (`description` → *"BIRD: question / Spider: question"*, `sql` → *"BIRD: SQL / Spider: query"*, `evidence` → *"BIRD: evidence"*, …). The manifest (`apps/ingest/lib/sources-manifest.json`, `_field_definitions`) does the same split as "BIRD-SQL standard" vs. "Training extension", and aligns `evidence` with LiveSQLBench's `external_knowledge`. What no artifact does is place the corpus on the third axis — the agentic one. That is done here:

### Positioning table

| Dimension | Spider 1.0 (2018) | BIRD (2023) | **This corpus (2026)** | Spider 2.0 (2024) |
|-----------|-------------------|-------------|------------------------|-------------------|
| Turn structure | Single-turn | Single-turn | Single-turn gold, with agentic-loop scaffolding specified | Multi-step agentic workflows |
| External knowledge | — | `evidence` | `evidence` + `description` + per-DB documentation | Dispersed project docs the agent must find |
| Primary metric | Exact match (EM) | Execution accuracy (EX) | EX vs. `expected_output`, EM secondary | Task success |
| Schema scale | Modest | Large | 1–34 tables/DB; up to 707 documented columns (db-6) | 1,000+ columns |
| Dialects | SQLite | SQLite | **PostgreSQL only** — stated plainly | BigQuery, Snowflake, DuckDB, PostgreSQL |
| Observability | Full schema | Full schema | **Partial by design** (`schema_context`) | Partial by reality |
| Contamination | Public since 2018 | Public since 2023 | **Private, non-webcrawlable by rule** | Public tasks; enterprise DBs semi-private |
| Live environment | No | No | **Yes** — 16 containers | Yes |

The corpus's distinctive combination: **BIRD-superset annotation, live execution environments, engineered partial observability, and contamination-free provenance** — the last being the property no public benchmark can retain after release, and the reason the "must not be webcrawlable" sourcing rule was worth its cost.

**What this corpus is not, today:** multi-dialect, multi-database-per-task, long-horizon, or ambiguous-by-design. It contains **zero Spider 2.0 references** — the term appears nowhere in this repository before this document, and no integration exists. The gap is the roadmap.

---

## The 16 Databases as an Environment Suite

What each database contributes to the suite is *domain* structure — the thing that makes gold SQL require external knowledge:

- **Spatial reasoning environments**: db-6 (PostGIS weather/NEXRAD/insurance — 34-table source schema), db-7 (AIS maritime), db-16 (flood risk) — geography, projections, spatial joins.
- **Time-series and windowing**: db-1 (aircraft telemetry), db-14/db-15 (cost curves) — window frames, gap detection, rolling statistics.
- **Hierarchies and graphs**: db-3 (recursive order trees), db-8 (occupational taxonomies) — recursive CTEs.
- **Transactional/financial logic**: db-2, db-5, db-9, db-10, db-11, db-12 — reconciliation, cohort math, rate optimization.
- **Self-reference**: db-13 is a database *of AI benchmark results* — a benchmark environment about benchmarks.

Diversity here is of domain, not dialect: every environment speaks PostgreSQL. That is a genuine limitation against Spider 2.0's multi-dialect demand, and it is listed as such below.

---

## Honest Gaps and the Road to Spider2-Grade

| Verified today | Spider2-grade requires (forward-looking) |
|----------------|------------------------------------------|
| Single-turn episodes with executable gold actions | Long-horizon, multi-step episodes with intermediate observations |
| One database per episode | Cross-database workflow tasks |
| PostgreSQL only | Multi-dialect (BigQuery, Snowflake, DuckDB) |
| Well-posed questions with gold answers | Ambiguous/underspecified tasks requiring clarification or exploration |
| Evaluation harness wired but **never executed live** (CRITIC 0/3 connection-refused; workbench all-skipped) | A closed agent-evaluation loop with reported success rates |
| Documentation as policy context | Dispersed docs the agent must *choose* to consult |

**The seeds are already planted, in the original requirements themselves:**

- Query **chaining** — *"one query's output feeds into another query's input"* (`project-requirements.mdc:172-184`) — is the multi-step episode, specified in 2026 before anyone named it.
- The **query graph** — queries as nodes, reducible via Dijkstra/Bellman-Ford/Floyd-Warshall (`:190-224`) — is a transition structure over the action space, waiting to be executed rather than described.
- `scripts/agentic_mount.py` and the BDD feature spec already define the environment-mount interface an agent harness needs.

### Roadmap

| Priority | Work | Success criterion |
|----------|------|-------------------|
| **P0** | Close the loop: run the BIRD-CRITIC / workbench harness against the live containers (fix the 0/3). **Partially closed 2026-08-05** — 288/480 gold queries executed live on fresh vanilla-PG instances ([TECHNICAL_EXECUTION.md](TECHNICAL_EXECUTION.md) §2); remaining: PostGIS instance for 6 spatial DBs, data-at-scale, result-set materialization | A report with real (non-skipped) per-task pass/fail against ports 5436–5451 — first artifact: `results/gold_query_execution_20260805.json` |
| **P1** | Compose chained queries into multi-step episodes using the specified query graph | ≥1 database with N-step episodes and per-step rewards |
| **P2** | Cross-database workflow tasks (the suite already shares domain seams: weather ↔ flood ↔ maritime) | Episodes whose gold trajectory touches ≥2 environments |
| **P3** | Dialect expansion (per ROADMAP §12's "Optional Snowflake/BigQuery") and ambiguity injection | Corpus entries with under-specified questions + clarification turns |

This roadmap extends [docs/ROADMAP.md](ROADMAP.md) Epic 5 (LiveSQLBench) and §3.3 (BIRD Benchmark); the knowledge-graph track ([docs/BIRD_KNOWLEDGE_GRAPH.md](BIRD_KNOWLEDGE_GRAPH.md), arXiv 2311.07509) is complementary policy-context work.

---

## Act VI — Provenance: What Actually Shipped

*Source for this entire act: the [provenance package](provenance/README.md), whose every figure was recomputed from the shipped files on 2026-08-05. Where this act corrects earlier sections, the shipped evidence wins.*

### The timeline behind the tuple

The engagement's arc, from [provenance STORY.md](provenance/STORY.md) and [story-timeline.json](provenance/story-timeline.json):

| Date | Event |
|------|-------|
| 2025-09-17 | Intake: a *coding-agent evaluation* rubric — 9 scoring dimensions, 16-code failure taxonomy. The buyer's bar was structured judgment from day one |
| 2025-10-29 | NDA + Data Submission Agreement execute together — the expert *submits* data; ownership had to be contracted |
| 2026-02-01–09 | Apprentice deliveries establish the house format: `database/ + documentation/ + README + one-command bring-up`, then the Description/SQL/Expected-Output triad |
| 2026-02-14 | Statement of Work: positioned explicitly against **BIRD-SQL / LiveSQLBench**; 11 databases, Full-Service tier |
| 2026-02-18 | **Industrialization day**: 9 schemas at 06:54, all 13 documentation sets at 17:39, all 13 gigabyte datasets written inside a two-minute window at 19:19–19:20 |
| 2026-03-09 | `client-db.zip` ships: 13 databases, 390 pairs, 21.5 GB extracted |
| *undated* | Client feedback: *"Databases look good, only comment: the descriptions are AI-generated"* → active remediation ([REMEDIATION.md](provenance/REMEDIATION.md)) |
| 2026-08-05 | Provenance reconstruction; every claim measured against the shipped files |

### The provenance pivot — the story's honest core

The first five databases were **exports of real production systems** (a live ADS-B receiver, a Kenyan POS instance, live Django/Supabase apps). Maximum authenticity, maximum provenance risk. From db-6 onward the method inverted: databases **purpose-built to mirror named commercial products** (Linescape, jobright.ai, Pirate Ship, Brickseek, SpotHero, CardPointers, Artificial Analysis), populated from public and government sources (NOAA, USCG, BLS, USPS, Census, FEMA, NIST). db-1, db-4, db-5 were cut, not failed — their audits pass; they were never migrated to the new method ([STORY.md §5](provenance/STORY.md)).

The materially honest statement about the data, from [STORY.md §10](provenance/STORY.md), quoted because it corrects this document's own earlier drafts: *"No row of shipped data is real production data; no schema is arbitrary."* Rows were generated (`generate_large_dataset.py`, ~1 GiB floor per database — twelve of thirteen files land within kilobytes of exactly 1 GiB); schemas and query semantics are the real-modeled parts. For the MDP framing this means: **the environment's transition dynamics (schema, constraints, SQL semantics) are grounded; its state distribution is synthetic.** Conclusions about real-world data distributions do not transfer; conclusions about SQL competence over realistic schema structure do.

### The feedback loop as reward signal

The client's one-sentence review — *"the descriptions are AI-generated"* — is, in this document's own vocabulary, a **reward signal on the annotation policy**, and the provenance package did the right thing with it: measured it (mean description length 193 chars; 0/390 descriptions name user intent; the 1,053 near-duplicates are the objective form of the same finding) and converted it into a bounded work order with acceptance criteria ([REMEDIATION.md](provenance/REMEDIATION.md)). The recoverable asset: four-lens intent documentation (Use Case / What it does / Business Value / Purpose) already exists in the working tree for 11 of 13 shipped databases — remediation is recovery plus editing, not authoring ([STORY.md §15](provenance/STORY.md)).

### Frontier context — how frontier was this, actually

On **February 5, 2026**, OpenAI announced **Frontier**, its enterprise platform for building and managing AI agents — agents onboarded and managed "the same way companies manage human employees," with feedback loops for improvement. Meta Superintelligence Labs spent 2026 training its Muse model line specifically for agentic capability. That is the market moment this engagement sits inside: the SOW positioning the work against BIRD-SQL/LiveSQLBench predates the Frontier announcement by nine days in the artifact record's framing week (SOW 2026-02-14; industrialization 2026-02-18), and the corpus's design center — **private, contamination-free environments with gold actions, executable reward, and curriculum structure for training and evaluating data agents** — is precisely the substrate the frontier-agent category consumes.

Three sober observations, in the package's own plain register:

1. **The architecture anticipated the category.** An engagement scoped as data sourcing produced, by February 2026, the environment structure (state/action/reward/curriculum, live instances, benchmark alignment) that frontier-agent platforms announced that same month now presuppose. That is the substantive sense in which the architecture was frontier — contemporaneous with, not derivative of, the platform wave.
2. **The strategic gap the record itself names is the frontier gap.** The Slack record's counter-position ([sources/keeping-track-of-things.txt](provenance/sources/keeping-track-of-things.txt)): a language model cannot certify that data is good for training — that takes execution-accuracy harnesses, ablations against BIRD/Spider, downstream product metrics. Closing that gap (roadmap P0) is what converts a data vendor into infrastructure for frontier agents.
3. **No client identity is asserted here.** This repository's documents refer to the engagement's counterparties as they appear in the artifacts. The frontier-agent context above cites public announcements only.

---

## Companion Artifacts

- **Stakeholder showcase (this repo):** [`mdp-tuple-architecture.html`](../mdp-tuple-architecture.html) — the story version, dark-theme single file.
- **Worked example (this repo):** [`mdp-architecture-db6.html`](../mdp-architecture-db6.html) — one full db-6 episode (Query 26, NEXRAD storm-cell tracking) rendered as observation → gold action → reward target. Originally deployed from the `db-6-weather-documentation` repository; consolidated here 2026-08-05.
- **Provenance package (this repo):** [`docs/provenance/`](provenance/README.md) — the forensic record of what shipped, and the authority this document defers to on shipped figures.
- **Technical execution record (this repo):** [`docs/TECHNICAL_EXECUTION.md`](TECHNICAL_EXECUTION.md) — the factory inventory, the industrialization timeline, and the first genuinely closed execution loop (2026-08-05: 288/480 live), with defect ledger and a design brief for the styling pass.

---

## References

- Yu, T., et al. (2018). *Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task.* EMNLP 2018.
- Li, J., et al. (2023). *Can LLM Already Serve as a Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs (BIRD).* NeurIPS 2023.
- Lei, F., et al. (2024). *Spider 2.0: Evaluating Language Models on Real-World Enterprise Text-to-SQL Workflows.* arXiv:2411.07763.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.
- Kaelbling, L. P., Littman, M. L., & Cassandra, A. R. (1998). *Planning and acting in partially observable stochastic domains.* Artificial Intelligence, 101(1-2).
- Sequeda, J., et al. (2023). *A Benchmark to Understand the Role of Knowledge Graphs on Large Language Model's Accuracy for Question Answering on Enterprise SQL Databases.* arXiv:2311.07509.
- TechCrunch (2026-02-05). *OpenAI launches a way for enterprises to build and manage AI agents* — the OpenAI Frontier platform announcement. https://techcrunch.com/2026/02/05/openai-launches-a-way-for-enterprises-to-build-and-manage-ai-agents/
- Provenance package (2026-08-05). [docs/provenance/](provenance/README.md) — STORY.md, story-timeline.json, REMEDIATION.md; all shipped-package figures re-verified from the delivered files.

---

**Last Updated:** 2026-08-05 (rev. 2 — provenance package incorporated, shipped-scope corrections, frontier context)

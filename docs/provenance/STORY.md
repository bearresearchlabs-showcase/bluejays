---
title: How These Databases Came To Be
description: Provenance narrative for the 13-database BIRD-style text-to-SQL package — from sales intake through delivery.
audience: engineering retrospective · client case study · research methods note
status: reconstructed from artifacts, February 2026 – March 2026
last_verified: 2026-08-05
---

# How These Databases Came To Be

*From sales intake to thirteen shipped databases.*

This document reconstructs the origin of the package in this repository: **13 databases,
390 question–SQL pairs, 19.4 GB of generated data**, built for text-to-SQL / BIRD-style
RL environment work.

Everything below is reconstructed from artifacts on disk — executed agreements, onboarding
documents, a statement of work, working-tree audit reports, file timestamps, and the shipped
files themselves. Where the artifacts do not support a claim, the document says so rather
than filling the gap. Section 6 lists what the evidence *does not* show.

It is written in three registers, because three audiences need it:

| Part | Register | For |
| --- | --- | --- |
| **I** | Case study | Clients and partners — what was built and why it holds up |
| **II** | Retrospective | The build team — what actually happened, including what broke |
| **III** | Methods note | ML research engineers — data provenance, for anyone training on this |
| **IV** | Feedback loop | The account — what the client said, measured, and what to do next |

---

## Part 0 — The Shape of It

Before the story, the object. Thirteen databases shipped, numbered non-contiguously —
**db-2, db-3, db-6 through db-16**. The gaps are not accidents. They are the plot.

| DB | Domain | Tables | FKs | Idx | Queries |
| --- | --- | ---: | ---: | ---: | ---: |
| db-2 | Filling Station Retail / POS | 7 | 7 | 0 | 30 |
| db-3 | Hierarchical Orders (LinkWay) | 3 | 4 | 6 | 30 |
| db-6 | Weather Data Pipeline System | 34 | 14 | 44 | 30 |
| db-7 | Maritime Shipping Intelligence | 14 | 0 | 36 | 30 |
| db-8 | Job Market Intelligence | 12 | 11 | 30 | 30 |
| db-9 | Shipping Intelligence | 14 | 21 | 14 | 30 |
| db-10 | Marketing Intelligence | 12 | 11 | 30 | 30 |
| db-11 | Parking Intelligence | 14 | 18 | 19 | 30 |
| db-12 | Credit Card & Rewards Optimization | 15 | 28 | 32 | 30 |
| db-13 | AI Benchmark Marketing | 11 | 10 | 23 | 30 |
| db-14 | Cloud Instance Cost | 11 | 18 | 16 | 30 |
| db-15 | Electricity Cost & Solar Rebate | 17 | 29 | 29 | 30 |
| db-16 | Flood Risk Assessment (M&A DD) | 12 | 0 | 24 | 30 |
| | **Total** | **176** | **171** | **303** | **390** |

Every database ships the same four-part bundle: `DATABASE/` (schema + data),
`QUERIES/` (authored markdown + extracted JSON), `DOCUMENTATION/` (schema and data
dictionary), and a `vercel.json`. Uniformity was the product. Getting to uniformity
was the work.

---

## Part I — The Case Study

### 1. Intake: five months before a single table existed

The engagement did not begin with a database. It began with a rubric.

**September 17, 2025.** A requirements document arrives —
`[AfterQuery] Code Eval Requirements`. It has nothing to do with SQL. It is a spec for
evaluating *coding agents*: author a prompt on a "0-1 full-stack development theme,"
run two models against it, score nine dimensions (`Context Awareness`, `Instruction
Following`, `Tool Use`, `Planning`, `Error Recovery and Debugging`, `Code Quality`,
`Transparency and Explainability`, `Agent Initiative`, `User Experience and Trust`),
and tag failures from a fixed 16-code taxonomy — *at the correct turn*.

This document matters to the story not for its subject but for its posture. It
established, at intake, that the buyer's quality bar was **structured judgment**, not
volume. Five prompt-admission gates. Explicit bad examples ("Write a haiku about
servers." ❌ Not in any coding category). A standing instruction against thin work:
*"Avoid giving one sentence rationale with minimal context."*

**October 29, 2025.** Two agreements execute together — an **NDA** and a **Data
Submission Agreement**. The pairing is the tell. This is not a labeling gig where the
buyer supplies the data; it is a program where the expert *submits* data, and the
contract has to say who owns what.

**November 20–29, 2025.** Counterparty diligence runs in the other direction: a
Crunchbase company profile and funding history is pulled on the buyer, alongside their
financial-details and privacy documents. Before scaling delivery, the vendor checked
whether the customer could pay and would persist.

**January 14 and January 17, 2026.** Two project onboarding documents — **Project
Excel**, then **Project Green**. They are the same Google Doc with the name changed;
the Green document still asks for *"quality Excel experts."* Eight onboarding steps:
join Slack → log into the platform → sign the two legal documents → connect Stripe as
an **Individual** with the product description *"AfterQuery Expert - Data Annotator"* →
finish training → ping your administrator. Time tracked in Hubstaff. Pay rate stated
nowhere — deferred to a per-project instruction sheet, and *approval-gated*: "if your
work is approved, then you will be paid."

Enforcement was reputational and binary. *"Admins can and will remove those who
consistently submit low quality work... Repeated offenders will be removed from projects
and/or banned."*

That is the intake funnel: **public recruiting → verification → self-serve contracting →
a reused onboarding template → a human on Slack who DMs you the real spec.** An expert
network optimizing for throughput, gating on output quality rather than input credentials.

### 2. The apprentice deliveries

**February 1–2, 2026.** Two deliveries land, and they are the hinge of the entire story.

`AfterQuery_final_delivery_food_delivery_db.zip` — eight files, 307 KB:

```
README.md
docker-compose.yml
check-database.ps1
database/schema.sql
database/data.sql
database/full_dump.sql
documentation/SCHEMA.md
documentation/DATA_DICTIONARY.md
```

And `AFTERQUERY-20260202T192519Z-3-001.zip` — the same skeleton at 8 MB, with a
`DATABASE_README.md`.

Small deliveries. But look at the shape: **database/ + documentation/ + a README + a
one-command bring-up.** That is the pattern that would be run thirteen times. The
apprentice work was not just work — it was the specification, learned by doing it.

**February 9, 2026.** `SQL Queries_AfterQuery.docx` — thirty annotated queries against an
inter-agency messaging schema (Keycloak IDs, agencies, groups, attachments). Each entry
has exactly three parts:

> **Description / Purpose** — what the query is for, in prose
> **SQL** — the query
> **Expected Output** — what the result table should contain

Compare the shipped `queries.json` field set in this repository: `description`, `sql`,
`expected_output`. **The annotation schema is a direct lift from the house style learned
on the client's own work.** Nothing was invented at the schema layer; it was inherited,
then formalized.

### 3. The Statement of Work

**February 14, 2026.** `AQ_Client_SOW_BIRD-SQL.docx`. The consultancy stops being a
participant in someone else's program and becomes a vendor with its own.

The SOW positions the work explicitly against **BIRD-SQL / LiveSQLBench**, and the
value proposition is stated plainly:

> "Text-to-SQL training evaluation annotation is not a commodity data labeling task. It
> requires annotators who can read production SQL, understand the business intent behind
> complex queries, and express that intent in structured formats that AI models can learn
> from. Errors in annotation directly degrade evaluation set quality and, downstream, the
> models trained and evaluated against those datasets."

Two tiers. **Introductory at $2,000/db** — automated parsing, keyword-level tags, single
dialect, no review cycles. **Full-Service at $5,500/db** — expert schema deep-dive,
human-authored intent narratives, BIRD-SQL + RLHF-compliant JSON, 40+ dialect coverage,
QA report, two review rounds. Volume ladder: $5,500 (1–15) → $5,000 (16–50) → $4,500
(51–100) → $4,000 (100+).

The initial engagement: **11 databases, Standard tier, $60,500, 6–8 weeks.** Payment
50/25/25 against execution, Batch 1, and final delivery. Quality floor: ≥95% annotation
accuracy, 100% query coverage, schema compliance validated before delivery.

The Introductory tier is a real product, but its function in the document is rhetorical:
it exists so the Full-Service tier can be measured against it. The SOW then anchors the
number in the market — *"the $3,500 – $8,000 range that domain-expert annotation commands"* —
placing $5,500 defensibly mid-band.

**The engagement scoped 11. Thirteen shipped.** That gap is Part II.

### 4. What was delivered

By March 9, 2026, `client-db.zip` weighs **2,424,282,003 bytes**. Extracted: 21.5 GB
across 97 files. Thirteen databases, 176 tables, 171 foreign keys, 303 indexes, 390
annotated query pairs, each with question, gold SQL, description, evidence,
expected output, and complexity tag.

---

## Part II — The Retrospective

This is the internal version. It is more useful and less flattering.

### 5. The provenance pivot — why db-1, db-4 and db-5 are missing

The first five databases were not built. They were **exported**.

| DB | What it actually was | Source system |
| --- | --- | --- |
| db-1 | Airplane Tracking (ADS-B) | Supabase; Raspberry Pi running `dump1090`, receiver `labgpspi` |
| db-2 | Filling Station POS | PHP Point of Sale instance — a closed family business in Kenya |
| db-3 | LinkWay Ecommerce | Live Django backend export |
| db-4 | Seydam AI | Live Django + Supabase app — `seydam_customuser`, `seydam_payment` |
| db-5 | SharedAI | Live Supabase chat app, project `mwjdnauqugpdagkhzmef` |

These were real production systems with real users. That was the *point* — the buyer
wanted contamination-free data, and nothing is less contaminated than a database no
crawler has ever seen.

One artifact in the working tree marks the moment this got examined:
`db-1/docs/manual-review-checklist.md`. It contains a **Provenance Check** requiring
that the source is *"NOT publicly available on GitHub"* and *"NOT easily
webcrawled/scraped."* Every checkbox in it is unticked.

From db-6 onward the method inverts completely. Databases are **purpose-built to mirror
a named commercial product**, populated from public and government APIs:

| DB | Modeled on | Fed by |
| --- | --- | --- |
| db-6 | — (NOAA pipeline) | NOAA GRIB2, NEXRAD, shapefiles, NWS API |
| db-7 | Linescape | NOAA, US Coast Guard, MARAD |
| db-8 | jobright.ai | USAJobs.gov, BLS, Dept. of Labor |
| db-9 | Pirate Ship | USPS Developer Portal, UPS, Census, Data.gov |
| db-10 | Brickseek | Census MRTS, BLS CPI/PPI, FTC |
| db-11 | SpotHero | municipal / public parking data |
| db-12 | CardPointers | public card and rewards terms |
| db-13 | Artificial Analysis | NIST, NSF, DARPA, Papers with Code, HF, GitHub |
| db-14 | AWS / GCP / Azure pricing | public pricing APIs |
| db-15 | — (utility rates) | US electricity rates, federal/state/utility rebates |
| db-16 | — (flood risk) | FEMA, NOAA, USGS, NASA |

Same evaluation goal, different risk posture: instead of *"here is someone's real
database,"* it became *"here is a faithful reconstruction of a real system's problem
shape, built from data anyone may lawfully use."*

**db-1, db-4 and db-5 did not fail. They were cut.** Their audits pass —
`db1_live_query_audit.json` reports `{"status":"SUCCESS","total_queries":30,"passed":30,
"failed":0}` at a 100% pass rate and 16.25 ms average. All three have complete 30-query
sets. What they lack is everything the new method produced: no `db-N.ipynb`, no
`deliverable.openapi.yaml`, no `data_large.sql`, no web deliverable folder. They were
built under the old method and never migrated.

db-2 and db-3 survived, but only after heavy anonymization. db-3 shipped with its tables
renamed to `table1`, `table2`, `table3` — three tables, no domain vocabulary at all. It is
the most abstract database in the package because it had the most to hide.

**No file in the tree states the reason for the cut.** The reconstruction above is
inference from what the artifacts contain and what they conspicuously lack.

### 6. What the evidence does not support

Honest limitations, all independently verified against the shipped files on 2026-08-05.
Any of these can be fixed; none of them are fixed yet.

**6.1 — The promised notebook does not ship.**
The root `README.md` states the package provides *"a notebook for ingest, validation, and
environment setup."* `find client/ -name '*.ipynb'` returns zero results. The notebooks
exist — `db-N.ipynb`, 26 cells, PostgreSQL install → schema load → data load → execute all
30 → visualize → save results JSON — but only in the working tree, and only for db-6
through db-16. **The client package promises an artifact it does not contain.**

**6.2 — 1,053 near-duplicate query pairs, concentrated in 8 of 13 databases.**
No two queries in any database are byte-identical. But at ≥99% textual similarity after
whitespace and case normalization:

| DB | Near-dup pairs ≥0.99 | Queries involved (of 30) |
| --- | ---: | ---: |
| db-6, db-7, db-8, db-9, db-15 | **0** | 0 |
| db-13 | 57 | 18 |
| db-2 | 50 | 26 |
| db-14 | 80 | 23 |
| db-12 | 136 | 20 |
| db-3 | 141 | 29 |
| db-16 | 167 | 23 |
| db-11 | 210 | 21 |
| db-10 | 212 | 24 |

The five clean databases are not lucky — they are the ones that got a second pass. The
working tree records the moment it was caught: `db-9/results/qc_additional_checks.json`,
timestamped `20260208-2110`, reports `duplicates: {"passed": 15, "failed": 15}` with the
note *"Query 16 appears to be duplicate"* running through Query 30. **db-9 was rewritten
in response and now ships clean. The fix was never propagated to the other eight.**

For an RL environment this matters concretely: a policy trained on db-10 sees 212 pairs of
near-identical gold actions, which inflates apparent competence and narrows the effective
action distribution to well under 30 distinct behaviors.

**6.3 — `complexity` carries no signal.**
All 390 queries are tagged `"moderate"`. The root README offers this field for *"curriculum
or difficulty-based sampling."* It cannot support that use. The SOW's own assumptions
section is consistent — *"Database complexity is estimated at moderate level"* — so this is
a scope statement that was never revisited, not a labeling error. Real difficulty signal is
recoverable from the schemas (3 to 34 tables) and from per-query CTE, join, and window-function
counts already computed in `results/`.

**6.4 — Audits ran against seed data, not shipped data.**
`db9_dq_audit.json` reports 80 total rows across 14 tables. The shipped
`db-9/DATABASE/data_large.sql` is **4.79 GB**. Every performance audit in the tree is
identical: `{"issues":[],"unused_indexes":[],"missing_fk_indexes":[],"cache_hit_ratio":100.0}` —
a perfect cache-hit ratio on an 80-row table is not a finding. `db9_comprehensive_report.json`
reports 30/30 passed at 100% success, with `row_count: 0` on every query. **The queries were
validated for syntax and execution, not for returning correct results at scale.**

**6.5 — Pipeline metadata records intent, not execution.**
`pipeline_metadata.json` lists every configured pipeline with
`status: "Configured"`, `execution_count: 0`, `success_count: 0`, and an empty
`execution_logs` array. The government-API ingest scripts (`ingest_nws_api.py`,
`ingest_geoplatform.py`, `ingest_aws_opendata.py`, `extract_gov_data.py`) exist and are
real. The bulk data that shipped came from `generate_large_dataset.py` — a synthetic row
generator. **The data is synthetic; the schemas and the domain semantics are the parts
grounded in real sources.**

**6.6 — Template leakage.**
`db-9/deliverable.openapi.yaml` still carries db-1's examples: `database_name: db-1`,
`database_type: Chat/Messaging System`, `total_tables: 11`. Cosmetic, but it is a
fingerprint of the same root cause as 6.2 — a template propagated faster than it was
proofread.

**6.7 — One internal report contradicts itself.**
`db-9/results/final_comprehensive_validation_report.json` records `Pass: 1` while its own
phase-2 section logs query 1 failing with `relation "packages" does not exist` and queries
2+ returning `InFailedSqlTransaction`. Its phase-3 block is stamped `"database": "db-6"` with
an empty query array. A copy-paste artifact in the reporting layer, not in the deliverable —
but it means the validation reports cannot be taken at face value without re-running them.

### 7. The 1 GiB tell

Twelve of the thirteen `data_large.sql` files land within a few kilobytes of
**1,073,741,824 bytes** — exactly 1 GiB:

```
db-15  1,073,742,313      db-13  1,073,766,531
db-11  1,073,742,341      db-14  1,079,171,827
db-10  1,073,742,402      db-6   1,076,717,064
db-12  1,073,743,330      db-7   1,077,441,845
db-8   1,073,743,745      db-2   1,080,786,098
                          db-3   1,086,687,152

db-16  2,728,033,725      db-9   4,793,732,133
```

That distribution is a generator writing rows until it crosses a 1 GiB floor, then stopping
at the end of the current statement. Not a coincidence — a spec, enforced by a loop.
The two outliers are the two pathfinders, generated before the floor was standardized.

### 8. February 18, 2026 — the day it became a factory

The timestamps for the final build day tell the story with no narration required:

| Time (UTC) | Event |
| --- | --- |
| 06:54 | 9 schemas written in a single batch |
| 07:03 | db-6 schema consolidated — 43 KB, 34 tables, merged from 4 separate schema files |
| 08:28 | First 5 `queries.json` extracted |
| 17:17 | All 13 `queries.md` regenerated |
| 17:39 | All 13 `DOCUMENTATION/README.md` + remaining `queries.json` + all `vercel.json` |
| 17:47 | db-2 `queries.json` — the last straggler |
| 17:49 | Root `README.md` |
| 19:19–19:20 | All 13 `data_large.sql` generated — 19.4 GB, all written inside a two-minute window |

Nine schemas at 06:54. Thirteen documentation files at 17:39. Thirteen gigabyte-scale
datasets inside a two-minute window. Nothing about that cadence is manual.

The extraction metadata records the same industrialization one step earlier: eleven
`queries.json` files stamped `20260216-2320`, with db-6 re-extracted at `20260217-0009`
and db-16 at `20260217-0146` — two reruns after a batch, exactly where you would expect
them for the two most complex databases.

Every shipped `queries.json` still names its source of record:
`/Users/machine/Documents/AQ/db/source/db-N/queries/queries.md`. **That directory no longer
exists.** The source tree was consolidated after packaging; the working tree survives at
`Downloads/db (1)`, and the delivered package is the only complete copy of what shipped.

### 9. Eleven became thirteen

The SOW dated February 14 scopes **11 databases at $5,500 each — $60,500**. Thirteen
shipped. The artifacts do not record whether the additional two were a change order, a
goodwill inclusion, or the recovery of two databases that had been written off. It is
worth resolving, because at Standard-tier pricing the difference is $11,000.

---

## Part III — The Methods Note

*For anyone building an RL environment on this data.*

### 10. Data lineage in one paragraph

Schemas are hand-authored, modeled on the observable behavior of named commercial systems
(§5) and on public-sector data models. Row data is **synthetic**, produced by
`generate_large_dataset.py`, sized to a ~1 GiB floor per database. Queries are hand-authored
in `queries.md` and mechanically extracted to `queries.json` by `extract_queries_to_json.py`
via `^## Query (\d+):\s*(.+)$`. Documentation is generated from the schema files. No row of
shipped data is real production data; no schema is arbitrary.

### 11. Field semantics, as actually populated

All 390 items carry 8 keys. 150 items (db-6, db-7, db-8, db-13, db-15) carry two more.

| Field | Coverage | What it actually is | Safe use |
| --- | --- | --- | --- |
| `question` | 390/390 | Natural-language user utterance | Observation / intent |
| `sql` | 390/390 | Gold query, PostgreSQL dialect | Imitation target |
| `description` | 390/390 | Business purpose, prose | Policy conditioning |
| `evidence` | 390/390 | Technical reasoning for the approach | CoT / auxiliary loss |
| `expected_output` | 390/390 | **Prose description of the result shape** — not result rows | Reflection signal only |
| `complexity` | 390/390 | Constant `"moderate"` — see §6.3 | **Do not use for curriculum** |
| `number` | 390/390 | 1–30 within each database | Logging / eval keys |
| `line_number` | 390/390 | Offset in the source `queries.md` | Provenance |
| `title` | 150/390 | Short query name | Display |
| `normal_query` | 150/390 | Simplified variant of the gold SQL | Difficulty pairing |

`expected_output` is the field most likely to be misused. It reads like a verification
target and is not one — it is a human description of what the result table should contain.
Any reward function needing exact-match verification must execute the gold SQL against a
loaded instance and capture real rows.

### 12. Recommended handling

1. **Deduplicate before training.** Cluster each database's 30 queries at ≥0.99 normalized
   similarity and keep one representative. Expect roughly 30 distinct behaviors in db-6,
   db-7, db-8, db-9 and db-15, and materially fewer in the other eight (§6.2).
2. **Derive your own difficulty labels.** Compute CTE depth, join count, window-function
   count, and referenced-table count per query. Do not read `complexity`.
3. **Materialize ground truth.** Load `schema.sql` + `data_large.sql`, execute each gold
   `sql`, and persist real result sets. Treat `expected_output` as a description, not an oracle.
4. **Treat the data as synthetic.** Distributional realism was not a design goal; schema
   and query realism were. Conclusions about real-world data distributions do not transfer.
5. **Re-run validation.** The shipped audits were computed against seed data (§6.4) and at
   least one report is internally inconsistent (§6.7).

---

## Part IV — The Feedback Loop

*Source: `Keeping track of things` — a Slack-exported working document, included in this
package at `sources/keeping-track-of-things.pdf`. Meeting dates are not recorded in the
artifact; the sequence is.*

### 13. The client read it first

The package shipped. Then the client read it, and returned one sentence that reframes
everything in Parts I–III:

> **"Databases look good, only comment: the descriptions are AI-generated."**

Not the schemas. Not the SQL. Not the data volume. The *descriptions* — the one field the
Statement of Work priced at **$1,500 per database**, the single line item that justified
Full-Service over Introductory tier. The buyer bought human intent documentation and
received something that read as machine-written.

The relayed to-do list was specific:

- Make the descriptions **100% human-made**
- Descriptions should express **query intent — what the query is aiming to do** — not summarize what the SQL does
- **Longer descriptions, more deeply contextualized**
- Some JSON files **do not match their `.md`** in description and detail
- Specifically flagged: **db-2, db-3, db-6, db-7, db-10** — JSON missing intent/purpose fields
- Client will send a **file format to ingest data**
- Standing concern: **complexity and quality must not diminish as the engagement scales**

### 14. The complaint, measured

Every claim above was checked against the shipped files on 2026-08-05. Four of five are
objectively confirmed; one does not reproduce as stated.

**14.1 — Descriptions are short.** Corpus-wide mean **193 characters** — one to two
sentences per query.

| DB | Mean description | DB | Mean description |
| --- | ---: | --- | ---: |
| db-8 | 138 | db-13 | 198 |
| db-10 | 152 | db-15 | 208 |
| db-7 | 155 | db-2 | 209 |
| db-11 | 166 | db-16 | 216 |
| db-3 | 174 | db-9 | 240 |
| db-14 | 177 | db-12 | 277 |
| db-6 | 197 | | |

**14.2 — Zero of 390 descriptions contain the words "intent" or "purpose."** The field is
uniformly written as *what the query computes*, not *what the user is trying to learn*.
The client asked for the second and received the first, 390 times out of 390.

**14.3 — The `.md` / `.json` mismatch is real and localized to db-2.** `queries.md` is not
a prose document; it is `## Query N` headers wrapping fenced JSON blocks, so the two files
should agree by construction. They do, except:

| DB | Descriptions matching `queries.md` |
| --- | --- |
| db-2 | **18 / 30** — queries 17 and 20–30 diverge |
| db-6, db-11 | 29 / 30 |
| all others | 30 / 30 |

db-2's JSON was edited after its markdown was generated, and the markdown was never
regenerated. Twelve queries out of 390 — small, but exactly the kind of inconsistency that
reads as carelessness to a reviewer already primed to distrust the descriptions.

**14.4 — The near-duplicate finding is the objective form of the complaint.**
Section 6.2 documented **1,053 near-duplicate query pairs** at ≥99% similarity across 8 of
13 databases, found independently before this feedback document was read. That is the
measurable fingerprint of generated-and-not-reviewed content. **The client's impression and
the forensic evidence are the same finding arrived at from two directions.** This is
usable: it converts a subjective accusation into a bounded, countable remediation target.

**14.5 — The flagged five do not separate.** The client named db-2, db-3, db-6, db-7 and
db-10 as missing intent/purpose fields. In the shipped package, *no* database has such a
field — the deficiency is universal, not specific to those five. The most likely reading is
that the complaint refers to an earlier revision, or to the `db-N_deliverable.json` files
(which carry `title`/`description`/`complexity`/`expected_output`/`sql` and drop `question`
and `evidence` entirely). Worth confirming with the client before remediating against the
wrong artifact.

### 15. The regression nobody logged

Here is the part that matters most, and it is good news.

The rich intent documentation **was written.** It exists right now, in the working tree, for
**11 of the 13 shipped databases** — and it never shipped:

| File | Use Case blocks | Business Value | Purpose |
| --- | ---: | ---: | ---: |
| `db-6/db-6.md` | 32 | 30 | 30 |
| `db-7/db-7.md` | 34 | 33 | 30 |
| `db-8/db-8.md` | 93 | 63 | 60 |
| `db-9/db-9.md` | 63 | 33 | 30 |
| `db-10/db-10.md` | 63 | 33 | 30 |
| `db-11/db-11.md` | 63 | 33 | 30 |
| `db-12/db-12.md` | 65 | 34 | 30 |
| `db-13/db-13.md` | 69 | 33 | 30 |
| `db-14/db-14.md` | 35 | 34 | 30 |
| `db-15/db-15.md` | 63 | 33 | 30 |
| `db-16/db-16.md` | 30 | 30 | 30 |

The February 9 pathfinder format — `db-9.md`, 4,423 lines — documented every query through
four lenses:

> **Use Case:** Shipping platform needs to compare rates across USPS, UPS, and other
> carriers for a package and recommend the most cost-effective option based on weight,
> dimensions, and destination zone.
> **What it does:** Comprehensive rate comparison across multiple carriers with zone-based
> analysis, dimensional weight calculations, and cost optimization recommendation…
> **Business Value:** Enables shippers to save up to 87% on shipping costs by automatically
> identifying the cheapest carrier…
> **Purpose:** Provide real-time rate comparison and cost optimization recommendations to
> help users select the most appropriate service…

That is intent documentation. *Use Case* and *Purpose* are precisely the "what is the query
aiming to do" framing the client asked for.

The shipped `queries.json` kept one condensed `description` and dropped the rest.

**The industrialization of February 18 (§8) optimized for uniformity and, in doing so,
regressed the deliverable's richest field.** Nine schemas at 06:54, thirteen documentation
files at 17:39 — the batch pipeline produced a consistent, minimal record and left the
four-lens material behind in the working tree. No one logged the trade-off because from
inside the pipeline it did not look like one.

**Remediation is therefore recovery plus editing, not authoring from scratch.** For 11 of
13 databases the source material already exists; db-2 and db-3 have no `db-N.md` and are
the only genuine greenfield cases. See `REMEDIATION.md`.

### 16. Commercial reality vs. the Statement of Work

The Slack record prices the work very differently from the SOW:

| Source | Databases | Rate per DB | Total |
| --- | ---: | ---: | ---: |
| `AQ_Client_SOW_BIRD-SQL.docx`, 2026-02-14 | 11 | $5,500 | $60,500 |
| Slack record — stated price point | 16 | $3,500 | $56,000 |
| Slack record — indicated ceiling if it scales | — | $3,000–$4,000 | — |
| Actually shipped | 13 | — | — |
| Referenced as "this initial…" | 14 | — | — |

**Four different database counts appear across the artifacts: 11, 13, 14 and 16.** Nothing
in the file tree reconciles them. This is the single highest-value open item in the whole
reconstruction — at the spread between $3,500 and $5,500, the difference across a 13-to-16
database batch is roughly **$26,000 to $32,000**.

Two further commercial facts from the record, both worth holding onto:

- The client's own SOW is **deferred until the initial batch is finished** — the interim
  instruction is to rework the SQL descriptions on the existing set. Contract terms follow
  quality remediation, not the other way round.
- The account is characterized internally as **strategically important — the only active
  engagement with that client** — with a stated willingness to fund the higher rate *even
  at a loss* if it scales. The pressure on this work is retention pressure, not margin
  pressure. That changes what "done" means: the deliverable is the relationship.

### 17. The second meeting

A prep sheet was compiled for the follow-up. Its shape is worth preserving, because it is
the correct instinct — **convert a subjective complaint into a written specification before
doing any more work.**

*Alignment*
- "Can you walk us through what your ideal final deliverable looks like end to end?"
- "Is there a written rubric or spec we can reference for quality reviews going forward?"

*Requirements*
- What defines a 5/5 query description versus a 1/5? Can you show an example of each?
- Is the primary concern SQL correctness, natural-language quality, or both?
- When you flag something as AI-generated — what specifically does that mean? Generic
  language, missing context, something else?
- Are you benchmarking against BIRD or Spider? What methodology will you use to test it?

*Process*
- Who signs off on delivery acceptance?
- What does the internal review process look like — who reviews, what tool, in what order?
- How much lead time do you need before the weekly meeting?

*Success criteria*
- What is the target execution accuracy or F1 score?
- How many queries per batch, and what turnaround?
- What would make you confident enough to scale the engagement?

*Boundary* — proposed close: lock a written spec on the call so execution can proceed
without mid-cycle pivots.

**Every one of these questions is unanswered in the artifacts.** Until they are answered, a
rewrite is a guess with a cost attached. §14.5 is the concrete illustration: the client's
own bug report does not reproduce, and remediating against it literally would mean editing
the wrong file.

### 18. The strategic read

The internal note on the account is blunt: the relationship is under strain, and the
qualification framework applied to it (MEDDPICC) reads the client as dissatisfied. That is
worth recording plainly rather than softening — it is the operating condition, and Parts I
through III are the record of how a well-executed pipeline still arrived here.

The counter-position recorded alongside it is the substantive one, and it is correct:
**a language model cannot certify that data is good for training.** Determining whether a
dataset improves a benchmark or a trained model requires ML/DS work — execution accuracy
against a held-out set, F1, ablations against BIRD or Spider, downstream task metrics on a
real product. Nothing in this package measures that, because nothing in the engagement was
scoped to measure it. The client asked for annotation and got annotation; the question they
are actually trying to answer — *is this data good?* — was never anyone's deliverable.

That gap is the strongest available argument for expanding scope rather than defending the
current batch. The three things that would answer it are all buildable from what already
exists:

1. **An execution-accuracy harness** — load each schema and dataset, execute all 390 gold
   queries, capture real result sets. Turns `expected_output` (§6, §11) from prose into an
   oracle and produces the first real number in the engagement.
2. **BIRD/Spider alignment evidence** — the SOW already claims BIRD-SQL / LiveSQLBench
   familiarity; a published field-level mapping and a contamination check converts that
   claim into an artifact.
3. **A jointly-authored rubric** — §17's first question. Whoever writes the rubric defines
   acceptance, and acceptance is currently defined by one sentence of client impression.

The distinction the record draws — between *producing annotation* and *demonstrating that
annotation improves a model* — is the difference between a per-database vendor and a
partner on the roadmap. It is also, at $3,500 versus $5,500 per database, the difference the
pricing argument has been missing.

---

## Timeline

| Date | Event |
| --- | --- |
| 2025-09-17 | `[AfterQuery] Code Eval Requirements` — first spec; 9-dimension rubric, 16 error codes |
| 2025-10-29 | NDA and Data Submission Agreement executed |
| 2025-11-20 | Counterparty diligence — Crunchbase profile and funding history |
| 2025-11-29 | Financial details and privacy documents |
| 2026-01-14 | Project **Excel** onboarding |
| 2026-01-17 | Project **Green** onboarding — same template, name changed |
| 2026-01-25 | Expert-network recruiting deck |
| 2026-02-01 | `food_delivery_db` final delivery — the bundle shape that became the house format |
| 2026-02-02 | `AFTERQUERY` database bundle |
| 2026-02-04 | db-9 deliverable created; first comprehensive validation report `20260204-2021` |
| 2026-02-06 | db-6 and db-9 pathfinder builds |
| 2026-02-08 | db-9 QC flags duplicate queries 16–30 → db-9 rewritten |
| 2026-02-09 | `SQL Queries_AfterQuery.docx` — the Description/SQL/Expected-Output triad |
| 2026-02-10 | Working tree consolidated: 16 candidates, db-1 … db-16 |
| 2026-02-14 | **Statement of Work** — BIRD-SQL program, 11 databases, $5,500/db, $60,500 |
| 2026-02-15 | NDA and DSA re-executed; db-2 schema authored |
| 2026-02-16 | Batch extraction — 11 `queries.json` at `20260216-2320` |
| 2026-02-17 | db-6 and db-16 re-extracted; db-3 schema authored |
| 2026-02-18 | **Industrialization day** — schemas 06:54 → data 19:20 (§8) |
| 2026-03-09 | `client-db.zip` packaged — 2,424,282,003 bytes |
| 2026-03-11 | SOW revision |
| *undated* | **Meeting 1** — client feedback: *"the descriptions are AI-generated"* (§13) |
| *undated* | **Meeting 2** — prep sheet: convert the complaint into a written rubric (§17) |
| 2026-08-05 | Provenance reconstruction; complaint measured against shipped files (§14) |

---

## Verification

Every quantitative claim in this document was recomputed from the shipped package on
**2026-08-05**, not copied from prior reports:

- Query counts, key coverage, and complexity distribution — parsed from all 13 `queries.json`
- Table, foreign-key, index, and view counts — regex over all 13 `schema.sql`
- Near-duplicate analysis — pairwise `difflib.SequenceMatcher` on whitespace- and
  case-normalized SQL, threshold 0.99, all 13 databases
- File sizes and timestamps — `stat` on the extracted package
- Notebook absence — `find client/ -name '*.ipynb'` → 0 results

Statements about intake, contracting, and the working tree are sourced to the specific
artifacts named inline. Where a reason is not recorded in any file — most importantly the
cut of db-1, db-4 and db-5 (§5) and the 11→13 scope change (§9) — the document says so.

---

*Reconstructed from primary artifacts. Corrections belong in this file; it is the record.*

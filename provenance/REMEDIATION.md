# Remediation Work Order — Query Description Rewrite

**Trigger:** client feedback — *"Databases look good, only comment: the descriptions are AI-generated."*
**Scope:** the `description` field of all 390 query pairs across 13 shipped databases.
**Out of scope:** schemas, SQL, data. The client explicitly said the databases look good.
**Companion:** [`STORY.md`](STORY.md) §13–§18 for the full context. This file is the execution plan.

> **Read §0 before starting.** Two of the client's five named databases do not reproduce the
> defect as described. Remediating literally would mean editing the wrong artifact.

---

## 0. Confirm before you build

Three questions gate this work. Answering them is cheaper than a wrong rewrite.

| # | Question | Why it blocks |
| --- | --- | --- |
| Q1 | Which artifact were you reviewing — `QUERIES/queries.json`, or `db-N_deliverable.json`? | The client flagged db-2, db-3, db-6, db-7, db-10 as *"missing intent/purpose fields."* In the shipped `queries.json`, **no** database has such a field — the gap is universal, not specific to those five. The `db-N_deliverable.json` files *do* drop `question` and `evidence`. The complaint most likely describes that file. |
| Q2 | What defines a 5/5 description versus a 1/5? One example of each. | Acceptance is currently one sentence of impression. Without a rubric this rewrite cannot be verified, only resubmitted. |
| Q3 | Is the ingest file format ready? | The client committed to sending one. Rewriting descriptions into the current shape and then reformatting is double work. |

If Q1–Q3 cannot be answered before work starts, execute **Phase 1 only** (the mechanical
fixes, which are correct under any rubric) and hold Phase 2.

---

## 1. Measured baseline

Recomputed from the shipped package on 2026-08-05. These are the numbers to move.

| Metric | Current | Target |
| --- | --- | --- |
| Mean description length | **193 chars** (range 138–277 by db) | 450–800 chars |
| Descriptions naming user intent (`intent`/`purpose`/`aiming to`) | **0 / 390** | 390 / 390 |
| Near-duplicate SQL pairs ≥0.99 similarity | **1,053** across 8 of 13 dbs | 0 |
| `queries.json` ↔ `queries.md` description agreement | **370 / 390** | 390 / 390 |
| Databases with distinct query sets | 5 / 13 | 13 / 13 |

### Per-database work profile

`Harvest` = a `db-N.md` with Use Case / Business Value / Purpose blocks exists in the working
tree and can be mined. `Greenfield` = no such file; descriptions must be authored.

| DB | Mean desc | Near-dups | md↔json | Source material | Effort |
| --- | ---: | ---: | ---: | --- | --- |
| db-2 | 209 | 50 | **18/30** | **none** — no `db-2.md` | **Greenfield + md regen** |
| db-3 | 174 | 141 | 30/30 | **none** — no `db-3.md` | **Greenfield** |
| db-6 | 197 | 0 | 29/30 | `db-6.md` — 32 UC / 30 BV / 30 P | Harvest |
| db-7 | 155 | 0 | 30/30 | `db-7.md` — 34 / 33 / 30 | Harvest |
| db-8 | 138 | 0 | 30/30 | `db-8.md` — 93 / 63 / 60 | Harvest (richest) |
| db-9 | 240 | 0 | 30/30 | `db-9.md` — 63 / 33 / 30 | Harvest |
| db-10 | 152 | **212** | 30/30 | `db-10.md` — 63 / 33 / 30 | Harvest + dedupe |
| db-11 | 166 | **210** | 29/30 | `db-11.md` — 63 / 33 / 30 | Harvest + dedupe |
| db-12 | 277 | **136** | 30/30 | `db-12.md` — 65 / 34 / 30 | Harvest + dedupe |
| db-13 | 198 | 57 | 30/30 | `db-13.md` — 69 / 33 / 30 | Harvest + dedupe |
| db-14 | 177 | 80 | 30/30 | `db-14.md` — 35 / 34 / 30 | Harvest + dedupe |
| db-15 | 208 | 0 | 30/30 | `db-15.md` — 63 / 33 / 30 | Harvest |
| db-16 | 216 | **167** | 30/30 | `db-16.md` — 30 / 30 / 30 | Harvest + dedupe |

**Sequence by value:** db-10, db-11, db-16, db-12 (worst duplication, harvest available) →
db-13, db-14 → db-2, db-3 (greenfield) → db-6, db-7, db-8, db-9, db-15 (descriptions only).

---

## 2. The target description shape

The client asked for **intent, not summary**, and **deeper context**. The February 9
pathfinder format already answers this. Fold its four lenses into one field.

**Current — db-9, query 1 (265 chars, describes the mechanism):**

> Shipping operations teams need to optimize carrier selection and reduce costs. Historical
> data from shipments, carriers, and routes captures performance metrics. Operators need
> rate comparisons to identify the cheapest and fastest options for each shipment scenario.

**Available in `db-9.md` but never shipped:**

> **Use Case:** Shipping platform needs to compare rates across USPS, UPS, and other carriers
> for a package and recommend the most cost-effective option based on weight, dimensions, and
> destination zone.
> **Business Value:** Enables shippers to save up to 87% on shipping costs by automatically
> identifying the cheapest carrier…
> **Purpose:** Provide real-time rate comparison and cost optimization recommendations to help
> users select the most appropriate service…

**Target — four beats, 450–800 characters:**

1. **Who is asking and what decision they are trying to make.** A named role in a real
   situation, not "users."
2. **What they cannot see without this query.** The gap in their knowledge — this is the
   *intent*, and it is the beat currently missing from all 390.
3. **What the answer lets them do.** The action the result enables.
4. **Why this is non-trivial against this schema.** One clause anchoring it to *these*
   tables — the detail no generic description can fake.

Beats 1–3 come from `db-N.md`. Beat 4 comes from `evidence`, which is already good
(mean 274 chars, specific about CTEs and columns) and should be preserved.

### Rules

- **No template.** If two descriptions in a database can be diffed to a noun swap, rewrite both.
- **Do not restate the SQL.** "This query joins X to Y and aggregates Z" is a summary — the
  exact failure mode being corrected.
- **Do not use** *comprehensive, robust, leverage, seamless, utilize, facilitate, in today's
  fast-paced.* Generic register is what reads as machine-written.
- **Vary sentence count and opening structure across the 30.** Uniform rhythm is a tell
  independent of word choice.
- **Domain vocabulary is required.** Say *dimensional weight*, *DIM divisor 166*, *SCAC code*
  — not *shipping attributes*.
- **`question` stays a natural utterance.** Do not academicize it.

---

## 3. Execution

### Phase 1 — mechanical (no rubric required, safe to run now)

**1.1 Fix the db-2 divergence.** Queries **17, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30**
have `queries.json` descriptions absent from `queries.md`. `queries.md` is `## Query N` headers
wrapping fenced JSON, so regenerate it from the JSON — do not hand-edit. Re-verify all 13
databases at 30/30 afterwards.

**1.2 Inventory the duplicate clusters.** For each database, cluster the 30 `sql` values at
≥0.99 normalized similarity. Emit `audit/duplicate-clusters.json`:

```json
{"db-10": [{"cluster": 1, "queries": [7, 8, 14, 26], "similarity": 0.9968,
            "differs_by": "date_trunc unit: week vs month"}]}
```

`differs_by` must state the actual textual delta. Do not delete anything — the report is the
deliverable of this step, and the client has not approved reducing query counts.

**1.3 Harvest the intent blocks.** Parse `db-N.md` for all 11 databases that have one; extract
Use Case / Business Value / Purpose per query number into
`working/db-N-intent-harvest.json`. Report coverage — flag any query number missing a block.

**1.4 Regenerate the baseline metrics** from §1 into `audit/baseline-metrics.json` so progress
is measurable per database.

### Phase 2 — rewrite (needs Q1–Q3 answered)

**2.1** Rewrite descriptions per §2, working database by database in the §1 order.

**2.2** For each duplicate cluster from 1.2, either differentiate the underlying queries so
each answers a distinct question, or consolidate and replace — **client decision, not an
implementation choice.** Present the cluster report and ask.

**2.3** Regenerate `queries.md` from `queries.json` after every database. Never edit both by hand.

**2.4** Re-run §1 metrics per database and record the delta.

### Phase 3 — verify

**3.1** Every check in §4 passes.
**3.2** Sample 3 rewritten descriptions per database (39 total) for human read-through. A
description that could be pasted into a different database without editing has failed.
**3.3** Regenerate `audit/baseline-metrics.json` and diff against Phase 1.

---

## 4. Acceptance criteria

Machine-checkable. All must pass before resubmission.

| # | Check | Threshold |
| --- | --- | --- |
| A1 | `queries.json` parses; 30 items; keys unchanged | 13/13 databases |
| A2 | Mean description length per database | ≥ 450 chars |
| A3 | Minimum description length, any query | ≥ 300 chars |
| A4 | Descriptions naming a user, a decision, and an action | 390 / 390 |
| A5 | Pairwise description similarity within a database | < 0.75, all pairs |
| A6 | Banned-phrase list (§2) | 0 occurrences |
| A7 | Description ↔ `queries.md` agreement | 390 / 390 |
| A8 | `sql`, `question`, `evidence`, `expected_output` byte-identical to shipped | unchanged |
| A9 | Duplicate cluster report exists and every cluster is dispositioned | 100% |

**A8 is the guardrail.** This work order changes descriptions only. Any diff touching SQL is
a bug in the rewrite, not an improvement.

---

## 5. What this does not fix

Deliberately out of scope; carry forward separately. Detail in `STORY.md` §6.

| | Issue | Note |
| --- | --- | --- |
| 6.1 | Promised setup notebook never shipped | `db-N.ipynb` exists in the working tree for db-6 … db-16. Shipping it is a 15-minute fix and closes a stated promise. |
| 6.3 | `complexity` constant at `"moderate"` | Blocks curriculum sampling. Derive from CTE depth / join count / window functions and propose to the client. |
| 6.4 | Audits ran against seed data | db-9 audited at 80 rows; ships 4.79 GB. Re-run against real data. |
| — | **No execution-accuracy number exists** | The strongest available scope expansion (`STORY.md` §18): execute all 390 gold queries against loaded data, capture real result sets, publish accuracy. It is the only thing that answers *is this data good* — and nothing in the engagement currently does. |

---

## 6. Open commercial items

Not engineering, but they determine how much of the above is worth doing. See `STORY.md` §16.

1. **Reconcile the database count.** Four numbers appear across the artifacts — **11** (SOW),
   **13** (shipped), **14** ("this initial 14"), **16** (stated price point). Nothing reconciles them.
2. **Reconcile the rate.** SOW: $5,500/db. Slack record: $3,500/db, with $3,000–4,000
   indicated at scale. The spread across a 13–16 database batch is roughly **$26,000–32,000**.
3. **The client's SOW is deferred** until the initial batch is finished. Remediation quality
   gates the contract, not the reverse.

---

*Baseline measured 2026-08-05 against the shipped package. Re-measure before starting — if
the files have changed since, §1 is stale.*

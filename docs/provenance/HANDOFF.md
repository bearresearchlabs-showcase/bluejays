# Handoff to Claude Code

**Target session:** https://claude.ai/code/session_01GKYrLcsVXivXJmVndTR5kS
**Prepared:** 2026-08-05
**Package:** `db-provenance-package.zip`

This package was assembled in a Cowork session with read access to the delivered client
package, the working tree, and the intake artifacts. Claude Code cannot see any of that
history — this file carries it across.

---

## Where the files are

| Path on this Mac | What it is |
| --- | --- |
| `~/Downloads/client/db/` | **The delivered package.** 13 databases, 21.5 GB. Repo root. |
| `~/Downloads/db (1)/` | **The working tree.** 16 candidates, audits, scripts, notebooks, `db-N.md` intent docs. |
| `~/Downloads/AQ_Client_SOW_BIRD-SQL.docx` | Statement of Work, 2026-02-14 |
| `~/Documents/AQ/` | Moved on to other work — the `db/source/` tree referenced by every `queries.json` no longer exists |

Unzip this package into `~/Downloads/client/db/` (files already written there as of
2026-08-05; the zip is the portable copy).

---

## Read in this order

1. **`CLAUDE.md`** — repository rules and verified figures. Six hard rules; rule 1 and rule 2
   are the ones that prevent damage.
2. **`REMEDIATION.md`** — the active work order. §0 is a gate: three questions that should be
   answered before Phase 2 starts.
3. **`STORY.md`** §13–§18 — why this work exists. Skip Parts 0–III unless context is needed.
4. **`story-timeline.json`** — everything above as structured data.

---

## Kick-off prompt

Paste this into the Claude Code session:

```
Read CLAUDE.md and REMEDIATION.md in this repo before doing anything.

Context: this is a delivered client package of 13 text-to-SQL databases. The client
accepted the databases and rejected the descriptions — "the descriptions are
AI-generated." The rewrite plan is in REMEDIATION.md with measured baselines and
machine-checkable acceptance criteria.

Start with REMEDIATION.md Phase 1 only — it is safe under any rubric and does not
need client input:

  1.1  Fix the db-2 divergence: queries 17 and 20-30 have queries.json descriptions
       that do not appear in queries.md. Regenerate queries.md from queries.json.
       Do not hand-edit both. Verify all 13 databases at 30/30 afterwards.
  1.2  Cluster each database's 30 SQL queries at >=0.99 normalized similarity.
       Write audit/duplicate-clusters.json with the actual textual delta per cluster
       in a "differs_by" field. Do not delete anything.
  1.3  Harvest Use Case / Business Value / Purpose blocks from
       "~/Downloads/db (1)/db-N/db-N.md" for db-6 through db-16 into
       working/db-N-intent-harvest.json. Report per-query coverage gaps.
       db-2 and db-3 have no such file — flag them as greenfield.
  1.4  Write audit/baseline-metrics.json with the §1 metrics per database.

Hard constraints: change descriptions only. sql, question, evidence and
expected_output stay byte-identical (acceptance check A8). Never regenerate
data_large.sql. Do not delete queries.

Stop after Phase 1 and report the four artifacts. Phase 2 needs client answers to
REMEDIATION.md §0 Q1-Q3.
```

---

## What Phase 1 should produce

| Artifact | Contents |
| --- | --- |
| `audit/baseline-metrics.json` | Per-database: mean/min/max description length, near-duplicate pair count, md↔json agreement |
| `audit/duplicate-clusters.json` | Every ≥0.99 SQL cluster with query numbers, similarity, and the actual delta |
| `working/db-N-intent-harvest.json` | Use Case / Business Value / Purpose per query, for db-6 … db-16 |
| `db-2/QUERIES/queries.md` | Regenerated — 30/30 agreement with its JSON |

Expected: **1,053** near-duplicate pairs across 8 databases (db-6, db-7, db-8, db-9, db-15
should come back clean at 0). If those numbers differ materially, the files changed since
2026-08-05 and `REMEDIATION.md` §1 is stale — re-measure before proceeding.

---

## Three things not to get wrong

**Do not resolve the duplicate clusters.** Every database ships exactly 30 queries.
Consolidating changes the delivered count, which is a client decision. Report and stop.

**Do not treat the client's bug report as literal.** They flagged db-2, db-3, db-6, db-7,
db-10 as missing intent/purpose fields. No shipped `queries.json` has such a field — the gap
is universal. The complaint most likely describes `db-N_deliverable.json`, which drops
`question` and `evidence`. `REMEDIATION.md` §0 Q1.

**Do not trust the shipped validation reports.** `db-9/results/final_comprehensive_validation_report.json`
records `Pass: 1` while logging `relation "packages" does not exist`, and its phase-3 block
is stamped with the wrong database. Recompute; do not cite.

---

## Open items Claude Code cannot resolve

These need the client or the account owner, not a code change:

1. **Which artifact was reviewed** (§0 Q1) — blocks correct targeting.
2. **The acceptance rubric** — what is a 5/5 description versus a 1/5. Blocks verification.
3. **The database count** — 11 (SOW) / 13 (shipped) / 14 (referenced) / 16 (priced). Blocks invoicing.
4. **The rate** — $5,500/db (SOW) versus $3,500/db (working record). ~$26k–32k spread.

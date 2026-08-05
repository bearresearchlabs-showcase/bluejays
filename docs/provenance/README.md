# Provenance Package — Index

This directory is the **db provenance package**, incorporated into this repository on 2026-08-05 (uploaded as `dbprovenancepackage.zip`). It is the forensic record of the client deliverable — 13 databases, 390 question–SQL pairs, 19.4 GB of generated data — reconstructed and re-verified from the shipped files themselves.

Every figure in these documents was **recomputed from the shipped package on 2026-08-05**, not carried over from prior reports. Where these figures disagree with other documents in this repository (including [`docs/MDP_TUPLE_ARCHITECTURE.md`](../MDP_TUPLE_ARCHITECTURE.md) as first written), **the provenance package is authoritative for what shipped**; the repository describes the working corpus.

| File | What it is |
|------|------------|
| [STORY.md](STORY.md) | The full provenance narrative, Parts 0–IV: intake (Sep 2025) → apprentice deliveries → SOW → the provenance pivot (why db-1/4/5 were cut) → industrialization day (Feb 18, 2026) → delivery (Mar 9, 2026) → client feedback and its measurement |
| [story-timeline.json](story-timeline.json) | The same history as structured data: phases, 24 events, per-database records, known gaps, open questions, commercial record |
| [REMEDIATION.md](REMEDIATION.md) | The active work order: query-description rewrite (client feedback: "the descriptions are AI-generated"), with measured baselines and acceptance criteria |
| [HANDOFF.md](HANDOFF.md) | Hand-off brief for executing the remediation |
| [PACKAGE_README.md](PACKAGE_README.md) | The package's own README — verified shipped figures, field coverage, known gaps (was `README.md` in the package root) |
| [PACKAGE_BRIEF.md](PACKAGE_BRIEF.md) | The package's working brief and editing rules (was `CLAUDE.md` in the package root; renamed so it is not picked up as this repository's project instructions — its rules govern the delivered package tree, not this repo) |
| [sources/](sources/) | Primary artifact: `keeping-track-of-things` (Slack-exported working document behind STORY.md Part IV), txt + pdf |

## The five facts that correct this repository's other documents

1. **Shipped scope is 13 databases / 390 pairs** (db-2, db-3, db-6…db-16). The 16-database / 480-pair figures elsewhere in this repo describe the working corpus, of which the client package is the delivered subset. db-1, db-4, db-5 were cut in the provenance pivot (STORY.md §5).
2. **The bulk row data is synthetic.** Rows were produced by `generate_large_dataset.py` to a ~1 GiB-per-database floor. Schemas and query semantics are the parts grounded in real systems and public/government data models. "No row of shipped data is real production data; no schema is arbitrary" (STORY.md §10).
3. **`complexity` carries no signal in the shipped package** — constant `"moderate"` across all 390 items. Difficulty must be derived (CTE depth, join count, window functions, schema breadth).
4. **1,053 near-duplicate query pairs** at ≥0.99 normalized similarity, in 8 of 13 shipped databases. Clean: db-6, db-7, db-8, db-9, db-15.
5. **`expected_output` is prose, not result rows.** Any execution-accuracy reward must be materialized by executing the gold SQL against a loaded instance.

---

**Last Updated:** 2026-08-05

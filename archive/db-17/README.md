# db-17 — Archived

db-17 is not part of the active database set. The active set is **db-1 … db-16** — every pipeline script, compose file, and validation harness iterates `range(1, 17)`.

This directory records the archival so the boundary is explicit:

- Root and `source/` must not contain a `db-17/` (enforced by `tests/test_single_source_of_truth.py::TestNoDb17InActiveSet`).
- `docs/ROADMAP.md` §12 lists "Extend to db-17+ with same patterns" as future work — when that happens, db-17 starts life in `source/db-17/` under the Iron Triangle rules, and this archive entry is superseded.
- One legacy script (`scripts/test_all_databases_consistency_acid.py`) still iterates through db-17; it predates the 16-database consolidation.

No db-17 data or schema ever shipped in a client package (see `docs/provenance/` — shipped set is db-2, db-3, db-6 … db-16).

**Last Updated:** 2026-08-05

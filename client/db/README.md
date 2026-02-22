# Client Test Repo — Agentic Data Agent

**Audience:** ML research engineers and technical practitioners building reinforcement learning (RL) environments for text-to-SQL data agents.

This package provides training data and infrastructure for developing an RL-trained data agent: 13 databases (db-2, db-3, db-6 through db-16) with BIRD-style question–SQL pairs, schema documentation, and a notebook for ingest, validation, and environment setup.

**When shared as a zip:** This folder is the repo root. Extract the zip and use this README to set up.

---

## BIRD-Style Metadata (RL Training Data)

Each `db/db-N/QUERIES/queries.json` includes fields for RL environment design. Only keys present in the JSON are included.


| Field             | Use in RL Environment                                     |
| ----------------- | --------------------------------------------------------- |
| `question`        | User utterance → observation / intent / state input       |
| `sql`             | Gold action (target for imitation / reward baseline)      |
| `description`     | Domain context for policy conditioning                    |
| `evidence`        | Technical reasoning for chain-of-thought / auxiliary loss |
| `expected_output` | Verification / reflection signal                          |
| `complexity`      | Optional: curriculum or difficulty-based sampling         |
| `number`          | Query ID for logging and evaluation                       |


---

**Last Updated:** 2026-02-18
# Project context for Claude Code

Working brief for the 13-database BIRD-style text-to-SQL package. Read this first, then
`REMEDIATION.md` for the active work order and `STORY.md` for full provenance.

## What this repository is

A delivered client package: **13 databases** (`db-2`, `db-3`, `db-6` … `db-16`),
**390 question–SQL pairs** (30 each), 19.4 GB of generated data. Built for text-to-SQL /
BIRD-style RL environment work. Delivered March 2026.

```
db/
├── README.md                 # package overview, verified figures
├── STORY.md                  # provenance narrative, Parts 0–IV
├── REMEDIATION.md            # ACTIVE WORK ORDER — read before editing anything
├── story-timeline.json       # the history as structured data
├── sources/                  # primary artifacts the narrative is built from
└── db-N/
    ├── DATABASE/{schema.sql, data_large.sql}
    ├── QUERIES/{queries.md, queries.json}
    ├── DOCUMENTATION/README.md
    └── vercel.json
```

## Current state

The client accepted the databases and rejected the descriptions:
*"Databases look good, only comment: the descriptions are AI-generated."*

Active work is the description rewrite in `REMEDIATION.md`. Everything else is stable.

## Rules for this repository

**1. Change descriptions only.** `sql`, `question`, `evidence` and `expected_output` must stay
byte-identical to what shipped unless a change order says otherwise. Acceptance check A8.

**2. `queries.md` is generated, never hand-edited.** It is `## Query N` headers wrapping fenced
JSON blocks. Edit `queries.json`, then regenerate the markdown. Hand-editing both is what
produced the db-2 divergence (queries 17, 20–30).

**3. Do not delete queries.** Every database ships exactly 30. The near-duplicate clusters are
real defects, but consolidating them changes the delivered count — a client decision, not an
implementation choice. Report clusters; do not resolve them unilaterally.

**4. Never regenerate `data_large.sql`.** ~1 GiB per database, 19.4 GB total, and the shipped
bytes are what the client has. Regenerating desynchronizes the delivery.

**5. Measure before and after.** Every claim in `STORY.md` and `REMEDIATION.md` was recomputed
from the files, not carried over from prior reports. Hold that standard — the shipped
validation reports are known to be unreliable (`STORY.md` §6.7: one records `Pass: 1` while
logging `relation "packages" does not exist`).

**6. State what the evidence does not support.** Two open questions have no answer in any file:
why db-1, db-4 and db-5 were cut, and how 11 scoped databases became 13 shipped. Do not
resolve them by inference in any generated artifact.

## Verified figures — do not restate from memory

| | |
| --- | --- |
| Databases / queries | 13 / 390 (30 each) |
| Tables / FKs / Indexes | 176 / 171 / 303 |
| Bulk data | 19.4 GB across 13 `data_large.sql` |
| Extracted / zipped | 21,525,194,003 bytes / 2,424,282,003 bytes |
| Mean description length | 193 chars |
| Near-duplicate pairs ≥0.99 | 1,053 across 8 of 13 databases |
| Clean databases | db-6, db-7, db-8, db-9, db-15 |
| `complexity` values | `"moderate"` × 390 — carries no signal |

## Useful invariants

- All 390 items carry: `number`, `question`, `sql`, `description`, `evidence`,
  `expected_output`, `complexity`, `line_number`.
- 150 items (db-6, db-7, db-8, db-13, db-15) additionally carry `title` and `normal_query`.
- Top-level keys in every `queries.json`: `source_file`, `extraction_timestamp`,
  `total_queries`, `queries`.
- `source_file` points at `/Users/machine/Documents/AQ/db/source/db-N/queries/queries.md` —
  **that path no longer exists.** The working tree survives at `Downloads/db (1)`.
- Intent documentation (Use Case / Business Value / Purpose, 30 blocks each) exists in
  `Downloads/db (1)/db-N/db-N.md` for **db-6 … db-16** only. db-2 and db-3 have none.

## Commands

```bash
# validate every queries.json
for d in db-*/QUERIES/queries.json; do python3 -c "
import json,sys; q=json.load(open('$d')); assert len(q['queries'])==30, '$d'"; done

# description length by database
python3 -c "
import json,glob
for f in sorted(glob.glob('db-*/QUERIES/queries.json')):
    q=json.load(open(f))['queries']; L=[len(i['description']) for i in q]
    print(f, sum(L)//len(L))"

# near-duplicate detection
python3 -c "
import json,glob,re,difflib
for f in sorted(glob.glob('db-*/QUERIES/queries.json')):
    s=[re.sub(r'\s+',' ',i['sql']).strip().lower() for i in json.load(open(f))['queries']]
    n=sum(1 for i in range(len(s)) for j in range(i+1,len(s))
          if difflib.SequenceMatcher(None,s[i],s[j]).ratio()>=0.99)
    print(f, n)"
```

## Tone for generated documentation

Plain, specific, quantified. Name the file and the number. No marketing register — the
active complaint against this package is that its prose reads as machine-written, so
generic language is a live failure mode, not a style preference.

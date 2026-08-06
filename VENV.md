# Running MIRROR-SQL in a venv

Everything below runs inside an isolated virtualenv. No system Python is touched.

```bash
python3 -m venv .venv
./.venv/bin/pip install -e '.[dev]'          # gymnasium, sqlglot, pytest, matplotlib
./.venv/bin/pip install 'psycopg[binary]'    # for the PostgreSQL backend
```

Verified in this venv (Python 3.11.15):

```
./.venv/bin/python -m pytest tests/ -q
  28 passed

./.venv/bin/python -m mirrorsql.verify <corpus>
  corpus: 13 databases, 390 gold queries, 222 effective (57%)
  invariants: 3/8 hold

./.venv/bin/python -m mirrorsql.repair <corpus> --check
  R1 dialect leak : 22 VARCHAR(16777216) -> TEXT
  R2 undeclared   : 6 schemas needed a PostGIS declaration
```

## Secrets — 1Password, never in the shell history or this repo

Follow the pattern already in `~/.config/op/agy.env`: the file holds **references**,
`op run` resolves them into the child process, and no secret is written to disk.

```bash
# .op.env  (committed — it contains references only, never values)
HF_TOKEN=op://Cowork-CLI-Keys/HUGGING_FACE_WRITE/credential

op run --env-file=.op.env -- ./upload_hf.sh
```

### Blocker: 1Password Environments are not CLI-readable

`HUGGING_FACE_WRITE` currently lives in a 1Password **Environment**
(`omrvrhnqc2vn5tbytc2ionkvey`). The CLI refuses every access path to Environments:

```
op item get   -> Validation: This operation cannot be performed on 1Password Environments
op read       -> same
op run        -> same
op vault get  -> same
```

Verified on **2.35.0 and 2.38.1** (the CLI was upgraded during this session, which did not
help — Environments are consumed by the 1Password SDKs and app integrations, not by
`op read`). Environments also do not appear in `op vault list`.

**Fix, about fifteen seconds in the 1Password app:** move or copy the `HUGGING_FACE_WRITE`
item into a regular vault — `Cowork-CLI-Keys` is the natural home, it already holds the
other CLI credentials. Then `.op.env` resolves and the upload runs unchanged.

If the field is not named `credential`, adjust the last path segment:

```bash
op item get HUGGING_FACE_WRITE --vault Cowork-CLI-Keys --format=json \
  | python3 -c "import json,sys;[print(f['label']) for f in json.load(sys.stdin)['fields']]"
```

## What the upload does

`upload_hf.sh` creates `1digitaldesign/mirror-sql` as a dataset repo and pushes
`hf-dataset/` — 13 repaired schemas, 390 annotated pairs, the BIRD-format JSONL with
per-query execution status, the manifest and the dataset card. 8.2 MB.

The ~19.4 GB of instance data is not in the bundle; push it separately from
`~/Downloads/client/db` (see `PUSH.md`), applying `mirrorsql.repair` first so the
published schemas match the ones that load.

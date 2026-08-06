# Pushing MIRROR-SQL

This sandbox has no Hugging Face write token and no GitHub credential for
`bearresearchlabs-showcase/bluejays`, so both pushes are one command each from your Mac.

## 1. Hugging Face dataset

Everything is staged in `hf-dataset/` — 13 repaired schemas, 390 annotated pairs,
a BIRD-format JSONL with per-query execution status, a manifest, and the dataset card.
8.6 MB total.

```bash
pip install -U huggingface_hub
hf auth login                       # or: export HF_TOKEN=...

hf upload 1digitaldesign/mirror-sql ./hf-dataset . \
    --repo-type dataset --commit-message "MIRROR-SQL v1.0"
```

Then the card renders at https://huggingface.co/datasets/1digitaldesign/mirror-sql

### Instance data (~19.4 GB), separately

The `data_large.sql` files are on your Mac at `~/Downloads/client/db/db-N/DATABASE/`.
They were never in this sandbox. Push them from there:

```bash
cd ~/Downloads/client/db
for n in 2 3 6 7 8 9 10 11 12 13 14 15 16; do
  hf upload 1digitaldesign/mirror-sql \
      db-$n/DATABASE/data_large.sql instances/db-$n.sql --repo-type dataset
done
```

Apply the schema repairs first so the published schemas match the ones that load:

```bash
python -m mirrorsql.repair ~/Downloads/client/db --check   # dry run
python -m mirrorsql.repair ~/Downloads/client/db           # in place
```

## 2. GitHub

```bash
git remote add origin git@github.com:bearresearchlabs-showcase/bluejays.git
git fetch origin && git checkout -b mirror-sql
git push -u origin mirror-sql        # then open a PR into main
```

This repo is a clean history (3 commits) so it merges as a branch without
disturbing the existing 16-environment tree. MIRROR-SQL is the analysis layer:
the audited 13-environment client delivery, plus the package, paper and repairs.

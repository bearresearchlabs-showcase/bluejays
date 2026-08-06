#!/usr/bin/env bash
# Publish MIRROR-SQL to Hugging Face. HF_TOKEN is injected by `op run` into this
# process only — never written to disk, echoed, or logged.
set -euo pipefail
cd "$(dirname "$0")"
REPO="${1:-1digitaldesign/mirror-sql}"
[ -n "${HF_TOKEN:-}" ] || { echo "HF_TOKEN unset — use: op run --env-file=.op.env -- ./upload_hf.sh"; exit 1; }
HF="./.venv/bin/hf"; [ -x "$HF" ] || HF="./.venv/bin/huggingface-cli"
echo "authenticated as: $($HF auth whoami 2>/dev/null | head -1)"
$HF repo create "$REPO" --repo-type dataset --exist-ok
$HF upload "$REPO" ./hf-dataset . --repo-type dataset \
   --commit-message "MIRROR-SQL v1.0 - 13 environments, 390 pairs, 287 execution-verified"
echo "done: https://huggingface.co/datasets/$REPO"

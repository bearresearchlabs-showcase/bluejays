#!/usr/bin/env python3
"""
One-time restore of queries.json from 38ce1cd for db-1..16.
Source at 38ce1cd: source/db-N/app/QUERIES/queries.json
Target: source/db-N/queries/queries.json (current structure)
Updates source_file in JSON to new path.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
COMMIT = "38ce1cd"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Restore queries.json from 38ce1cd to source/db-N/queries/"
    )
    ap.add_argument("--dbs", type=int, nargs="*", help="DB numbers (default: 1-16)")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = ap.parse_args()

    dbs = args.dbs if args.dbs else list(range(1, 17))
    restored = 0
    for n in dbs:
        src_path = f"source/db-{n}/app/QUERIES/queries.json"
        try:
            result = subprocess.run(
                ["git", "show", f"{COMMIT}:{src_path}"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            print(f"  db-{n}: timeout", file=sys.stderr)
            continue
        if result.returncode != 0 or not result.stdout.strip():
            continue
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"  db-{n}: invalid JSON: {e}", file=sys.stderr)
            continue

        # Update source_file to current path
        data["source_file"] = str(ROOT / "source" / f"db-{n}" / "queries" / "queries.md")

        target_dir = ROOT / "source" / f"db-{n}" / "queries"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "queries.json"

        if args.dry_run:
            print(f"  Would restore db-{n}: {target}")
        else:
            target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  Restored db-{n}: {target}")
        restored += 1

    print(f"Restored {restored} database(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

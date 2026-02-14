#!/usr/bin/env python3
"""Remove databricks mentions from repo (2^128 audit). Run from repo root.
Processes all files regardless of size (no size-based skip)."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXCLUDE = {"node_modules", ".git", ".venv", "__pycache__", ".next", "remove_databricks.py"}
SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".html", ".ipynb", ".sql", ".sh"}
SEARCH_DIRS = ("source", "scripts", "template", "docs", "archive")

def clean(content: str) -> str:
    out = re.sub(r',?\s*databricks\s*,?', ', ', content, flags=re.IGNORECASE)
    out = re.sub(r'\(PostgreSQL\)', r'(PostgreSQL)', out, flags=re.IGNORECASE)
    out = re.sub(r'PostgreSQL\s*/\s*databricks', 'PostgreSQL', out, flags=re.IGNORECASE)
    out = re.sub(r'databricks\s*/\s*', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\s+to\s+databricks\.?', '.', out, flags=re.IGNORECASE)
    out = re.sub(r'\bdatabricks\b', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\n\s*-\s*\*\*databricks\*\*:.*\n', '\n', out, flags=re.IGNORECASE)
    out = re.sub(r'\n\s*-\s*databricks:.*\n', '\n', out, flags=re.IGNORECASE)
    out = re.sub(r'"databricks"\s*:\s*\{[^}]*\},?\s*', '', out, flags=re.IGNORECASE)
    out = re.sub(r',\s*,', ',', out)
    out = re.sub(r'\s+to\s+\.', '.', out)
    return out

def main():
    import argparse
    import subprocess
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    n = 0
    try:
        r = subprocess.run(
            ["rg", "-l", "-i", "databricks"] + list(SEARCH_DIRS),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        files = [ROOT / p for p in r.stdout.strip().split("\n") if p] if r.returncode == 0 else []
    except Exception:
        files = []
        for d in SEARCH_DIRS:
            base = ROOT / d
            if base.exists():
                files.extend(f for f in base.rglob("*") if f.is_file())
    for f in files:
        if not f.is_file() or any(x in f.parts for x in EXCLUDE):
            continue
        if f.name == "remove_databricks.py":
            continue
        if f.suffix.lower() not in SUFFIXES:
            continue
        try:
            raw = f.read_text(encoding="utf-8", errors="ignore")
            if "databricks" not in raw.lower():
                continue
            out = clean(raw)
            if out != raw:
                rel = f.relative_to(ROOT)
                if args.dry_run:
                    print(f"  [dry-run] {rel}")
                else:
                    f.write_text(out, encoding="utf-8")
                    print(f"  cleaned: {rel}")
                n += 1
        except Exception:
            pass
    print(f"\nTotal: {n} files")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

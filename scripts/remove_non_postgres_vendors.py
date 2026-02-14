#!/usr/bin/env python3
"""Remove databricks, snowflake, and other non-PostgreSQL vendor mentions from repo.
Run from repo root. Replaces remove_databricks.py for comprehensive cleanup.
Processes all files regardless of size (no size-based skip)."""
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXCLUDE = {"node_modules", ".git", ".venv", "__pycache__", ".next", "remove_databricks.py", "remove_non_postgres_vendors.py", "snowflake_credentials.json"}
SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".html", ".ipynb", ".sql", ".sh", ".groovy"}
SEARCH_DIRS = ("source", "scripts", "template", "docs", "archive", ".")

# Combined pattern for rg: match any vendor
VENDOR_PATTERN = "databricks|snowflake"


def clean(content: str) -> str:
    """Remove databricks and snowflake references, normalize to PostgreSQL-only."""
    out = content

    # Preserve script references (update to new script name)
    out = re.sub(r'remove_databricks\.py', 'remove_non_postgres_vendors.py', out, flags=re.IGNORECASE)

    # --- Databricks patterns ---
    out = re.sub(r',?\s*databricks\s*,?', ', ', out, flags=re.IGNORECASE)
    out = re.sub(r'PostgreSQL\s*/\s*databricks', 'PostgreSQL', out, flags=re.IGNORECASE)
    out = re.sub(r'databricks\s*/\s*', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\s+to\s+databricks\.?', '.', out, flags=re.IGNORECASE)
    out = re.sub(r'\bdatabricks\b', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\n\s*-\s*\*\*databricks\*\*:.*\n', '\n', out, flags=re.IGNORECASE)
    out = re.sub(r'\n\s*-\s*databricks:.*\n', '\n', out, flags=re.IGNORECASE)
    out = re.sub(r'"databricks"\s*:\s*\{[^}]*\},?\s*', '', out, flags=re.IGNORECASE)

    # --- Snowflake patterns ---
    out = re.sub(r',?\s*snowflake\s*,?', ', ', out, flags=re.IGNORECASE)
    out = re.sub(r'PostgreSQL\s*/\s*snowflake', 'PostgreSQL', out, flags=re.IGNORECASE)
    out = re.sub(r'snowflake\s*/\s*', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\s+and\s+snowflake\b', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\(PostgreSQL,\s*and\s+Snowflake\)', '(PostgreSQL)', out, flags=re.IGNORECASE)
    out = re.sub(r'Compatible with PostgreSQL,?\s*and\s+Snowflake', 'Compatible with PostgreSQL', out, flags=re.IGNORECASE)
    out = re.sub(r'Compatible with PostgreSQL,?\s*and\s+snowflake', 'Compatible with PostgreSQL', out, flags=re.IGNORECASE)
    out = re.sub(r'\*\*Snowflake\*\*:.*?(?=\n\n|\n-|\Z)', '', out, flags=re.IGNORECASE | re.DOTALL)
    out = re.sub(r'\n\s*-\s*\*\*Snowflake\*\*:.*\n', '\n', out, flags=re.IGNORECASE)
    out = re.sub(r'\n\s*-\s*Snowflake:.*\n', '\n', out, flags=re.IGNORECASE)
    out = re.sub(r'"snowflake"\s*:\s*\{[^}]*\},?\s*', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\bSnowflake\s+Setup:.*?(?=\n\n|\n\d\.|\Z)', '', out, flags=re.IGNORECASE | re.DOTALL)
    out = re.sub(r'3\.\s*\*\*Snowflake\s+Setup\*\*:.*?(?=\n\n|\n\d\.|\Z)', '', out, flags=re.IGNORECASE | re.DOTALL)
    out = re.sub(r'\(Snowflake/\s*,?\s*\)', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\(Snowflake/\)', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\(Snowflake/,?\s*\)', '', out, flags=re.IGNORECASE)
    out = re.sub(r'\([^)]*Snowflake/[^)]*\)', '', out, flags=re.IGNORECASE)
    out = re.sub(r'JSON/variant data \(Snowflake/,?\s*\)', 'JSON/variant data', out, flags=re.IGNORECASE)
    out = re.sub(r'\bsnowflake\b', '', out, flags=re.IGNORECASE)

    # --- Normalize artifacts ---
    out = re.sub(r',\s*,', ',', out)
    out = re.sub(r'\s+to\s+\.', '.', out)
    out = re.sub(r',\s+\)', ')', out)
    out = re.sub(r'\(\s*,', '(', out)
    out = re.sub(r'\n{3,}', '\n\n', out)
    return out


CHUNK_SIZE = 64 * 1024 * 1024  # 64MB
OVERLAP = 512  # Avoid splitting words like "databricks" across chunks


def _process_large_file(path: Path, clean_fn, dry_run: bool = False) -> tuple[str, str]:
    """Process large file in chunks; stream to temp file to avoid loading multi-GB into memory."""
    import tempfile
    import shutil
    # Quick scan to detect if file has matches (avoid full read if not)
    has_match = False
    with path.open(encoding="utf-8", errors="ignore") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), ""):
            if "databricks" in chunk.lower() or "snowflake" in chunk.lower():
                has_match = True
                break
    if not has_match:
        return "", ""  # Caller will skip (has_match check uses raw)
    if dry_run:
        return "databricks", ""  # Signal: would modify
    # Process in chunks, write to temp
    fd, tmp = tempfile.mkstemp(suffix=".tmp", prefix="clean_")
    try:
        with path.open(encoding="utf-8", errors="ignore") as fp, open(fd, "w", encoding="utf-8") as out_fp:
            buffer = ""
            while True:
                chunk = fp.read(CHUNK_SIZE)
                if not chunk and not buffer:
                    break
                work = buffer + chunk
                if not chunk:
                    out_fp.write(clean_fn(work))
                    break
                last_nl = work.rfind("\n", 0, max(1, len(work) - OVERLAP))
                if last_nl < 0:
                    last_nl = max(0, len(work) - OVERLAP)
                process_part = work[: last_nl + 1]
                buffer = work[last_nl + 1 :]
                out_fp.write(clean_fn(process_part))
        shutil.move(tmp, path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise
    return "databricks", ""  # Signal: file was modified (has_match=True, raw!=out)

def main():
    import argparse
    import subprocess
    ap = argparse.ArgumentParser(description="Remove databricks/snowflake from repo")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--databricks-only", action="store_true", help="Only clean databricks (legacy)")
    ap.add_argument("--snowflake-only", action="store_true", help="Only clean snowflake")
    args = ap.parse_args()

    pattern = "databricks" if args.databricks_only else ("snowflake" if args.snowflake_only else VENDOR_PATTERN)
    n = 0
    try:
        r = subprocess.run(
            ["rg", "-l", "-i", pattern] + list(SEARCH_DIRS),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        files = [ROOT / p for p in r.stdout.strip().split("\n") if p] if r.returncode == 0 else []
    except Exception:
        files = []
        for d in SEARCH_DIRS:
            base = ROOT / d if d != "." else ROOT
            if not base.exists():
                continue
            if base.is_file():
                files.append(base)
            else:
                files.extend(f for f in base.rglob("*") if f.is_file())

    seen = set()
    for f in files:
        try:
            f = Path(f) if not isinstance(f, Path) else f
            if not f.is_file() or any(x in f.parts for x in EXCLUDE):
                continue
            if f.name in ("remove_databricks.py", "remove_non_postgres_vendors.py"):
                continue
            if f.suffix.lower() not in SUFFIXES and f.name not in ("Makefile", "Jenkinsfile"):
                continue
            if str(f) in seen:
                continue
            seen.add(str(f))
            size_mb = f.stat().st_size / (1024 * 1024)
            if size_mb > 50:
                raw, out = _process_large_file(f, clean, args.dry_run)
            else:
                raw = f.read_text(encoding="utf-8", errors="ignore")
                out = clean(raw)
            lower = raw.lower()
            has_match = ("databricks" in lower if "databricks" in pattern else False) or (
                "snowflake" in lower if "snowflake" in pattern else False
            )
            if not has_match:
                continue
            if out != raw:
                try:
                    rel = f.relative_to(ROOT)
                except ValueError:
                    rel = f
                if args.dry_run:
                    print(f"  [dry-run] {rel}")
                elif size_mb <= 50:
                    f.write_text(out, encoding="utf-8")
                    print(f"  cleaned: {rel}")
                else:
                    print(f"  cleaned: {rel} (streamed)")
                n += 1
        except Exception:
            pass
    print(f"\nTotal: {n} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
2^6 artifact audit: 6 binary dimensions × 64 combinations.
Metaprogrammatic recursive scan for useless artifacts.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).parent.parent
EXCLUDE = {"node_modules", ".git", ".venv", "venv_selenium", "__pycache__", ".pytest_cache", ".next"}


def should_skip(p: Path) -> bool:
    return any(x in p.parts for x in EXCLUDE)


def d1_backup(p: Path) -> bool:
    """D1: backup/bak/bak2/tmp"""
    return bool(re.search(r"\.(backup|bak|bak2|tmp)(\.|$)", p.name))


def d2_lock_temp(p: Path) -> bool:
    """D2: lock/temp files"""
    return p.name.startswith(".~lock") or p.suffix in (".tmp", ".temp")


def d3_empty(p: Path) -> bool:
    """D3: empty files (exclude valid empties)"""
    if not p.is_file():
        return False
    try:
        return p.stat().st_size == 0
    except OSError:
        return False


def d4_ds_store(p: Path) -> bool:
    """D4: macOS .DS_Store"""
    return p.name == ".DS_Store"


def d5_wrong_location(p: Path) -> bool:
    """D5: files in wrong canonical location"""
    s = str(p)
    if "DATABASE (1)" in s or "LEGAL (1)" in s:
        return True
    if "source/db-" in s and "/QUERIES/" in s and "/app/" not in s:
        return "queries" in p.name and "archive" not in s
    return False


def d6_duplicate_stem(p: Path) -> bool:
    """D6: duplicate basename patterns (simplified)"""
    return "_20260213" in p.name or "_20260204" in p.name


def scan(root: Path) -> dict:
    """Recursive scan, 6 dimensions."""
    out = {
        "d1_backup": [],
        "d2_lock_temp": [],
        "d3_empty": [],
        "d4_ds_store": [],
        "d5_wrong_loc": [],
        "d6_duplicate": [],
        "summary": {},
    }
    for f in root.rglob("*"):
        if not f.is_file() or should_skip(f):
            continue
        rel = f.relative_to(root)
        if d1_backup(f):
            out["d1_backup"].append(str(rel))
        if d2_lock_temp(f):
            out["d2_lock_temp"].append(str(rel))
        if d3_empty(f) and "py.typed" not in str(f) and "__init__.py" not in str(f):
            if "venv" not in str(f) and "node_modules" not in str(f):
                out["d3_empty"].append(str(rel))
        if d4_ds_store(f):
            out["d4_ds_store"].append(str(rel))
        if d5_wrong_location(f):
            out["d5_wrong_loc"].append(str(rel))
        if d6_duplicate_stem(f) and "archive" not in str(f):
            out["d6_duplicate"].append(str(rel))
    out["summary"] = {k: len(v) for k, v in out.items() if isinstance(v, list)}
    return out


def clean(r: dict, dry_run: bool = True) -> int:
    """Remove artifacts. Returns count removed."""
    removed = 0
    for key in ("d1_backup", "d2_lock_temp", "d4_ds_store"):
        for rel in r.get(key, []):
            p = ROOT / rel
            if p.exists():
                if dry_run:
                    print(f"  [dry-run] would remove: {rel}")
                else:
                    p.unlink()
                    print(f"  removed: {rel}")
                removed += 1
    return removed


def main():
    import argparse
    ap = argparse.ArgumentParser(description="2^6 artifact audit")
    ap.add_argument("--clean", action="store_true", help="Remove d1,d2,d4 artifacts")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be removed")
    args = ap.parse_args()
    r = scan(ROOT)
    print(json.dumps(r, indent=2))
    total = sum(v for k, v in r["summary"].items() if isinstance(v, int))
    print(f"\nTotal artifacts: {total}")
    if args.clean:
        n = clean(r, dry_run=args.dry_run)
        print(f"Cleaned: {n} files")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

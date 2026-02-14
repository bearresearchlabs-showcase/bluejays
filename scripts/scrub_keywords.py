#!/usr/bin/env python3
"""Configurable keyword scrubbing tool for repo cleanup.
Supports worktree partitioning for Cursor's 4x Parallel Agents.
Safe for concurrent execution when using --worktree (each process gets disjoint files).

Library usage:
  from scripts.scrub_keywords import scrub_run, load_config
  n = scrub_run(worktree_index=0, worktree_total=4)

CLI usage:
  python3 scripts/scrub_keywords.py
  python3 scripts/scrub_keywords.py --worktree 0 4
  python -m scripts.scrub_keywords --dry-run
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import Callable

__all__ = [
    "load_config",
    "build_clean_fn",
    "get_keywords",
    "find_files",
    "partition_files",
    "scrub_run",
]

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / ".cursor" / "scrub_config.yaml"
EXCLUDE = {"node_modules", ".git", ".venv", "__pycache__", ".next"}
SUFFIXES = {".md", ".py", ".yaml", ".yml", ".json", ".html", ".ipynb", ".sql", ".sh", ".groovy"}
SEARCH_DIRS = ("source", "scripts", "template", "docs", "archive", ".")
CHUNK_SIZE = 64 * 1024 * 1024
OVERLAP = 512


def load_config(path: Path) -> dict:
    """Load scrub config from YAML."""
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return {}


def build_clean_fn(config: dict):
    """Build clean function from config patterns."""
    patterns = config.get("patterns", [])
    if not patterns:
        return lambda s: s

    def clean(content: str) -> str:
        out = content
        for p in patterns:
            find = p.get("find")
            replace = p.get("replace", "")
            flags = re.IGNORECASE if p.get("ignore_case", True) else 0
            if not find:
                continue
            try:
                out = re.sub(find, replace, out, flags=flags)
            except re.error:
                out = out.replace(find, replace) if not p.get("regex", True) else out
        # Normalize artifacts
        out = re.sub(r',\s*,', ',', out)
        out = re.sub(r'\n{3,}', '\n\n', out)
        return out

    return clean


def get_keywords(config: dict) -> str:
    """Get pipe-separated keywords for rg search."""
    if "keywords" in config:
        return str(config["keywords"])
    keywords = []
    for p in config.get("patterns", []):
        find = p.get("find")
        if find and p.get("regex", True):
            m = re.search(r'\\b(\w+)\\b', find)
            if m:
                keywords.append(m.group(1).lower())
    return "|".join(k for k in keywords if k)


def find_files(root: Path, pattern: str) -> list[Path]:
    """Find files containing pattern."""
    try:
        r = subprocess.run(
            ["rg", "-l", "-i", pattern] + list(SEARCH_DIRS),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode == 0:
            return [root / p for p in r.stdout.strip().split("\n") if p]
    except Exception:
        pass
    files = []
    for d in SEARCH_DIRS:
        base = root / d if d != "." else root
        if not base.exists():
            continue
        if base.is_file():
            files.append(base)
        else:
            files.extend(f for f in base.rglob("*") if f.is_file())
    return files


def partition_files(files: list[Path], index: int, total: int) -> list[Path]:
    """Partition files for worktree index (0..total-1)."""
    if total <= 1:
        return files
    sorted_files = sorted(files, key=lambda p: str(p))
    return [f for i, f in enumerate(sorted_files) if i % total == index]


def _process_large_file(path: Path, clean_fn, keywords: str, dry_run: bool) -> tuple[str | None, str | None]:
    """Stream large file, apply clean. Returns (None, None) if no match, else (dummy, dummy) when modified."""
    import shutil
    import tempfile

    kws = keywords.lower().split("|")
    has_match = False
    with path.open(encoding="utf-8", errors="ignore") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), ""):
            if any(kw in chunk.lower() for kw in kws):
                has_match = True
                break
    if not has_match:
        return None, None
    if dry_run:
        return "_", "_"
    # Process-prefix avoids temp collisions when many concurrent sessions run
    fd, tmp = tempfile.mkstemp(suffix=".tmp", prefix=f"scrub_{os.getpid()}_")
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
    return "_", "_"


def scrub_run(
    root: Path | None = None,
    config_path: Path | None = None,
    dry_run: bool = False,
    worktree_index: int | None = None,
    worktree_total: int | None = None,
    exclude_extra: set[str] | None = None,
    on_file: Callable[[Path, bool], None] | None = None,
) -> int:
    """Run scrub. Callable from other modules. Safe for concurrent sessions with worktree partitioning.

    Args:
        root: Repo root (default: parent of script)
        config_path: Config YAML path
        dry_run: If True, don't write
        worktree_index: Partition index (0..worktree_total-1)
        worktree_total: Total partitions for concurrent runs
        exclude_extra: Additional exclude names
        on_file: Callback(path, streamed) when a file is cleaned

    Returns:
        Number of files cleaned.
    """
    root = Path(root or ROOT).resolve()
    config_path = config_path or (root / ".cursor" / "scrub_config.yaml")
    config = load_config(config_path)
    if not config:
        return -1
    clean_fn = build_clean_fn(config)
    keywords = get_keywords(config)
    if not keywords:
        return -1
    exclude = set(config.get("exclude", [])) | EXCLUDE | (exclude_extra or set())
    exclude.update(("scrub_keywords.py", "remove_databricks.py", "remove_non_postgres_vendors.py"))

    files = find_files(root, keywords)
    if worktree_index is not None and worktree_total is not None and worktree_total > 1:
        files = partition_files(files, worktree_index, worktree_total)

    seen = set()
    n = 0
    for f in files:
        try:
            f = Path(f)
            if not f.is_file() or any(x in f.parts for x in exclude):
                continue
            if f.suffix.lower() not in SUFFIXES and f.name not in ("Makefile", "Jenkinsfile"):
                continue
            if str(f) in seen or f.name in exclude:
                continue
            seen.add(str(f))
            size_mb = f.stat().st_size / (1024 * 1024)
            modified = False
            if size_mb > 50:
                raw, out = _process_large_file(f, clean_fn, keywords, dry_run)
                if raw is None or out is None:
                    continue
                modified = True
            else:
                raw = f.read_text(encoding="utf-8", errors="ignore")
                out = clean_fn(raw)
                if not raw or out == raw:
                    continue
                if not any(kw in raw.lower() for kw in keywords.split("|")):
                    continue
                modified = True
            if dry_run:
                pass
            elif size_mb <= 50:
                f.write_text(out, encoding="utf-8")
            if modified:
                n += 1
            if on_file:
                try:
                    rel = f.relative_to(root)
                except ValueError:
                    rel = f
                on_file(rel, size_mb > 50)
        except Exception:
            pass
    return n


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Scrub configurable keywords from repo")
    ap.add_argument("--config", type=Path, default=None, help="Config YAML path")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--worktree", nargs=2, metavar=("INDEX", "TOTAL"), help="Worktree index and total (e.g. 0 4 for 4x parallel)")
    args = ap.parse_args()

    worktree_index = worktree_total = None
    if args.worktree:
        worktree_index, worktree_total = int(args.worktree[0]), int(args.worktree[1])

    def on_file(rel: Path, streamed: bool) -> None:
        if args.dry_run:
            print(f"  [dry-run] {rel}", flush=True)
        else:
            suffix = " (streamed)" if streamed else ""
            print(f"  cleaned: {rel}{suffix}", flush=True)

    n = scrub_run(
        config_path=args.config,
        dry_run=args.dry_run,
        worktree_index=worktree_index,
        worktree_total=worktree_total,
        on_file=on_file,
    )
    if n < 0:
        print("No config or empty config. Create .cursor/scrub_config.yaml", file=__import__("sys").stderr)
        return 1
    print(f"\nTotal: {n} files", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

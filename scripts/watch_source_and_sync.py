#!/usr/bin/env python3
"""
File-based CDC: Watch source/ for changes and propagate to app/, client/, and optionally Docker.

Watches: queries.json, queries_header.yaml, schema.sql, data.sql.
On change: run source_material_checks → populate_app_trifecta → resync_client_db → (optional) docker_postgres_qa.

Usage:
    python3 scripts/watch_source_and_sync.py              # Daemon mode
    python3 scripts/watch_source_and_sync.py --once db-1   # One-shot for db-1
    python3 scripts/watch_source_and_sync.py --no-docker   # Skip Docker reload
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

WATCHED_FILES = {"queries.json", "queries_header.yaml", "queries_header.json", "schema.sql", "data.sql"}


def extract_db_num_from_path(path: Path) -> int | None:
    """Extract db-N from path like source/db-3/queries/queries.json."""
    try:
        parts = path.relative_to(SOURCE).parts
        if parts and parts[0].startswith("db-"):
            n = int(parts[0].replace("db-", ""))
            if 1 <= n <= 16:
                return n
    except (ValueError, IndexError):
        pass
    return None


def run_sync_for_db(db_num: int, reload_docker: bool = True) -> bool:
    """Run checks, populate, resync, and optionally Docker for one db-N."""
    from source_material_checks import check_db

    r = check_db(db_num)
    if not r["pass"]:
        print(f"  db-{db_num}: source checks FAILED, skipping sync")
        for e in r.get("errors", []):
            print(f"    ERROR: {e}")
        return False

    subprocess.run(
        [sys.executable, str(SCRIPTS / "populate_app_trifecta.py"), f"db-{db_num}"],
        cwd=ROOT,
        capture_output=True,
        timeout=60,
    )
    subprocess.run(
        [sys.executable, str(SCRIPTS / "resync_client_db.py"), "--dbs", str(db_num)],
        cwd=ROOT,
        capture_output=True,
        timeout=30,
    )

    if reload_docker:
        subprocess.run(
            ["bash", str(SCRIPTS / "docker_postgres_qa.sh"), f"db-{db_num}"],
            cwd=ROOT,
            capture_output=True,
            timeout=120,
        )
    return True


def main():
    ap = argparse.ArgumentParser(description="Watch source/ and sync on change (file-based CDC)")
    ap.add_argument("dbs", nargs="*", help="db-1, db-2, ... or empty for all on change")
    ap.add_argument("--once", action="store_true", help="Run once for specified dbs, then exit")
    ap.add_argument("--no-docker", action="store_true", help="Skip Docker PostgreSQL reload")
    ap.add_argument("--debounce", type=float, default=2.0, help="Debounce seconds (default 2)")
    args = ap.parse_args()

    if args.once:
        db_nums = []
        for a in args.dbs:
            a = str(a).replace("db-", "")
            try:
                db_nums.append(int(a))
            except ValueError:
                pass
        if not db_nums:
            db_nums = list(range(1, 17))
        for n in db_nums:
            run_sync_for_db(n, reload_docker=not args.no_docker)
        return 0

    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("Install watchdog: pip install watchdog")
        return 1

    pending: set[int] = set()
    last_run: dict[int, float] = {}

    class Handler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.is_directory:
                return
            p = Path(event.src_path)
            if p.name not in WATCHED_FILES:
                return
            n = extract_db_num_from_path(p)
            if n:
                pending.add(n)

    observer = Observer()
    observer.schedule(Handler(), str(SOURCE), recursive=True)
    observer.start()
    print(f"Watching {SOURCE} for {WATCHED_FILES}... (Ctrl+C to stop)")

    try:
        while True:
            time.sleep(args.debounce)
            now = time.time()
            for n in list(pending):
                if now - last_run.get(n, 0) < args.debounce:
                    continue
                print(f"\n[{time.strftime('%H:%M:%S')}] Syncing db-{n}...")
                run_sync_for_db(n, reload_docker=not args.no_docker)
                last_run[n] = now
                pending.discard(n)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Watch mode: run validate/build/qa when any file in the repo changes.
Polls every 0.5 seconds for changes in source/, scripts/, template/.
Usage:
  python3 scripts/watch_validate.py              # validate db-1 on change
  python3 scripts/watch_validate.py validate db-1 db-2
  python3 scripts/watch_validate.py build db-1    # build (includes format step)
  python3 scripts/watch_validate.py qa -a
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
INTERVAL = 0.5
WATCH_DIRS = ("source", "scripts", "template", ".cursor")


def _collect_mtimes(root: Path, dirs: tuple) -> dict:
    out = {}
    for d in dirs:
        p = root / d
        if not p.exists():
            continue
        for f in p.rglob("*"):
            if f.is_file() and ".git" not in str(f):
                try:
                    out[str(f)] = os.path.getmtime(f)
                except OSError:
                    pass
    return out


def main():
    argv = sys.argv[1:]
    if argv and argv[0] in ("validate", "build", "qa", "integrity", "compliance"):
        subcmd = argv[0]
        args = argv[1:] or ["db-1"]
    else:
        subcmd = "validate"
        args = argv or ["db-1"]
    cmd = [sys.executable, str(ROOT / "scripts" / "db_check.py"), subcmd] + args
    print(f"Watching: {WATCH_DIRS}")
    print(f"On change: {' '.join(cmd)}")
    print(f"Poll: {INTERVAL}s (Ctrl+C to stop)\n")
    prev = _collect_mtimes(ROOT, WATCH_DIRS)
    try:
        while True:
            time.sleep(INTERVAL)
            curr = _collect_mtimes(ROOT, WATCH_DIRS)
            if prev != curr:
                prev = curr
                subprocess.run(cmd, cwd=str(ROOT))
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

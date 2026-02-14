#!/usr/bin/env python3
"""
Rotate/trim DB check logs to prevent unbounded growth.
Keeps last N lines of db_check.log and last M telemetry entries.
Usage: python3 scripts/rotate_logs.py [--max-lines 10000] [--max-telemetry 1000]
"""

import argparse
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
log_dir = root_dir / "logs"


def rotate_log(max_lines: int = 10000) -> None:
    """Keep last max_lines of db_check.log."""
    log_file = log_dir / "db_check.log"
    if not log_file.exists():
        return
    lines = log_file.read_text(encoding="utf-8").splitlines()
    if len(lines) <= max_lines:
        return
    kept = lines[-max_lines:]
    log_file.write_text("\n".join(kept) + "\n")


def rotate_telemetry(max_entries: int = 1000) -> None:
    """Keep last max_entries of telemetry.ndjson."""
    ndjson_file = log_dir / "telemetry.ndjson"
    if not ndjson_file.exists():
        return
    lines = [l for l in ndjson_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    if len(lines) <= max_entries:
        return
    kept = lines[-max_entries:]
    ndjson_file.write_text("\n".join(kept) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-lines", type=int, default=10000, help="Max lines in db_check.log")
    ap.add_argument("--max-telemetry", type=int, default=1000, help="Max entries in telemetry.ndjson")
    args = ap.parse_args()

    if not log_dir.exists():
        return 0

    rotate_log(args.max_lines)
    rotate_telemetry(args.max_telemetry)
    return 0


if __name__ == "__main__":
    sys.exit(main())

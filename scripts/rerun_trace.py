#!/usr/bin/env python3
"""
Replay commands from a session trace.
Usage: rerun_trace.py {session_id}
Uses traces/{session_id}/config.json and run.ndjson for reproducibility.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
TRACES_DIR = root_dir / "traces"


def load_config(session_id: str) -> Optional[dict]:
    """Load config.json for session."""
    path = TRACES_DIR / session_id / "config.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def infer_command(config: dict) -> Optional[str]:
    """
    Infer the command to replay from config args.
    db_check uses args like ["validate", "1"] -> python3 scripts/db_check.py validate 1
    """
    args = config.get("args", [])
    if not args:
        return None
    # Assume db_check if first arg is a known subcommand
    subcmd = args[0].lower() if args else ""
    known = {"validate", "format", "qa", "integrity", "compliance", "qa-suite", "full", "rotate", "debug"}
    if subcmd in known:
        cmd = ["python3", str(scripts_dir / "db_check.py")] + args
        return " ".join(cmd)
    # Generic: assume db_check
    cmd = ["python3", str(scripts_dir / "db_check.py")] + args
    return " ".join(cmd)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: rerun_trace.py <session_id>")
        print("Example: rerun_trace.py 14628b73-78f7-4ace-9e56-49f505ee789a")
        return 1

    session_id = sys.argv[1].strip()
    config = load_config(session_id)
    if not config:
        print(f"Trace not found: {TRACES_DIR / session_id}")
        return 1

    cmd_str = infer_command(config)
    if not cmd_str:
        print("Could not infer command from config args:", config.get("args"))
        return 1

    print(f"Replaying session {session_id}")
    print(f"Command: {cmd_str}")
    ec = subprocess.call(cmd_str, shell=True, cwd=str(root_dir))
    return ec


if __name__ == "__main__":
    sys.exit(main())

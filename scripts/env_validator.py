#!/usr/bin/env python3
"""
Validate and load .env for DB check infrastructure.
Loads root .env and client/.env (client overrides root).
Fails fast with clear error if required vars missing for operation.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Set

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent

# Required vars per operation
REQUIRED_FOR_DB = {"PG_HOST", "PG_USER", "PG_PASSWORD", "PG_DATABASE"}
REQUIRED_FOR_CLAUDE = {"ANTHROPIC_API_KEY"}
REQUIRED_FOR_K8S = {"KUBE_NAMESPACE"}


def load_dotenv(path: Path) -> None:
    """Load .env file into os.environ (simple parser, no external deps)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1].replace('\\"', '"')
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1].replace("\\'", "'")
            os.environ[key] = value


def load_env() -> None:
    """Load root .env then client/.env (client overrides)."""
    load_dotenv(root_dir / ".env")
    load_dotenv(root_dir / "client" / ".env")


def validate_required(required: Set[str], operation: str) -> bool:
    """Check required vars are set. Returns True if ok, False and prints error otherwise."""
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"ERROR: Missing required env vars for {operation}: {', '.join(missing)}", file=sys.stderr)
        print("Set them in .env or client/.env. See .env.example", file=sys.stderr)
        return False
    return True


def ensure_env(operation: str = "db") -> bool:
    """
    Load env and validate for operation.
    operation: "db" | "claude" | "k8s" | "all"
    Returns True if valid, False otherwise.
    """
    load_env()
    if operation == "db":
        return validate_required(REQUIRED_FOR_DB, "database operations (PG_*)")
    if operation == "claude":
        return validate_required(REQUIRED_FOR_CLAUDE, "Claude QA (ANTHROPIC_API_KEY)")
    if operation == "k8s":
        return validate_required(REQUIRED_FOR_K8S, "Kubernetes (KUBE_NAMESPACE)")
    if operation == "all":
        ok = validate_required(REQUIRED_FOR_DB, "database")
        ok = validate_required(REQUIRED_FOR_CLAUDE, "Claude") and ok
        ok = validate_required(REQUIRED_FOR_K8S, "K8s") and ok
        return ok
    return True


def main() -> int:
    """CLI: validate env for given operation."""
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--op", choices=["db", "claude", "k8s", "all"], default="db")
    args = ap.parse_args()
    load_env()
    if ensure_env(args.op):
        print("OK: env valid for", args.op)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Unify all artifacts from the single source of truth (db-N/).
Runs: resync -> verify. Optionally prepares zip for distribution.

Usage:
    python3 scripts/unify_from_source.py              # Resync + verify
    python3 scripts/unify_from_source.py --zip        # Also prepare drive-ready zip
"""
import argparse
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent


def run(cmd: list[str], desc: str) -> bool:
    print(f"\n{'='*60}\n{desc}\n{'='*60}")
    r = subprocess.run(cmd, cwd=BASE)
    return r.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Unify client and zip from source (db-N/)")
    parser.add_argument("--zip", action="store_true", help="Also prepare db_drive_ready and zip")
    parser.add_argument("--skip-verify", action="store_true", help="Skip byte-for-byte verification")
    args = parser.parse_args()

    print("Unifying from SOURCE OF TRUTH: db-N/")
    print("Flow: source -> resync -> client -> [prepare -> zip]")

    if not run([sys.executable, str(BASE / "scripts" / "resync_client_db.py")], "1. Resync source -> client"):
        sys.exit(1)

    if not args.skip_verify:
        if not run([sys.executable, str(BASE / "scripts" / "reconcile_and_verify_queries.py"), "--skip-resync"],
                   "2. Verify byte-for-byte (source = client)"):
            sys.exit(1)

    if args.zip:
        if not run([sys.executable, str(BASE / "scripts" / "prepare_client_db_for_drive.py")],
                   "3. Prepare client for Drive"):
            sys.exit(1)
        if not run([sys.executable, str(BASE / "scripts" / "create_drive_upload_package.py")],
                   "4. Create zip package"):
            sys.exit(1)

    print("\n" + "=" * 60)
    print("Unify complete. Client (and zip if --zip) now match source.")
    print("=" * 60)


if __name__ == "__main__":
    main()

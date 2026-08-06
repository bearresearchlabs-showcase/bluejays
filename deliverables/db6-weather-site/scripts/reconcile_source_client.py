#!/usr/bin/env python3
"""
Reconcile source (main db-N) with client/db and repopulate.
1. Generate web deliverable from db-N/data -> deliverable/dbN-*/
2. Resync client from main (db-N/data primary, deliverable secondary)

Usage:
    python3 scripts/reconcile_source_client.py
    python3 scripts/reconcile_source_client.py --dbs 1 6 10
"""

import argparse
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def main():
    parser = argparse.ArgumentParser(description="Reconcile source with client and repopulate")
    parser.add_argument("--dbs", type=int, nargs="*", help="DB numbers (default: 1-16)")
    args = parser.parse_args()

    db_nums = args.dbs if args.dbs else list(range(1, 17))

    print("=" * 60)
    print("Reconcile: source -> deliverable -> client")
    print("=" * 60)

    # 1. Generate web deliverable (db-N/data -> deliverable)
    print("\n1. Generating web deliverable from db-N/data...")
    cmd = [sys.executable, str(BASE_DIR / "scripts" / "generate_web_deliverable.py")] + [str(n) for n in db_nums]
    r = subprocess.run(cmd, cwd=BASE_DIR)
    if r.returncode != 0:
        sys.exit(r.returncode)

    # 2. Resync client from main
    print("\n2. Resyncing client from main source...")
    cmd = [sys.executable, str(BASE_DIR / "scripts" / "resync_client_db.py"), "--dbs"] + [str(n) for n in db_nums]
    r = subprocess.run(cmd, cwd=BASE_DIR)
    if r.returncode != 0:
        sys.exit(r.returncode)

    print("\n" + "=" * 60)
    print("Reconcile complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()

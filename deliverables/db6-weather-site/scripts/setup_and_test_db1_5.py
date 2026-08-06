#!/usr/bin/env python3
"""
Setup databases db-1 through db-5 and run query tests.
Creates databases, loads schema.sql + data.sql, then runs test_all_queries_postgresql.
"""

import os
import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).parent.parent
PG_HOST = os.environ.get("PG_HOST", "127.0.0.1")
PG_PORT = int(os.environ.get("PG_PORT", "5432"))
PG_USER = os.environ.get("PG_USER", os.environ.get("USER", "postgres"))
PG_PASSWORD = os.environ.get("PG_PASSWORD", "")


def run_psql(db_name: str, sql_file: Path, extra_args: list = None) -> bool:
    """Run SQL file against database via psql."""
    env = os.environ.copy()
    if PG_PASSWORD:
        env["PGPASSWORD"] = PG_PASSWORD
    cmd = [
        "psql",
        "-h", PG_HOST,
        "-p", str(PG_PORT),
        "-U", PG_USER,
        "-d", db_name,
        "-f", str(sql_file),
        "-v", "ON_ERROR_STOP=0",
        "-q",
    ]
    if extra_args:
        cmd.extend(extra_args)
    try:
        r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
        return r.returncode == 0 or "CREATE" in (r.stdout or "") or "INSERT" in (r.stdout or "")
    except Exception as e:
        print(f"  Error: {e}")
        return False


def create_db(db_name: str) -> bool:
    """Drop if exists and create database."""
    env = os.environ.copy()
    if PG_PASSWORD:
        env["PGPASSWORD"] = PG_PASSWORD
    try:
        subprocess.run(
            ["dropdb", "-h", PG_HOST, "-p", str(PG_PORT), "-U", PG_USER, "--if-exists", db_name],
            env=env, capture_output=True, timeout=10
        )
        subprocess.run(
            ["createdb", "-h", PG_HOST, "-p", str(PG_PORT), "-U", PG_USER, db_name],
            env=env, capture_output=True, timeout=10, check=True
        )
        return True
    except Exception as e:
        print(f"  create_db error: {e}")
    return False


def main():
    print("=" * 70)
    print("Setup and Test db-1 through db-5")
    print("=" * 70)

    # Ensure PostgreSQL is reachable
    try:
        subprocess.run(
            ["psql", "-h", PG_HOST, "-p", str(PG_PORT), "-U", PG_USER, "-d", "postgres",
             "-c", "SELECT 1"],
            env={**os.environ, "PGPASSWORD": PG_PASSWORD} if PG_PASSWORD else os.environ,
            capture_output=True, check=True, timeout=5
        )
    except Exception as e:
        print(f"\nPostgreSQL not available: {e}")
        print("Start PostgreSQL and set PG_HOST, PG_PORT, PG_USER, PG_PASSWORD if needed.")
        return 1

    for n in range(1, 6):
        db_name = f"db{n}"
        db_dir = BASE / f"db-{n}" / "data"
        schema_file = db_dir / "schema.sql"
        data_file = db_dir / "data.sql"

        print(f"\n--- db-{n} ---")
        create_db(db_name)

        if schema_file.exists():
            print(f"  Loading schema...")
            run_psql(db_name, schema_file)
        else:
            print(f"  No schema.sql")

        schema_models = db_dir / "schema_models.sql"
        if schema_models.exists():
            print(f"  Loading schema_models...")
            run_psql(db_name, schema_models)

        if data_file.exists():
            print(f"  Loading data...")
            run_psql(db_name, data_file)
        else:
            print(f"  No data.sql")

    print("\n" + "=" * 70)
    print("Running query tests...")
    print("=" * 70)

    # Run test_all_queries_postgresql for db 1-5
    sys.path.insert(0, str(BASE / "scripts"))
    from test_all_queries_postgresql import test_database

    for n in range(1, 6):
        result = test_database(n, BASE)
        status = result.get("status", "UNKNOWN")
        err = result.get("error", "")
        print(f"  db-{n}: {status}" + (f" - {err[:50]}" if err else ""))

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

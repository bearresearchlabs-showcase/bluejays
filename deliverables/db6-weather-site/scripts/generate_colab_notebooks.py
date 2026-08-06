#!/usr/bin/env python3
"""
Generate clean, Colab-compatible Jupyter notebooks for each database.
Produces properly formatted .ipynb files that work on Google Colab.
"""

import json
import sys
from pathlib import Path


def make_md_cell(source: str) -> dict:
    """Create a markdown cell."""
    lines = [line + '\n' for line in source.split('\n')]
    if lines:
        lines[-1] = lines[-1].rstrip('\n')
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": lines
    }


def make_code_cell(source: str) -> dict:
    """Create a code cell with proper line formatting."""
    lines = [line + '\n' for line in source.split('\n')]
    if lines:
        lines[-1] = lines[-1].rstrip('\n')
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines
    }


def generate_notebook(db_num: int, db_name: str, queries: list,
                      schema_sql: str, has_data_large: bool) -> dict:
    """Generate a complete Colab notebook for a database."""

    db_id = f"db-{db_num}"
    pg_db_name = f"db{db_num}"

    cells = []

    # ── Title ──
    cells.append(make_md_cell(
        f"# {db_id}: {db_name} - Query Testing Notebook\n"
        f"\n"
        f"This notebook tests all 30 SQL queries for **{db_id}** on PostgreSQL in Google Colab.\n"
        f"\n"
        f"**Steps:**\n"
        f"1. Install PostgreSQL and psycopg2\n"
        f"2. Create database and load schema\n"
        f"3. Load sample data\n"
        f"4. Execute all 30 queries\n"
        f"5. Generate results report"
    ))

    # ── Cell 1: Colab environment check ──
    cells.append(make_code_cell(
        '# Verify Google Colab environment\n'
        'import sys\n'
        'import os\n'
        '\n'
        'IS_COLAB = False\n'
        'try:\n'
        '    import google.colab\n'
        '    IS_COLAB = True\n'
        'except ImportError:\n'
        '    if os.path.exists("/content"):\n'
        '        IS_COLAB = True\n'
        '\n'
        'if IS_COLAB:\n'
        '    print("Running in Google Colab")\n'
        'else:\n'
        '    print("Not running in Colab - some cells may need adjustment")\n'
        '\n'
        f'DB_NUM = {db_num}\n'
        f'DB_NAME = "{pg_db_name}"\n'
        f'DB_LABEL = "{db_name}"\n'
        'print(f"Database: {DB_NAME} ({DB_LABEL})")'
    ))

    # ── Cell 2: Install PostgreSQL ──
    cells.append(make_md_cell("## Step 1: Install PostgreSQL"))
    cells.append(make_code_cell(
        '# Install PostgreSQL on Colab\n'
        'import subprocess\n'
        'import shutil\n'
        '\n'
        'if IS_COLAB:\n'
        '    print("Installing PostgreSQL...")\n'
        '    subprocess.run(["apt-get", "update", "-qq"], capture_output=True)\n'
        '    subprocess.run(\n'
        '        ["apt-get", "install", "-y", "-qq", "postgresql", "postgresql-contrib", "libpq-dev"],\n'
        '        capture_output=True\n'
        '    )\n'
        '    # Start PostgreSQL\n'
        '    subprocess.run(["service", "postgresql", "start"], capture_output=True)\n'
        '    # Set postgres user password\n'
        '    subprocess.run(\n'
        '        ["sudo", "-u", "postgres", "psql", "-c", "ALTER USER postgres PASSWORD \'postgres\';"],\n'
        '        capture_output=True\n'
        '    )\n'
        '    print("PostgreSQL installed and started")\n'
        'else:\n'
        '    print("Skipping PostgreSQL install (not Colab)")\n'
        '    print("Ensure PostgreSQL is running locally")'
    ))

    # ── Cell 3: Install Python packages ──
    cells.append(make_md_cell("## Step 2: Install Python Packages"))
    cells.append(make_code_cell(
        '# Install required Python packages\n'
        'import subprocess\n'
        'import sys\n'
        '\n'
        'packages = [\n'
        '    "psycopg2-binary>=2.9.0",\n'
        '    "pandas>=2.0.0",\n'
        '    "matplotlib>=3.7.0",\n'
        '    "seaborn>=0.12.0",\n'
        ']\n'
        '\n'
        'for pkg in packages:\n'
        '    name = pkg.split(">=")[0]\n'
        '    try:\n'
        '        __import__(name.replace("-binary", "").replace("-", "_"))\n'
        '        print(f"  {name}: already installed")\n'
        '    except ImportError:\n'
        '        print(f"  {name}: installing...")\n'
        '        subprocess.check_call(\n'
        '            [sys.executable, "-m", "pip", "install", pkg, "-q"],\n'
        '            stdout=subprocess.DEVNULL\n'
        '        )\n'
        '        print(f"  {name}: installed")\n'
        '\n'
        'import psycopg2\n'
        'import pandas as pd\n'
        'import matplotlib.pyplot as plt\n'
        'import seaborn as sns\n'
        'import time\n'
        'import json\n'
        'from datetime import datetime\n'
        '\n'
        'print("All packages imported successfully")'
    ))

    # ── Cell 4: Database connection helper ──
    cells.append(make_md_cell("## Step 3: Database Connection"))
    cells.append(make_code_cell(
        '# Database connection configuration\n'
        'def get_connection(dbname="postgres"):\n'
        '    """Get PostgreSQL connection."""\n'
        '    if IS_COLAB:\n'
        '        return psycopg2.connect(\n'
        '            host="localhost",\n'
        '            port=5432,\n'
        '            user="postgres",\n'
        '            password="postgres",\n'
        '            database=dbname\n'
        '        )\n'
        '    else:\n'
        '        # Local connection (adjust as needed)\n'
        '        return psycopg2.connect(\n'
        '            host="localhost",\n'
        '            port=5432,\n'
        '            user=os.environ.get("USER", "postgres"),\n'
        '            password=os.environ.get("PG_PASSWORD", ""),\n'
        '            database=dbname\n'
        '        )\n'
        '\n'
        '# Test connection\n'
        'try:\n'
        '    conn = get_connection()\n'
        '    conn.autocommit = True\n'
        '    print("PostgreSQL connection successful")\n'
        '    cur = conn.cursor()\n'
        '    cur.execute("SELECT version();")\n'
        '    print(f"  Version: {cur.fetchone()[0][:60]}")\n'
        '    cur.close()\n'
        '    conn.close()\n'
        'except Exception as e:\n'
        '    print(f"Connection failed: {e}")'
    ))

    # ── Cell 5: Create database ──
    cells.append(make_md_cell("## Step 4: Create Database and Load Schema"))
    cells.append(make_code_cell(
        f'# Create database {pg_db_name}\n'
        'conn = get_connection("postgres")\n'
        'conn.autocommit = True\n'
        'cur = conn.cursor()\n'
        '\n'
        '# Drop and recreate\n'
        f'cur.execute("DROP DATABASE IF EXISTS {pg_db_name}")\n'
        f'cur.execute("CREATE DATABASE {pg_db_name}")\n'
        f'print("Database {pg_db_name} created")\n'
        'cur.close()\n'
        'conn.close()\n'
        '\n'
        '# Connect to the new database\n'
        f'conn = get_connection("{pg_db_name}")\n'
        'conn.autocommit = True\n'
        'cur = conn.cursor()\n'
        '\n'
        '# Enable PostGIS if available\n'
        'try:\n'
        '    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")\n'
        '    print("PostGIS extension enabled")\n'
        'except Exception as e:\n'
        '    print(f"PostGIS not available: {e}")\n'
        '    conn.rollback()\n'
        '\n'
        'cur.close()\n'
        'conn.close()\n'
        f'print("Database {pg_db_name} ready")'
    ))

    # ── Cell 6: Schema SQL embedded ──
    # Escape the schema for embedding
    schema_escaped = schema_sql.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
    # Too large to embed as string literal - use triple-quote approach
    cells.append(make_md_cell("## Step 4b: Load Schema"))

    # Split schema into manageable chunks if needed
    schema_lines = schema_sql.split('\n')
    schema_clean = '\n'.join(schema_lines)

    cells.append(make_code_cell(
        f'# Load schema into {pg_db_name}\n'
        f'conn = get_connection("{pg_db_name}")\n'
        'conn.autocommit = True\n'
        'cur = conn.cursor()\n'
        '\n'
        'SCHEMA_SQL = """\n'
        + schema_clean + '\n'
        '"""\n'
        '\n'
        '# Execute schema statements one at a time\n'
        'statements = [s.strip() for s in SCHEMA_SQL.split(";") if s.strip()]\n'
        'success = 0\n'
        'errors = 0\n'
        'for stmt in statements:\n'
        '    if not stmt or stmt.startswith("--"):\n'
        '        continue\n'
        '    try:\n'
        '        cur.execute(stmt + ";")\n'
        '        success += 1\n'
        '    except Exception as e:\n'
        '        err_msg = str(e).split("\\n")[0]\n'
        '        if "already exists" not in err_msg:\n'
        '            errors += 1\n'
        '            if errors <= 5:\n'
        '                print(f"  Warning: {err_msg[:80]}")\n'
        '        conn.rollback()\n'
        '        conn.autocommit = True\n'
        '\n'
        'print(f"Schema loaded: {success} statements, {errors} errors")\n'
        '\n'
        '# Verify tables\n'
        'cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema=\'public\' AND table_type=\'BASE TABLE\'")\n'
        'table_count = cur.fetchone()[0]\n'
        'print(f"Tables created: {table_count}")\n'
        'cur.close()\n'
        'conn.close()'
    ))

    # ── Cell 7: Load data (generate sample data inline) ──
    cells.append(make_md_cell("## Step 5: Load Sample Data"))
    cells.append(make_code_cell(
        f'# Load sample data into {pg_db_name}\n'
        f'conn = get_connection("{pg_db_name}")\n'
        'conn.autocommit = True\n'
        'cur = conn.cursor()\n'
        '\n'
        '# Check if data directory has data files\n'
        'import os\n'
        'data_dir = os.path.join(os.path.dirname(os.path.abspath("__file__")), "data")\n'
        '\n'
        '# Try loading from data.sql file if available\n'
        'data_loaded = False\n'
        'for data_file in ["data/data.sql", "data/data_large_postgresql.sql", "data/data_large.sql"]:\n'
        '    if os.path.exists(data_file):\n'
        '        print(f"Loading data from {data_file}...")\n'
        '        try:\n'
        '            with open(data_file, "r") as f:\n'
        '                sql = f.read()\n'
        '            # Execute in chunks\n'
        '            stmts = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]\n'
        '            loaded = 0\n'
        '            for stmt in stmts[:1000]:  # Limit for Colab memory\n'
        '                try:\n'
        '                    cur.execute(stmt + ";")\n'
        '                    loaded += 1\n'
        '                except Exception:\n'
        '                    conn.rollback()\n'
        '                    conn.autocommit = True\n'
        '            print(f"  Loaded {loaded} statements from {data_file}")\n'
        '            data_loaded = True\n'
        '            break\n'
        '        except Exception as e:\n'
        '            print(f"  Error loading {data_file}: {e}")\n'
        '\n'
        'if not data_loaded:\n'
        '    print("No data file found - tables will be empty")\n'
        '    print("Queries will still execute but return 0 rows")\n'
        '\n'
        '# Show row counts\n'
        'cur.execute("""\n'
        '    SELECT relname, n_live_tup\n'
        '    FROM pg_stat_user_tables\n'
        '    WHERE schemaname = \'public\' AND relname != \'spatial_ref_sys\'\n'
        '    ORDER BY n_live_tup DESC\n'
        '""")\n'
        'print("\\nTable row counts:")\n'
        'for row in cur.fetchall():\n'
        '    print(f"  {row[0]}: {row[1]} rows")\n'
        '\n'
        'cur.close()\n'
        'conn.close()'
    ))

    # ── Cell 8: Query execution function ──
    cells.append(make_md_cell("## Step 6: Query Execution Function"))
    cells.append(make_code_cell(
        '# Query execution with metrics\n'
        'def execute_query(conn, query_sql, query_num, query_title=""):\n'
        '    """Execute a query and return results with metrics."""\n'
        '    result = {\n'
        '        "query_number": query_num,\n'
        '        "title": query_title,\n'
        '        "success": False,\n'
        '        "execution_time_ms": 0,\n'
        '        "row_count": 0,\n'
        '        "columns": [],\n'
        '        "error": None\n'
        '    }\n'
        '    try:\n'
        '        conn.autocommit = True\n'
        '        cur = conn.cursor()\n'
        '        # Set statement timeout (30 seconds)\n'
        '        cur.execute("SET statement_timeout = \'30000\'")\n'
        '        # Add LIMIT if not present\n'
        '        sql = query_sql.rstrip(";")\n'
        '        if "LIMIT" not in sql.upper() and "FETCH" not in sql.upper():\n'
        '            sql += " LIMIT 100"\n'
        '        start = time.time()\n'
        '        cur.execute(sql)\n'
        '        rows = cur.fetchmany(100)\n'
        '        elapsed = (time.time() - start) * 1000\n'
        '        result["success"] = True\n'
        '        result["execution_time_ms"] = round(elapsed, 2)\n'
        '        result["row_count"] = len(rows)\n'
        '        result["columns"] = [d[0] for d in cur.description] if cur.description else []\n'
        '        cur.close()\n'
        '    except Exception as e:\n'
        '        result["error"] = str(e)[:200]\n'
        '        try:\n'
        '            conn.rollback()\n'
        '        except Exception:\n'
        '            pass\n'
        '    return result\n'
        '\n'
        'print("Query execution function defined")'
    ))

    # ── Cell 9: Embed queries ──
    cells.append(make_md_cell("## Step 7: Load Queries"))

    # Build queries list as Python code
    queries_code = 'QUERIES = [\n'
    for q in queries:
        title_esc = q['title'].replace('"', '\\"')
        sql_esc = q['sql'].replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
        queries_code += f'    {{\n'
        queries_code += f'        "number": {q["number"]},\n'
        queries_code += f'        "title": "{title_esc}",\n'
        queries_code += f'        "sql": """{sql_esc}"""\n'
        queries_code += f'    }},\n'
    queries_code += ']\n'
    queries_code += f'print(f"Loaded {{len(QUERIES)}} queries")'

    cells.append(make_code_cell(queries_code))

    # ── Cell 10: Execute all queries ──
    cells.append(make_md_cell("## Step 8: Execute All Queries"))
    cells.append(make_code_cell(
        f'# Execute all queries on {pg_db_name}\n'
        f'conn = get_connection("{pg_db_name}")\n'
        'results = []\n'
        '\n'
        'print("=" * 70)\n'
        f'print("Executing {len(queries)} queries on {pg_db_name}")\n'
        'print("=" * 70)\n'
        '\n'
        'for q in QUERIES:\n'
        '    r = execute_query(conn, q["sql"], q["number"], q["title"])\n'
        '    results.append(r)\n'
        '    status = "PASS" if r["success"] else "FAIL"\n'
        '    time_str = f\' ({r["execution_time_ms"]}ms)\' if r["success"] else ""\n'
        '    err_str = f\' - {r["error"][:50]}\' if r["error"] else ""\n'
        '    print(f\'  Q{q["number"]:02d}: {status}{time_str}{err_str}\')\n'
        '\n'
        'conn.close()\n'
        '\n'
        '# Summary\n'
        'passed = sum(1 for r in results if r["success"])\n'
        'total = len(results)\n'
        'sep = "=" * 70\n'
        'print(f"\\n{sep}")\n'
        'print(f"Results: {passed}/{total} passed ({passed*100//total}%)")\n'
        'print(sep)'
    ))

    # ── Cell 11: Results visualization ──
    cells.append(make_md_cell("## Step 9: Results Visualization"))
    cells.append(make_code_cell(
        '# Visualize query execution results\n'
        'df = pd.DataFrame(results)\n'
        '\n'
        'fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n'
        '\n'
        '# Pass/Fail chart\n'
        'pass_fail = df["success"].value_counts()\n'
        'colors = ["#2ecc71" if k else "#e74c3c" for k in pass_fail.index]\n'
        'axes[0].bar(["Pass" if k else "Fail" for k in pass_fail.index], pass_fail.values, color=colors)\n'
        'axes[0].set_title("Query Pass/Fail")\n'
        'axes[0].set_ylabel("Count")\n'
        '\n'
        '# Execution time chart (successful queries only)\n'
        'success_df = df[df["success"] == True].copy()\n'
        'if not success_df.empty:\n'
        '    axes[1].bar(success_df["query_number"], success_df["execution_time_ms"], color="#3498db")\n'
        '    axes[1].set_title("Query Execution Time (ms)")\n'
        '    axes[1].set_xlabel("Query Number")\n'
        '    axes[1].set_ylabel("Time (ms)")\n'
        '    axes[1].tick_params(axis="x", rotation=45)\n'
        '\n'
        'plt.tight_layout()\n'
        'plt.show()\n'
        '\n'
        '# Summary stats\n'
        'if not success_df.empty:\n'
        '    print(f"\\nExecution Time Stats (successful queries):")\n'
        '    print(f"  Mean: {success_df[\'execution_time_ms\'].mean():.2f} ms")\n'
        '    print(f"  Median: {success_df[\'execution_time_ms\'].median():.2f} ms")\n'
        '    print(f"  Max: {success_df[\'execution_time_ms\'].max():.2f} ms")\n'
        '    print(f"  Min: {success_df[\'execution_time_ms\'].min():.2f} ms")'
    ))

    # ── Cell 12: Failed queries detail ──
    cells.append(make_md_cell("## Step 10: Failed Query Details"))
    cells.append(make_code_cell(
        '# Show details of any failed queries\n'
        'failed = [r for r in results if not r["success"]]\n'
        '\n'
        'if failed:\n'
        '    print(f"{len(failed)} queries failed:\\n")\n'
        '    for r in failed:\n'
        '        print(f"  Query {r[\'query_number\']}: {r[\'title\'][:60]}")\n'
        '        print(f"    Error: {r[\'error\']}")\n'
        '        print()\n'
        'else:\n'
        '    print("All queries passed successfully!")'
    ))

    # ── Cell 13: Save results ──
    cells.append(make_md_cell("## Step 11: Save Results"))
    cells.append(make_code_cell(
        '# Save execution results\n'
        'output = {\n'
        f'    "database": "{db_id}",\n'
        f'    "database_name": "{db_name}",\n'
        '    "test_date": datetime.now().isoformat(),\n'
        '    "total_queries": len(results),\n'
        '    "passed": sum(1 for r in results if r["success"]),\n'
        '    "failed": sum(1 for r in results if not r["success"]),\n'
        '    "success_rate": round(sum(1 for r in results if r["success"]) / len(results) * 100, 2),\n'
        '    "results": results\n'
        '}\n'
        '\n'
        f'output_path = "results/{db_id}_colab_test_results.json"\n'
        'os.makedirs("results", exist_ok=True)\n'
        'with open(output_path, "w") as f:\n'
        '    json.dump(output, f, indent=2, default=str)\n'
        'print(f"Results saved to {output_path}")\n'
        'print(f"\\nFinal: {output[\'passed\']}/{output[\'total_queries\']} queries passed ({output[\'success_rate\']}%)")'
    ))

    # ── Build notebook ──
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {
                "provenance": [],
                "name": f"{db_id} Query Testing"
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3"
            },
            "language_info": {
                "name": "python",
                "version": "3.10.0"
            }
        },
        "cells": cells
    }

    return notebook


def main():
    base = Path('/Users/machine/Documents/AQ/db/client/db')

    db_names = {
        6: "Weather Data Pipeline System",
        7: "Maritime Shipping Intelligence",
        8: "Job Market Intelligence",
        9: "Shipping Intelligence",
        10: "Marketing Intelligence",
        11: "Parking Intelligence",
        12: "Credit Card and Rewards Optimization",
        13: "AI Benchmark Marketing Database",
        14: "Cloud Instance Cost Database",
        15: "Electricity Cost and Solar Rebate Database",
        16: "Flood Risk Assessment for M&A Due Diligence",
    }

    for db_num in range(6, 17):
        db_dir = base / f'db-{db_num}'
        if not db_dir.exists():
            print(f"db-{db_num}: directory not found, skipping")
            continue

        # Load queries
        qj_path = db_dir / 'queries' / 'queries.json'
        if not qj_path.exists():
            print(f"db-{db_num}: queries.json not found, skipping")
            continue

        qj = json.loads(qj_path.read_text())
        queries = qj.get('queries', [])

        # Load schema (prefer PostgreSQL version)
        schema_path = db_dir / 'data' / 'schema_postgresql.sql'
        if not schema_path.exists():
            schema_path = db_dir / 'data' / 'schema.sql'
        schema_sql = schema_path.read_text() if schema_path.exists() else ""

        # Fix schema for PostgreSQL compatibility
        schema_sql = schema_sql.replace('TIMESTAMP_NTZ', 'TIMESTAMP')
        schema_sql = schema_sql.replace('CURRENT_TIMESTAMP()', 'CURRENT_TIMESTAMP')

        has_data_large = (db_dir / 'data' / 'data_large.sql').exists()

        db_name = db_names.get(db_num, f"Database {db_num}")

        nb = generate_notebook(db_num, db_name, queries, schema_sql, has_data_large)

        # Write notebook
        nb_path = db_dir / f'db-{db_num}.ipynb'
        nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False))

        cell_count = len(nb['cells'])
        code_cells = sum(1 for c in nb['cells'] if c['cell_type'] == 'code')
        print(f"db-{db_num}: Generated {nb_path.name} ({cell_count} cells, {code_cells} code, {nb_path.stat().st_size} bytes)")


if __name__ == '__main__':
    main()

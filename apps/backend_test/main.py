"""
Lightweight FastAPI app that mounts all 16 DBs and exposes health, query, benchmark, and BIRD endpoints.
Represents the Model layer in MVC - backend for testing DB connectivity.
"""

import json
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Repo root and scripts path
_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root / "scripts"))

# Load env and validate before starting
from env_validator import load_env, ensure_env
load_env()
if not ensure_env("db"):
    raise RuntimeError("Missing PG_* env vars. Set in .env or client/.env. See .env.example")

DB_PORTS_START = int(os.getenv("DB_PORTS_START", "5436"))
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
BIRD_EXPORT_DIR = _repo_root / "bird_export"


def get_db_config(db_num: int) -> dict:
    return {
        "host": PG_HOST,
        "port": DB_PORTS_START + db_num - 1,
        "dbname": f"db{db_num}",
        "user": PG_USER,
        "password": PG_PASSWORD,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Cleanup if needed


app = FastAPI(title="DB Backend Test", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/db/{db_num:int}")
async def health_db(db_num: int):
    """Check connectivity to a specific DB (1-16)."""
    if db_num < 1 or db_num > 16:
        return JSONResponse({"error": "db_num must be 1-16"}, status_code=400)
    try:
        import psycopg2
        cfg = get_db_config(db_num)
        conn = psycopg2.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            dbname=cfg["dbname"],
            connect_timeout=3,
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"db": f"db-{db_num}", "status": "connected"}
    except Exception as e:
        return JSONResponse(
            {"db": f"db-{db_num}", "status": "error", "error": str(e)[:200]},
            status_code=503,
        )


@app.get("/health/all")
async def health_all():
    """Check connectivity to all 16 DBs."""
    results = []
    for n in range(1, 17):
        try:
            import psycopg2
            cfg = get_db_config(n)
            conn = psycopg2.connect(
                host=cfg["host"],
                port=cfg["port"],
                user=cfg["user"],
                password=cfg["password"],
                dbname=cfg["dbname"],
                connect_timeout=2,
            )
            conn.close()
            results.append({"db": f"db-{n}", "status": "connected"})
        except Exception as e:
            results.append({"db": f"db-{n}", "status": "error", "error": str(e)[:100]})
    return {"databases": results}


# --- /query ---
@app.post("/query")
async def execute_query(body: dict):
    """Execute SQL and return result. Body: { "db_id": "db-1", "sql": "SELECT ..." }"""
    db_id = body.get("db_id", "").strip()
    sql = body.get("sql", "").strip()
    if not db_id or not sql:
        raise HTTPException(400, "db_id and sql required")
    try:
        db_num = int(db_id.replace("db-", ""))
    except ValueError:
        raise HTTPException(400, "db_id must be db-1..db-16")
    if db_num < 1 or db_num > 16:
        raise HTTPException(400, "db_id must be db-1..db-16")
    cfg = get_db_config(db_num)
    try:
        import psycopg2
        conn = psycopg2.connect(**cfg, connect_timeout=5)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        cur.close()
        conn.close()
        return {"columns": cols, "rows": rows, "row_count": len(rows)}
    except Exception as e:
        raise HTTPException(500, str(e)[:300])


# --- /benchmark ---
@app.post("/benchmark")
async def run_benchmark(body: dict):
    """Run selected queries from queries.json. Body: { "db_id": "db-1", "query_ids": [1,2,3] }"""
    db_id = body.get("db_id", "").strip()
    query_ids = body.get("query_ids", [])
    if not db_id:
        raise HTTPException(400, "db_id required")
    try:
        db_num = int(db_id.replace("db-", ""))
    except ValueError:
        raise HTTPException(400, "db_id must be db-1..db-16")
    if db_num < 1 or db_num > 16:
        raise HTTPException(400, "db_id must be db-1..db-16")
    qj = _repo_root / f"db-{db_num}" / "queries" / "queries.json"
    if not qj.exists():
        raise HTTPException(404, f"queries.json not found for {db_id}")
    data = json.loads(qj.read_text(encoding="utf-8"))
    queries = {q["number"]: q for q in data.get("queries", [])}
    if not query_ids:
        query_ids = list(queries.keys())[:10]
    cfg = get_db_config(db_num)
    results = []
    for qid in query_ids:
        q = queries.get(qid)
        if not q:
            results.append({"query_id": qid, "success": False, "error": "not found"})
            continue
        sql = (q.get("sql") or "").strip()
        if not sql:
            results.append({"query_id": qid, "success": False, "error": "no sql"})
            continue
        try:
            import psycopg2
            conn = psycopg2.connect(**cfg, connect_timeout=10)
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            results.append({"query_id": qid, "success": True, "row_count": len(rows)})
        except Exception as e:
            results.append({"query_id": qid, "success": False, "error": str(e)[:200]})
    passed = sum(1 for r in results if r["success"])
    return {"db_id": db_id, "total": len(results), "passed": passed, "results": results}


# --- /bird/export ---
@app.get("/bird/export")
async def bird_export(db_id: str = "db-1"):
    """Return BIRD-formatted export for a db. Query param: db_id=db-1"""
    try:
        db_num = int(db_id.replace("db-", ""))
    except ValueError:
        raise HTTPException(400, "db_id must be db-1..db-16")
    if db_num < 1 or db_num > 16:
        raise HTTPException(400, "db_id must be db-1..db-16")
    path = BIRD_EXPORT_DIR / f"db-{db_num}_bird.json"
    if not path.exists():
        raise HTTPException(404, f"Run bird_export.py first to create {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


# --- /bird/validate ---
@app.post("/bird/validate")
async def bird_validate(body: dict):
    """Validate a db against BIRD schema requirements. Body: { "db_id": "db-1" }"""
    db_id = body.get("db_id", "").strip() or "db-1"
    try:
        db_num = int(db_id.replace("db-", ""))
    except ValueError:
        raise HTTPException(400, "db_id must be db-1..db-16")
    if db_num < 1 or db_num > 16:
        raise HTTPException(400, "db_id must be db-1..db-16")
    qj = _repo_root / f"db-{db_num}" / "queries" / "queries.json"
    schema_path = _repo_root / f"db-{db_num}" / "data" / "schema.sql"
    if not schema_path.exists():
        schema_path = _repo_root / f"db-{db_num}" / "data" / "schema_postgresql.sql"
    checks = []
    if qj.exists():
        data = json.loads(qj.read_text(encoding="utf-8"))
        queries = data.get("queries", [])
        has_question = all(q.get("question") or q.get("use_case") or q.get("description") for q in queries)
        checks.append(("queries have question/use_case/description", has_question))
        checks.append(("30 queries", len(queries) == 30))
    else:
        checks.append(("queries.json exists", False))
    checks.append(("schema exists", schema_path.exists()))
    passed = sum(1 for _, ok in checks if ok)
    return {"db_id": db_id, "checks": checks, "passed": passed, "total": len(checks)}

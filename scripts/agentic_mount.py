"""
Agentic data agent mount — load client databases with BIRD-style question-SQL pairs.

Used by client/doc/agentic_data_agent_mount.ipynb and tests.
Paths resolve to client/db/, not source/ (bounded context).
"""
import json
from pathlib import Path

DB_PORTS_START = 5436


def get_pg_port(db_num: int) -> int:
    """Return PostgreSQL port for db-N (5436 + n - 1)."""
    return DB_PORTS_START + db_num - 1


def load_client_db(client_db_dir: Path, db_num: int) -> dict:
    """
    Load documentation and queries for client/db/db-N.

    Returns dict with keys: db, docs, queries.
    - db: str like "db-2"
    - docs: str or None (DOCUMENTATION/README.md content)
    - queries: list of query dicts from QUERIES/queries.json
    """
    db_id = f"db-{db_num}"
    db_dir = client_db_dir / db_id
    if not db_dir.exists():
        return {"db": db_id, "docs": None, "queries": [], "error": "not found"}

    docs_path = db_dir / "DOCUMENTATION" / "README.md"
    queries_path = db_dir / "QUERIES" / "queries.json"

    docs = None
    if docs_path.exists():
        docs = docs_path.read_text(encoding="utf-8")

    queries = []
    if queries_path.exists():
        data = json.loads(queries_path.read_text(encoding="utf-8"))
        queries = data.get("queries", [])

    return {"db": db_id, "docs": docs, "queries": queries}


def get_bird_pairs(mounted: dict, db_num: int) -> list:
    """
    Return BIRD-style (question, sql, description, evidence, expected_output) for db-N.

    mounted: result of load_client_db(client_db_dir, db_num)
    Returns list of dicts with: question, normal_query, sql, description, evidence, expected_output, number
    """
    queries = mounted.get("queries", [])
    result = []
    for q in queries:
        sql = q.get("sql") or q.get("SQL") or ""
        result.append({
            "question": q.get("question", ""),
            "normal_query": q.get("normal_query", ""),
            "sql": sql,
            "description": q.get("description", ""),
            "evidence": q.get("evidence", ""),
            "expected_output": q.get("expected_output", ""),
            "number": q.get("number"),
        })
    return result

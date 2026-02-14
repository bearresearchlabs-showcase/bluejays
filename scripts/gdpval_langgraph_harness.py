#!/usr/bin/env python3
"""
GDPval-style LangGraph harness: prompt + reference(SQL) + deliverable(queries.md).
Uses .env for ANTHROPIC_API_KEY, PG_*, etc. Runs validation as a stateful graph.
"""
import warnings
warnings.filterwarnings("ignore")  # No warnings from build (e.g. langchain Pydantic on Python 3.14)

import json
import os
import sys
from pathlib import Path
from typing import TypedDict

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

# .env harness - load before any other imports
from env_validator import load_env, ensure_env
load_env()

try:
    from timestamp_utils import get_est_timestamp
except ImportError:
    from datetime import datetime
    def get_est_timestamp():
        return datetime.now().strftime('%Y%m%d-%H%M')

try:
    from db_logger import log, record_telemetry
except ImportError:
    def log(*a, **k): pass
    def record_telemetry(*a, **k): pass


# --- GDPval-style task model ---
# prompt: instruction text
# reference: SQL query (gold SQL from queries.json)
# deliverable: queries.md path/content


class GDPvalState(TypedDict):
    """State for GDPval LangGraph workflow."""
    db_num: int
    db_dir: Path
    prompt: str
    reference_sql: str
    reference_query_num: int
    deliverable_path: Path
    deliverable_exists: bool
    schema_path: Path
    steps: list
    status: str
    error: str


def get_db_dir(db_num: int) -> Path:
    """Resolve db-N directory (source/db-N)."""
    return root_dir / "source" / f"db-{db_num}"


def get_queries_dir(db_dir: Path) -> Path:
    """Resolve queries dir (app/QUERIES or queries)."""
    from db_paths import get_queries_dir as _get
    return _get(db_dir)


def get_data_dir(db_dir: Path) -> Path:
    """Resolve data dir (app/DATABASE or data)."""
    from db_paths import get_data_dir as _get
    return _get(db_dir)


def load_task(db_num: int) -> GDPvalState:
    """Load task: prompt + reference(SQL) + deliverable(queries.md)."""
    db_dir = get_db_dir(db_num)
    queries_dir = get_queries_dir(db_dir)
    data_dir = get_data_dir(db_dir)

    # prompt: GDPval-style instruction
    prompt = (
        f"Validate db-{db_num}: ensure schema, queries.json, and deliverable (queries.md) meet requirements. "
        "Reference attachment is the gold SQL query. Deliverable is queries.md."
    )

    # reference: SQL query from queries.json (first query as example)
    reference_sql = ""
    reference_query_num = 0
    qj = queries_dir / "queries.json"
    if qj.exists():
        try:
            data = json.loads(qj.read_text(encoding="utf-8"))
            queries = data.get("queries", [])
            if queries:
                q = queries[0]
                reference_sql = q.get("sql", "")
                reference_query_num = q.get("number", 1)
        except (json.JSONDecodeError, OSError):
            pass

    # deliverable: queries.md
    deliverable_path = queries_dir / "queries.md"
    deliverable_exists = deliverable_path.exists()

    # schema
    schema_path = data_dir / "schema.sql"
    if not schema_path.exists():
        schema_path = data_dir / "schema_postgresql.sql"

    return GDPvalState(
        db_num=db_num,
        db_dir=db_dir,
        prompt=prompt,
        reference_sql=reference_sql,
        reference_query_num=reference_query_num,
        deliverable_path=deliverable_path,
        deliverable_exists=deliverable_exists,
        schema_path=schema_path,
        steps=[],
        status="PASS",
        error="",
    )


def validate_reference(state: GDPvalState) -> GDPvalState:
    """Validate reference SQL (EXPLAIN syntax check)."""
    steps = list(state.get("steps", []))
    sql = state.get("reference_sql", "")
    if not sql:
        steps.append({"step": "reference", "status": "FAIL", "message": "No reference SQL"})
        return {**state, "steps": steps, "status": "FAIL", "error": "No reference SQL"}

    # Try EXPLAIN if PG available. CI/CD, SLURM, Jenkins set PG_*; no particular port required.
    host = os.getenv("PG_HOST")
    if not host:
        steps.append({"step": "reference", "status": "SKIP", "message": "PG_HOST not set (set in .env)"})
        return {**state, "steps": steps}
    db_num = state.get("db_num", 1)
    port_str = os.getenv("PG_PORT") or os.getenv(f"PG_PORT_DB{db_num}")
    port = int(port_str) if port_str else int(os.getenv("DB_PORTS_START", "5432")) + db_num - 1
    user = os.getenv("PG_USER", "postgres")
    password = os.getenv("PG_PASSWORD", "")
    database = os.getenv("PG_DATABASE", f"db{db_num}")

    try:
        import psycopg2
        conn = psycopg2.connect(
            host=host, port=port, user=user, password=password, dbname=database,
            connect_timeout=5,
        )
        cur = conn.cursor()
        cur.execute(f"EXPLAIN {sql}")
        cur.fetchall()
        cur.close()
        conn.close()
        steps.append({"step": "reference", "status": "PASS", "message": "EXPLAIN ok"})
    except ImportError:
        steps.append({"step": "reference", "status": "SKIP", "message": "psycopg2 not installed"})
    except Exception as e:
        err = str(e).lower()
        # Connection refused / DB unavailable -> SKIP (like GDPval step 4)
        if "connection refused" in err or "could not connect" in err or "timeout" in err:
            steps.append({"step": "reference", "status": "SKIP", "message": f"DB unavailable: {str(e)[:100]}"})
        else:
            steps.append({"step": "reference", "status": "FAIL", "message": str(e)[:200]})
            return {**state, "steps": steps, "status": "FAIL", "error": str(e)[:200]}

    return {**state, "steps": steps}


def validate_deliverable(state: GDPvalState) -> GDPvalState:
    """Validate deliverable (queries.md exists and has content)."""
    steps = list(state.get("steps", []))
    path = state.get("deliverable_path")
    exists = state.get("deliverable_exists", False)

    if not exists or not path:
        steps.append({"step": "deliverable", "status": "FAIL", "message": "queries.md missing"})
        return {**state, "steps": steps, "status": "FAIL", "error": "queries.md missing"}

    try:
        content = path.read_text(encoding="utf-8")
        has_queries = "## Query" in content or "```sql" in content
        steps.append({
            "step": "deliverable",
            "status": "PASS" if has_queries else "FAIL",
            "message": f"queries.md exists, {len(content)} chars" + ("" if has_queries else ", missing Query blocks"),
        })
        if not has_queries:
            return {**state, "steps": steps, "status": "FAIL", "error": "queries.md missing Query blocks"}
    except Exception as e:
        steps.append({"step": "deliverable", "status": "FAIL", "message": str(e)[:200]})
        return {**state, "steps": steps, "status": "FAIL", "error": str(e)[:200]}

    return {**state, "steps": steps}


def load_task_node(state: dict) -> dict:
    """Node: load task from db_num in state."""
    db_num = state.get("db_num", 1)
    return load_task(db_num)


def build_graph():
    """Build LangGraph workflow: load_task -> validate_reference -> validate_deliverable."""
    try:
        from langgraph.graph import END, StateGraph, START
    except ImportError:
        return None

    workflow = StateGraph(GDPvalState)
    workflow.add_node("load_task", load_task_node)
    workflow.add_node("validate_reference", validate_reference)
    workflow.add_node("validate_deliverable", validate_deliverable)

    workflow.add_edge(START, "load_task")
    workflow.add_edge("load_task", "validate_reference")
    workflow.add_edge("validate_reference", "validate_deliverable")
    workflow.add_edge("validate_deliverable", END)

    return workflow.compile()


def run_without_langgraph(db_nums: list[int]) -> dict:
    """Fallback: run GDPval-style validation without LangGraph."""
    report = {
        "validation_date": get_est_timestamp(),
        "mode": "fallback",
        "databases": {},
        "summary": {"passed": 0, "failed": 0},
    }
    for db_num in db_nums:
        state = load_task(db_num)
        state = validate_reference(state)
        state = validate_deliverable(state)
        status = state.get("status", "FAIL")
        report["databases"][f"db-{db_num}"] = {
            "steps": state.get("steps", []),
            "overall": status,
            "prompt": state.get("prompt", ""),
            "reference_query_num": state.get("reference_query_num", 0),
            "deliverable": str(state.get("deliverable_path", "")),
        }
        if status == "PASS":
            report["summary"]["passed"] += 1
        else:
            report["summary"]["failed"] += 1
    return report


def run_with_langgraph(db_nums: list[int]) -> dict:
    """Run GDPval-style validation with LangGraph."""
    app = build_graph()
    if app is None:
        print("ERROR: LangGraph required. Install: pip install langgraph langchain-anthropic. No fallback mode.", file=sys.stderr)
        sys.exit(1)

    report = {
        "validation_date": get_est_timestamp(),
        "mode": "langgraph",
        "databases": {},
        "summary": {"passed": 0, "failed": 0},
    }
    for db_num in db_nums:
        db_dir = get_db_dir(db_num)
        if not db_dir.exists():
            continue
        initial = {"db_num": db_num}
        result = app.invoke(initial)
        status = result.get("status", "FAIL")
        report["databases"][f"db-{db_num}"] = {
            "steps": result.get("steps", []),
            "overall": status,
            "prompt": result.get("prompt", ""),
            "reference_query_num": result.get("reference_query_num", 0),
            "deliverable": str(result.get("deliverable_path", "")),
        }
        if status == "PASS":
            report["summary"]["passed"] += 1
        else:
            report["summary"]["failed"] += 1
    return report


def main() -> int:
    try:
        from db_args import parse_db_args
    except ImportError:
        def parse_db_args(a):
            if not a:
                return list(range(1, 17))
            if "-a" in a or "--all" in a:
                return list(range(1, 17))
            out = []
            for x in a:
                x = str(x).strip()
                if x.startswith("db-"):
                    out.append(int(x.split("db-")[1]))
                elif x.isdigit():
                    out.append(int(x))
            if len(out) == 2 and out[0] < out[1]:
                out = list(range(out[0], out[1] + 1))
            return sorted(set(out)) if out else [1]

    # .env harness: load env; DB optional (validate_reference SKIPs if PG unavailable)
    load_env()
    db_nums = parse_db_args(sys.argv[1:])
    if not db_nums:
        db_nums = [1]

    log("gdpval_langgraph", "run", status="start", data={"db_nums": db_nums})
    report = run_with_langgraph(db_nums)
    log("gdpval_langgraph", "run", status="ok" if report["summary"]["failed"] == 0 else "fail", data=report["summary"])

    print(json.dumps(report, indent=2))
    out = root_dir / "results" / "gdpval_langgraph_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"\nReport saved to: {out}")

    return 1 if report["summary"]["failed"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Generate db_metadata.json for each database.
Schema: id, name, version, created_date, queries_count, schema_hash, queries_hash,
       deliverable_files, rl_ready, client_ready.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

scripts_dir = Path(__file__).parent
root_dir = scripts_dir.parent
sys.path.insert(0, str(scripts_dir))

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


def sha256_file(path: Path) -> str:
    if not path.exists():
        return ""
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_db_name(db_dir: Path, db_num: int) -> str:
    """Infer DB name from README or DELIVERABLE.md."""
    for f in (db_dir / "README.md", db_dir / "DELIVERABLE.md", db_dir / "deliverable" / f"db-{db_num}.md"):
        if f.exists():
            text = f.read_text(encoding="utf-8")[:500]
            for line in text.split("\n"):
                if line.startswith("# ") and "Database" in line:
                    return line.replace("#", "").strip().split("Database")[-1].strip() or f"db-{db_num}"
    return f"db-{db_num}"


def generate_metadata(db_num: int) -> Dict[str, Any]:
    db_dir = root_dir / "source" / f"db-{db_num}"
    if not db_dir.exists():
        return {}

    from db_paths import get_data_dir, get_queries_dir
    data_dir = get_data_dir(db_dir)
    queries_dir = get_queries_dir(db_dir)

    # Schema file
    schema_path = data_dir / "schema.sql"
    if not schema_path.exists():
        schema_path = data_dir / "schema_postgresql.sql"
    schema_hash = sha256_file(schema_path) if schema_path.exists() else ""

    # Queries
    qj = queries_dir / "queries.json"
    queries_hash = sha256_file(qj) if qj.exists() else ""
    queries_count = 0
    if qj.exists():
        try:
            data = json.loads(qj.read_text(encoding="utf-8"))
            queries_count = len(data.get("queries", []))
        except (json.JSONDecodeError, OSError):
            pass

    # Deliverable files present
    deliverable_files: List[str] = []
    for name in ["schema.sql", "schema_postgresql.sql", "data.sql", "queries.json", "queries.md"]:
        if name.endswith(".sql"):
            p = data_dir / name
        else:
            p = queries_dir / name
        if p.exists():
            deliverable_files.append(name)

    client_db = root_dir / "client" / "db" / f"db-{db_num}"
    has_html = has_json = False
    if client_db.exists():
        doc_dir = client_db / "DOCUMENTATION"
        if doc_dir.exists():
            has_html = (doc_dir / f"db-{db_num}_documentation.html").exists()
            has_json = (doc_dir / f"db-{db_num}_deliverable.json").exists()
            if has_html:
                deliverable_files.append(f"db-{db_num}_documentation.html")
            if has_json:
                deliverable_files.append(f"db-{db_num}_deliverable.json")

    # rl_ready: queries valid, schema documented, sample data
    rl_ready = (
        queries_count == 30
        and bool(schema_hash)
        and (data_dir / "data.sql").exists()
    )

    # client_ready: full deliverable
    client_ready = (
        has_html
        and has_json
        and queries_count == 30
        and (client_db / "vercel.json").exists()
    )

    return {
        "id": f"db-{db_num}",
        "name": get_db_name(db_dir, db_num),
        "version": "1.0",
        "created_date": "2026-02-13",
        "queries_count": queries_count,
        "schema_hash": schema_hash,
        "queries_hash": queries_hash,
        "deliverable_files": deliverable_files,
        "rl_ready": rl_ready,
        "client_ready": client_ready,
        "generated_at": get_est_timestamp(),
    }


def main() -> int:
    import time
    start = time.perf_counter()
    try:
        from db_args import parse_db_args
    except ImportError:
        def parse_db_args(a):
            if not a: return list(range(1, 17))
            if "-a" in a or "--all" in a: return list(range(1, 17))
            out = []
            for x in a:
                x = str(x).strip()
                if x.startswith("db-"): out.append(int(x.split("db-")[1]))
                elif x.isdigit(): out.append(int(x))
            if len(out) == 2 and out[0] < out[1]: out = list(range(out[0], out[1] + 1))
            return sorted(set(out)) if out else list(range(1, 17))
    db_nums = parse_db_args(sys.argv[1:])
    if not db_nums:
        db_nums = list(range(1, 17))

    log("generate_db_metadata", "run", status="start", data={"db_nums": db_nums})
    generated = 0
    for db_num in db_nums:
        meta = generate_metadata(db_num)
        if not meta:
            continue
        out_dir = root_dir / "source" / f"db-{db_num}" / "metadata"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "db_metadata.json"
        out_file.write_text(json.dumps(meta, indent=2))
        print(f"  db-{db_num}: {out_file}")
        generated += 1

    duration_ms = (time.perf_counter() - start) * 1000
    record_telemetry("generate_db_metadata", "run", passed=generated, failed=0, extra={"total": len(db_nums)})
    log("generate_db_metadata", "run", status="ok", duration_ms=duration_ms, data={"generated": generated, "total": len(db_nums)})
    return 0


if __name__ == "__main__":
    sys.exit(main())

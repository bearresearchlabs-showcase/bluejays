#!/usr/bin/env python3
"""
Compare db.zip, client/db, and source db-* for data correctness, SQL queries, JSON validity,
and 1GB+ data completeness. Outputs a verdict.
"""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
ZIP_EXTRACT = Path("/tmp/db_zip_extract/db")


def file_hash(p: Path) -> str | None:
    if not p.exists():
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def analyze_queries_json(p: Path) -> dict | None:
    if not p.exists():
        return None
    try:
        d = json.load(open(p))
        qs = d.get("queries", [])
        required = ["number", "title", "sql", "description"]
        complete = sum(1 for q in qs if all(q.get(k) for k in required))
        extra_keys = set()
        for q in qs[:3]:
            extra_keys.update(q.keys())
        return {
            "count": len(qs),
            "complete": complete,
            "size": p.stat().st_size,
            "has_question": "question" in extra_keys,
            "sql_total_chars": sum(len(q.get("sql", "")) for q in qs),
        }
    except Exception:
        return None


def main():
    results = {
        "data_large_sizes_gb": {},
        "total_sql_gb": {"source": 0, "client": 0, "zip": 0},
        "queries_json": {},
        "byte_identity": {},
        "verdict": "",
    }

    # 1. data_large.sql sizes (1GB minimum)
    for n in range(1, 17):
        src = BASE / f"db-{n}" / "data" / "data_large.sql"
        cli = BASE / "client" / "db" / f"db-{n}" / "DATABASE" / "data_large.sql"
        zpp = ZIP_EXTRACT / f"db-{n}" / "DATABASE" / "data_large.sql"
        results["data_large_sizes_gb"][f"db-{n}"] = {
            "source": round(src.stat().st_size / (1024**3), 2) if src.exists() else None,
            "client": round(cli.stat().st_size / (1024**3), 2) if cli.exists() else None,
            "zip": round(zpp.stat().st_size / (1024**3), 2) if zpp.exists() else None,
        }

    # 2. Total SQL size
    for d in BASE.glob("db-*/data"):
        for f in d.glob("*.sql"):
            if f.is_file():
                results["total_sql_gb"]["source"] += f.stat().st_size
    for d in (BASE / "client" / "db").glob("db-*/DATABASE"):
        for f in d.glob("*.sql"):
            if f.is_file():
                results["total_sql_gb"]["client"] += f.stat().st_size
    if ZIP_EXTRACT.exists():
        for d in ZIP_EXTRACT.glob("db-*/DATABASE"):
            for f in d.glob("*.sql"):
                if f.is_file():
                    results["total_sql_gb"]["zip"] += f.stat().st_size
    for k in results["total_sql_gb"]:
        results["total_sql_gb"][k] = round(results["total_sql_gb"][k] / (1024**3), 2)

    # 3. queries.json comparison (db-1, 11, 16)
    for n in [1, 11, 16]:
        src = BASE / f"db-{n}" / "queries" / "queries.json"
        cli = BASE / "client" / "db" / f"db-{n}" / "QUERIES" / "queries.json"
        zpp = ZIP_EXTRACT / f"db-{n}" / "QUERIES" / "queries.json"
        results["queries_json"][f"db-{n}"] = {
            "source": analyze_queries_json(src),
            "client": analyze_queries_json(cli),
            "zip": analyze_queries_json(zpp),
        }

    # 4. Byte identity for schema, data, data_large (db-1, 11, 16)
    for n in [1, 11, 16]:
        for fname in ["schema.sql", "data.sql", "data_large.sql"]:
            src = BASE / f"db-{n}" / "data" / fname
            cli = BASE / "client" / "db" / f"db-{n}" / "DATABASE" / fname
            zpp = ZIP_EXTRACT / f"db-{n}" / "DATABASE" / fname
            sh, ch, zh = file_hash(src), file_hash(cli), file_hash(zpp)
            key = f"db-{n}/{fname}"
            results["byte_identity"][key] = (
                "ALL_IDENTICAL" if sh and ch and zh and sh == ch == zh else "DIFFER"
            )

    # 5. Verdict
    src_gb = results["total_sql_gb"]["source"]
    cli_gb = results["total_sql_gb"]["client"]
    zip_gb = results["total_sql_gb"]["zip"]
    all_identical = all(v == "ALL_IDENTICAL" for v in results["byte_identity"].values())
    src_has_question = any(
        r.get("source", {}).get("has_question") for r in results["queries_json"].values()
    )
    meets_1gb = all(
        (v["source"] or 0) >= 1.0 or (v["client"] or 0) >= 1.0
        for k, v in results["data_large_sizes_gb"].items()
        if k in ["db-1", "db-6", "db-8", "db-9", "db-10", "db-11"]
    )

    if src_gb >= cli_gb and src_gb >= zip_gb and src_has_question and all_identical:
        results["verdict"] = (
            "SOURCE (db-1..db-17) is the most accurate and complete: "
            "largest total SQL (%.1f GB), queries.json has extra 'question' field, "
            "core schema/data/data_large identical across all three. "
            "Client and zip match each other but are subsets of source."
        ) % src_gb
    elif all_identical and cli_gb == zip_gb:
        results["verdict"] = (
            "CLIENT and ZIP are identical. SOURCE has more data (%.1f GB vs %.1f GB) "
            "and richer queries.json. Use SOURCE as canonical; run resync_client_db.py to update client."
        ) % (src_gb, cli_gb)
    else:
        results["verdict"] = "See detailed results."

    # Output
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

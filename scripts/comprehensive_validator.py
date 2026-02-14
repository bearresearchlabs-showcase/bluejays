#!/usr/bin/env python3
"""
Shared comprehensive validation (Phase 2 & 4).
Uses source/db-N via db_paths. Reads from queries.json.
Usage: python3 comprehensive_validator.py <db_num>
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List

scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from timestamp_utils import get_est_timestamp
from db_paths import get_queries_dir

try:
    import psycopg2
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False


def _load_queries_from_json(queries_dir: Path) -> List[Dict]:
    """Load queries from queries.json. Supports both sql and SQL keys."""
    qj = queries_dir / "queries.json"
    if not qj.exists():
        return []
    data = json.loads(qj.read_text(encoding="utf-8"))
    queries = data.get("queries", [])
    out = []
    for q in queries:
        sql = q.get("sql") or q.get("SQL", "")
        out.append({
            "number": q.get("number") or q.get("question_id", 0),
            "title": q.get("title") or q.get("question", ""),
            "sql": sql,
            "description": q.get("description") or q.get("evidence", "")[:200],
        })
    return sorted(out, key=lambda x: x["number"])


class SyntaxValidator:
    def __init__(self):
        self.pg_conn = None
        self.results = {"postgresql": {"available": False, "queries": []}}

    def connect_postgresql(self, config: Dict) -> bool:
        if not PG_AVAILABLE:
            return False
        try:
            self.pg_conn = psycopg2.connect(
                host=config.get("host", "localhost"),
                port=config.get("port", 5432),
                database=config.get("database", "postgres"),
                user=config.get("user", os.environ.get("USER", "postgres")),
                password=config.get("password", ""),
            )
            self.results["postgresql"]["available"] = True
            return True
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            return False

    def validate_syntax_postgresql(self, query: Dict) -> Dict:
        result = {"query_number": query["number"], "success": False, "error": None}
        if not self.pg_conn:
            result["error"] = "PostgreSQL not connected"
            return result
        try:
            cursor = self.pg_conn.cursor()
            cursor.execute(f"EXPLAIN {query['sql']}")
            cursor.fetchall()
            cursor.close()
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
        return result

    def validate_all_queries(self, queries: List[Dict], pg_config: Dict = None):
        if pg_config and self.connect_postgresql(pg_config):
            for query in queries:
                r = self.validate_syntax_postgresql(query)
                self.results["postgresql"]["queries"].append(r)
            if self.pg_conn:
                self.pg_conn.close()


class QueryEvaluator:
    @staticmethod
    def evaluate_query_count(queries: List[Dict]) -> Dict:
        c = len(queries)
        return {"requirement": "Exactly 30 queries", "found": c, "status": "PASS" if c == 30 else "FAIL"}

    @staticmethod
    def evaluate_recursive_cte_usage(queries: List[Dict]) -> Dict:
        mismatched = []
        for q in queries:
            sql_upper = q["sql"].upper()
            has_recursive = bool(re.search(r"\bWITH\s+RECURSIVE\b", sql_upper))
            claims = "recursive" in (q.get("description") or "").lower() or "recursive" in (q.get("title") or "").lower()
            if claims and not has_recursive:
                mismatched.append({"query_number": q["number"]})
        return {
            "requirement": "Queries claiming recursive CTE must have WITH RECURSIVE",
            "mismatched": len(mismatched),
            "status": "PASS" if not mismatched else "FAIL",
            "mismatched_queries": mismatched,
        }

    @staticmethod
    def evaluate_cte_usage(queries: List[Dict]) -> Dict:
        without = [q for q in queries if "WITH " not in q["sql"].upper()]
        return {
            "requirement": "All queries must use CTEs",
            "queries_without_cte": len(without),
            "status": "PASS" if not without else "FAIL",
        }

    @staticmethod
    def evaluate_complexity(queries: List[Dict]) -> Dict:
        if not queries:
            return {}
        cte_counts = [len(re.findall(r"\bWITH\s+(?:RECURSIVE\s+)?\w+\s+AS\s*\(", q["sql"].upper())) for q in queries]
        return {"average_cte_count": sum(cte_counts) / len(cte_counts)}


def main():
    root = scripts_dir.parent
    if len(sys.argv) < 2:
        print("Usage: comprehensive_validator.py <db_num>")
        sys.exit(1)
    try:
        db_num = int(sys.argv[1].replace("db-", ""))
    except ValueError:
        print("Invalid db number")
        sys.exit(1)

    db_dir = root / "source" / f"db-{db_num}"
    queries_dir = get_queries_dir(db_dir)
    results_file = db_dir / "results" / "comprehensive_validation_report.json"

    queries = _load_queries_from_json(queries_dir)
    if not queries:
        print(f"Error: No queries found in {queries_dir / 'queries.json'}")
        sys.exit(1)

    results = {
        "validation_date": get_est_timestamp(),
        "database": f"db-{db_num}",
        "file": str(queries_dir / "queries.json"),
        "total_queries": len(queries),
        "syntax_validation": {},
        "evaluation": {},
    }

    # Phase 2: Syntax validation
    validator = SyntaxValidator()
    pg_config = {
        "host": os.environ.get("PG_HOST", "localhost"),
        "port": int(os.environ.get("PG_PORT", 5432)),
        "user": os.environ.get("PG_USER", os.environ.get("USER", "postgres")),
        "password": os.environ.get("PG_PASSWORD", ""),
        "database": os.environ.get("PG_DATABASE", f"db{db_num}"),
    }
    if not PG_AVAILABLE:
        pg_config = None
    validator.validate_all_queries(queries, pg_config)
    results["syntax_validation"] = validator.results

    # Phase 4: Evaluation
    evaluator = QueryEvaluator()
    results["evaluation"]["query_count"] = evaluator.evaluate_query_count(queries)
    results["evaluation"]["recursive_cte_usage"] = evaluator.evaluate_recursive_cte_usage(queries)
    results["evaluation"]["cte_usage"] = evaluator.evaluate_cte_usage(queries)
    results["evaluation"]["complexity"] = evaluator.evaluate_complexity(queries)

    results_file.parent.mkdir(parents=True, exist_ok=True)
    results_file.write_text(json.dumps(results, indent=2, default=str))
    print(f"Results saved to {results_file}")


if __name__ == "__main__":
    main()

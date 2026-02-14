#!/usr/bin/env python3
"""
Template-format formatter for queries.md — matches @template/queries.md bit-for-bit.

All scripts that generate or write queries.md MUST use this module to ensure
exact format, spacing, and architecture match with template/.

Structure (from template/queries.md):
  # {Database Name} — Query Documentation
  ## Database Overview (YAML block)
  ## Purpose, ## Use Case, ## Business Value (text blocks)
  ## Schema (optional CREATE TABLE blocks)
  ## Domain Knowledge, ## Query Difficulty Distribution (text blocks)
  ## Queries
    ### Query N — {difficulty} / {query_category}
    ```json
    { ... }
    ```

Query block format: `### Query N — {difficulty} / {query_category}` (em dash)
JSON block: 2-space indent, fields: db_id, question_id, question, SQL, evidence,
difficulty, query_category, tables_used, schema_context, expected_output
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from db_paths import ROOT, TEMPLATE
except ImportError:
    ROOT = Path(__file__).parent.parent
    TEMPLATE = ROOT / "template"

# Canonical section order and spacing from template
TEMPLATE_SECTIONS = [
    ("Database Overview", "yaml"),
    ("Purpose", "text"),
    ("Use Case", "text"),
    ("Business Value", "text"),
    ("Schema", "sql"),
    ("Domain Knowledge", "text"),
    ("Query Difficulty Distribution", "text"),
    ("Queries", "queries"),
]


def _normalize_query(q: Dict[str, Any], db_id: str) -> Dict[str, Any]:
    """Normalize query dict to template format (question_id, question, SQL, evidence, etc.)."""
    num = q.get("question_id", q.get("number", 0))
    question = q.get("question", q.get("title", q.get("use_case", f"Query {num}")))
    sql = q.get("SQL", q.get("sql", ""))
    evidence = q.get("evidence", q.get("description", ""))
    difficulty = q.get("difficulty", _map_complexity(q.get("complexity", "")))
    category = q.get("query_category", "aggregation")
    tables = q.get("tables_used", [])
    schema_ctx = q.get("schema_context", {})
    expected = q.get("expected_output", "[]")
    if not tables and sql:
        tables = _infer_tables(sql)
    if not category and sql:
        category = _infer_category(sql, difficulty)
    return {
        "db_id": db_id,
        "question_id": num,
        "question": question,
        "SQL": sql,
        "evidence": evidence,
        "difficulty": difficulty,
        "query_category": category,
        "tables_used": tables,
        "schema_context": schema_ctx,
        "expected_output": expected,
    }


def _map_complexity(c: str) -> str:
    """Map complexity string to simple|moderate|challenging."""
    if not c:
        return "moderate"
    c = c.lower()
    if any(x in c for x in ["simple", "basic", "single"]):
        return "simple"
    if any(x in c for x in ["recursive", "4 cte", "3 cte", "9 window"]):
        return "challenging"
    return "moderate"


def _infer_tables(sql: str) -> List[str]:
    """Extract table names from FROM/JOIN."""
    tables = []
    for m in re.finditer(r"\b(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)", sql, re.I):
        t = m.group(1).lower()
        if t not in ("select", "where", "on", "and", "as", "with") and t not in tables:
            tables.append(t)
    return tables


def _infer_category(sql: str, difficulty: str) -> str:
    """Infer query_category from SQL patterns."""
    s = sql.upper()
    if "WITH RECURSIVE" in s or "RECURSIVE" in s:
        return "recursive_cte"
    if "ROW_NUMBER()" in s or "RANK()" in s or "DENSE_RANK()" in s:
        return "window/ranking"
    if "GROUP BY" in s and "HAVING" in s:
        return "aggregation"
    if "GROUP BY" in s:
        return "aggregation"
    if "JOIN" in s:
        return "join"
    return "filtering/lookup"


def _format_query_block(q: Dict[str, Any], db_id: str) -> str:
    """Format one query as template block: ### Query N — difficulty / query_category + ```json."""
    nq = _normalize_query(q, db_id)
    header = f"### Query {nq['question_id']} — {nq['difficulty']} / {nq['query_category']}"
    # JSON with 2-space indent, exclude internal keys
    out = {
        "db_id": nq["db_id"],
        "question_id": nq["question_id"],
        "question": nq["question"],
        "SQL": nq["SQL"],
        "evidence": nq["evidence"],
        "difficulty": nq["difficulty"],
        "query_category": nq["query_category"],
        "tables_used": nq["tables_used"],
        "schema_context": nq["schema_context"],
        "expected_output": nq["expected_output"],
    }
    json_str = json.dumps(out, indent=2, default=str)
    return f"{header}\n\n```json\n{json_str}\n```\n"


def format_queries_md_template(
    queries: List[Dict[str, Any]],
    db_id: str,
    db_name: str,
    overview_yaml: Optional[str] = None,
    purpose_text: Optional[str] = None,
    use_case_text: Optional[str] = None,
    business_value_text: Optional[str] = None,
    schema_sql: Optional[str] = None,
    domain_knowledge_text: Optional[str] = None,
    difficulty_dist_text: Optional[str] = None,
) -> str:
    """
    Generate queries.md in exact template format (bit-for-bit structure match).

    Section order and spacing match template/queries.md.
    """
    db_id = db_id or "db-1"
    db_name = db_name or f"Database {db_id}"

    overview_yaml = overview_yaml or f"""db_id: {db_id}
domain: Database domain
source: [synthetic / open / commercial]
license_type: [Commercial / Open / Academic]
license_cost: [Annual cost if applicable]
tables: 0
total_rows: ~0
date_range: 2020-01-01 to 2024-12-31
sql_dialect: PostgreSQL
"""

    purpose_text = purpose_text or f"This database supports analytics for {db_id}."
    use_case_text = use_case_text or f"Target use cases for {db_id}: analytics, reporting, dashboards."
    business_value_text = business_value_text or f"Business value for {db_id}."
    schema_sql = schema_sql or "-- Schema from schema.sql"
    domain_knowledge_text = domain_knowledge_text or "Domain-specific concepts for this database."
    difficulty_dist_text = (
        difficulty_dist_text
        or """Target distribution across 30 queries:
- simple (10): Single-table, basic aggregation
- moderate (12): 2-3 table joins, GROUP BY
- challenging (8): CTEs, window functions
"""

    )

    sections = []

    # Title
    sections.append(f"# {db_name} — Query Documentation\n")

    # Database Overview
    sections.append("## Database Overview\n")
    sections.append("```yaml")
    sections.append(overview_yaml.strip())
    sections.append("```\n")

    # Purpose
    sections.append("## Purpose\n")
    sections.append("```text")
    sections.append(purpose_text.strip())
    sections.append("```\n")

    # Use Case
    sections.append("## Use Case\n")
    sections.append("```text")
    sections.append(use_case_text.strip())
    sections.append("```\n")

    # Business Value
    sections.append("## Business Value\n")
    sections.append("```text")
    sections.append(business_value_text.strip())
    sections.append("```\n")

    # Schema (minimal if no CREATE TABLE)
    sections.append("## Schema\n")
    sections.append("```sql")
    sections.append(schema_sql.strip())
    sections.append("```\n")

    # Domain Knowledge
    sections.append("## Domain Knowledge\n")
    sections.append("```text")
    sections.append(domain_knowledge_text.strip())
    sections.append("```\n")

    # Query Difficulty Distribution
    sections.append("## Query Difficulty Distribution\n")
    sections.append("```text")
    sections.append(difficulty_dist_text.strip())
    sections.append("```\n")

    # Queries
    sections.append("## Queries\n")
    for q in queries:
        sections.append(_format_query_block(q, db_id))

    return "\n".join(sections)


def format_query_block_template(
    number: int,
    title: str,
    description: str = "",
    use_case: str = "",
    business_value: str = "",
    purpose: str = "",
    complexity: str = "",
    expected_output: str = "",
    sql: str = "",
    db_id: str = "db-1",
    **kwargs: Any,
) -> str:
    """
    Format a single query block in template format.
    Accepts old-format args and normalizes to template.
    """
    q = {
        "number": number,
        "question_id": number,
        "title": title,
        "question": title or use_case,
        "description": description,
        "evidence": description,
        "use_case": use_case,
        "business_value": business_value,
        "purpose": purpose,
        "complexity": complexity,
        "expected_output": expected_output,
        "sql": sql,
        **kwargs,
    }
    return _format_query_block(q, db_id)

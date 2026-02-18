#!/usr/bin/env python3
"""
Load queries.md header sections from source/db-N/queries_header.yaml or queries_header.json.

The header file lives at the TOP LEVEL of source/db-N/ (not in app/). It provides
the content for Database Overview, Purpose, Use Case, Business Value, Schema,
Domain Knowledge, and Query Difficulty Distribution sections.

Usage:
    from load_queries_header import load_queries_header
    header = load_queries_header(SOURCE / "db-1")
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None


def load_queries_header(db_dir: Path) -> Optional[Dict[str, Any]]:
    """
    Load header sections from source/db-N/queries_header.yaml or queries_header.json.

    Returns dict with keys: db_name, overview_yaml, purpose_text, use_case_text,
    business_value_text, schema_sql, domain_knowledge_text, difficulty_dist_text.
    Returns None if no header file exists.
    """
    if not db_dir or not db_dir.is_dir():
        return None

    # Prefer YAML, then JSON
    yaml_path = db_dir / "queries_header.yaml"
    json_path = db_dir / "queries_header.json"

    raw: Dict[str, Any] = {}
    if yaml_path.exists():
        if yaml is None:
            raise ImportError(
                "PyYAML required for queries_header.yaml. Install with: pip install pyyaml"
            )
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    elif json_path.exists():
        raw = json.loads(json_path.read_text(encoding="utf-8"))

    if not raw:
        return None

    # schema_from: load schema from file (path relative to db_dir)
    schema_sql = raw.get("schema") or raw.get("schema_sql") or ""
    schema_from = raw.get("schema_from")
    if schema_from and not schema_sql.strip():
        p = (db_dir / schema_from).resolve()
        if p.exists():
            schema_sql = p.read_text(encoding="utf-8").strip()

    return {
        "db_name": raw.get("db_name", ""),
        "overview_yaml": raw.get("database_overview") or raw.get("overview_yaml") or "",
        "purpose_text": raw.get("purpose") or raw.get("purpose_text") or "",
        "use_case_text": raw.get("use_case") or raw.get("use_case_text") or "",
        "business_value_text": raw.get("business_value") or raw.get("business_value_text") or "",
        "schema_sql": schema_sql or raw.get("schema_sql") or "",
        "domain_knowledge_text": raw.get("domain_knowledge") or raw.get("domain_knowledge_text") or "",
        "difficulty_dist_text": raw.get("query_difficulty_distribution")
        or raw.get("difficulty_dist_text")
        or raw.get("difficulty_distribution")
        or "",
    }


def header_to_format_args(header: Dict[str, Any]) -> Dict[str, Any]:
    """Convert loaded header dict to kwargs for format_queries_md_template."""
    return {
        "db_name": header.get("db_name") or None,
        "overview_yaml": header.get("overview_yaml") or None,
        "purpose_text": header.get("purpose_text") or None,
        "use_case_text": header.get("use_case_text") or None,
        "business_value_text": header.get("business_value_text") or None,
        "schema_sql": header.get("schema_sql") or None,
        "domain_knowledge_text": header.get("domain_knowledge_text") or None,
        "difficulty_dist_text": header.get("difficulty_dist_text") or None,
    }

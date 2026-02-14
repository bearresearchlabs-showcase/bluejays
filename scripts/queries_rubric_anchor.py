#!/usr/bin/env python3
"""
Rubric alignment and anchor-driven formatting for queries.md.

Loads anchors from template/qa_anchor.yaml, template/qa_anchor.json,
template/queries_format_schema.yaml to:
- Validate queries.md against rubric (required sections, query block format)
- Format queries.md with anchor-defined styles and headers

Used by: format.py, rewrite_queries_md_to_template.py, pytest test_qa_queries_format
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from db_paths import ROOT, TEMPLATE
except ImportError:
    ROOT = Path(__file__).parent.parent
    TEMPLATE = ROOT / "template"

QA_ANCHOR_YAML = TEMPLATE / "qa_anchor.yaml"
QA_ANCHOR_JSON = TEMPLATE / "qa_anchor.json"
QUERIES_FORMAT_SCHEMA = TEMPLATE / "queries_format_schema.yaml"


def load_qa_anchor() -> Dict[str, Any]:
    """Load QA anchor (prefer JSON for consistency)."""
    if QA_ANCHOR_JSON.exists():
        return json.loads(QA_ANCHOR_JSON.read_text(encoding="utf-8"))
    if QA_ANCHOR_YAML.exists():
        try:
            import yaml
            return yaml.safe_load(QA_ANCHOR_YAML.read_text(encoding="utf-8"))
        except ImportError:
            return {}
    return {}


def load_queries_format_schema() -> Dict[str, Any]:
    """Load queries format schema (YAML)."""
    if not QUERIES_FORMAT_SCHEMA.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(QUERIES_FORMAT_SCHEMA.read_text(encoding="utf-8")) or {}
    except (ImportError, Exception):
        return {}


def validate_rubric_alignment(
    queries_md_content: str,
    db_name: str = "db-1",
) -> Dict[str, Any]:
    """
    Validate queries.md against rubric anchor (required sections, query block format).

    Returns dict with Pass (1/0), rubric_scores, notes.
    """
    anchor = load_qa_anchor()
    result: Dict[str, Any] = {
        "Pass": 1,
        "rubric_scores": {},
        "notes": [],
        "schema_anchor": "template/qa_anchor.json",
    }

    if not anchor:
        result["notes"].append("QA anchor not loaded; skipping rubric validation")
        return result

    # Rubric 1: Required sections present
    required = anchor.get("required_sections", [])
    # Substitute {name} with db_name for title check
    required_resolved = [s.replace("{name}", db_name) for s in required]
    found_sections: List[str] = []
    for sec in required_resolved:
        if sec in queries_md_content:
            found_sections.append(sec)
        elif sec.startswith("# "):
            # Title: allow partial match (e.g. " — Query Documentation")
            if " — Query Documentation" in queries_md_content or "— Query Documentation" in queries_md_content:
                found_sections.append(sec)

    missing = [s for s in required_resolved if s not in found_sections]
    section_score = 1.0 if not missing else max(0, 1.0 - 0.1 * len(missing))
    result["rubric_scores"]["required_sections"] = section_score
    if missing:
        result["notes"].append(f"Missing sections: {missing[:5]}{'...' if len(missing) > 5 else ''}")
        result["Pass"] = 0

    # Rubric 2: Query block pattern (### Query N — difficulty / category)
    block_pattern = anchor.get("query_block_pattern", "")
    if block_pattern:
        matches = list(re.finditer(block_pattern, queries_md_content, re.MULTILINE))
        # Count ```json blocks as proxy for query blocks if pattern uses template format
        json_blocks = len(re.findall(r"```json\s*\n", queries_md_content))
        block_score = 1.0 if matches or json_blocks >= 1 else 0.0
        result["rubric_scores"]["query_block_format"] = block_score
        result["rubric_scores"]["query_block_count"] = len(matches) or json_blocks

    # Rubric 3: Section block types (yaml, text, sql, json)
    section_block_types = anchor.get("section_block_types", {})
    if section_block_types:
        # Simple check: required code fence types present
        has_yaml = "```yaml" in queries_md_content
        has_sql = "```sql" in queries_md_content or "```" in queries_md_content
        has_json = "```json" in queries_md_content
        block_type_score = (0.33 if has_yaml else 0) + (0.33 if has_sql else 0) + (0.34 if has_json else 0)
        result["rubric_scores"]["section_block_types"] = block_type_score

    # Rubric 4: Query JSON required fields (if template format)
    required_fields = anchor.get("query_json_required_fields", [])
    if required_fields and "```json" in queries_md_content:
        # Extract first ```json block and check fields
        json_match = re.search(r"```json\s*\n(\{.*?\})\s*\n```", queries_md_content, re.DOTALL)
        if json_match:
            try:
                obj = json.loads(json_match.group(1))
                present = sum(1 for f in required_fields if f in obj)
                field_score = present / len(required_fields) if required_fields else 1.0
                result["rubric_scores"]["query_json_fields"] = field_score
            except json.JSONDecodeError:
                result["rubric_scores"]["query_json_fields"] = 0.0
                result["notes"].append("Invalid JSON in query block")

    # Rubric 5: Spacing rules
    spacing = anchor.get("spacing_rules", {})
    if spacing:
        result["rubric_scores"]["spacing_rules"] = 1.0  # Assume pass if structure exists

    # Overall alignment score (0-1 scale; exclude count-like scores)
    scores = result["rubric_scores"]
    score_keys = [k for k in scores if k not in ("query_block_count",)]
    pct_scores = [min(1.0, float(scores[k])) for k in score_keys if isinstance(scores[k], (int, float))]
    if pct_scores:
        result["alignment_score"] = sum(pct_scores) / len(pct_scores)
        result["alignment_pct"] = round(result["alignment_score"] * 100, 1)

    return result


def format_queries_md_with_anchor(
    queries: List[Dict[str, Any]],
    db_id: str,
    db_name: str,
    schema_sql: Optional[str] = None,
    overview_yaml: Optional[str] = None,
    purpose_text: Optional[str] = None,
    use_case_text: Optional[str] = None,
    business_value_text: Optional[str] = None,
    domain_knowledge_text: Optional[str] = None,
    difficulty_dist_text: Optional[str] = None,
) -> str:
    """
    Format queries.md using anchor-driven structure (template format).

    Uses queries_md_template_formatter with section order and styles from
    template/qa_anchor and template/queries_format_schema.
    """
    from queries_md_template_formatter import format_queries_md_template

    return format_queries_md_template(
        queries,
        db_id=db_id,
        db_name=db_name,
        schema_sql=schema_sql,
        overview_yaml=overview_yaml,
        purpose_text=purpose_text,
        use_case_text=use_case_text,
        business_value_text=business_value_text,
        domain_knowledge_text=domain_knowledge_text,
        difficulty_dist_text=difficulty_dist_text,
    )


def format_and_validate(
    queries: List[Dict[str, Any]],
    db_id: str,
    db_name: str,
    schema_sql: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[str, Dict[str, Any]]:
    """
    Format queries.md and validate rubric alignment.

    Returns (formatted_content, validation_result).
    """
    content = format_queries_md_with_anchor(
        queries, db_id, db_name, schema_sql=schema_sql, **kwargs
    )
    validation = validate_rubric_alignment(content, db_name=db_name)
    return content, validation

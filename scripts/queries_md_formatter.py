#!/usr/bin/env python3
"""
Canonical formatter for queries.md files.

All scripts that generate or write queries.md MUST use this module to ensure
consistent formatting. See docs/QUERIES_MD_FORMAT.md for the format spec.

Format:
- # SQL Queries for db-{N}
- ## Query N: Title
- **Description:** ...
- **Use Case:** ...
- **Business Value:** ...
- **Purpose:** ...
- **Complexity:** ...
- **Expected Output:** ...
- ```sql
- SQL
- ```

Blank line (\n\n) between each metadata field. Field order is fixed.
"""

from typing import Any, Dict, List, Optional


def format_query_block(
    number: int,
    title: str,
    description: str = "",
    use_case: str = "",
    business_value: str = "",
    purpose: str = "",
    complexity: str = "",
    expected_output: str = "",
    sql: str = "",
) -> str:
    """Format a single query block with canonical metadata order and spacing."""
    lines = [
        f"## Query {number}: {title}",
        "",
        f"**Description:** {description}",
        "",
        f"**Use Case:** {use_case}",
        "",
        f"**Business Value:** {business_value}",
        "",
        f"**Purpose:** {purpose}",
        "",
        f"**Complexity:** {complexity}",
        "",
        f"**Expected Output:** {expected_output}",
        "",
        "```sql",
        sql.strip(),
        "```",
        "",
    ]
    return "\n".join(lines)


def format_queries_md(
    queries: List[Dict[str, Any]],
    db_num: Optional[int] = None,
    intro: Optional[str] = None,
) -> str:
    """
    Generate full queries.md content from a list of query dicts.

    Each query dict should have: number, title, description, use_case,
    business_value, purpose, complexity, expected_output, sql.
    Missing keys default to empty string.

    Args:
        queries: List of query dicts (from queries.json, deliverable JSON, etc.)
        db_num: Database number for header (e.g. 1 -> "SQL Queries for db-1")
        intro: Optional intro text after header, before first query

    Returns:
        Full queries.md content string
    """
    header = f"# SQL Queries for db-{db_num}\n\n" if db_num else "# SQL Queries for Database\n\n"
    if intro:
        header += intro.strip() + "\n\n"

    blocks = []
    for q in queries:
        num = q.get("number", 0)
        title = q.get("title", f"Query {num}")
        blocks.append(
            format_query_block(
                number=num,
                title=title,
                description=q.get("description", ""),
                use_case=q.get("use_case", ""),
                business_value=q.get("business_value", ""),
                purpose=q.get("purpose", ""),
                complexity=q.get("complexity", ""),
                expected_output=q.get("expected_output", ""),
                sql=q.get("sql", ""),
            )
        )

    return header + "\n".join(blocks)

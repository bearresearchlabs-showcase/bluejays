#!/usr/bin/env python3
"""
Tests that queries.md supports natural human text without breaking extraction.
Run: pytest tests/test_queries_md_human_text.py -v
"""
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from extract_queries_to_json import QueryExtractor


SAMPLE_WITH_INTRO = """# SQL Queries for Test DB

This file contains queries for the test database. You can add any natural language
intro here before the first query. It will not break extraction.

## Query 1: Simple Count

**Description:** Counts rows.
**Complexity:** Simple
**Expected Output:** Single row with count

```sql
SELECT COUNT(*) AS cnt FROM t;
```

## Query 2: Another Query

**Description:** Another example.
**Complexity:** Simple
**Expected Output:** Results

```sql
SELECT 1 AS x;
```
"""

SAMPLE_WITH_EXTRA_PARAGRAPHS = """## Query 1: With Extra Notes

This query is useful when you need to analyze customer behavior.
Add as much natural text as you want between the header and the SQL block.
It all gets included in the description for the query.

**Description:** Customer analysis.
**Complexity:** Medium
**Expected Output:** Customer metrics

```sql
SELECT * FROM customers LIMIT 10;
```
"""


class TestHumanTextInQueriesMd:
    """Extraction must work when queries.md contains natural human text."""

    def test_intro_before_query_1_does_not_break(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_WITH_INTRO)
            path = Path(f.name)
        try:
            ext = QueryExtractor(path)
            queries = ext.extract_all_queries()
            assert len(queries) == 2
            assert queries[0]["number"] == 1
            assert queries[0]["sql"].strip().startswith("SELECT COUNT(*)")
            assert queries[1]["number"] == 2
        finally:
            path.unlink()

    def test_extra_paragraphs_before_sql_included_in_description(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(SAMPLE_WITH_EXTRA_PARAGRAPHS)
            path = Path(f.name)
        try:
            ext = QueryExtractor(path)
            queries = ext.extract_all_queries()
            assert len(queries) == 1
            desc = queries[0]["description"]
            # Natural text should be in description
            assert "customer" in desc.lower() or "analyze" in desc.lower() or "behavior" in desc.lower()
        finally:
            path.unlink()

    def test_real_db1_extraction_has_30_queries(self):
        qm = ROOT / "db-1" / "queries" / "queries.md"
        if not qm.exists():
            pytest.skip("db-1/queries/queries.md not found")
        ext = QueryExtractor(qm)
        queries = ext.extract_all_queries()
        assert len(queries) == 30
        for i, q in enumerate(queries, 1):
            assert q["number"] == i
            assert q["sql"].strip(), f"Query {i} has empty SQL"

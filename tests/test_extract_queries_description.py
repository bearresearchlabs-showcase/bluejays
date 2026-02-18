#!/usr/bin/env python3
"""
TDD: When JSON block has no description, extraction sets description='' not evidence.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_extract_queries_missing_description_uses_empty_not_evidence(tmp_path):
    """TDD: When JSON block has no description, extraction sets description='' not evidence."""
    from extract_queries_to_json import extract_queries

    md_content = """
## Query 1: Test

```json
{
  "question": "Test?",
  "evidence": "The query uses CTEs and window functions.",
  "SQL": "SELECT 1 AS x"
}
```
"""
    md_path = tmp_path / "queries.md"
    md_path.write_text(md_content, encoding="utf-8")

    results = extract_queries(md_path)
    assert len(results) == 1
    entry = results[0]
    # description must not equal evidence when description is missing from block
    assert entry["description"] != entry["evidence"], (
        "extraction must not use evidence as description fallback"
    )
    # When description missing, should be empty (or short placeholder), not full evidence
    ev = entry.get("evidence", "")
    desc = entry.get("description", "")
    assert not (desc and ev and desc == ev[: len(desc)]), (
        "description must not be prefix of evidence when block had no description"
    )

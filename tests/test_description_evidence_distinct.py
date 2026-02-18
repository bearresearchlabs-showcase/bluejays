#!/usr/bin/env python3
"""
TDD: description and evidence must be distinct in queries.json.
No query may have description == evidence or evidence overlapping description.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"


def _find_queries_json(db_num: int) -> Path | None:
    """Find queries.json for db-N (queries/ or app/QUERIES)."""
    for sub in ("queries", "app/QUERIES"):
        p = SOURCE / f"db-{db_num}" / sub / "queries.json"
        if p.exists():
            return p
    return None


def test_queries_json_description_evidence_distinct():
    """TDD: No query may have description == evidence (or evidence starting with description)."""
    for db_num in range(1, 17):
        qj = _find_queries_json(db_num)
        if not qj:
            continue
        data = json.loads(qj.read_text())
        for q in data.get("queries", []):
            desc = (q.get("description") or "").strip()
            ev = (q.get("evidence") or "").strip()
            assert desc != ev, (
                f"db-{db_num} query {q.get('number')}: description == evidence"
            )
            assert not (
                ev.startswith(desc) and len(desc) > 50
            ), (
                f"db-{db_num} query {q.get('number')}: evidence overlaps description"
            )

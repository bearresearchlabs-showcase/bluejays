#!/usr/bin/env python3
"""
Copy Domain Knowledge, Business Value, Use Case, Purpose, and Database Overview
from client/db/db-{N}/QUERIES/queries.md to source/db-{N}/app/QUERIES/queries.md.

Usage:
    python3 scripts/sync_queries_md_sections.py [db-1] [db-5] | -a
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SECTIONS = ["Database Overview", "Purpose", "Use Case", "Business Value", "Domain Knowledge"]


def extract_section(content: str, section_name: str) -> str | None:
    """Extract a section including its ## header and content until next ##."""
    pattern = rf"(^## {re.escape(section_name)}\s*\n.*?)(?=^## |\Z)"
    m = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    return m.group(1).rstrip() if m else None


def extract_all_sections(content: str) -> dict[str, str]:
    """Extract the 5 target sections from content."""
    result = {}
    for name in SECTIONS:
        block = extract_section(content, name)
        if block:
            result[name] = block
    return result


def replace_sections(source_content: str, sections: dict[str, str]) -> str:
    """Replace the 5 sections in source_content with content from sections dict."""
    result = source_content
    for name in SECTIONS:
        new_block = sections.get(name)
        if not new_block:
            continue
        pattern = rf"^## {re.escape(name)}\s*\n.*?(?=^## |\Z)"
        result = re.sub(pattern, new_block + "\n\n", result, count=1, flags=re.MULTILINE | re.DOTALL)
    return result


def sync_db(db_id: str) -> bool:
    """Sync the 5 sections from client to source for one database."""
    client_path = ROOT / "client" / "db" / db_id / "QUERIES" / "queries.md"
    source_path = ROOT / "source" / db_id / "app" / "QUERIES" / "queries.md"

    if not client_path.exists():
        print(f"  skip: client {client_path} not found")
        return False
    if not source_path.exists():
        print(f"  skip: source {source_path} not found")
        return False

    client_content = client_path.read_text(encoding="utf-8")
    source_content = source_path.read_text(encoding="utf-8")

    sections = extract_all_sections(client_content)
    if not sections:
        print(f"  skip: no target sections found in client")
        return False

    new_source = replace_sections(source_content, sections)
    if new_source == source_content:
        print(f"  no change")
        return True

    source_path.write_text(new_source, encoding="utf-8")
    print(f"  updated: {', '.join(sections.keys())}")
    return True


def main():
    args = sys.argv[1:]
    if "-a" in args:
        dbs = [f"db-{n}" for n in range(1, 17)]
    elif args:
        dbs = [a if a.startswith("db-") else f"db-{a}" for a in args]
    else:
        dbs = [f"db-{n}" for n in range(1, 17)]

    for db_id in dbs:
        print(f"{db_id}:")
        sync_db(db_id)


if __name__ == "__main__":
    main()

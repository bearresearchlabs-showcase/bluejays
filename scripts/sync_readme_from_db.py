#!/usr/bin/env python3
"""
Sync source/db-{N}/app/DOCUMENTATION/README.md with the actual database:
- Title from queries.md (first # line)
- Table count and names from app/DATABASE/schema.sql (or schema_postgresql.sql)
- Correct psql paths: DATABASE/schema.sql, DATABASE/data.sql
- Preserves existing Data Dictionary and other sections when possible
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"


def get_tables_from_schema(db_dir: Path) -> list[str]:
    """Extract table names from schema.sql or schema_postgresql.sql."""
    data_dir = db_dir / "app" / "DATABASE"
    if not data_dir.exists():
        return []
    for name in ("schema.sql", "schema_postgresql.sql"):
        path = data_dir / name
        if path.exists():
            content = path.read_text(encoding="utf-8")
            tables = []
            for m in re.finditer(r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:public\.)?(\w+)", content, re.I):
                tables.append(m.group(1))
            return tables
    return []


def get_title_from_queries(db_dir: Path) -> str:
    """Extract database title from queries.md first heading."""
    qpath = db_dir / "app" / "QUERIES" / "queries.md"
    if not qpath.exists():
        qpath = db_dir / "queries" / "queries.md"
    if not qpath.exists():
        return f"Database db-{db_dir.name.split('-')[1]}"
    content = qpath.read_text(encoding="utf-8")
    m = re.search(r"^#\s+(.+?)\s*—", content, re.M)
    if m:
        return m.group(1).strip()
    m = re.search(r"^#\s+(.+)", content, re.M)
    return m.group(1).strip() if m else f"Database {db_dir.name}"


def has_data_sql(db_dir: Path) -> bool:
    """Check if data.sql exists."""
    return (db_dir / "app" / "DATABASE" / "data.sql").exists()


def update_readme_in_place(readme_path: Path, db_id: str, db_dir: Path) -> bool:
    """Update README in place: fix title, paths, schema overview. Returns True if changed."""
    original = readme_path.read_text(encoding="utf-8")
    content = original
    tables = get_tables_from_schema(db_dir)
    if not tables:
        return False
    title = get_title_from_queries(db_dir)
    schema_path = "DATABASE/schema.sql"
    data_path = "DATABASE/data.sql"

    # Fix frontmatter title and database
    content = re.sub(r"^title:\s*.+$", f"title: {title} — Documentation", content, count=1, flags=re.M)
    content = re.sub(r"^database:\s*\S+", f"database: {db_id}", content, count=1, flags=re.M)

    # Fix main heading (first # in body, after frontmatter)
    content = re.sub(r"^#\s+.+$", f"# {title} — Documentation", content, count=1, flags=re.M)

    # Fix psql paths: schema.sql -> DATABASE/schema.sql when run from app/
    content = re.sub(r"-f\s+schema\.sql", f"-f {schema_path}", content)
    content = re.sub(r"-f\s+data\.sql", f"-f {data_path}", content)

    # Fix Schema Overview: total tables and list
    table_list = "\n".join(f"- `{t}` — (see data dictionary)" for t in tables)
    new_overview = f"**Total tables:** {len(tables)}\n\n{table_list}"
    overview_pattern = r"\*\*Total tables:\*\*\s*\d+\s*\n\n(?:- `[\w_]+` — \(see data dictionary\)\n?)+"
    m = re.search(overview_pattern, content)
    if m:
        content = content[: m.start()] + new_overview + content[m.end() :]

    if content != original:
        readme_path.write_text(content, encoding="utf-8")
        return True
    return False


def main():
    args = sys.argv[1:]
    if "-a" in args or "--all" in args:
        dbs = [f"db-{n}" for n in range(1, 17)]
    elif args:
        dbs = [a if a.startswith("db-") else f"db-{a}" for a in args]
    else:
        dbs = [f"db-{n}" for n in range(1, 17)]

    for db_id in dbs:
        db_dir = SOURCE / db_id
        readme_path = db_dir / "app" / "DOCUMENTATION" / "README.md"
        if not readme_path.exists():
            print(f"{db_id}: README.md not found, skip")
            continue
        tables = get_tables_from_schema(db_dir)
        if not tables:
            print(f"{db_id}: no schema found, skip")
            continue
        if update_readme_in_place(readme_path, db_id, db_dir):
            print(f"{db_id}: updated ({len(tables)} tables)")
        else:
            print(f"{db_id}: no change")


if __name__ == "__main__":
    main()

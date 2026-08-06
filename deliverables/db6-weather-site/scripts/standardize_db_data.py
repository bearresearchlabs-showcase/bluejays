#!/usr/bin/env python3
"""
Standardize db-1 through db-16 to have only:
- data/schema.sql
- data/data.sql
- deliverable/db{N}-{name}/db-{N}.md (and related docs)

Removes extra SQL files, consolidates schema where needed.
"""

import shutil
from pathlib import Path

BASE = Path(__file__).parent.parent

def main():
    for n in range(1, 17):
        data_dir = BASE / f"db-{n}" / "data"
        if not data_dir.exists():
            continue

        sql_files = list(data_dir.glob("*.sql"))
        keep = {"schema.sql", "data.sql"}
        to_remove = [f for f in sql_files if f.name not in keep]

        # db-4: merge schema_models.sql into schema.sql
        if n == 4:
            schema_models = data_dir / "schema_models.sql"
            if schema_models.exists():
                schema = data_dir / "schema.sql"
                models_content = schema_models.read_text()
                if "CREATE TABLE" in models_content and schema.exists():
                    # Prepend or append models - append before final \unrestrict if present
                    content = schema.read_text()
                    if "\\unrestrict" in content:
                        insert_before = content.rfind("\\unrestrict")
                        content = content[:insert_before] + "\n\n" + models_content + "\n\n" + content[insert_before:]
                    else:
                        content += "\n\n" + models_content
                    schema.write_text(content)
                to_remove.append(schema_models)

        # db-6: merge schema_extensions, insurance_schema, nexrad_satellite_schema into schema.sql
        if n == 6:
            schema = data_dir / "schema.sql"
            if schema.exists():
                parts = [schema.read_text()]
                for ext in ["schema_extensions.sql", "insurance_schema.sql", "nexrad_satellite_schema.sql"]:
                    p = data_dir / ext
                    if p.exists():
                        parts.append(p.read_text())
                schema.write_text("\n\n--\n\n".join(parts))

        for f in to_remove:
            if f.is_file():
                f.unlink()
                print(f"  Removed {f.relative_to(BASE)}")

        remaining = list(data_dir.glob("*.sql"))
        print(f"db-{n}: {[x.name for x in sorted(remaining)]}")

        # Also clean deliverable/data/ and deliverable/dbN-name/data/
        for sub in ["deliverable/data", f"deliverable/db{n}-*/data"]:
            for d in (BASE / f"db-{n}").glob(sub):
                if d.is_dir():
                    for f in d.glob("*.sql"):
                        if f.name not in keep:
                            f.unlink()
                            print(f"  Removed {f.relative_to(BASE)}")

if __name__ == "__main__":
    main()

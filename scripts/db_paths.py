"""Resolve effective paths for source/db-N. Single source: data/, queries/, docs/ -> DATABASE/, QUERIES/, DOCUMENTATION/."""

from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
TEMPLATE = ROOT / "template"  # Canonical template: @template/queries.md, queries.json


def get_canonical_dir(db_dir: Path) -> Path | None:
    """Return db_dir if it has canonical structure (DATABASE/, DOCUMENTATION/, QUERIES/), else None."""
    if (db_dir / "DATABASE").exists() and (db_dir / "QUERIES").exists():
        return db_dir
    return None


def get_app_dir(db_dir: Path) -> Path | None:
    """Return dir with canonical structure: root (DATABASE/) or legacy app/. Backwards compat."""
    if (db_dir / "DATABASE").exists():
        return db_dir
    app = db_dir / "app"
    if app.exists() and (app / "DATABASE").exists():
        return app
    return None


def get_data_dir(db_dir: Path) -> Path:
    """Return effective data dir. Single source: data/; compiled: DATABASE/ or app/DATABASE/."""
    if (db_dir / "DATABASE").exists():
        return db_dir / "DATABASE"
    app = db_dir / "app"
    if app.exists() and (app / "DATABASE").exists():
        return app / "DATABASE"
    return db_dir / "data"


def get_queries_dir(db_dir: Path) -> Path:
    """Return effective queries dir. Single source: queries/; compiled: QUERIES/ or app/QUERIES/."""
    if (db_dir / "QUERIES").exists():
        return db_dir / "QUERIES"
    app = db_dir / "app"
    if app.exists() and (app / "QUERIES").exists():
        return app / "QUERIES"
    return db_dir / "queries"


def get_doc_dir(db_dir: Path) -> Path | None:
    """Return effective documentation dir. Single source: docs/; compiled: DOCUMENTATION/ or app/DOCUMENTATION/."""
    if (db_dir / "DOCUMENTATION").exists():
        return db_dir / "DOCUMENTATION"
    app = db_dir / "app"
    if app.exists() and (app / "DOCUMENTATION").exists():
        return app / "DOCUMENTATION"
    if (db_dir / "docs").exists():
        return db_dir / "docs"
    return None


GB = 1024**3


def get_primary_data_file(all_sql: dict[str, Path]) -> tuple[str, Path] | None:
    """Return (dest_name, path) for the primary data file. Prefer data_large >= 1GB; else data.sql."""
    for src in ["data_large_postgresql.sql", "data_large.sql"]:
        if src in all_sql and all_sql[src].stat().st_size >= GB:
            return ("data_large.sql", all_sql[src])
    if "data.sql" in all_sql and all_sql["data.sql"].stat().st_size >= GB:
        return ("data_large.sql", all_sql["data.sql"])  # db-16: data.sql is 2.5GB
    if "data.sql" in all_sql:
        return ("data.sql", all_sql["data.sql"])
    return None


def get_primary_data_path(data_dir: Path) -> tuple[str, Path] | None:
    """Return (key, path) for primary data file in data_dir. Key for integrity: data.sql or data_large.sql."""
    if not data_dir.exists():
        return None
    all_sql = {f.name: f for f in data_dir.iterdir() if f.is_file() and f.suffix.lower() == ".sql"}
    return get_primary_data_file(all_sql)

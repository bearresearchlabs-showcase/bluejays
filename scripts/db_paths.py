"""Resolve effective paths for source/db-N. Prefers app/ (iron triangle) when present."""

from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "source"
TEMPLATE = ROOT / "template"  # Canonical template: @template/queries.md, queries.json


def get_app_dir(db_dir: Path) -> Path | None:
    """Return app/ dir if it exists with DATABASE/, else None."""
    app = db_dir / "app"
    if app.exists() and (app / "DATABASE").exists():
        return app
    return None


def get_data_dir(db_dir: Path) -> Path:
    """Return effective data dir: app/DATABASE/ or data/."""
    app = get_app_dir(db_dir)
    if app:
        return app / "DATABASE"
    return db_dir / "data"


def get_queries_dir(db_dir: Path) -> Path:
    """Return effective queries dir: app/QUERIES/ or queries/ or QUERIES/."""
    app = get_app_dir(db_dir)
    if app and (app / "QUERIES").exists():
        return app / "QUERIES"
    if (db_dir / "QUERIES").exists():
        return db_dir / "QUERIES"
    return db_dir / "queries"


def get_doc_dir(db_dir: Path) -> Path | None:
    """Return effective documentation dir: app/DOCUMENTATION/ or None (use deliverable)."""
    app = get_app_dir(db_dir)
    if app and (app / "DOCUMENTATION").exists():
        return app / "DOCUMENTATION"
    return None

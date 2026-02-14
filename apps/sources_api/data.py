"""
Core logic for sources discovery and query loading. No FastAPI dependency.
Unit-tested in isolation.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = ROOT / "source"
TEMPLATE_DIR = ROOT / "template"


def discover_sources() -> list[str]:
    """Discover database sources from source/ and template/. Returns ['template', 'db-1', ...]."""
    sources = ["template"]
    if not SOURCE_DIR.exists():
        return sources

    dirs = [
        d.name
        for d in SOURCE_DIR.iterdir()
        if d.is_dir() and d.name.startswith("db-")
    ]
    dirs.sort(key=lambda x: int(x.replace("db-", "")) if x.replace("db-", "").isdigit() else 999)

    for name in dirs:
        base1 = SOURCE_DIR / name / "app" / "QUERIES" / "queries.json"
        base2 = SOURCE_DIR / name / "QUERIES" / "queries.json"
        base3 = ROOT / name / "queries" / "queries.json"
        if base1.exists() or base2.exists() or base3.exists():
            sources.append(name)
    return sources


def load_queries(source: str) -> tuple[list[dict], str | None]:
    """Load queries from source. Returns (queries, error)."""
    if source.lower() == "template":
        path = TEMPLATE_DIR / "queries.json"
    else:
        try:
            num = int(source.replace("db-", "").strip())
        except ValueError:
            return [], f"Invalid source: {source}"
        bases = [
            SOURCE_DIR / f"db-{num}" / "app" / "QUERIES" / "queries.json",
            SOURCE_DIR / f"db-{num}" / "QUERIES" / "queries.json",
            ROOT / f"db-{num}" / "queries" / "queries.json",
        ]
        path = None
        for p in bases:
            if p.exists():
                path = p
                break
        if not path:
            return [], f"Not found: {source}"

    try:
        import json
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            queries = [q for q in data if isinstance(q, dict) and (q.get("question_id") is not None or q.get("number") is not None or q.get("sql") is not None)]
        else:
            queries = data.get("queries") or data.get("data", {}).get("queries") or []
        return queries, None
    except Exception as e:
        return [], str(e)

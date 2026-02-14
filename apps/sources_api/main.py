"""
Sources API microservice — smallest feature: discover database sources and load queries.
Mirrors lib/data.ts logic for annotator. Unit → Integration → UAT → Docker.
"""
from fastapi import FastAPI, HTTPException

from .data import discover_sources, load_queries

app = FastAPI(title="Sources API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "sources-api"}


@app.get("/sources")
def get_sources():
    """List discovered database sources."""
    sources = discover_sources()
    return {"sources": sources}


@app.get("/queries")
def get_queries(source: str):
    """Load queries for a source."""
    if not source:
        raise HTTPException(400, "source query param required")
    queries, err = load_queries(source)
    if err:
        raise HTTPException(404, err)
    return {"queries": queries}

"""
Work API — Microservice for storing and querying work in Qdrant.

Exposes REST API for:
- Storing work items (annotations, queries, schemas)
- Semantic search over stored work
- Ingesting databases from source/ into Qdrant
- Collection management

Connects to Qdrant via QDRANT_URL (default: http://qdrant:6333).
"""
from contextlib import asynccontextmanager
import json
import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = os.getenv("WORK_COLLECTION", "work_items")
VECTOR_SIZE = int(os.getenv("WORK_VECTOR_SIZE", "384"))  # all-MiniLM-L6-v2 default
SOURCE_DIR = Path(os.getenv("SOURCE_DIR", "/app/source"))
TEMPLATE_DIR = Path(os.getenv("TEMPLATE_DIR", "/app/template"))


class WorkItem(BaseModel):
    """Work item to store."""
    kind: str  # annotation, query, schema, note
    source: str  # db-1, template, label_studio
    content: dict[str, Any]
    text: str = ""  # For embedding; if empty, use json.dumps(content)


class WorkSearch(BaseModel):
    """Search request."""
    query: str
    limit: int = 10
    filter_kind: str | None = None
    filter_source: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure collection exists on startup."""
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url=QDRANT_URL)
        collections = client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config={"size": VECTOR_SIZE, "distance": "Cosine"},
            )
    except Exception as e:
        print(f"Qdrant init warning: {e}")
    yield


app = FastAPI(title="Work API", lifespan=lifespan)


def _get_embedding(text: str) -> list[float]:
    """Embedding via sentence-transformers or fallback for dev."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(text).tolist()
    except ImportError:
        # Fallback: deterministic pseudo-vector from text hash (dev only)
        import hashlib
        h = hashlib.sha256(text.encode()).digest()
        return [(int(h[i % 32]) - 128) / 128.0 for i in range(VECTOR_SIZE)]


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok", "qdrant_url": QDRANT_URL}


@app.post("/work")
def store_work(item: WorkItem):
    """Store a work item."""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct
    except ImportError:
        raise HTTPException(500, "qdrant-client not installed")
    text = item.text or str(item.content)
    vector = _get_embedding(text)
    point_id = str(uuid.uuid4())
    payload = {
        "kind": item.kind,
        "source": item.source,
        "content": item.content,
    }
    client = QdrantClient(url=QDRANT_URL)
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=point_id, vector=vector, payload=payload)],
    )
    return {"id": point_id, "status": "stored"}


@app.post("/search")
def search_work(req: WorkSearch):
    """Semantic search over work items."""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
    except ImportError:
        raise HTTPException(500, "qdrant-client not installed")
    vector = _get_embedding(req.query)
    client = QdrantClient(url=QDRANT_URL)
    q_filter = None
    if req.filter_kind or req.filter_source:
        must = []
        if req.filter_kind:
            must.append(FieldCondition(key="kind", match=MatchValue(value=req.filter_kind)))
        if req.filter_source:
            must.append(FieldCondition(key="source", match=MatchValue(value=req.filter_source)))
        if must:
            q_filter = Filter(must=must)
    resp = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=req.limit,
        query_filter=q_filter,
    )
    return {
        "results": [
            {"id": str(p.id), "score": p.score, "payload": p.payload}
            for p in resp.points
        ]
    }


@app.get("/collections")
def list_collections():
    """List collections."""
    try:
        from qdrant_client import QdrantClient
    except ImportError:
        raise HTTPException(500, "qdrant-client not installed")
    client = QdrantClient(url=QDRANT_URL)
    cols = client.get_collections().collections
    return {"collections": [{"name": c.name} for c in cols]}


def _discover_and_load_queries() -> list[tuple[str, dict]]:
    """Discover all queries from source/ and template/. Returns [(source, query_dict), ...]."""
    items: list[tuple[str, dict]] = []
    # template
    template_path = TEMPLATE_DIR / "queries.json"
    if template_path.exists():
        data = json.loads(template_path.read_text(encoding="utf-8"))
        queries = [x for x in (data if isinstance(data, list) else data.get("queries", [])) if isinstance(x, dict) and "question_id" in x]
        for q in queries:
            items.append(("template", q))
    # source/db-N
    if SOURCE_DIR.exists():
        def _sort_key(p):
            if not p.name.startswith("db-"):
                return (1, p.name)
            try:
                return (0, int(p.name.replace("db-", "")))
            except ValueError:
                return (0, 999)
        for d in sorted(SOURCE_DIR.iterdir(), key=_sort_key):
            if not d.is_dir() or not d.name.startswith("db-"):
                continue
            for base in ["app/QUERIES", "QUERIES"]:
                qpath = d / base / "queries.json"
                if qpath.exists():
                    data = json.loads(qpath.read_text(encoding="utf-8"))
                    queries = data.get("queries", []) if isinstance(data, dict) else [x for x in data if isinstance(x, dict) and "question_id" in x]
                    for q in queries:
                        items.append((d.name, q))
                    break
    return items


@app.post("/ingest")
def ingest_source_databases():
    """Ingest all databases from source/ and template/ into Qdrant."""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct
    except ImportError:
        raise HTTPException(500, "qdrant-client not installed")
    items = _discover_and_load_queries()
    if not items:
        return {"status": "ok", "ingested": 0, "message": "No queries found in SOURCE_DIR or TEMPLATE_DIR"}
    client = QdrantClient(url=QDRANT_URL)
    points = []
    for source, q in items:
        text = q.get("question", "") + " " + q.get("SQL", q.get("sql", "")) + " " + str(q.get("evidence", ""))
        vector = _get_embedding(text)
        point_id = uuid.uuid4()
        payload = {"kind": "query", "source": source, "content": q, "question_id": q.get("question_id")}
        points.append(PointStruct(id=point_id, vector=vector, payload=payload))
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"status": "ok", "ingested": len(points), "sources": list({s for s, _ in items})}


@app.get("/ingest/status")
def ingest_status():
    """Return discovery status (how many queries would be ingested)."""
    items = _discover_and_load_queries()
    by_source = {}
    for s, _ in items:
        by_source[s] = by_source.get(s, 0) + 1
    return {"total": len(items), "by_source": by_source, "source_dir": str(SOURCE_DIR), "template_dir": str(TEMPLATE_DIR)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

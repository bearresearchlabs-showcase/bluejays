# Query Descriptions: Intent-Focused Natural Language

## Overview

Query descriptions in this project follow **LiveSQLBench** and **BenchPress** style: intent-focused, natural-language text that expresses what the user wants to accomplish, not technical summaries of SQL operations.

## Preferred Format

### 1. Natural Language Query (Best)

Use a first-person, intent-focused sentence:

- **Good**: "I want to analyze how weather station coverage varies by forecast office and identify gaps in our monitoring network."
- **Good**: "Show me the top 10 credit cards by rewards value for travel spending in the last 90 days."
- **Avoid**: "JOINs weather_stations with shapefile_boundaries and aggregates by office_code."

### 2. Intent Field

When `natural_language_query` is not available, the system uses `intent`:

```json
{
  "number": 1,
  "title": "Weather Station Coverage Analysis",
  "intent": "I want to analyze how weather station coverage varies by forecast office.",
  "description": "Uses spatial joins and aggregations..."
}
```

### 3. Fallback: Combined Metadata

If neither `natural_language_query` nor `intent` exists, the website builds display text from:

1. `use_case` (Business Use Case)
2. `business_value` (Client Deliverable)
3. `purpose` (Purpose/Reason)
4. `description` (Technical description, if not redundant)

## Display in Website

The website (`apps/web/`) shows query intent under an **"Intent"** label in:

- **Database detail view** – Query preview cards
- **Docs content** – Full query documentation
- **Comprehensive database JSON** – `intent_display` field (built by `build-comprehensive-database.js`)

## Data Flow

1. **Source**: `queries.json` or `*_deliverable.json` with `natural_language_query`, `intent`, `use_case`, `business_value`, `purpose`, `description`
2. **Build**: `scripts/build-comprehensive-database.js` → `buildIntentDisplay()` → `intent_display`
3. **API**: `/api/databases/[id]` returns `queries.preview[].intent_display`
4. **Docs**: `/api/deliverable/[id]` returns raw queries; `DocsContent` builds intent client-side

## Qdrant Propagation

After building the website (`npm run sync-content`), propagate to Qdrant (Docker):

```bash
# From repo root: Start Work API + Qdrant
docker compose -f docker/docker-compose.work-microservices.yml up -d

# Sync website data to Qdrant
WORK_API_URL=http://localhost:8010 npm run sync-to-qdrant
```

The Work API `POST /ingest/website` accepts `comprehensive-database.json` and uses `intent_display` for vector embeddings.

## References

- **LiveSQLBench**: Long, natural-language queries for text-to-SQL evaluation
- **BenchPress**: Human-in-the-loop curation; humans edit LLM drafts for accuracy and domain fit

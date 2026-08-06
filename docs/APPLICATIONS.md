# Applications — The Labeling Workbench and Its Constellation

**How the BLUEJAYS corpus is labeled, validated, and served.** The centerpiece is the **SQL Annotator Workbench** (`apps/ingest`) — the app built so a human annotator can open any of the 16 environments, edit a gold episode's `question`, `sql`, `evidence`, and `difficulty`, and have the save flow write straight back into the corpus's canonical source-of-truth layer. Around it sit four supporting applications. Every claim below is traceable to a file in this repository.

---

## 1. The Constellation

| App | Stack | Purpose | Entry |
|-----|-------|---------|-------|
| **`apps/ingest`** | Next.js 16 (App Router) | **The labeling workbench**: annotation UI, RBAC, validation, schema tooling, customer delivery API | port 3007 (`npm run dev:test`), 3000 (`dev`) |
| `apps/annotator` | Next.js | The workbench's lighter predecessor — same credential model, subset of views; Vercel root-dir deployable | port 3001 |
| `apps/web` | Next.js | Public-facing corpus documentation site (deployed to Vercel) | — |
| `apps/backend_test` | FastAPI | Query/benchmark test API: `/query`, `/benchmark`, `/bird/export`, `/bird/validate`, `/health/db/{n}` | — |
| `apps/sources_api` | FastAPI | Read-only sources/queries API | — |

---

## 2. The Labeling Workbench (`apps/ingest`)

### 2.1 The labeling loop

The workbench home (`app/page.tsx`) states its own contract: *"Select a database, pick a query, and edit question, SQL, evidence, and difficulty. Save writes to queries.json."* The loop, component by component:

```text
  source/db-N/…/queries.json ──▶ scripts/generate-sources-manifest.js ──▶ lib/sources-manifest.json
                                                                                  │
        GET /api/sources  ◀───────────────────────────────────────────────────────┘
        GET /api/queries?source=db-N
                │
                ▼
  AnnotatorWorkbench.tsx        (components/AnnotatorWorkbench.tsx)
    · source picker  · query list  · field editor (question / sql / evidence / difficulty)
    · skips the manifest's _field_definitions sentinel record
                │  save
                ▼
  POST /api/queries · POST /api/queries/sync    (app/api/queries/sync/route.ts)
    · annotator + staff only — customers get 403 ("customers cannot edit queries")
    · md ↔ json round-trip via lib/queries-convert (parseQueriesMd / formatQueriesMd)
    · writes source/<db-N>/app/QUERIES/queries.{json,md}   ← the Iron Triangle layer
                │
                ▼
  db_check.py build  ──▶  client/db/db-N/  ──▶  bird_export/  (BIRD-format episodes)
```

The important design fact: **labels land in the canonical `source/` layer**, not a side store — so an annotator's save is upstream of every derived artifact (client mirror, BIRD exports, deliverable sites). The md↔json converter keeps `queries.md` (human-authored source of record) and `queries.json` (machine-extracted) in lockstep, the discipline the provenance record flagged when it broke (db-2's 12-query divergence, [provenance STORY.md §14.3](provenance/STORY.md)).

### 2.2 Identity and role model

Authentication (`lib/auth.ts`): JWT session cookie, HTML form POST to `/api/login`, three users — `staff`, `annotator`, `customer` (dev password `123123`, `USER_CREDENTIALS`).

Authorization (`lib/privileges.ts` + `data/privileges-config.json`): a privilege ladder **annotator < customer < staff < system_owner**, with per-role view allowlists editable live at `/admin/privileges` (system-owner only). Staff can switch working modes — **Annotator | Staff | Customer | System owner** — via `/api/set-mode`, letting one operator experience each role's exact surface.

Enforcement is server-side: `components/RoleGuard.tsx` (rendered from the root layout) reads the request path from the `x-pathname` header set by `middleware.ts` and redirects any view not in the active role's allowlist. Two defects in this chain were found and fixed by the first-ever CI execution of the e2e suite (PR #18): the middleware itself was missing — making every unauthenticated `/login` visit an infinite 307 loop — and the login form's labels were not programmatically associated with their inputs. Both fixes are part of the app's history and its test suite now locks them in.

### 2.3 Route map

**Pages** (all under `RoleGuard`):

| Route | View | Who |
|-------|------|-----|
| `/` | Annotator workbench + schema view | annotator, customer (read), staff |
| `/dashboard` | Dashboard + LiveSQLBench ingest form (staff) | all roles |
| `/suite` | Databases overview | customer, staff |
| `/customer` | Customer portal: task tables, CSV export links, interactive drill-down charts | customer, staff |
| `/staff` · `/staff/pipeline` | Task pipeline phases (`components/TaskPipeline.tsx`) | staff |
| `/admin/tasks` | Task board | annotator, customer, staff |
| `/admin/privileges` | Live privilege editor | system_owner |
| `/validate` | Database × role × view validation matrix with side panel | staff |
| `/login` | Credential form | public |

**API routes** (23; `app/api/**/route.ts`):

| Group | Routes | Notes |
|-------|--------|-------|
| Session | `login`, `logout`, `me`, `set-mode`, `set-role` | JWT cookie; mode switching |
| Corpus | `sources`, `queries`, `queries/sync`, `schema`, `schema/raw`, `schema/dbml` | manifest-backed reads; guarded writes; DBML via `lib/schema-to-dbml.ts` |
| Validation | `validate/query`, `validate/batch` | `lib/sql-validator.ts` + `lib/sql-executor.ts`; feeds `ValidationSidePanel` |
| Delivery | `export`, `v2/datasets`, `v2/datasets/delivery`, `v2/datasets/task`, `v2/datasets/tasks` | role-gated (`canExport`); see §2.4 |
| Ingest | `ingest/livesqlbench` | LiveSQLBench JSON → corpus namespace |
| Ops | `health`, `privileges`, `debug` | `health` added as the unauthenticated readiness probe |

### 2.4 The Scale-style delivery API

`lib/scale-types.ts` models the **Scale AI Data Engine** API shape (docs.genai.scale.com) and maps the corpus onto it explicitly: **1 Dataset = 1 db-N · 1 Delivery = 30 queries · 1 Task = 1 query.** The `v2/datasets*` routes serve the corpus in that industry-standard envelope — a customer integrating against a Scale-shaped client can consume BLUEJAYS deliveries without custom plumbing. Paired with the BIRD-format exports, the corpus speaks both the research dialect (BIRD/LiveSQLBench) and the commercial one (Scale-style deliveries).

### 2.5 Schema and validation tooling

- **Schema view**: `SchemaView`/`SchemaViewWrapper` render each environment's schema in-app; `schema/dbml` converts DDL to DBML for diagram tools.
- **ERD embeds**: `ChartDBEmbed`, `LiamEmbed`, `DbDiagramEmbed`, surfaced via `ToolsSection` (ROADMAP Epic 8).
- **Validation**: `/validate` runs per-query syntax/materialized-view/execution checks through `validate/query` and `validate/batch` (ROADMAP Epic 9), results in `ValidationSidePanel`.
- **Benchmark ingest**: `LiveSQLBenchIngestForm` posts external LiveSQLBench JSON into the corpus namespace (ROADMAP Epic 5).

### 2.6 Test pyramid

148 Jest unit tests, 14 integration tests (4 suites, run against a live dev server), and a 38-spec Playwright e2e suite covering the login flow, annotator flow (*"save triggers sync"*), customer portal, staff pipeline, mode switching, and role-based API access — wired into CI (`.github/workflows/ci.yml`, `scripts/test-app-running.sh`, health-probe readiness, port handoff between integration and e2e phases). Run locally: `npm run test:app`.

---

## 3. The Predecessor (`apps/annotator`)

The original labeling app, kept as the deployable lightweight variant: same three-credential model, pages `/`, `/dashboard`, `/staff`, `/suite`, `/customer`, `/login`, its own `middleware.ts` (the pattern the workbench later lost and regained), Vercel root-directory deployment with optional Neon/Supabase Postgres. It is the app the workbench grew out of; the provenance record's "built the documentation site in 30 minutes" era belongs to this lineage.

---

## 4. Supporting Services

- **`apps/web`** — the corpus documentation site (design system, per-database pages, deployed to Vercel; see `apps/web/WEBSITE_ARCHITECTURE.md`).
- **`apps/backend_test`** — FastAPI harness exposing `/query`, `/benchmark`, `/bird/export`, `/bird/validate`, and per-database health checks; the API face of the validation suite.
- **`apps/sources_api`** — minimal read-only FastAPI for sources and queries.

---

**Last Updated:** 2026-08-06 · Companion docs: [MDP_TUPLE_ARCHITECTURE.md](MDP_TUPLE_ARCHITECTURE.md) · [TECHNICAL_EXECUTION.md](TECHNICAL_EXECUTION.md) · [provenance/](provenance/README.md)

# ROADMAP — Data Labeling, Annotation & Export Platform

Product roadmap for a **data labeling, annotation, evaluation, and customer-facing export platform** built on 16 production databases and text-to-SQL benchmark infrastructure.

---

## Product Pillars

| Pillar | Purpose |
|--------|---------|
| **Data Labeling** | Structured labeling of SQL queries, schema, and expected outputs |
| **Annotation** | Human-in-the-loop annotation via Label Studio and annotator apps |
| **Evaluation** | Validation, execution testing, BIRD benchmark, GDPval LangGraph |
| **Customer-Facing Export** | Web-deployable deliverables, BIRD export, client/db sync for customers |

---

## 1. Database Portfolio (16 Production Databases)

| ID | Domain | Description |
|----|--------|-------------|
| db-1 | Chat Messaging Platform | Aircraft tracking, multi-window time-series analytics |
| db-2 | Filling Station Retail | POS sales, customer segmentation |
| db-3 | Hierarchical Orders | E-commerce order hierarchy |
| db-4 | SharedAI Models | AI model registry and metadata |
| db-5 | POS Retail | Point-of-sale retail analytics |
| db-6 | Weather Consulting Insurance | Weather, NEXRAD, insurance, PostGIS |
| db-7 | Maritime Shipping Intelligence | AIS vessel tracks, shipping lanes |
| db-8 | Job Market Intelligence | Job postings, labor market analytics |
| db-9 | Shipping Intelligence | Postal, ZCTA, shipping analytics |
| db-10 | Marketing Intelligence | Marketing campaign analytics |
| db-11 | Parking Intelligence | Parking operations, occupancy |
| db-12 | Credit Card & Rewards Optimization | Card programs, rewards |
| db-13 | AI Benchmark Marketing Database | Marketing text-to-SQL benchmark |
| db-14 | Cloud Instance Cost Database | Cloud pricing, instance costs |
| db-15 | Electricity Cost & Solar Rebate | Utility rates, solar incentives |
| db-16 | Flood Risk Assessment | Flood risk, property exposure |

Each database: 30+ complex SQL queries, PostgreSQL schema, sample/large data, web-deployable documentation.

---

## 2. Deliverable Pipeline

### 2.1 Format Command
- **Input**: `DELIVERABLE.md` or `_doc_config.yaml`, `queries.md`
- **Output**: `deliverable/db-N.md`, `deliverable.openapi.yaml`, web-deployable `dbN-*/`
- **Features**: OpenAPI 3.0.3 spec, canonical query block format, embedded documentation

### 2.2 Populate App (Iron Triangle)
- **Input**: `data/`, `deliverable/`, `queries/` or `QUERIES/`
- **Output**: `app/DATABASE/`, `app/DOCUMENTATION/`, `app/QUERIES/`
- **Features**: Schema selection (PostgreSQL), data_large (≥1GB), doc copy

### 2.3 Resync Client
- **Input**: `source/db-N/app/`
- **Output**: `client/db/db-N/` (DATABASE, DOCUMENTATION, QUERIES, vercel.json)
- **Features**: Dry-run, app-first sync, legacy fallback

---

## 3. Validation & QA

### 3.1 Validation Suite (Phase 0–5)
- **Phase 0**: Extract `queries.md` → `queries.json`
- **Phase 1**: Fix verification (labels, formatting)
- **Phase 2**: Syntax validation (PostgreSQL EXPLAIN)
- **Phase 3**: Execution testing
- **Phase 4**: Comprehensive evaluation (CTE, complexity)
- **Phase 5**: Final report generation

### 3.2 QA Suite
- Format → Populate → Resync → Audit → Compliance → Integrity
- Client/db structure verification (DATABASE/, DOCUMENTATION/, QUERIES/)
- Compliance checklist (30 queries, schema, docs)
- Integrity checks (CRC-32, CRC-64, SHA-256)

### 3.3 BIRD Benchmark
- Export to BIRD-bench format (`bird_export/db-N_bird.json`)
- Workbench assertions (ACID/BASE)
- tb3_workbench integration

### 3.4 GDPval LangGraph
- GDPval-style harness: prompt + reference SQL + deliverable
- LangGraph validation flow

---

## 4. Query Management

### 4.1 Canonical Format
- **queries_md_formatter.py**: Single source of truth for `queries.md`
- **Field order**: Description, Use Case, Business Value, Purpose, Complexity, Expected Output, SQL
- **docs/QUERIES_MD_FORMAT.md**: Format spec

### 4.2 Template Format
- **template/queries.md**, **template/queries.json**: BIRD-style format
- **convert_queries_to_template_format.py**: Legacy → template
- **rewrite_queries_md_to_template.py**: Bit-for-bit template match
- **template_config.yaml**: difficulty_rules, query_categories, sql_key

### 4.3 Extraction & Round-Trip
- **extract_queries_to_json.py**: queries.md → queries.json (all canonical fields)
- **queries_md_json_translator.py**: md↔json API response, round-trip validation

---

## 5. Source Cleanup & Analysis

### 5.1 Redundancy Analysis
- **analyze_source_redundancy.py**: Identifies files not needed for app/ generation
- Reports required vs redundant per db-N

### 5.2 Archive Redundant
- **archive_source_redundant.py**: Moves research/, results/, docs/, metadata/, scripts/, etc. to `archive/source-redundant/`
- Dry-run support

---

## 6. CI/CD & Infrastructure

### 6.1 Jenkins Pipeline
- Checkout, env validation, remove non-Postgres vendors (dry-run)
- Build (db + tb3_workbench + langgraph)
- Docker Compose (multi-db)
- Parallel validate (db-1..db-16)
- BIRD Export, BIRD Workbench, GDPval LangGraph
- MVC Backend Test
- Artifact archive (traces, logs, compliance_report.json)

### 6.2 Docker
- **docker-compose.multi-db.yml**: Per-db PostgreSQL instances
- **docker-compose.test-postgresql.yml**: Test instance
- Per-db Dockerfiles (db-6..db-15)
- Notebook execution in containers

### 6.3 Environment
- **env_validator.py**: Validates PG_*, DB_PORTS_START, ANTHROPIC_API_KEY
- **remove_non_postgres_vendors.py**: Strips Databricks/BigQuery references

---

## 7. Platform: Labeling, Annotation, Evaluation & Export

### 7.1 Data Labeling
- **Canonical format** (queries_md_formatter, QUERIES_MD_FORMAT): Structured labels for Description, Use Case, Business Value, Purpose, Complexity, Expected Output
- **Template format** (BIRD-style): difficulty, query_category, schema_context, tables_used
- **Label Studio config**: template/label_studio_config.xml for annotation projects

### 7.2 Annotation
- **Label Studio**: export_queries_to_label_studio.py → label_studio_tasks.json
- **Annotator app** (port 8766): queries.json + Label Studio integration
- **Multi-session, gates**: Session management and annotation workflow

### 7.3 Evaluation
- **Validation suite** (Phase 0–5): Extract, verify, syntax, execution, report
- **BIRD Workbench**: ACID/BASE assertions, tb3_workbench
- **GDPval LangGraph**: Prompt + reference SQL + deliverable validation
- **MVC Backend Test**: /query, /benchmark endpoints for automated evaluation

### 7.4 Customer-Facing Export
- **Web-deployable deliverables**: HTML, JSON, vercel.json per db-N
- **BIRD export**: bird_export/db-N_bird.json for benchmark consumers
- **client/db sync**: DATABASE/, DOCUMENTATION/, QUERIES/ for customer deployment
- **Backend Test API**: /bird/export, /bird/validate for programmatic export

---

## 8. Documentation & Standards

### 8.1 Cursor Commands
- `/format`: Format deliverables
- `/validate`: Run validation suite
- `/QA`: Full QA suite (format, resync, audit, compliance, integrity)

### 8.2 Rules
- **database-creation-workflow.mdc**: Directory structure, validation phases, deliverable format
- **database-compatibility.mdc**: Query requirements, PostgreSQL compatibility
- **query-validation-suite.mdc**: Phase 0–5, timestamp format
- **deliverable-formatting.mdc**: OpenAPI, web-deployable structure
- **format-golden-solution.mdc**: db-6 reference implementation
- **database-er-diagrams.mdc**: Mermaid.js ER diagrams
- **qa-workflow-cursor.mdc**: End-to-end QA workflow

---

## 9. Data & Schema

### 9.1 Schema Standards
- PostgreSQL-only (schema.sql, schema_postgresql.sql)
- PostGIS for spatial (db-6, db-9, db-16)
- Production-grade comments (no "Created:" dates)

### 9.2 Data Volumes
- **data.sql**: Sample/seed data
- **data_large.sql**: ≥1GB for benchmarks (when available)

---

## 10. Future Considerations

- **Platform**: Unified web UI for labeling, annotation, evaluation, and export
- **Customer portal**: Self-service export, API keys, usage analytics
- Extend to db-17+ with same patterns
- Optional Snowflake/BigQuery support (currently PostgreSQL-only)
- Label Studio annotation workflow refinement
- Hardened PostgreSQL Docker images per db-N

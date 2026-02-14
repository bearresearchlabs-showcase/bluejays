# JIRA — Epics, Tasks, Subtasks & User Stories

Epics, tasks, subtasks, and user stories for the **data labeling, annotation, evaluation, and customer-facing export platform**.

---

## Product Vision

Build a platform that supports:
- **Data Labeling**: Structured labels for SQL queries, schema, and expected outputs
- **Annotation**: Human-in-the-loop review via Label Studio and annotator apps
- **Evaluation**: Validation, execution testing, BIRD benchmark, GDPval LangGraph
- **Customer-Facing Export**: Web deliverables, BIRD export, client/db sync for customers

---

## Epic 1: Database Portfolio & Deliverables

### Task 1.1: Create 16 Production Databases
**Subtasks:**
- [ ] db-1: Chat Messaging Platform
- [ ] db-2: Filling Station Retail
- [ ] db-3: Hierarchical Orders
- [ ] db-4: SharedAI Models
- [ ] db-5: POS Retail
- [ ] db-6: Weather Consulting Insurance (PostGIS)
- [ ] db-7: Maritime Shipping Intelligence
- [ ] db-8: Job Market Intelligence
- [ ] db-9: Shipping Intelligence
- [ ] db-10: Marketing Intelligence
- [ ] db-11: Parking Intelligence
- [ ] db-12: Credit Card & Rewards Optimization
- [ ] db-13: AI Benchmark Marketing Database
- [ ] db-14: Cloud Instance Cost Database
- [ ] db-15: Electricity Cost & Solar Rebate
- [ ] db-16: Flood Risk Assessment

**User Stories:**
- As a data engineer, I need each database to have 30+ complex SQL queries so we can benchmark text-to-SQL systems.
- As a client, I need PostgreSQL-only schema and data so I can run queries without vendor lock-in.
- As a developer, I need web-deployable documentation (HTML, JSON, Vercel config) for each database.

---

## Epic 2: Format & Deliverable Pipeline

### Task 2.1: Format Command
**Subtasks:**
- [ ] Parse DELIVERABLE.md or _doc_config.yaml
- [ ] Parse queries.md with canonical field extraction
- [ ] Generate deliverable/db-N.md
- [ ] Generate deliverable.openapi.yaml (OpenAPI 3.0.3)
- [ ] Generate web-deployable dbN-*/ folder (HTML, JSON, vercel.json, data/)

**User Stories:**
- As a developer, I want to run `/format db-1` and get a complete deliverable package.
- As an API consumer, I want an OpenAPI spec for all queries and schema.

### Task 2.2: Populate App (Iron Triangle)
**Subtasks:**
- [ ] Populate app/DATABASE/ from data/ (schema.sql, data.sql, data_large.sql)
- [ ] Populate app/DOCUMENTATION/ from deliverable/
- [ ] Populate app/QUERIES/ from queries/ or QUERIES/
- [ ] Enforce PostgreSQL-only schema selection
- [ ] Require data_large.sql ≥1GB when available

**User Stories:**
- As a QA engineer, I need app/ to contain exactly DATABASE/, DOCUMENTATION/, QUERIES/ for downstream sync.

### Task 2.3: Resync Client
**Subtasks:**
- [ ] Sync source/db-N/app/ → client/db/db-N/
- [ ] Support dry-run mode
- [ ] Support app-first vs legacy fallback
- [ ] Copy vercel.json for deployment

**User Stories:**
- As a deployer, I want client/db/ to mirror source app/ output for static hosting.

---

## Epic 3: Validation & QA

### Task 3.1: Validation Suite (Phase 0–5)
**Subtasks:**
- [ ] Phase 0: extract_queries_to_json.py (queries.md → queries.json)
- [ ] Phase 1: verify_fixes.py (labels, formatting)
- [ ] Phase 2: comprehensive_validator.py (PostgreSQL EXPLAIN)
- [ ] Phase 3: execution_tester.py
- [ ] Phase 4: Comprehensive evaluation (CTE, complexity)
- [ ] Phase 5: generate_final_report.py

**User Stories:**
- As a developer, I want `/validate db-1` to run all phases and report Pass/Fail.
- As a CI pipeline, I need JSON reports (fix_verification.json, comprehensive_validation_report.json, etc.) with Pass: 1|0.

### Task 3.2: QA Suite
**Subtasks:**
- [ ] Format → Populate → Resync
- [ ] verify_unified_structure.py (client/db audit)
- [ ] Compliance check (30 queries, schema, docs)
- [ ] integrity_checks.py (CRC-32, CRC-64, SHA-256)
- [ ] Update metadata/integrity.json

**User Stories:**
- As a QA engineer, I want `/QA -a` to run the full pipeline and report compliance.

### Task 3.3: BIRD Benchmark
**Subtasks:**
- [ ] bird_export.py: Export to BIRD-bench format
- [ ] bird-workbench: ACID/BASE assertions via tb3_workbench
- [ ] bird_critic_format.py, bird_critic_runner.py

**User Stories:**
- As a benchmark researcher, I need BIRD-formatted exports for text-to-SQL evaluation.

### Task 3.4: GDPval LangGraph
**Subtasks:**
- [ ] GDPval harness: prompt + reference SQL + deliverable
- [ ] LangGraph validation flow

**User Stories:**
- As an AI engineer, I need to validate text-to-SQL outputs against reference queries.

---

## Epic 4: Query Management

### Task 4.1: Canonical queries.md Format
**Subtasks:**
- [ ] queries_md_formatter.py: Single source of truth
- [ ] docs/QUERIES_MD_FORMAT.md: Format spec
- [ ] Field order: Description, Use Case, Business Value, Purpose, Complexity, Expected Output, SQL
- [ ] format.py: Use format_query_block for embedded blocks

**User Stories:**
- As a developer, I want all generated queries.md to use the same canonical format.

### Task 4.2: Template Format (BIRD-style)
**Subtasks:**
- [ ] template/queries.md, template/queries.json
- [ ] convert_queries_to_template_format.py
- [ ] rewrite_queries_md_to_template.py
- [ ] template_config.yaml, qa_anchor.yaml

**User Stories:**
- As a benchmark maintainer, I need template format for BIRD compatibility.

### Task 4.3: Extraction & Round-Trip
**Subtasks:**
- [ ] extract_queries_to_json.py: All canonical fields
- [ ] queries_md_json_translator.py: md↔json, round-trip validation

**User Stories:**
- As a script author, I need queries.json to stay in sync with queries.md.

---

## Epic 5: Source Cleanup & Analysis

### Task 5.1: Redundancy Analysis
**Subtasks:**
- [ ] analyze_source_redundancy.py
- [ ] Report required vs redundant per db-N

**User Stories:**
- As a maintainer, I want to know which files are needed for app/ generation.

### Task 5.2: Archive Redundant
**Subtasks:**
- [ ] archive_source_redundant.py
- [ ] Archive research/, results/, docs/, metadata/, scripts/, etc.
- [ ] archive/source-redundant/README.md

**User Stories:**
- As a maintainer, I want to archive files not needed for app/ without losing them.

---

## Epic 6: CI/CD & Infrastructure

### Task 6.1: Jenkins Pipeline
**Subtasks:**
- [ ] Checkout, env validation
- [ ] remove_non_postgres_vendors.py (dry-run)
- [ ] Build db, tb3_workbench, langgraph
- [ ] Docker Compose multi-db
- [ ] Parallel validate db-1..db-16
- [ ] BIRD Export, BIRD Workbench, GDPval LangGraph
- [ ] MVC Backend Test
- [ ] Artifact archive

**User Stories:**
- As a DevOps engineer, I want Jenkins to validate all databases on every commit.

### Task 6.2: Docker
**Subtasks:**
- [ ] docker-compose.multi-db.yml
- [ ] docker-compose.test-postgresql.yml
- [ ] Per-db Dockerfiles (db-6..db-15)
- [ ] Notebook execution in containers

**User Stories:**
- As a developer, I want to run each database in an isolated Docker container.

### Task 6.3: Environment Validation
**Subtasks:**
- [ ] env_validator.py (PG_*, DB_PORTS_START, ANTHROPIC_API_KEY)
- [ ] remove_non_postgres_vendors.py

**User Stories:**
- As a developer, I want clear errors when required env vars are missing.

---

## Epic 7: Platform — Labeling, Annotation, Evaluation & Export

### Task 7.1: Data Labeling
**Subtasks:**
- [ ] Canonical format (queries_md_formatter, QUERIES_MD_FORMAT)
- [ ] Template format (BIRD-style: difficulty, query_category, schema_context)
- [ ] Label Studio config (label_studio_config.xml)

**User Stories:**
- As a labeler, I need structured fields (Description, Use Case, Business Value, etc.) for each query.
- As a platform admin, I want consistent labeling schema across all 16 databases.

### Task 7.2: Annotation
**Subtasks:**
- [ ] export_queries_to_label_studio.py → label_studio_tasks.json
- [ ] Annotator app (port 8766)
- [ ] Multi-session, gates, template config

**User Stories:**
- As an annotator, I want to review and correct queries in Label Studio.
- As an annotator, I want a simple UI (annotator app) to annotate queries.

### Task 7.3: Evaluation
**Subtasks:**
- [ ] Validation suite (Phase 0–5)
- [ ] BIRD Workbench (ACID/BASE)
- [ ] GDPval LangGraph
- [ ] MVC Backend Test (/query, /benchmark)

**User Stories:**
- As an evaluator, I need automated validation and execution testing.
- As an AI engineer, I need to validate text-to-SQL outputs against reference queries.

### Task 7.4: Customer-Facing Export
**Subtasks:**
- [ ] Web-deployable deliverables (HTML, JSON, vercel.json)
- [ ] BIRD export (bird_export/db-N_bird.json)
- [ ] client/db sync (DATABASE/, DOCUMENTATION/, QUERIES/)
- [ ] Backend API (/bird/export, /bird/validate)

**User Stories:**
- As a customer, I want to export databases in web-deployable format.
- As a customer, I want BIRD-formatted exports for benchmark integration.
- As a customer, I want programmatic access via API for export.

---

## Epic 8: Documentation & Standards

### Task 8.1: Cursor Commands
**Subtasks:**
- [ ] /format command
- [ ] /validate command
- [ ] /QA command

**User Stories:**
- As a Cursor user, I want slash commands for format, validate, and QA.

### Task 8.2: Rules & Workflows
**Subtasks:**
- [ ] database-creation-workflow.mdc
- [ ] database-compatibility.mdc
- [ ] query-validation-suite.mdc
- [ ] deliverable-formatting.mdc
- [ ] format-golden-solution.mdc
- [ ] database-er-diagrams.mdc
- [ ] qa-workflow-cursor.mdc

**User Stories:**
- As an AI agent, I need rules to generate consistent deliverables.

---

## Epic 9: Data & Schema Standards

### Task 9.1: Schema Standards
**Subtasks:**
- [ ] PostgreSQL-only schema
- [ ] PostGIS for spatial databases
- [ ] Production-grade comments (no "Created:" dates)

**User Stories:**
- As a client, I need schema that runs on standard PostgreSQL.

### Task 9.2: Data Volumes
**Subtasks:**
- [ ] data.sql: Sample/seed
- [ ] data_large.sql: ≥1GB for benchmarks

**User Stories:**
- As a benchmark runner, I need large datasets for realistic performance tests.

---

## Epic 10: Unified Web Platform (Future)

### Task 10.1: Unified Web UI
**Subtasks:**
- [ ] Single web app for labeling, annotation, evaluation, export
- [ ] Customer portal: self-service export, API keys
- [ ] Usage analytics

**User Stories:**
- As a user, I want one website to label, annotate, evaluate, and export.
- As a customer, I want self-service export without contacting support.

---

## Summary

| Epic | Tasks | Status |
|------|-------|--------|
| 1. Database Portfolio | 16 databases | Done |
| 2. Format & Deliverable Pipeline | Format, Populate, Resync | Done |
| 3. Validation & QA | Validation, QA Suite, BIRD, GDPval | Done |
| 4. Query Management | Canonical, Template, Extraction | Done |
| 5. Source Cleanup | Analysis, Archive | Done |
| 6. CI/CD & Infrastructure | Jenkins, Docker, Env | Done |
| 7. Platform (Labeling, Annotation, Evaluation, Export) | Labeling, Annotation, Evaluation, Customer Export | Done |
| 8. Documentation & Standards | Commands, Rules | Done |
| 9. Data & Schema Standards | Schema, Data volumes | Done |
| 10. Unified Web Platform | Web UI, Customer portal | Future |

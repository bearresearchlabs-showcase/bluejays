# Cloud Architecture and Scaling

This document describes the scaling path from Vercel edge and small databases to dedicated PostgreSQL infrastructure, following Well-Architected principles.

## Overview

The SQL annotation workbench and database suite support multiple deployment modes:

- **Vercel (default)**: Edge functions, serverless, file-based storage
- **Self-hosted**: Dedicated PostgreSQL, connection pooling, read replicas
- **Hybrid**: Vercel frontend + external PostgreSQL

## Well-Architected Framework

### Operational Excellence

- **Infrastructure as Code**: Docker Compose for PostgreSQL (db-1..db-16), hardened images
- **Automation**: `scripts/docker_postgres_qa.sh` for schema load, integrity checks
- **Monitoring**: Transaction integrity checks (EXPLAIN, CHECK constraints) post-load
- **CI/CD**: Validation suite, BIRD workbench ACID/BASE tests

### Security

- **PostgreSQL**: SCRAM-SHA-256, `no-new-privileges` in containers
- **Secrets**: Environment variables for `PG_HOST`, `PG_USER`, `PG_PASSWORD`
- **Network**: Port mapping 5436–5451 per database; restrict exposure in production

### Reliability

- **Health checks**: `pg_isready` in Docker healthcheck
- **Redundancy**: Queries designed for independent execution across PostgreSQL
- **Failover**: Connection string supports multiple hosts (future)

### Performance

- **Connection pooling**: Use PgBouncer or similar when scaling beyond single connections
- **Read replicas**: Route read-only queries to replicas; writes to primary
- **Partitioning**: Schema supports partitioning for large tables (see database rules)

### Cost

- **Vercel**: Free tier for edge; upgrade for persistent connections
- **Self-hosted PostgreSQL**: Fixed cost; scale vertically then horizontally
- **Docker Hub**: Optional image push for `db-postgres-db-N`; reduce build time in CI

## Scaling Path: Vercel → Dedicated DB

### Phase 1: Vercel + File-Based (Current)

- Queries and schema in `source/db-N/`, `client/db/`
- No persistent database required for annotation UI
- Export to CSV/JSON; validation against Docker PostgreSQL locally

### Phase 2: Vercel + External PostgreSQL

1. Set `PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE` (or per-db `PG_PORT_DB1` etc.)
2. Validation scripts and execution tester connect to external DB
3. Connection limits: Vercel serverless has short-lived connections; use connection pooling if many concurrent requests

### Phase 3: Self-Hosted Full Stack

1. **Application**: Deploy ingest app to VPS, ECS, or Kubernetes
2. **PostgreSQL**: Dedicated instance(s); consider managed (RDS, Cloud SQL)
3. **Connection pooling**: PgBouncer or RDS Proxy between app and DB
4. **Read replicas**: For read-heavy workloads (e.g., customer portal, export)

### Phase 4: Multi-Tenant / Schema-per-Tenant

- **Schema-per-tenant**: Each customer gets `db1`, `db2`, … in separate schemas or databases
- **Connection config**: `PG_DATABASE` per tenant or connection string with schema
- **Isolation**: Separate credentials or row-level security (RLS) for tenant isolation

## Environment-Based Config

| Variable | Vercel | Self-Hosted | Notes |
|----------|--------|-------------|-------|
| `PG_HOST` | External DB host | `localhost` or internal | |
| `PG_PORT` | 5432 or custom | 5432, 5436–5451 (Docker) | |
| `PG_PORT_DB{N}` | Per-db port | Optional override | |
| `PG_USER` | DB user | `postgres` (dev) | |
| `PG_PASSWORD` | Secret | Env or secret manager | |
| `PG_DATABASE` | Default DB | `db1` etc. | |
| `DB_PORTS_START` | N/A | 5436 | For Docker QA |
| `DOCKER_HUB_USER` | N/A | Optional | For image pull |

## Connection Pooling

When scaling beyond a few connections:

```text
App → PgBouncer (transaction or session mode) → PostgreSQL
```

- **Transaction mode**: Short-lived; good for serverless
- **Session mode**: Long-lived; good for persistent app servers
- **Pool size**: Match `max_connections` on PostgreSQL

## Read Replicas

For read-heavy workloads (customer portal, exports):

- Primary: Writes (annotation saves, schema updates)
- Replica: Reads (query execution, export, validation)
- Use `?prefer-replica` or separate connection string in app

## References

- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [Vercel Serverless Functions](https://vercel.com/docs/functions)
- [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/)
- `scripts/docker_postgres_qa.sh` — Docker QA and integrity checks
- `.cursor/rules/qa-workflow-cursor.mdc` — QA workflow

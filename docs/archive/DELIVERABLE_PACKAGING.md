# Deliverable Packaging Guide

## Overview

The `/format` command packages database deliverables into `/deliverable` folders with a coherent structure containing only 2 essential components:

1. **DELIVERABLE.md** - Complete documentation in markdown (single comprehensive file)
2. **Database** - All database components (queries/, data/ folders)

## Command Usage

The `/format` command accepts the same arguments as `/validate`:

```bash
# Format single database
/format @db/db-1/

# Format range of databases
/format @db/db-1/ @db/db-5/

# Format all databases
/format -a

# Format by database number
/format db-1

# Format range by database numbers
/format db-1 db-5
```

## Deliverable Structure

```
db-{N}/deliverable/
├── README.md                   # Quick start guide
├── DELIVERABLE.md              # Complete documentation (single markdown file)
├── deliverable.openapi.yaml    # OpenAPI specification (optional, for API tools)
├── queries/                    # Database component: SQL queries
│   ├── queries.md              # SQL queries (30+ queries)
│   └── queries.json            # Query metadata (JSON)
└── data/                       # Database component: Schema and data
    ├── schema.sql             # Database schema
    ├── data.sql               # Sample data (if applicable)
    └── *.sql                  # Additional SQL files
```

## Two Essential Components

### 1. DELIVERABLE.md (Single Markdown File)

The `DELIVERABLE.md` file contains **everything** needed to understand the database:

- **Database Overview**: Description, features, supported platforms
- **Complete Schema Documentation**:
  - All tables with detailed column definitions
  - All indexes and constraints
  - Table relationships
  - **ER Diagrams**: Mermaid.js diagrams showing all relationships
- **SQL Queries Documentation**: Reference to queries with descriptions
- **Usage Instructions**: For data scientists and database administrators
- **Platform Compatibility**: PostgreSQL notes

### 2. Database Components

The database components are organized in folders:

- **queries/**:
  - `queries.md` - All 30+ SQL queries with descriptions and code
  - `queries.json` - Query metadata for programmatic access
- **data/**:
  - `schema.sql` - Complete database schema
  - `data.sql` - Sample data (if applicable)
  - Additional SQL files as needed

## ER Diagrams

All deliverables include Mermaid.js ER diagrams showing:

- All tables with key columns
- Primary keys (PK), Foreign keys (FK), Unique keys (UK)
- Spatial columns (SPATIAL marker for spatial databases)
- Relationship cardinality (one-to-many, many-to-many, etc.)
- Self-referential relationships

## OpenAPI Specification

The `deliverable.openapi.yaml` file provides:

- Machine-readable schema definitions
- Query metadata in structured format
- Integration with Swagger UI, Postman, code generators
- API documentation generation

## Packaging Process

When you run `/format`, the command:

1. **Reads** `db-{N}/DELIVERABLE.md` (source documentation)
2. **Creates** `db-{N}/deliverable/` folder
3. **Copies** DELIVERABLE.md to deliverable folder (single markdown file)
4. **Copies** queries/ folder (database component)
5. **Copies** data/ folder (database component)
6. **Generates** OpenAPI specification
7. **Generates** README.md for quick start

## Coherent Document Structure

The deliverable package is designed to be:

- **Self-contained**: Everything needed is in the deliverable folder
- **Coherent**: Single markdown file with all documentation
- **Complete**: Database components organized logically
- **Ready to use**: Can be distributed as-is

## Examples

### db-1 (Chat/Messaging System)

```
db-1/deliverable/
├── DELIVERABLE.md              # 636 lines - Complete documentation
├── queries/
│   ├── queries.md              # 30 SQL queries
│   └── queries.json            # Query metadata
└── deliverable.openapi.yaml    # OpenAPI spec
```

### db-6 (Weather Data Pipeline)

```
db-6/deliverable/
├── DELIVERABLE.md              # 769 lines - Complete documentation with spatial info
├── queries/
│   ├── queries.md              # 30 SQL queries
│   └── queries.json            # Query metadata
├── data/
│   ├── schema.sql             # Main schema
│   ├── data.sql               # Sample data
│   ├── insurance_schema.sql   # Additional schemas
│   ├── nexrad_satellite_schema.sql
│   └── schema_extensions.sql
└── deliverable.openapi.yaml    # OpenAPI spec with spatial operations
```

## Integration with Validate

The `/format` and `/validate` commands work together:

1. **Run `/validate`**: Validate queries and schema
2. **Run `/format`**: Package validated deliverables
3. **Distribute**: Deliverable folder is ready for distribution

## Best Practices

1. **Run Format After Changes**: Re-run `/format` after updating DELIVERABLE.md
2. **Keep Coherent**: Ensure DELIVERABLE.md contains all documentation
3. **Organize Database Components**: Keep queries and data in separate folders
4. **Include ER Diagrams**: Always include Mermaid.js ER diagrams
5. **Test Deliverable**: Verify deliverable folder is complete before distribution

---

**Last Updated**: 2026-02-03
**Version**: 1.0

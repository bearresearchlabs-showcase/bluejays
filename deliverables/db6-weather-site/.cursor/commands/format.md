---
name: format
description: Format database deliverables using OpenAPI/Swagger specification format
usage: |
  /format @db/db-1/              # Format single database
  /format @db/db-1/ @db/db-5/    # Format range of databases
  /format -a                     # Format all databases (db-1 through db-15)
  /format db-1                    # Format by database number
  /format db-1 db-5              # Format range by database numbers
---

# Format Command

Format database deliverables using OpenAPI/Swagger specification format and package into `/deliverable` folder.

## Usage

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

## What It Does

The format command:

1. **Reads** database documentation and schema from `db-{N}/`
2. **Generates** OpenAPI 3.0.3 YAML specification
3. **Packages** deliverable into `db-{N}/deliverable/` folder with:
   - **DELIVERABLE.md**: Complete documentation (single markdown file)
   - **Database files**: Schema, queries, data (database components)

## Output Structure

The `/format` command creates a `deliverable/` folder containing:

```
db-{N}/deliverable/
├── README.md                   # Quick start guide
├── DELIVERABLE.md              # Complete documentation (single markdown file)
├── deliverable.openapi.yaml    # OpenAPI specification (optional, for API tools)
├── queries/                    # Database component: SQL queries
│   ├── queries.md              # SQL queries (30+ queries)
│   └── queries.json           # Query metadata (JSON)
└── data/                       # Database component: Schema and data
    ├── schema.sql             # Database schema
    ├── data.sql               # Sample data (if applicable)
    └── *.sql                  # Additional SQL files
```

**Key Principle**: **ONLY ONE FILE**:
1. **DELIVERABLE.md** - Complete comprehensive markdown file containing:
   - Complete database documentation (schema, tables, ER diagrams)
   - **ALL 30 SQL queries embedded inline** with full business context
   - Table of contents with natural language descriptions
   - Business context explaining queries come from $1M+ ARR companies
   - What each query does and what business case it accomplishes

The deliverable is ONE comprehensive markdown file that explains every query, every aspect of the database, with a table of contents using natural language to specify what each query does and what business case it has accomplished. These databases were sourced from businesses with at least $1M ARR per year.

## Examples

```bash

# Format db-1

/format @db/db-1/

# Format db-1 through db-6

/format @db/db-1/ @db/db-6/

# Format all databases

/format -a

# Format by number

/format db-1
```

## Exit Codes

- `0`: Formatting completed successfully
- `1`: One or more formatting operations failed
- `2`: Partial formatting (some databases skipped)

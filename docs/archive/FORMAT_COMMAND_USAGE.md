# Format Command Usage

## Overview

The `/format` command formats database deliverables using OpenAPI/Swagger specification format, converting human-readable `DELIVERABLE.md` files into machine-readable OpenAPI 3.0.3 YAML specifications.

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

1. **Reads** `DELIVERABLE.md` file from database directory
2. **Extracts** database metadata, schema information, and query references
3. **Reads** `queries/queries.json` for query metadata (if available)
4. **Generates** OpenAPI 3.0.3 YAML specification
5. **Writes** output to `deliverable.openapi.yaml`

## Output

- **File**: `db-{N}/deliverable.openapi.yaml`
- **Format**: OpenAPI 3.0.3 YAML specification
- **Encoding**: UTF-8
- **Structure**: Complete OpenAPI spec with paths, schemas, and examples

## OpenAPI Specification Structure

The generated OpenAPI specifications include:

### Info Section
- Database name and type
- Description
- Version (1.0.0)
- Contact and license information

### Servers Section
- PostgreSQL server URL
 server URL
 server URL

### Tags Section
- `schema`: Database schema information
- `tables`: Table definitions
- `queries`: SQL query definitions
- `relationships`: Table relationships
- `spatial`: Spatial operations (for spatial databases)

### Paths Section
- `GET /schema`: Get schema overview
- `GET /tables`: List all tables
- `GET /tables/{tableName}`: Get table details
- `GET /queries`: List all queries
- `GET /queries/{queryNumber}`: Get query details
- `GET /spatial/operations`: List spatial operations (spatial databases only)

### Components Section
- **Schemas**: Data models (SchemaOverview, Table, Column, Query, etc.)
- **Examples**: Example data structures

## Examples

### Format Single Database

```bash
/format @db/db-1/
```

Generates: `db-1/deliverable.openapi.yaml`

### Format Multiple Databases

```bash
/format @db/db-1/ @db/db-6/
```

Generates:
- `db-1/deliverable.openapi.yaml`
- `db-6/deliverable.openapi.yaml`

### Format All Databases

```bash
/format -a
```

Generates OpenAPI specs for db-1 through db-15.

## Using Generated OpenAPI Specs

The generated OpenAPI specifications can be used with:

### Swagger UI
Generate interactive API documentation:

```bash
# Install Swagger UI
npm install -g swagger-ui-serve

# Serve OpenAPI spec
swagger-ui-serve db-1/deliverable.openapi.yaml
```

### Swagger Editor
Edit and validate specifications:
- Open `deliverable.openapi.yaml` in Swagger Editor
- Validate OpenAPI compliance
- Edit specifications

### Swagger Codegen
Generate client libraries and server stubs:

```bash
# Generate Python client
swagger-codegen generate -i db-1/deliverable.openapi.yaml -l python -o ./client

# Generate JavaScript client
swagger-codegen generate -i db-1/deliverable.openapi.yaml -l javascript -o ./client
```

### Postman
Import specifications for API testing:
1. Open Postman
2. Import → File
3. Select `deliverable.openapi.yaml`
4. Generate collection from OpenAPI spec

### OpenAPI Generator
Generate code in various languages:

```bash
# Generate TypeScript client
openapi-generator generate -i db-1/deliverable.openapi.yaml -g typescript-axios -o ./client
```

## Requirements

- Python 3.7+
- PyYAML library (for YAML generation)
- `DELIVERABLE.md` file in database directory
- `queries/queries.json` file (optional, for enhanced query metadata)

## Error Handling

The format command handles:

- **Missing Files**: Reports error if `DELIVERABLE.md` is missing
- **Invalid Content**: Reports parsing errors
- **YAML Generation**: Reports YAML generation errors
- **File Writing**: Reports file writing errors

## Integration with Validation

The format command can be run:

- **Before Validation**: Format deliverables before running validation suite
- **After Validation**: Format deliverables after validation completes
- **Standalone**: Run format independently of validation

## Best Practices

1. **Keep Specs Updated**: Re-run formatting after changes to `DELIVERABLE.md`
2. **Validate Output**: Validate generated OpenAPI specs using Swagger Editor
3. **Version Control**: Commit OpenAPI specs to version control
4. **Documentation**: Keep `DELIVERABLE.md` and OpenAPI spec in sync
5. **Examples**: Review examples in OpenAPI spec for accuracy

## Related Commands

- `/validate`: Run validation suite for database repositories
- See `.cursor/rules/deliverable-formatting.mdc` for detailed formatting rules

---

**Last Updated**: 2026-02-03
**Version**: 1.0

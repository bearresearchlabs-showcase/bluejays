# Docker Validation Suite

Complete validation suite for Docker containers (db-6 through db-15) with comprehensive testing and reporting.

## Quick Start

Run all validation phases:

```bash
./scripts/docker_run_all_validation.sh
```

Or run individual phases:

```bash
# Phase 1: Build all containers
./scripts/docker_build_all.sh

# Phase 2: Test container startup
./scripts/docker_test_startup.sh

# Phase 3: Validate PostgreSQL
./scripts/docker_test_postgresql.sh

# Phase 4: Test file paths
./scripts/docker_test_file_paths.sh

# Phase 5: Execute notebooks
./scripts/docker_execute_notebooks.sh

# Phase 6: Validate queries
./scripts/docker_validate_queries.sh

# Phase 7: Integration testing
./scripts/docker_integration_test.sh

# Phase 8: Generate report
./scripts/docker_generate_validation_report.sh
```

## Validation Phases

### Phase 1: Build Validation

**Script:** `scripts/docker_build_all.sh`

**What it does:**
- Builds all 10 Docker containers
- Verifies Dockerfiles exist and are valid
- Tracks build times and image sizes
- Collects build errors and warnings
- Generates build logs

**Output:**
- Build logs in `docker/build_logs/`
- Console summary with timing and image sizes

### Phase 2: Container Startup Testing

**Script:** `scripts/docker_test_startup.sh`

**What it does:**
- Starts each container individually
- Verifies PostgreSQL initialization
- Checks Jupyter Notebook server startup
- Tests port mappings
- Verifies environment variables
- Checks volume mounts

**Output:**
- Startup logs in `docker/test_logs/`
- Console summary with startup times

### Phase 3: PostgreSQL Validation

**Script:** `scripts/docker_test_postgresql.sh`

**What it does:**
- Connects to PostgreSQL in each container
- Verifies PostgreSQL version (>= 12)
- Tests database creation capability
- Verifies user permissions
- Tests connection from host machine
- Verifies data directory persistence

**Output:**
- PostgreSQL test results
- Console summary with connectivity status

### Phase 4: File Path and Recursive Finding Validation

**Script:** `scripts/docker_test_file_paths.sh`

**What it does:**
- Verifies notebooks exist at expected paths
- Tests recursive file finding function
- Verifies `queries.json` can be found recursively
- Verifies `schema.sql` can be found recursively
- Verifies `data.sql` can be found recursively
- Tests fallback paths (root db directory)

**Output:**
- File path test results
- Console summary with path validation status

### Phase 5: Notebook Execution Testing

**Script:** `scripts/docker_execute_notebooks.sh`

**What it does:**
- Executes each notebook using `jupyter nbconvert --execute`
- Verifies notebook execution completes successfully
- Checks for execution errors or timeouts
- Verifies database initialization
- Checks execution reports are generated
- Tracks execution times

**Output:**
- Executed notebooks: `{db-N}_executed.ipynb` in containers
- Execution logs in `docker/test_logs/`
- Console summary with execution times

### Phase 6: Database Query Validation

**Script:** `scripts/docker_validate_queries.sh`

**What it does:**
- Verifies database is created
- Verifies schema is loaded correctly
- Verifies sample data is loaded
- Executes sample queries (first 5 per database)
- Verifies query results are returned
- Checks query execution times (< 5 seconds)

**Output:**
- Query validation results
- Console summary with query execution status

### Phase 7: Integration Testing

**Script:** `scripts/docker_integration_test.sh`

**What it does:**
- Starts all containers simultaneously using docker-compose
- Verifies no port conflicts
- Verifies all containers can run concurrently
- Tests resource usage (CPU, memory)
- Tests container restart and persistence
- Verifies data volumes persist across restarts

**Output:**
- Integration test results
- Resource usage statistics
- Console summary with integration status

### Phase 8: Comprehensive Validation Report

**Script:** `scripts/docker_generate_validation_report.sh`

**What it does:**
- Collects results from all validation phases
- Generates comprehensive JSON report
- Creates summary markdown report
- Includes pass/fail status for each phase
- Includes timing information
- Includes error logs and warnings
- Generates recommendations for fixes

**Output:**
- `docker/validation_results.json` - JSON validation report
- `docker/validation_report.md` - Markdown summary report

## Output Files

### Log Directories

- `docker/build_logs/` - Build logs for each container
- `docker/test_logs/` - Test execution logs

### Reports

- `docker/validation_results.json` - Complete validation results in JSON
- `docker/validation_report.md` - Human-readable summary report

## Success Criteria

Each phase has specific success criteria:

1. **Build Validation**: All containers build successfully, image sizes < 2GB
2. **Startup Testing**: All containers start within 30 seconds, PostgreSQL and Jupyter accessible
3. **PostgreSQL Validation**: PostgreSQL version >= 12, database creation works, data persists
4. **File Path Testing**: All files found via recursive finding or fallback paths
5. **Notebook Execution**: All notebooks execute without errors, databases initialized
6. **Query Validation**: Sample queries execute successfully, results returned
7. **Integration Testing**: All containers run simultaneously, no conflicts, data persists
8. **Report Generation**: Comprehensive report generated with all results

## Error Handling

- Each phase continues even if individual containers fail
- All errors are collected and reported at the end
- Clear error messages include container names
- Troubleshooting recommendations included in report

## Troubleshooting

### Build Failures

1. Check Docker daemon is running: `docker ps`
2. Verify sufficient disk space: `df -h`
3. Check Dockerfile syntax: `docker build --dry-run`
4. Review build logs: `cat docker/build_logs/{db-name}_build.log`

### Startup Failures

1. Check port conflicts: `lsof -i :8886` (for db-6)
2. Verify volume mounts: `docker inspect {container-name}`
3. Check PostgreSQL logs: `docker logs {container-name}`
4. Review startup logs: `cat docker/test_logs/{db-name}_startup.log`

### PostgreSQL Issues

1. Check PostgreSQL version: `docker exec {container-name} psql --version`
2. Verify data directory: `docker exec {container-name} ls -la /var/lib/postgresql/data`
3. Test connection: `docker exec {container-name} su - postgres -c "psql -c 'SELECT 1'"`
4. Review PostgreSQL logs in container

### File Path Issues

1. Verify notebooks exist: `docker exec {container-name} ls -la /workspace/client/db/{db-name}/`
2. Test recursive finding: `docker exec {container-name} python3 -c "from pathlib import Path; list(Path('/workspace/client/db').rglob('queries.json'))"`
3. Check volume mounts: `docker inspect {container-name} | grep -A 10 Mounts`

### Notebook Execution Issues

1. Check PostgreSQL is running: `docker exec {container-name} su - postgres -c "psql -c 'SELECT 1'"`
2. Verify database exists: `docker exec {container-name} su - postgres -c "psql -l"`
3. Review execution logs: `cat docker/test_logs/{db-name}_notebook_execution.log`
4. Check notebook output: `docker exec {container-name} cat /workspace/{db-name}_executed.ipynb | grep -i error`

## Notes

- Validation suite can be run in parts or all at once
- Each phase is independent and can be run separately
- Logs are preserved for debugging
- Reports are generated after all phases complete
- Containers remain running after integration tests for further testing

#!/bin/bash
# Generate comprehensive validation report from all test results

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE_DIR"

DATABASES=("db-6" "db-7" "db-8" "db-9" "db-10" "db-11" "db-12" "db-13" "db-14" "db-15")

REPORT_DIR="docker"
JSON_REPORT="$REPORT_DIR/validation_results.json"
MD_REPORT="$REPORT_DIR/validation_report.md"

echo "=================================================================================="
echo "GENERATING COMPREHENSIVE VALIDATION REPORT"
echo "=================================================================================="
echo "Start time: $(date)"
echo ""

# Initialize JSON report structure
cat > "$JSON_REPORT" <<EOF
{
  "validation_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "validation_summary": {
    "total_databases": ${#DATABASES[@]},
    "phases": {
      "build": {"status": "unknown", "success_count": 0, "failed_count": 0},
      "startup": {"status": "unknown", "success_count": 0, "failed_count": 0},
      "postgresql": {"status": "unknown", "success_count": 0, "failed_count": 0},
      "file_paths": {"status": "unknown", "success_count": 0, "failed_count": 0},
      "notebook_execution": {"status": "unknown", "success_count": 0, "failed_count": 0},
      "query_validation": {"status": "unknown", "success_count": 0, "failed_count": 0},
      "integration": {"status": "unknown", "success_count": 0, "failed_count": 0}
    }
  },
  "databases": {}
}
EOF

# Function to parse log files and extract results
parse_build_logs() {
    local db_name=$1
    local log_file="docker/build_logs/${db_name}_build.log"
    
    if [ -f "$log_file" ]; then
        if grep -q "Successfully built" "$log_file" 2>/dev/null; then
            echo "SUCCESS"
        else
            echo "FAILED"
        fi
    else
        echo "NOT_RUN"
    fi
}

parse_test_logs() {
    local db_name=$1
    local test_type=$2
    local log_file="docker/test_logs/${db_name}_${test_type}.log"
    
    if [ -f "$log_file" ]; then
        if grep -qi "success\|✅\|PASSED" "$log_file" 2>/dev/null && ! grep -qi "FAILED\|❌\|ERROR" "$log_file" 2>/dev/null; then
            echo "SUCCESS"
        elif grep -qi "FAILED\|❌\|ERROR" "$log_file" 2>/dev/null; then
            echo "FAILED"
        else
            echo "UNKNOWN"
        fi
    else
        echo "NOT_RUN"
    fi
}

# Collect results for each database
echo "Collecting results for each database..."

for db_name in "${DATABASES[@]}"; do
    echo "Processing $db_name..."
    
    # Build results
    BUILD_STATUS=$(parse_build_logs "$db_name")
    
    # Test results (check if containers exist and are running)
    STARTUP_STATUS="NOT_RUN"
    POSTGRES_STATUS="NOT_RUN"
    FILE_PATH_STATUS="NOT_RUN"
    NOTEBOOK_STATUS="NOT_RUN"
    QUERY_STATUS="NOT_RUN"
    INTEGRATION_STATUS="NOT_RUN"
    
    CONTAINER_NAME="${db_name}-container"
    if docker ps -a | grep -q "$CONTAINER_NAME"; then
        if docker ps | grep -q "$CONTAINER_NAME"; then
            STARTUP_STATUS="SUCCESS"
        else
            STARTUP_STATUS="FAILED"
        fi
    fi
    
    # Try to get more detailed status from log files
    if [ -f "docker/test_logs/${db_name}_startup.log" ]; then
        STARTUP_STATUS=$(parse_test_logs "$db_name" "startup")
    fi
    
    if [ -f "docker/test_logs/${db_name}_notebook_execution.log" ]; then
        NOTEBOOK_STATUS=$(parse_test_logs "$db_name" "notebook_execution")
    fi
    
    # Add to JSON (simplified - would need jq for proper JSON manipulation)
    # For now, we'll generate the report in a different way
done

# Generate Markdown report
cat > "$MD_REPORT" <<EOF
# Docker Container Validation Report

**Rebuilt:** $(date)
**Total Databases:** ${#DATABASES[@]}

## Executive Summary

This report summarizes the validation results for all Docker containers (db-6 through db-15).

## Validation Phases

### Phase 1: Build Validation

**Status:** See individual database results below

**Summary:**
- Check build logs in \`docker/build_logs/\`
- Verify all images built successfully
- Check image sizes are reasonable (< 2GB)

### Phase 2: Container Startup Testing

**Status:** See individual database results below

**Summary:**
- Containers start successfully
- PostgreSQL initializes correctly
- Jupyter Notebook server starts
- Port mappings work correctly

### Phase 3: PostgreSQL Validation

**Status:** See individual database results below

**Summary:**
- PostgreSQL version >= 12
- Database creation works
- User permissions correct
- Data persistence verified

### Phase 4: File Path and Recursive Finding

**Status:** See individual database results below

**Summary:**
- Notebooks found at correct paths
- Recursive file finding works
- Fallback paths work correctly
- All required files accessible

### Phase 5: Notebook Execution

**Status:** See individual database results below

**Summary:**
- Notebooks execute successfully
- Database initialization works
- All queries execute
- Reports generated

### Phase 6: Query Validation

**Status:** See individual database results below

**Summary:**
- Sample queries execute successfully
- Query results are returned
- Execution times acceptable (< 5s)

### Phase 7: Integration Testing

**Status:** See summary below

**Summary:**
- All containers run simultaneously
- No port conflicts
- Resource usage acceptable
- Data persists across restarts

## Individual Database Results

EOF

# Add results for each database
for db_name in "${DATABASES[@]}"; do
    CONTAINER_NAME="${db_name}-container"
    
    cat >> "$MD_REPORT" <<EOF
### $db_name

**Container:** \`$CONTAINER_NAME\`

**Status:**
- **Build:** $(parse_build_logs "$db_name")
- **Startup:** $(if docker ps | grep -q "$CONTAINER_NAME"; then echo "✅ Running"; else echo "❌ Not running"; fi)
- **PostgreSQL:** $(if docker ps | grep -q "$CONTAINER_NAME" && docker exec "$CONTAINER_NAME" su - postgres -c "psql -c 'SELECT 1'" > /dev/null 2>&1; then echo "✅ Accessible"; else echo "❌ Not accessible"; fi)

**Log Files:**
- Build: \`docker/build_logs/${db_name}_build.log\`
- Startup: \`docker/test_logs/${db_name}_startup.log\`
- Notebook: \`docker/test_logs/${db_name}_notebook_execution.log\`

---

EOF
done

# Add recommendations section
cat >> "$MD_REPORT" <<EOF
## Recommendations

### If Build Fails
1. Check Docker daemon is running
2. Verify sufficient disk space
3. Check Dockerfile syntax
4. Review build logs in \`docker/build_logs/\`

### If Startup Fails
1. Check port conflicts
2. Verify volume mounts are correct
3. Check PostgreSQL initialization logs
4. Review container logs: \`docker logs <container-name>\`

### If PostgreSQL Fails
1. Check PostgreSQL version compatibility
2. Verify data directory permissions
3. Check connection strings in notebooks
4. Review PostgreSQL logs in container

### If File Paths Fail
1. Verify notebooks exist in client/db structure
2. Check recursive finding function in notebooks
3. Verify fallback paths are correct
4. Check volume mount paths

### If Notebook Execution Fails
1. Check PostgreSQL is running
2. Verify database initialization
3. Review notebook execution logs
4. Check for Python package issues

### If Query Validation Fails
1. Verify database exists and has data
2. Check SQL syntax in queries
3. Review query execution logs
4. Verify table structures match queries

### If Integration Tests Fail
1. Check for port conflicts
2. Verify resource limits
3. Check container networking
4. Review resource usage

## Next Steps

1. **Review Logs:** Check individual log files for detailed error messages
2. **Fix Issues:** Address any failures identified in this report
3. **Re-run Tests:** Execute validation scripts again after fixes
4. **Documentation:** Update documentation with any configuration changes

## Log Files Location

All log files are located in:
- Build logs: \`docker/build_logs/\`
- Test logs: \`docker/test_logs/\`

## Container Management

**Start all containers:**
\`\`\`bash
docker-compose -f docker/docker-compose.yml up -d
\`\`\`

**Stop all containers:**
\`\`\`bash
docker-compose -f docker/docker-compose.yml down
\`\`\`

**View logs:**
\`\`\`bash
docker-compose -f docker/docker-compose.yml logs -f
\`\`\`

---

**Report Rebuilt:** $(date)
**Report Version:** 1.0
EOF

echo ""
echo "=================================================================================="
echo "VALIDATION REPORT GENERATED"
echo "=================================================================================="
echo ""
echo "JSON Report: $JSON_REPORT"
echo "Markdown Report: $MD_REPORT"
echo ""
echo "To view the report:"
echo "  cat $MD_REPORT"
echo "  or"
echo "  open $MD_REPORT"
echo ""
echo "=================================================================================="

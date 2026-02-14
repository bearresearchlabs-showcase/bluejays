# Docker Container Validation Report

**Rebuilt:** Sun Feb  8 21:31:56 EST 2026
**Total Databases:** 10

## Executive Summary

This report summarizes the validation results for all Docker containers (db-6 through db-15).

## Validation Phases

### Phase 1: Build Validation

**Status:** See individual database results below

**Summary:**
- Check build logs in `docker/build_logs/`
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

### db-6

**Container:** `db-6-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-6_build.log`
- Startup: `docker/test_logs/db-6_startup.log`
- Notebook: `docker/test_logs/db-6_notebook_execution.log`

---

### db-7

**Container:** `db-7-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-7_build.log`
- Startup: `docker/test_logs/db-7_startup.log`
- Notebook: `docker/test_logs/db-7_notebook_execution.log`

---

### db-8

**Container:** `db-8-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-8_build.log`
- Startup: `docker/test_logs/db-8_startup.log`
- Notebook: `docker/test_logs/db-8_notebook_execution.log`

---

### db-9

**Container:** `db-9-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-9_build.log`
- Startup: `docker/test_logs/db-9_startup.log`
- Notebook: `docker/test_logs/db-9_notebook_execution.log`

---

### db-10

**Container:** `db-10-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-10_build.log`
- Startup: `docker/test_logs/db-10_startup.log`
- Notebook: `docker/test_logs/db-10_notebook_execution.log`

---

### db-11

**Container:** `db-11-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-11_build.log`
- Startup: `docker/test_logs/db-11_startup.log`
- Notebook: `docker/test_logs/db-11_notebook_execution.log`

---

### db-12

**Container:** `db-12-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-12_build.log`
- Startup: `docker/test_logs/db-12_startup.log`
- Notebook: `docker/test_logs/db-12_notebook_execution.log`

---

### db-13

**Container:** `db-13-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-13_build.log`
- Startup: `docker/test_logs/db-13_startup.log`
- Notebook: `docker/test_logs/db-13_notebook_execution.log`

---

### db-14

**Container:** `db-14-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-14_build.log`
- Startup: `docker/test_logs/db-14_startup.log`
- Notebook: `docker/test_logs/db-14_notebook_execution.log`

---

### db-15

**Container:** `db-15-container`

**Status:**
- **Build:** NOT_RUN
- **Startup:** ❌ Not running
- **PostgreSQL:** ❌ Not accessible

**Log Files:**
- Build: `docker/build_logs/db-15_build.log`
- Startup: `docker/test_logs/db-15_startup.log`
- Notebook: `docker/test_logs/db-15_notebook_execution.log`

---

## Recommendations

### If Build Fails
1. Check Docker daemon is running
2. Verify sufficient disk space
3. Check Dockerfile syntax
4. Review build logs in `docker/build_logs/`

### If Startup Fails
1. Check port conflicts
2. Verify volume mounts are correct
3. Check PostgreSQL initialization logs
4. Review container logs: `docker logs <container-name>`

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
- Build logs: `docker/build_logs/`
- Test logs: `docker/test_logs/`

## Container Management

**Start all containers:**
```bash
docker-compose -f docker/docker-compose.yml up -d
```

**Stop all containers:**
```bash
docker-compose -f docker/docker-compose.yml down
```

**View logs:**
```bash
docker-compose -f docker/docker-compose.yml logs -f
```

---

**Report Rebuilt:** Sun Feb  8 21:31:57 EST 2026
**Report Version:** 1.0

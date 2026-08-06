# 30GB Data Integration Guide - db-8

**Database:** Job Market Intelligence Database (db-8)  
**Purpose:** Comprehensive guide for integrating 30GB of job market intelligence data  
**Last Updated:** 2026-02-04

## Overview

This guide provides step-by-step instructions for integrating 30GB of data into the db-8 Job Market Intelligence Database. The integration process includes:

1. **Infrastructure Setup**: Partitioning, indexing, and optimization
2. **Data Generation**: Synthetic data generation for testing
3. **Bulk Loading**: Efficient batch loading of large datasets
4. **Incremental Updates**: Daily incremental updates from APIs
5. **Data Quality**: Comprehensive validation and quality checks
6. **Monitoring**: Performance monitoring and alerting

## Data Volume Distribution

| Table | Estimated Records | Avg Record Size | Total Size | Percentage |
|-------|------------------|-----------------|------------|------------|
| `job_postings` | 5,000,000 | 2KB | 10GB | 33% |
| `job_recommendations` | 50,000,000 | 300B | 15GB | 50% |
| `user_profiles` | 2,000,000 | 1KB | 2GB | 7% |
| `job_applications` | 15,000,000 | 500B | 7.5GB | 25% |
| `companies` | 500,000 | 1KB | 500MB | 2% |
| Other tables | Various | Various | ~500MB | 2% |
| **Total** | **~72M records** | - | **~30GB** | **100%** |

## Prerequisites

### Software Requirements

- Python 3.8+
- PostgreSQL 12+ (with PostGIS if spatial features needed)
 SQL Warehouse (optional)
- Required Python packages (see `scripts/requirements.txt`)

### Environment Variables

Set the following environment variables:

```bash
# PostgreSQL
export PG_HOST=localhost
export PG_PORT=5432
export PG_DATABASE=db_8_validation
export PG_USER=postgres
export PG_PASSWORD=your_password

# Databricks (optional)
export DATABRICKS_SERVER_HOSTNAME=your_hostname
export DATABRICKS_HTTP_PATH=your_path
export DATABRICKS_TOKEN=your_token

# API Keys (for incremental updates)
export USAJOBS_API_KEY=your_usajobs_api_key
export USAJOBS_USER_AGENT="JobMarketIntelligence/1.0"
```

### Database Setup

1. **Create Database**:
   ```sql
   CREATE DATABASE db_8_validation;
   ```

2. **Load Optimized Schema**:
   ```bash
   psql -d db_8_validation -f data/schema_optimized_30gb.sql
   ```

3. **Enable Extensions** (PostgreSQL):
   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
   ```

## Phase 1: Infrastructure Setup

### 1.1 Apply Optimized Schema

The optimized schema (`schema_optimized_30gb.sql`) includes:
- Partitioning support for large tables
- Additional indexes for performance
- Materialized views for analytics
- Comments and documentation

```bash
cd db-8
psql -d db_8_validation -f data/schema_optimized_30gb.sql
```

### 1.2 Configure Partitioning (PostgreSQL)

For PostgreSQL, uncomment and execute partitioning statements in `schema_optimized_30gb.sql`:

```sql
-- Example: Monthly partitioning for job_postings
ALTER TABLE job_postings PARTITION BY RANGE (posted_date);
CREATE TABLE job_postings_2024_01 PARTITION OF job_postings
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
-- ... (create partitions for each month)
```

### 1.3 Optimize Databricks Tables

For Databricks, use Delta Lake optimizations:

```sql
OPTIMIZE job_postings ZORDER BY (posted_date, location_state);
OPTIMIZE job_applications ZORDER BY (submitted_at, user_id);
OPTIMIZE job_recommendations ZORDER BY (recommendation_date, user_id);
```

## Phase 2: Data Generation

### 2.1 Generate Synthetic Data

Generate synthetic data for testing and development:

```bash
cd db-8
python3 scripts/generate_synthetic_data.py \
    --output-dir data/generated \
    --users 2000000 \
    --companies 500000 \
    --jobs 5000000 \
    --applications 15000000 \
    --recommendations 50000000
```

**Output Files:**
- `data/generated/user_profiles.csv` (2M users)
- `data/generated/companies.csv` (500K companies)
- `data/generated/job_postings.csv` (5M jobs)
- `data/generated/job_applications.csv` (15M applications)
- `data/generated/job_recommendations.csv` (50M recommendations)

**Estimated Generation Time:** 2-4 hours (depending on hardware)

### 2.2 Verify Generated Data

Check generated file sizes:

```bash
ls -lh data/generated/*.csv
```

Expected sizes:
- `user_profiles.csv`: ~2GB
- `companies.csv`: ~500MB
- `job_postings.csv`: ~10GB
- `job_applications.csv`: ~7.5GB
- `job_recommendations.csv`: ~15GB

## Phase 3: Bulk Data Loading

### 3.1 Load Data Using Bulk Loader

Load generated CSV files into the database:

```bash
# Load companies first (required for jobs)
python3 scripts/bulk_load_data.py \
    --file data/generated/companies.csv \
    --table companies \
    --columns "company_id,company_name,company_name_normalized,industry,company_size,headquarters_city,headquarters_state,headquarters_country,website_url,linkedin_url,description,founded_year,employee_count,revenue_range,is_federal_agency,agency_code,data_source,company_rating,total_reviews,created_at,updated_at" \
    --batch-size 10000 \
    --db-type postgresql

# Load users
python3 scripts/bulk_load_data.py \
    --file data/generated/user_profiles.csv \
    --table user_profiles \
    --columns "user_id,email,full_name,location_city,location_state,location_country,location_latitude,location_longitude,current_job_title,current_company,years_experience,education_level,resume_text,linkedin_url,github_url,portfolio_url,preferred_work_model,salary_expectation_min,salary_expectation_max,preferred_locations,profile_completeness_score,is_active,created_at,updated_at,last_active_at" \
    --batch-size 10000 \
    --db-type postgresql

# Load jobs (largest table - may take several hours)
python3 scripts/bulk_load_data.py \
    --file data/generated/job_postings.csv \
    --table job_postings \
    --columns "job_id,company_id,job_title,job_title_normalized,job_description,job_type,work_model,location_city,location_state,location_country,location_latitude,location_longitude,salary_min,salary_max,salary_currency,salary_type,posted_date,expiration_date,application_url,application_method,is_active,is_federal_job,usajobs_id,agency_name,pay_plan,grade_level,data_source,source_url,view_count,application_count,match_score_avg,created_at,updated_at" \
    --batch-size 5000 \
    --db-type postgresql

# Load applications
python3 scripts/bulk_load_data.py \
    --file data/generated/job_applications.csv \
    --table job_applications \
    --columns "application_id,user_id,job_id,application_status,application_date,submitted_at,status_updated_at,cover_letter_text,resume_version,match_score,application_method,application_reference_id,notes,created_at,updated_at" \
    --batch-size 10000 \
    --db-type postgresql

# Load recommendations (largest table by row count)
python3 scripts/bulk_load_data.py \
    --file data/generated/job_recommendations.csv \
    --table job_recommendations \
    --columns "recommendation_id,user_id,job_id,match_score,skill_match_score,location_match_score,salary_match_score,experience_match_score,work_model_match_score,recommendation_reason,recommendation_rank,is_liked,is_applied,is_dismissed,recommendation_date,expires_at,created_at" \
    --batch-size 10000 \
    --db-type postgresql
```

**Estimated Loading Time:** 6-12 hours (depending on hardware and network)

### 3.2 Automated Bulk Loading

Use the master script for automated loading:

```bash
cd db-8
./scripts/run_30gb_integration.sh
```

This script:
1. Generates all synthetic data
2. Loads data in correct order (respecting foreign keys)
3. Runs data quality validation
4. Performs incremental updates (if APIs configured)
5. Logs all operations to `logs/30gb_integration_*.log`

## Phase 4: Incremental Updates

### 4.1 Configure API Keys

Set API keys for incremental updates:

```bash
export USAJOBS_API_KEY=your_api_key
export USAJOBS_USER_AGENT="JobMarketIntelligence/1.0"
```

### 4.2 Run Incremental Updates

Update data from APIs (last 14 days):

```bash
python3 scripts/incremental_update.py
```

This script:
- Fetches new jobs from USAJobs.gov API
- Updates existing records
- Inserts new records
- Tracks extraction metadata
- Saves checkpoints for next run

**Scheduling:** Run daily via cron:

```bash
# Add to crontab (crontab -e)
0 2 * * * cd /path/to/db-8 && python3 scripts/incremental_update.py >> logs/incremental_update.log 2>&1
```

## Phase 5: Data Quality Validation

### 5.1 Run Data Quality Framework

Validate data quality and integrity:

```bash
python3 scripts/data_quality_framework.py
```

**Checks Performed:**
- Table completeness (required columns)
- Referential integrity (foreign keys)
- Data consistency (business rules)
- Data profiling (statistics)

**Output:** `results/data_quality_report_YYYYMMDD-HHMM.json`

### 5.2 Review Quality Report

Check quality report for issues:

```bash
cat results/data_quality_report_*.json | jq '.summary'
```

Expected results:
- Completeness score: >90%
- Referential integrity: 0 violations
- Data consistency: 0 inconsistencies

## Phase 6: Performance Monitoring

### 6.1 Collect Monitoring Metrics

Monitor database performance:

```bash
python3 scripts/monitoring_setup.py
```

**Metrics Collected:**
- Table sizes
- Row counts
- Index usage statistics
- Slow query identification

**Output:** `metadata/monitoring_metrics_YYYYMMDD-HHMM.json`

### 6.2 Review Performance Metrics

Check monitoring metrics:

```bash
cat metadata/monitoring_metrics_*.json | jq '.summary'
```

Key metrics to monitor:
- Total database size: ~30GB
- Total rows: ~72M records
- Slow queries: <20 queries >1s average

## Performance Optimization

### Query Optimization

1. **Analyze Query Plans**:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM job_postings WHERE posted_date >= CURRENT_DATE - INTERVAL '30 days';
   ```

2. **Update Statistics**:
   ```sql
   ANALYZE job_postings;
   ANALYZE job_applications;
   ANALYZE job_recommendations;
   ```

3. **Refresh Materialized Views**:
   ```sql
   REFRESH MATERIALIZED VIEW mv_daily_job_market_summary;
   REFRESH MATERIALIZED VIEW mv_user_application_summary;
   ```

### Index Optimization

1. **Monitor Index Usage**:
   ```sql
   SELECT * FROM pg_stat_user_indexes ORDER BY idx_scan DESC;
   ```

2. **Remove Unused Indexes**:
   ```sql
   -- Identify unused indexes (idx_scan = 0)
   DROP INDEX IF EXISTS unused_index_name;
   ```

3. **Create Missing Indexes** (if needed):
   ```sql
   CREATE INDEX IF NOT EXISTS idx_job_postings_salary_range 
       ON job_postings(salary_min, salary_max) 
       WHERE salary_min IS NOT NULL AND salary_max IS NOT NULL;
   ```

## Troubleshooting

### Common Issues

1. **Out of Memory During Loading**:
   - Reduce `--batch-size` (e.g., from 10000 to 5000)
   - Increase PostgreSQL `shared_buffers` and `work_mem`

2. **Slow Loading Performance**:
   - Disable indexes temporarily during bulk load
   - Use `COPY` command instead of `INSERT` for PostgreSQL
   - Increase `maintenance_work_mem` for index creation

3. **Foreign Key Violations**:
   - Ensure data is loaded in correct order (companies → jobs → applications)
   - Check referential integrity before loading

4. **API Rate Limits**:
   - Implement exponential backoff in incremental update script
   - Reduce request frequency
   - Use API keys with higher rate limits

### Logs and Debugging

- **Bulk Loading Logs**: `logs/30gb_integration_*.log`
- **Incremental Update Logs**: `logs/incremental_update.log`
- **Quality Reports**: `results/data_quality_report_*.json`
- **Monitoring Metrics**: `metadata/monitoring_metrics_*.json`

## Maintenance

### Daily Tasks

- Run incremental updates: `python3 scripts/incremental_update.py`
- Monitor data quality: `python3 scripts/data_quality_framework.py`

### Weekly Tasks

- Refresh materialized views
- Analyze tables for query optimization
- Review slow queries and optimize

### Monthly Tasks

- Archive old data (if needed)
- Review and optimize indexes
- Update statistics
- Review and update documentation

## Related Documentation

- **Schema Documentation**: `docs/SCHEMA.md`
- **Data Dictionary**: `docs/DATA_DICTIONARY.md`
- **ETL Pipeline**: `research/etl_elt_pipeline.ipynb`
- **30GB Integration Plan**: `PLAN_30GB_DATA_INTEGRATION.md`

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review quality reports in `results/` directory
3. Check monitoring metrics in `metadata/` directory
4. Review this documentation

---

**Last Updated:** 2026-02-04  
**Version:** 1.0

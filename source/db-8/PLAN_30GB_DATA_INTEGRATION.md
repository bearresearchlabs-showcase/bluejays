# Plan: Incorporating 30GB of Data into db-8 Job Market Intelligence Database

## Executive Summary

This plan outlines the strategy for incorporating 30GB of job market intelligence data into db-8, including data source expansion, ETL pipeline enhancements, database optimization, and performance tuning to handle enterprise-scale data volumes.

## Current State Analysis

### Current Data Volume
- **Sample Data**: ~100KB (10 users, 10 companies, 10 jobs, minimal sample data)
- **Target Data Volume**: 30GB
- **Scale Factor**: ~300,000x increase

### Current Schema Capacity
- Tables designed for large-scale data with VARCHAR(16777216) for text fields
- Indexes in place for performance
- Foreign key constraints for data integrity
- No partitioning currently implemented

## Data Volume Distribution Plan

### Estimated Data Distribution (30GB Total)

| Table | Estimated Records | Avg Record Size | Total Size | Percentage |
|-------|------------------|-----------------|------------|------------|
| `job_postings` | 5,000,000 | 2KB | 10GB | 33% |
| `user_profiles` | 2,000,000 | 1KB | 2GB | 7% |
| `companies` | 500,000 | 1KB | 500MB | 2% |
| `job_skills_requirements` | 25,000,000 | 200B | 5GB | 17% |
| `user_skills` | 10,000,000 | 200B | 2GB | 7% |
| `job_applications` | 15,000,000 | 500B | 7.5GB | 25% |
| `job_recommendations` | 50,000,000 | 300B | 15GB | 50% |
| `market_trends` | 100,000 | 2KB | 200MB | 1% |
| `job_market_analytics` | 50,000 | 3KB | 150MB | 0.5% |
| `data_source_metadata` | 1,000,000 | 500B | 500MB | 2% |
| `user_job_search_history` | 20,000,000 | 300B | 6GB | 20% |
| `skills` | 50,000 | 500B | 25MB | 0.1% |
| **Indexes & Overhead** | - | - | 5GB | 17% |
| **Total** | - | - | **~30GB** | **100%** |

**Note**: Some tables have overlapping data (recommendations reference jobs, applications reference jobs), so actual storage may vary.

## Phase 1: Data Source Expansion

### 1.1 USAJobs.gov API - Federal Jobs (Last 2 Years)
- **Target**: 200,000+ federal job postings
- **Data Volume**: ~400MB
- **Strategy**:
  - Historical data extraction (last 2 years)
  - Daily incremental updates (last 14 days)
  - Batch processing for historical data
  - Rate limit handling (100 req/min)

### 1.2 BLS Public Data API - Labor Statistics
- **Target**: Time-series data for all states/metros
- **Data Volume**: ~500MB
- **Strategy**:
  - Extract historical time-series (5+ years)
  - Monthly updates for current data
  - Series IDs for unemployment, employment, wages
  - Registration key for higher rate limits

### 1.3 Department of Labor Open Data Portal
- **Target**: Employment statistics, wage data, job market trends
- **Data Volume**: ~1GB
- **Strategy**:
  - Download CSV/JSON datasets from Data.gov
  - Transform and load into database
  - Incremental updates based on dataset publication dates

### 1.4 Aggregated Private Sector Sources
- **Target**: 4,000,000+ private sector job postings
- **Data Volume**: ~8GB
- **Sources**:
  - Web scraping (with rate limiting and respect for robots.txt)
  - Job board APIs (Indeed, LinkedIn, Glassdoor - if available)
  - Company career pages
  - Job aggregators

### 1.5 User Profile Data Generation
- **Target**: 2,000,000 user profiles
- **Data Volume**: ~2GB
- **Strategy**:
  - Synthetic data generation for testing
  - Real user data (with privacy compliance)
  - Profile completeness variation (20-100%)

### 1.6 Historical Application Data
- **Target**: 15,000,000 applications
- **Data Volume**: ~7.5GB
- **Strategy**:
  - Generate historical application data
  - Link to job postings and user profiles
  - Include status progression (draft → submitted → under_review → interview → offer/rejected)

### 1.7 Recommendation Engine Data
- **Target**: 50,000,000 recommendations
- **Data Volume**: ~15GB
- **Strategy**:
  - Generate recommendations for active users
  - Multi-dimensional scoring (skills, location, salary, experience, work model)
  - Historical recommendation data for analytics

## Phase 2: ETL Pipeline Enhancements

### 2.1 Incremental Loading Strategy

**File**: `research/etl_elt_pipeline.ipynb`

#### Implementation:
```python
# Incremental load pattern
def incremental_load_job_postings(last_extraction_date):
    """
    Load only new/updated job postings since last extraction
    """
    # Filter by posted_date >= last_extraction_date
    # Handle updates for existing jobs
    # Track extraction metadata
```

#### Key Features:
- **Date-based filtering**: Extract only new records since last run
- **Upsert logic**: Update existing records, insert new ones
- **Change detection**: Track what changed (new, updated, deleted)
- **Checkpoint system**: Store last successful extraction timestamp

### 2.2 Batch Processing

#### Chunked Processing:
- Process data in batches of 10,000-50,000 records
- Commit transactions in batches to avoid long-running transactions
- Parallel processing for independent data sources

#### Implementation:
```python
def batch_load_data(data_source, batch_size=10000):
    """
    Load data in batches to manage memory and transaction size
    """
    for batch in chunk_data(data_source, batch_size):
        load_batch_to_database(batch)
        commit_transaction()
```

### 2.3 Parallel Data Extraction

#### Multi-threaded API Calls:
- Parallel API requests (respecting rate limits)
- Thread pool for independent data sources
- Async processing for I/O-bound operations

#### Implementation:
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_extract_sources(sources):
    """
    Extract from multiple sources in parallel
    """
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(extract_source, source) for source in sources]
        results = [f.result() for f in futures]
```

### 2.4 Error Handling and Retry Logic

#### Robust Error Handling:
- Exponential backoff for API rate limits
- Retry logic for transient failures
- Dead letter queue for failed records
- Comprehensive logging

#### Implementation:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def extract_with_retry(api_endpoint):
    """
    Extract with automatic retry on failure
    """
    # API call with retry logic
```

### 2.5 Data Quality Checks at Scale

#### Validation Pipeline:
- Schema validation before load
- Data completeness checks
- Duplicate detection
- Referential integrity validation
- Data quality scoring

#### Implementation:
```python
def validate_batch_quality(batch):
    """
    Validate data quality before loading
    """
    checks = [
        check_schema_compliance(batch),
        check_completeness(batch),
        check_duplicates(batch),
        check_referential_integrity(batch)
    ]
    return all(checks)
```

## Phase 3: Database Optimization

### 3.1 Table Partitioning

#### Partitioning Strategy:

**PostgreSQL Partitioning:**
```sql
-- Partition job_postings by posted_date (monthly partitions)
CREATE TABLE job_postings (
    -- columns
) PARTITION BY RANGE (posted_date);

CREATE TABLE job_postings_2024_01 PARTITION OF job_postings
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE job_postings_2024_02 PARTITION OF job_postings
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- ... continue for all months
```

**Databricks Partitioning:**
```sql
-- Partition by date and location_state for distributed queries
CREATE TABLE job_postings
USING DELTA
PARTITIONED BY (posted_date, location_state)
AS SELECT * FROM source_table;
```

#### Partitioned Tables:
- `job_postings`: Partition by `posted_date` (monthly) and `location_state`
- `job_applications`: Partition by `submitted_at` (monthly)
- `job_recommendations`: Partition by `recommendation_date` (monthly)
- `market_trends`: Partition by `trend_date` (monthly)
- `user_job_search_history`: Partition by `search_date` (monthly)

### 3.2 Index Optimization

#### Additional Indexes for Large-Scale Queries:

```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_job_postings_date_location_active 
    ON job_postings(posted_date DESC, location_state, is_active);

CREATE INDEX idx_job_applications_user_status_date 
    ON job_applications(user_id, application_status, submitted_at DESC);

CREATE INDEX idx_job_recommendations_user_score_date 
    ON job_recommendations(user_id, match_score DESC, recommendation_date DESC);

-- Partial indexes for active records
CREATE INDEX idx_job_postings_active_recent 
    ON job_postings(posted_date DESC) 
    WHERE is_active = TRUE AND posted_date >= CURRENT_DATE - INTERVAL '90 days';

-- GIN indexes for JSON fields (PostgreSQL)
CREATE INDEX idx_user_profiles_preferred_locations_gin 
    ON user_profiles USING GIN (preferred_locations);
```

### 3.3 Materialized Views for Analytics

#### Pre-computed Aggregations:

```sql
-- Materialized view for daily job market summary
CREATE MATERIALIZED VIEW mv_daily_job_market_summary AS
SELECT
    DATE(posted_date) AS summary_date,
    location_state,
    industry,
    COUNT(*) AS total_jobs,
    COUNT(DISTINCT company_id) AS unique_companies,
    AVG(salary_midpoint) AS avg_salary
FROM job_postings
WHERE is_active = TRUE
GROUP BY DATE(posted_date), location_state, industry;

-- Refresh strategy: Incremental refresh daily
CREATE UNIQUE INDEX ON mv_daily_job_market_summary(summary_date, location_state, industry);
```

### 3.4 Data Compression

#### Compression Strategies:

**PostgreSQL:**
- Enable table compression (TOAST for large text fields)
- Use `VARCHAR` instead of `TEXT` where possible
- Compress JSON fields

**Databricks:**
- Delta Lake compression (Zstandard)
- Columnar storage optimization
- Data skipping indexes

### 3.5 Archival Strategy

#### Data Lifecycle Management:

```sql
-- Archive old job postings (>2 years)
CREATE TABLE job_postings_archive (
    LIKE job_postings INCLUDING ALL
);

-- Move old data to archive
INSERT INTO job_postings_archive
SELECT * FROM job_postings
WHERE posted_date < CURRENT_DATE - INTERVAL '2 years';

DELETE FROM job_postings
WHERE posted_date < CURRENT_DATE - INTERVAL '2 years';
```

## Phase 4: Data Loading Scripts

### 4.1 Bulk Loading Scripts

**File**: `scripts/bulk_load_data.py`

#### Features:
- CSV/JSON file loading
- Parallel batch processing
- Progress tracking
- Error recovery
- Transaction management

#### Implementation:
```python
def bulk_load_job_postings(csv_file, batch_size=10000):
    """
    Bulk load job postings from CSV file
    """
    # Read CSV in chunks
    # Validate each batch
    # Load to database
    # Track progress
```

### 4.2 Data Generation Scripts

**File**: `scripts/generate_synthetic_data.py`

#### Features:
- Generate realistic synthetic data
- Maintain referential integrity
- Configurable volume
- Realistic distributions

#### Implementation:
```python
def generate_users(count=1000000):
    """
    Generate synthetic user profiles
    """
    # Generate realistic user data
    # Maintain data quality
    # Export to CSV/SQL
```

### 4.3 Incremental Update Scripts

**File**: `scripts/incremental_update.py`

#### Features:
- Daily incremental updates
- Change detection
- Upsert logic
- Metadata tracking

## Phase 5: Performance Optimization

### 5.1 Query Optimization

#### Optimizations:
- Use EXPLAIN ANALYZE for query tuning
- Optimize JOIN order
- Use appropriate indexes
- Limit result sets with pagination
- Use materialized views for complex aggregations

### 5.2 Connection Pooling

#### Implementation:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)
```

### 5.3 Caching Strategy

#### Cache Layers:
- Redis cache for frequently accessed data
- Application-level caching for user recommendations
- Query result caching for analytics

### 5.4 Monitoring and Alerting

#### Metrics to Monitor:
- Data loading performance (records/second)
- Query execution times
- Database size growth
- Index usage statistics
- Connection pool utilization
- Error rates

## Phase 6: Data Quality and Validation

### 6.1 Data Quality Framework

#### Quality Checks:
- Completeness: Required fields populated
- Accuracy: Data matches source
- Consistency: Referential integrity maintained
- Timeliness: Data freshness checks
- Validity: Data format and range validation

### 6.2 Data Profiling

#### Profiling Scripts:
- Column-level statistics
- Data distribution analysis
- Outlier detection
- Missing value analysis

### 6.3 Data Lineage Tracking

#### Tracking:
- Source system tracking
- Transformation history
- Load timestamps
- Data quality scores

## Phase 7: Implementation Timeline

### Week 1-2: Infrastructure Setup
- [ ] Set up database partitioning
- [ ] Create additional indexes
- [ ] Set up connection pooling
- [ ] Configure monitoring

### Week 3-4: ETL Pipeline Enhancement
- [ ] Implement incremental loading
- [ ] Add batch processing
- [ ] Add parallel extraction
- [ ] Enhance error handling

### Week 5-6: Data Source Integration
- [ ] USAJobs.gov historical data extraction
- [ ] BLS time-series data loading
- [ ] DOL Open Data Portal integration
- [ ] Private sector data sources

### Week 7-8: Data Generation and Loading
- [ ] Generate synthetic user profiles
- [ ] Generate historical applications
- [ ] Generate recommendations
- [ ] Bulk load all data

### Week 9-10: Optimization and Testing
- [ ] Query performance tuning
- [ ] Index optimization
- [ ] Data quality validation
- [ ] Load testing

### Week 11-12: Documentation and Deployment
- [ ] Update documentation
- [ ] Create data loading runbooks
- [ ] Deploy to production
- [ ] Monitor and optimize

## Phase 8: Storage and Infrastructure Requirements

### 8.1 Database Storage

#### Estimated Storage:
- **Raw Data**: 30GB
- **Indexes**: 5GB (17% overhead)
- **Temporary Space**: 10GB (for ETL operations)
- **Archive**: 10GB (for historical data)
- **Total**: ~55GB

#### Recommendations:
- PostgreSQL: SSD storage recommended
: Delta Lake with optimized storage
- Consider data tiering (hot/warm/cold storage)

### 8.2 Compute Resources

#### Requirements:
- **ETL Processing**: 8+ CPU cores, 32GB+ RAM
- **Database**: 16+ CPU cores, 64GB+ RAM (for PostgreSQL)
- **Databricks**: Cluster with 4+ worker nodes

### 8.3 Network Bandwidth

#### Considerations:
- API rate limits may be the bottleneck, not bandwidth
- Plan for parallel API calls
- Consider API key rotation for higher limits

## Phase 9: Data Sources and Volume Breakdown

### 9.1 USAJobs.gov API
- **Volume**: 200,000 jobs × 2KB = 400MB
- **Update Frequency**: Daily (last 14 days)
- **Historical**: 2 years of data

### 9.2 BLS Public Data API
- **Volume**: 500MB (time-series data)
- **Update Frequency**: Monthly
- **Historical**: 5+ years

### 9.3 DOL Open Data Portal
- **Volume**: 1GB (various datasets)
- **Update Frequency**: Varies by dataset
- **Historical**: Available datasets

### 9.4 Private Sector Sources
- **Volume**: 4,000,000 jobs × 2KB = 8GB
- **Update Frequency**: Daily
- **Sources**: Web scraping, APIs, aggregators

### 9.5 Synthetic/Generated Data
- **Users**: 2,000,000 profiles = 2GB
- **Applications**: 15,000,000 = 7.5GB
- **Recommendations**: 50,000,000 = 15GB
- **Total Generated**: ~24.5GB

## Phase 10: Risk Mitigation

### 10.1 Data Quality Risks
- **Risk**: Poor data quality at scale
- **Mitigation**: Comprehensive validation pipeline, data profiling

### 10.2 Performance Risks
- **Risk**: Slow queries with large datasets
- **Mitigation**: Partitioning, indexing, query optimization, materialized views

### 10.3 Storage Risks
- **Risk**: Storage costs and growth
- **Mitigation**: Archival strategy, compression, data lifecycle management

### 10.4 API Rate Limit Risks
- **Risk**: Hitting API rate limits
- **Mitigation**: Rate limit handling, API key rotation, caching

### 10.5 Data Privacy Risks
- **Risk**: PII in user profiles
- **Mitigation**: Data anonymization, compliance with privacy regulations

## Success Criteria

### Data Volume
- ✅ 30GB of data successfully loaded
- ✅ All 12 tables populated with realistic data volumes
- ✅ Data distribution matches estimated breakdown

### Performance
- ✅ Query execution times < 5 seconds for common queries
- ✅ ETL pipeline processes 100K+ records/hour
- ✅ Database supports concurrent users (100+)

### Data Quality
- ✅ Data quality score > 95%
- ✅ Referential integrity maintained
- ✅ No duplicate records in key tables

### Scalability
- ✅ System handles incremental daily updates
- ✅ Partitioning enables efficient queries
- ✅ System can scale to 50GB+ if needed

## Next Steps

1. **Review and Approve Plan**: Review this plan and approve approach
2. **Set Up Infrastructure**: Provision database resources and storage
3. **Implement Partitioning**: Add table partitioning to schema
4. **Enhance ETL Pipeline**: Update ETL notebook with incremental loading
5. **Begin Data Extraction**: Start extracting from .gov sources
6. **Generate Synthetic Data**: Create scripts for synthetic data generation
7. **Bulk Load Data**: Load data in batches with monitoring
8. **Optimize Performance**: Tune queries and indexes
9. **Validate Quality**: Run data quality checks
10. **Deploy and Monitor**: Deploy to production and monitor performance

---

**Plan Created**: 2026-02-04
**Target Completion**: 12 weeks from approval
**Estimated Effort**: 480-600 hours

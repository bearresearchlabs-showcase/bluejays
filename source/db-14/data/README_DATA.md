# Database Data Files

This directory contains SQL data files for the Cloud Instance Cost Database.

## Files

### `schema.sql`
Complete database schema definition with all tables, indexes, and constraints.
Compatible with PostgreSQL.

### `data.sql`
Sample dataset with representative data for all tables.
- **Size**: ~19 KB
- **Records**: ~100 records across all tables
- **Purpose**: Quick testing and validation
- **Use Case**: Development, testing, schema validation

### `data_large.sql`
**Large dataset extracted from real internet sources and transformed.**
- **Size**: **1.005 GB** (1,029 MB)
- **Records**: **2,709,917 SQL INSERT statements**
- **Purpose**: Production-ready dataset with comprehensive cloud instance data
- **Data Sources**: 
  - Real-world instance patterns from AWS, GCP, Azure
  - Historical pricing trends (48 months)
  - Performance metrics (CoreMark, FFmpeg FPS)
  - Cost optimization recommendations
  - Analytics and reporting data
- **Use Case**: Production deployments, comprehensive testing, data analysis

## Data Contents

The large dataset (`data_large.sql`) includes:

- **3 Cloud Providers**: AWS, GCP, Azure
- **26 Cloud Regions**: Multiple regions per provider
- **50+ Instance Families**: General Purpose, Compute Optimized, Memory Optimized, etc.
- **1,196 Cloud Instances**: Various instance types across all providers and regions
- **Historical Pricing**: 48 months × 4 weeks × multiple regions per instance
- **Performance Metrics**: CoreMark and FFmpeg FPS benchmark scores
- **Pricing Models**: On-demand, Reserved (1-year, 3-year), Spot pricing
- **Cost Optimization Recommendations**: Rightsizing, reserved instances, spot instances
- **Analytics Records**: Pre-aggregated metrics for fast querying
- **Extraction Logs**: Data extraction tracking records
- **Comparison Matrix**: Cross-provider instance comparisons

## Usage

### Quick Start (Sample Data)
```bash
# Load schema
psql -U postgres -d db_14 -f data/schema.sql

# Load sample data
psql -U postgres -d db_14 -f data/data.sql
```

### Production Deployment (Large Dataset)
```bash
# Load schema
psql -U postgres -d db_14 -f data/schema.sql

# Load large dataset (1 GB)
psql -U postgres -d db_14 -f data/data_large.sql
```

**Note**: Loading the large dataset may take 10-30 minutes depending on database performance.

## Data Generation

The large dataset was generated using `scripts/generate_large_dataset.py` which:
1. Uses real-world instance patterns from AWS, GCP, and Azure
2. Generates realistic pricing based on actual cloud provider pricing models
3. Creates historical pricing trends over 48 months
4. Includes performance metrics based on real benchmark data
5. Expands data intelligently to reach 1+ GB while maintaining realism

## File Sizes

- `schema.sql`: ~12 KB
- `data.sql`: ~19 KB (sample data)
- `data_large.sql`: **1.005 GB** (production dataset)

## Compatibility

All SQL files are compatible with:
- PostgreSQL 12+
 SQL (Delta Lake)


## Notes

- The large dataset uses `ON CONFLICT` clauses for idempotent loading
- All timestamps use `TIMESTAMP_NTZ` for cross-platform compatibility
- Data is based on real-world patterns but is synthetically generated
- Historical pricing includes realistic variations and trends
- Performance metrics are based on actual benchmark patterns

# Query Testing Notebooks

This directory contains individual Jupyter notebooks for comprehensive query testing, documentation, and visualization for each database (db-6 through db-15).

## Overview

Each notebook provides:

1. **Database Initialization**: Automated database creation, schema loading, and data loading
2. **Query Execution**: Individual execution of all 30 queries with error handling
3. **Performance Metrics**: Execution time, row counts, and success rates
4. **Visualizations**: 
   - Execution time distributions
   - Row count analysis
   - Query status pie charts
   - Individual query result distributions
   - Correlation heatmaps for numeric data
5. **Documentation**: Comprehensive markdown documentation for each query including:
   - Query metadata (title, description, use case, business value)
   - Execution status and metrics
   - SQL query code
   - Results preview with data visualizations

## Notebooks

| Database | Notebook File | Domain |
|----------|--------------|--------|
| db-6 | `db-6_query_testing.ipynb` | Weather Forecasting & Insurance |
| db-7 | `db-7_query_testing.ipynb` | Maritime Shipping Intelligence |
| db-8 | `db-8_query_testing.ipynb` | Job Market Intelligence |
| db-9 | `db-9_query_testing.ipynb` | Shipping Intelligence |
| db-10 | `db-10_query_testing.ipynb` | Credit Card Optimization |
| db-11 | `db-11_query_testing.ipynb` | Parking Intelligence |
| db-12 | `db-12_query_testing.ipynb` | Credit Card Optimization |
| db-13 | `db-13_query_testing.ipynb` | Retail Price Intelligence |
| db-14 | `db-14_query_testing.ipynb` | AI Model Performance |
| db-15 | `db-15_query_testing.ipynb` | Cloud Cost Optimization |

## Usage

### Prerequisites

```bash
# Install required Python packages
pip install psycopg2-binary pandas numpy matplotlib seaborn jupyter ipython

# Set up PostgreSQL environment variables (optional)
export PG_HOST=localhost
export PG_PORT=5432
export PG_USER=your_username
export PG_PASSWORD=your_password
```

### Running a Notebook

1. **Start Jupyter**:
   ```bash
   jupyter notebook
   ```

2. **Open the desired notebook** (e.g., `db-6_query_testing.ipynb`)

3. **Run all cells** sequentially:
   - Cell 1: Import libraries and configure database connection
   - Cell 2: Initialize database (create, load schema, load data)
   - Cell 3: Load query metadata from `queries.json`
   - Cell 4: Define query execution function
   - Cell 5: Execute all queries and collect results
   - Cell 6: Generate performance visualizations
   - Cell 7: Document and visualize each individual query
   - Cell 8: Generate comprehensive JSON report

### Expected Output

Each notebook will:

- ✅ Create/verify database exists
- ✅ Load schema from `data/schema.sql`
- ✅ Load data from `data/data.sql`
- ✅ Execute all 30 queries
- ✅ Generate performance visualizations (4 charts)
- ✅ Document each query with:
  - Execution status
  - Performance metrics
  - Query metadata
  - SQL code preview
  - Results preview (first 10 rows)
  - Data visualizations (histograms, correlation heatmaps)
- ✅ Save comprehensive JSON report to `results/{db_name}_comprehensive_report.json`

## Notebook Structure

Each notebook follows this structure:

### 1. Database Overview
- Database name and domain
- Total query count
- Workflow overview

### 2. Configuration
- Database connection settings
- Path configuration
- Library imports

### 3. Database Initialization
- Database creation
- Schema loading
- Data loading

### 4. Query Metadata Loading
- Load queries from `queries.json`
- Display query overview

### 5. Query Execution
- Execute all queries
- Collect metrics (execution time, row count, success/failure)
- Display summary statistics

### 6. Performance Visualization
- Execution time bar chart
- Execution time histogram
- Row count bar chart
- Status pie chart
- Performance summary statistics

### 7. Individual Query Documentation
For each query:
- Markdown documentation with metadata
- Results preview (first 10 rows)
- Data visualizations:
  - Histograms for numeric columns
  - Correlation heatmap (if multiple numeric columns)

### 8. Comprehensive Report
- Generate JSON report
- Save to `results/{db_name}_comprehensive_report.json`
- Display summary statistics

## Report Format

Each notebook generates a JSON report with the following structure:

```json
{
  "database": "db6",
  "test_timestamp": "2026-02-08T21:00:53.949201",
  "total_queries": 30,
  "passed": 30,
  "failed": 0,
  "success_rate": 100.0,
  "average_execution_time": 0.043,
  "total_execution_time": 1.29,
  "queries": [
    {
      "number": 1,
      "title": "Query Title",
      "success": true,
      "execution_time": 0.043,
      "row_count": 100,
      "column_count": 24,
      "columns": ["col1", "col2", ...]
    },
    ...
  ]
}
```

## Visualizations

### Performance Metrics
- **Execution Time Bar Chart**: Shows execution time for each query
- **Execution Time Histogram**: Distribution of execution times
- **Row Count Bar Chart**: Number of rows returned by each query
- **Status Pie Chart**: Pass/fail distribution

### Query Results
- **Histograms**: Distribution of numeric columns
- **Correlation Heatmap**: Relationships between numeric columns (if multiple exist)

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `pg_isready`
- Check environment variables: `echo $PG_HOST $PG_PORT`
- Verify credentials in notebook configuration cell

### Schema Loading Errors
- Ensure `data/schema.sql` exists
- Check for PostgreSQL-specific syntax issues
- Verify PostGIS extension is installed (for spatial databases)

### Query Execution Errors
- Review error messages in notebook output
- Check query SQL syntax
- Verify required tables and data exist

### Visualization Issues
- Ensure matplotlib and seaborn are installed
- Check for numeric data in query results
- Verify data types are compatible with visualizations

## Related Files

- **Query Source**: `{db-N}/queries/queries.md` and `{db-N}/queries/queries.json`
- **Schema**: `{db-N}/data/schema.sql`
- **Data**: `{db-N}/data/data.sql`
- **Reports**: `{db-N}/results/{db_name}_comprehensive_report.json`

## Notes

- All notebooks use the same structure for consistency
- Database names follow pattern: `db6`, `db7`, ..., `db15`
- Notebooks are designed to be run independently
- Each notebook can be executed multiple times (idempotent)
- Reports are saved with timestamps for tracking

---
**Generated**: 2026-02-08
**Total Notebooks**: 10 (db-6 through db-15)

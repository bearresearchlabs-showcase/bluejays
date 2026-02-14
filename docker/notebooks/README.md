# Streamlit Dashboards for Database Query Analysis

## Overview

This directory contains interactive Streamlit dashboards for each database (db-6 through db-15). Each dashboard provides:

- **Interactive Query Execution**: Execute any of the 30 queries with real-time results
- **Data Visualization**: Automatic visualizations for numeric data (histograms, box plots, correlation matrices)
- **Performance Metrics**: Execution time, row counts, memory usage
- **Data Export**: Download results as CSV, JSON, or Excel
- **Environment Detection**: Automatically detects Docker, Google Colab, or local environment
- **Recursive File Finding**: Finds queries.json and database files from any location

## Dashboard Files

- `db-6_dashboard.py` - Weather Forecasting & Insurance Database
- `db-7_dashboard.py` - Maritime Shipping Intelligence Database
- `db-8_dashboard.py` - Job Market Intelligence Database
- `db-9_dashboard.py` - Shipping Database
- `db-10_dashboard.py` - Shopping Aggregator Database
- `db-11_dashboard.py` - Parking Intelligence Database
- `db-12_dashboard.py` - Credit Card & Rewards Optimization Database
- `db-13_dashboard.py` - AI Benchmark Marketing Database
- `db-14_dashboard.py` - Cloud Instance Cost Database
- `db-15_dashboard.py` - Electricity Cost & Solar Rebate Database

## Running Dashboards

### In Docker Containers

**Start all dashboards:**
```bash
./scripts/run_streamlit_dashboards.sh
```

**Start specific dashboard:**
```bash
./scripts/run_streamlit_dashboards.sh db-6
```

**Access dashboards:**
- db-6: http://localhost:8506
- db-7: http://localhost:8507
- db-8: http://localhost:8508
- db-9: http://localhost:8509
- db-10: http://localhost:8510
- db-11: http://localhost:8511
- db-12: http://localhost:8512
- db-13: http://localhost:8513
- db-14: http://localhost:8514
- db-15: http://localhost:8515

**Manual execution in container:**
```bash
docker exec db-6-container streamlit run \
    /workspace/docker/notebooks/db-6_dashboard.py \
    --server.port=8501 \
    --server.address=0.0.0.0
```

### Locally (Outside Docker)

**Prerequisites:**
```bash
pip install streamlit plotly openpyxl psycopg2-binary pandas numpy
```

**Run dashboard:**
```bash
streamlit run docker/notebooks/db-6_dashboard.py
```

**Access:** http://localhost:8501

### In Google Colab

1. Upload dashboard file to Colab
2. Install dependencies:
   ```python
   !pip install streamlit plotly openpyxl psycopg2-binary pandas numpy
   ```
3. Set PostgreSQL environment variables
4. Run:
   ```python
   !streamlit run db-6_dashboard.py --server.port=8501
   ```

## Testing Dashboards

**Test all dashboards:**
```bash
./scripts/test_streamlit_dashboards.sh
```

This script:
- Verifies containers are running
- Checks PostgreSQL connectivity
- Validates dashboard file existence
- Tests Streamlit and Plotly installation
- Validates dashboard syntax
- Tests dashboard imports

## Dashboard Features

### Query Selection
- Dropdown selector for all 30 queries
- Query metadata display (description, use case, business value)
- SQL query preview with syntax highlighting

### Query Execution
- One-click query execution
- Real-time execution metrics
- Row and column counts
- Execution time tracking
- Memory usage monitoring

### Visualizations
- **Automatic Distribution Plots**: Histograms for numeric columns
- **Box Plots**: Statistical summaries
- **Correlation Matrices**: Heatmaps for multi-column analysis
- **Time Series**: Line charts for temporal data
- **Interactive Charts**: Plotly-powered interactive visualizations

### Data Export
- **CSV Export**: Download results as CSV
- **JSON Export**: Download results as JSON
- **Excel Export**: Download results as Excel (requires openpyxl)

### Environment Detection
- Automatically detects Docker, Google Colab, or local environment
- Configures database connections based on environment
- Recursive file finding for queries.json and database files

## Dashboard Structure

Each dashboard includes:

1. **Header**: Database name and domain
2. **Sidebar**:
   - Environment information
   - Database connection status
   - Statistics (total queries)
   - Query selector
   - Execution options
3. **Main Content**:
   - Query information and metadata
   - SQL query display
   - Execution button
   - Results display
   - Visualizations
   - Export options
4. **Query List**: Expandable list of all queries

## Configuration

### Environment Variables

Dashboards respect these environment variables:

- `PG_HOST`: PostgreSQL host (default: `localhost`)
- `PG_PORT`: PostgreSQL port (default: `5432`)
- `PG_USER`: PostgreSQL user (default: `postgres` for Docker, `$USER` for local)
- `PG_PASSWORD`: PostgreSQL password (default: `postgres` for Docker, empty for local)

### Docker Configuration

Streamlit ports are configured in `docker/docker-compose.yml`:
- db-6: 8506
- db-7: 8507
- db-8: 8508
- db-9: 8509
- db-10: 8510
- db-11: 8511
- db-12: 8512
- db-13: 8513
- db-14: 8514
- db-15: 8515

## Troubleshooting

### Dashboard Not Loading

1. **Check container is running:**
   ```bash
   docker ps | grep db-6-container
   ```

2. **Check Streamlit is installed:**
   ```bash
   docker exec db-6-container pip list | grep streamlit
   ```

3. **Check dashboard file exists:**
   ```bash
   docker exec db-6-container ls -la /workspace/docker/notebooks/
   ```

4. **View Streamlit logs:**
   ```bash
   docker logs db-6-container | grep streamlit
   ```

### Database Connection Failed

1. **Check PostgreSQL is running:**
   ```bash
   docker exec db-6-container su - postgres -c "psql -c 'SELECT 1'"
   ```

2. **Check environment variables:**
   ```bash
   docker exec db-6-container env | grep PG_
   ```

3. **Test connection manually:**
   ```bash
   docker exec db-6-container python3 -c "
   import psycopg2
   conn = psycopg2.connect(
       host='localhost',
       port=5432,
       user='postgres',
       password='postgres',
       database='db6'
   )
   print('Connection successful')
   "
   ```

### Queries Not Found

1. **Check queries.json exists:**
   ```bash
   docker exec db-6-container find /workspace -name queries.json
   ```

2. **Verify file paths:**
   The dashboard uses recursive file finding, so queries.json should be found automatically.

## Development

### Creating New Dashboards

Use the generator script:
```bash
python3 scripts/create_streamlit_dashboards.py
```

### Updating Dashboards

Dashboards are generated from `queries.json` files. To update:
1. Update `queries.json` in the database directory
2. Regenerate dashboard:
   ```bash
   python3 scripts/create_streamlit_dashboards.py
   ```

### Customizing Dashboards

Each dashboard is a standalone Python file. You can customize:
- Visualizations (add new chart types)
- Layout (modify Streamlit components)
- Features (add new functionality)
- Styling (modify CSS)

## Related Files

- `scripts/create_streamlit_dashboards.py` - Dashboard generator
- `scripts/test_streamlit_dashboards.sh` - Dashboard testing script
- `scripts/run_streamlit_dashboards.sh` - Dashboard execution script
- `docker/docker-compose.yml` - Docker configuration with Streamlit ports
- `docker/Dockerfile.template` - Dockerfile template with Streamlit

## Port Mapping

| Database | Jupyter Port | PostgreSQL Port | Streamlit Port |
|----------|--------------|-----------------|----------------|
| db-6     | 8886         | 5436            | 8506           |
| db-7     | 8887         | 5437            | 8507           |
| db-8     | 8888         | 5438            | 8508           |
| db-9     | 8889         | 5439            | 8509           |
| db-10    | 8890         | 5440            | 8510           |
| db-11    | 8891         | 5441            | 8511           |
| db-12    | 8892         | 5442            | 8512           |
| db-13    | 8893         | 5443            | 8513           |
| db-14    | 8894         | 5444            | 8514           |
| db-15    | 8895         | 5445            | 8515           |

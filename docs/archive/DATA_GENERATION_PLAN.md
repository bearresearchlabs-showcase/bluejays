# Data Generation Plan - 1GB+ Datasets

## Status

**Databases with sufficient data (≥1GB):**
- ✅ db-9: 4.46 GB (shipping database)
- ✅ db-14: 1.01 GB (cloud instance cost database)

**Databases needing data generation:**
- ⚠️ db-6: Weather/Insurance database - needs NOAA/NWS data
- ⚠️ db-7: Maritime Shipping database - needs NOAA/USCG/MARAD data
- ⚠️ db-8: Job Market database - needs BLS/ONET data
- ⚠️ db-10: Shopping Aggregator database - needs product/price data
- ⚠️ db-11: Parking Intelligence database - needs parking/transportation data
- ⚠️ db-12: Credit Card/Rewards database - needs financial/transaction data
- ⚠️ db-13: AI Benchmark Marketing database - needs marketing/performance data
- ⚠️ db-15: Electricity/Solar Rebate database - needs energy/utility data

## Approach

Each database needs a `generate_large_dataset.py` script that:

1. **Identifies legitimate data sources** for the domain
2. **Extracts or generates** at least 1GB of realistic data
3. **Transforms** data to match the database schema
4. **Generates SQL INSERT statements** in `data_large.sql`
5. **Copies** to web-deployable folder

## Legitimate Data Sources by Domain

### db-6: Weather/Insurance
- **NOAA NWS API**: Weather forecasts, observations
- **Data.gov**: Weather datasets
- **GeoPlatform.gov**: Geospatial weather data
- **NEXRAD**: Radar data (if available)

### db-7: Maritime Shipping
- **NOAA**: Maritime data
- **US Coast Guard**: Vessel tracking, port data
- **MARAD**: Maritime Administration data
- **Data.gov**: Shipping/maritime datasets

### db-8: Job Market
- **BLS API**: Bureau of Labor Statistics
- **ONET**: Occupational Information Network
- **Data.gov**: Employment datasets
- **Indeed API**: Job listings (if available)

### db-10: Shopping Aggregator
- **Data.gov**: Product/price datasets
- **Open Product Data**: Open product databases
- **Retail APIs**: Public product APIs

### db-11: Parking Intelligence
- **Data.gov**: Transportation/parking datasets
- **OpenStreetMap**: Parking location data
- **City APIs**: Municipal parking APIs

### db-12: Credit Card/Rewards
- **Federal Reserve**: Financial data
- **Data.gov**: Financial datasets
- **Synthetic generation**: Realistic transaction patterns

### db-13: AI Benchmark Marketing
- **Data.gov**: Marketing/advertising datasets
- **Public APIs**: Marketing performance data
- **Synthetic generation**: Realistic marketing metrics

### db-15: Electricity/Solar Rebate
- **EIA**: Energy Information Administration
- **Data.gov**: Energy/utility datasets
- **State APIs**: Solar rebate program data

## Implementation Pattern

Each `generate_large_dataset.py` script follows this pattern:

```python
#!/usr/bin/env python3
"""
Generate Large Dataset Script for db-{N} {Database Name}
Generates at least 1 GB of realistic data from legitimate sources.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import random
import uuid

# Target: At least 1 GB of SQL data
TARGET_SIZE_GB = 1.0
TARGET_SIZE_BYTES = TARGET_SIZE_GB * 1024 * 1024 * 1024

def generate_data_sql(target_bytes: int) -> List[str]:
    """Generate SQL INSERT statements to reach target size"""
    sql = []
    current_size = 0
    
    # Generate data until reaching target size
    # Use legitimate sources and realistic patterns
    
    return sql

def main():
    """Main generation function"""
    all_sql = generate_data_sql(TARGET_SIZE_BYTES)
    
    # Write to data_large.sql
    output_file = DATA_DIR / 'data_large.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"-- Large Dataset for {DATABASE_NAME}\n")
        f.write(f"-- Rebuilt: {datetime.now().isoformat()}\n")
        f.write(f"-- Target size: {TARGET_SIZE_GB} GB\n")
        f.write(f"-- Total SQL statements: {len(all_sql):,}\n")
        f.write("-- Compatible with PostgreSQL\n\n")
        
        for sql in all_sql:
            f.write(sql + "\n\n")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
```

## Next Steps

1. Create `generate_large_dataset.py` for each database
2. Run scripts to generate data_large.sql files
3. Copy to web-deployable folders
4. Verify all databases have ≥1GB of data

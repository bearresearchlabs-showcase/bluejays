# Data Extraction Guide - 1 GB Shipping Intelligence Data

This guide explains how to extract 1 GB of shipping intelligence data from internet sources.

## Quick Start

```bash
cd db-9
python3 scripts/extract_large_datasets.py
python3 scripts/transform_large_datasets.py
```

## Data Sources and Expected Volumes

### 1. Census Bureau TIGER/Line ZCTA Files (500 MB - 2 GB)
- **Source**: https://www2.census.gov/geo/tiger/
- **Files**: `tl_YYYY_us_zcta510.zip` (one per year)
- **Size**: ~100-500 MB per year
- **Years**: 2022-2024 (3 files = 300 MB - 1.5 GB)
- **Status**: ✅ Working URLs (automatically downloaded)

### 2. Census Bureau SPI Databank via Data.gov (5-15 GB)
- **Source**: Data.gov (search for Census Bureau trade datasets)
- **Content**: Import data with HTSUSA codes, customs values
- **Size**: Varies by dataset (100 MB - 2 GB per dataset)
- **Status**: ⚠️ Requires Data.gov API search (may need manual URL discovery)

### 3. Data.gov Shipping/Postal Datasets (1-5 GB)
- **Source**: https://catalog.data.gov
- **Search Terms**: 'usps', 'shipping', 'postal', 'logistics'
- **Size**: Varies (10 MB - 500 MB per dataset)
- **Status**: ✅ Automated search and download

### 4. Postal Service Datasets (500 MB - 2 GB)
- **Source**: Data.gov, various postal data portals
- **Content**: Address validation, postal service data
- **Size**: Varies (10 MB - 200 MB per dataset)
- **Status**: ✅ Automated search and download

## Expected Total Volume

- **Target**: 1 GB (with current year TIGER files + recent Census SPI + limited Data.gov datasets)
- **Components**:
  - Census TIGER ZCTA (current year): ~100-500 MB
  - Census SPI (last 2 years): ~200-400 MB
  - Data.gov datasets (limited): ~200-300 MB
  - Postal datasets (limited): ~100-200 MB

## Manual Data Discovery

If automated downloads don't reach 2 GB, you can manually discover datasets:

### Census Bureau SPI Databank
1. Visit: https://www.census.gov/foreign-trade/data/SPIM.html
2. Download annual/monthly import files
3. Place in `data/raw_datasets/census_spi/`

### Data.gov Large Datasets
1. Visit: https://catalog.data.gov
2. Search for: 'census bureau foreign trade', 'import data', 'HTSUSA'
3. Filter by size (large datasets)
4. Download and place in appropriate directories

## Troubleshooting

### 404 Errors
- Some URLs may not exist - script will skip and continue
- Use Data.gov API search to find actual dataset URLs
- Check Census Bureau website for current file locations

### Rate Limiting
- Script includes delays between requests
- Data.gov API key increases rate limits (optional but recommended)
- Get API key: https://api.data.gov/signup/

### Disk Space
- Ensure at least 50 GB free space
- Raw datasets: 2-30 GB
- Transformed datasets: 1-15 GB
- Total: ~50 GB recommended

## Verification

After extraction, check download summary:

```bash
cat data/raw_datasets/download_summary.json
```

Look for:
- `total_size_gb`: Should be >= 2 GB
- `status`: Should be "SUCCESS" if >= 2 GB

## Next Steps

After extraction:
1. Transform datasets: `python3 scripts/transform_large_datasets.py`
2. Load to database: Configure `POSTGRES_CONNECTION_STRING` and run transformation script
3. Verify data: Check `data/transformed_datasets/` for CSV files

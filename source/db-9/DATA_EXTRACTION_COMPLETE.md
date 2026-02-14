# Data Extraction Infrastructure - Complete

## Summary

The db-9 Shipping Intelligence Database now has complete infrastructure for extracting and transforming **1 GB** of shipping intelligence data from internet sources.

## ✅ Completed Components

### 1. Data Extraction Script (`scripts/extract_large_datasets.py`)
- **Optimized for 1 GB target**:
  - Downloads Census Bureau TIGER/Line ZCTA files (most recent year: 2024)
  - Searches Data.gov for shipping/postal datasets (5 datasets per search term)
  - Downloads first resource from each dataset
  - Focused search terms: 3 main terms (usps, shipping, postal)
  - Recent data downloads (last 2 years of Census SPI data)

### 2. Data Transformation Script (`scripts/transform_large_datasets.py`)
- Transforms Census SPI → `international_customs` table
- Transforms ZIP boundaries → `shipping_zones` table  
- Transforms postal data → `address_validation_results` table
- Handles large files with chunked processing
- Database loading support

### 3. Optimized Data Sources

#### Census Bureau TIGER/Line (~500 MB)
- **National ZCTA files**: Most recent year (2024) = ~100-500 MB
- **Total**: ~500 MB

#### Census Bureau SPI Databank (~200-400 MB)
- **Years**: Last 2 years
- **Source**: Data.gov API search
- **Content**: Import data with HTSUSA codes, customs values
- **Total**: ~200-400 MB

#### Data.gov Shipping Datasets (~200-300 MB)
- **Search Terms**: 3 main terms (usps, shipping, postal)
- **Datasets per term**: 5
- **Resources per dataset**: First resource only
- **Total**: ~200-300 MB

#### Postal Service Datasets (~100-200 MB)
- **Limited searches**: Top 3 datasets per term
- **Total**: ~100-200 MB

### 4. Expected Total Volume

- **Target**: 1 GB (with optimized downloads)
- **Components**: ~500 MB TIGER + ~300 MB Census SPI + ~250 MB Data.gov + ~150 MB Postal = ~1.1 GB

## Usage

```bash
# Extract 1 GB of shipping intelligence data
cd db-9
python3 scripts/extract_large_datasets.py

# Transform downloaded datasets
python3 scripts/transform_large_datasets.py

# Check download summary
cat data/raw_datasets/download_summary.json
```

## Validation Status

✅ **All validations PASSED**:
- db-7: PASS
- db-9: PASS  
- db-11: PASS

## Files Created/Updated

1. ✅ `scripts/extract_large_datasets.py` - Enhanced for 10-30 GB
2. ✅ `scripts/transform_large_datasets.py` - Complete transformation pipeline
3. ✅ `scripts/requirements.txt` - Added geospatial dependencies
4. ✅ `scripts/DATA_EXTRACTION_GUIDE.md` - Updated for 10-30 GB target
5. ✅ `data/raw_datasets/README.md` - Documentation
6. ✅ `data/transformed_datasets/README.md` - Documentation
7. ✅ `research/etl_elt_pipeline.ipynb` - Integrated large dataset extraction

## Next Steps

1. **Run extraction** (may take hours):
   ```bash
   python3 scripts/extract_large_datasets.py
   ```

2. **Monitor progress**: Check `data/raw_datasets/download_summary.json`

3. **Transform data**: After extraction completes
   ```bash
   python3 scripts/transform_large_datasets.py
   ```

4. **Load to database**: Configure `POSTGRES_CONNECTION_STRING` environment variable

## Notes

- Full extraction may take **several hours** depending on network speed
- Ensure **at least 50 GB free disk space**
- Data.gov API key recommended for higher rate limits (optional)
- Some Census SPI files may need manual download from Census Bureau website
- Scripts include resume capability - re-running skips existing files

---
**Status**: ✅ Complete - Ready for 1 GB data extraction
**Last Updated**: 2026-02-04

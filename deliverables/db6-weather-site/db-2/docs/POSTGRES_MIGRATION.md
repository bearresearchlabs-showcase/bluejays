# PostgreSQL & Databricks Migration Guide

This document provides detailed instructions for migrating the Lucasa MySQL database to PostgreSQL.

## Overview

The database is provided in MySQL format (`database/full_dump.sql`). While this is production-ready for MySQL/MariaDB, migrating to PostgreSQL requires data type conversion and syntax adaptation.

**Recommended Approach**: Use **pgloader** - it's specifically designed for MySQL to PostgreSQL migrations and handles all edge cases automatically.

---

## Option 1: pgloader (Recommended)

pgloader is the industry-standard tool for MySQL → PostgreSQL migrations. It handles:
- Data type conversions (tinyint → boolean/smallint, BLOB → bytea)
- Character encoding
- Index creation
- Foreign keys
- All MySQL-specific syntax

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install pgloader

# macOS
brew install pgloader

# Or use Docker
docker pull dimitri/pgloader
```

### Method A: Direct Database-to-Database Migration

**Step 1**: Import into MySQL first
```bash
# Start MySQL container
docker run --name mysql-lucasa \
  -e MYSQL_ROOT_PASSWORD=yourpass \
  -e MYSQL_DATABASE=lucasa \
  -d -p 3306:3306 mysql:8.0

# Wait for MySQL to start
sleep 20

# Import the dump
docker exec -i mysql-lucasa mysql -uroot -pyourpass lucasa < database/full_dump.sql
```

**Step 2**: Start PostgreSQL
```bash
docker run --name postgres-lucasa \
  -e POSTGRES_PASSWORD=yourpass \
  -e POSTGRES_DB=lucasa \
  -d -p 5432:5432 postgres:16
```

**Step 3**: Run pgloader
```bash
pgloader mysql://root:yourpass@localhost:3306/lucasa \
         postgresql://postgres:yourpass@localhost:5432/lucasa
```

### Method B: Using pgloader Configuration File

Create `lucasa_migration.load`:
```lisp
LOAD DATABASE
     FROM mysql://root:yourpass@localhost:3306/lucasa
     INTO postgresql://postgres:yourpass@localhost:5432/lucasa

 WITH include drop, create tables, create indexes, reset sequences

  SET maintenance_work_mem to '512MB',
      work_mem to '256MB'

 CAST type tinyint(1) to boolean drop typemod,
      type tinyint to smallint drop typemod,
      type int unsigned to integer drop typemod,
      type bigint unsigned to bigint drop typemod;
```

Run:
```bash
pgloader lucasa_migration.load
```

### Expected Results

```
table name     errors       rows      bytes      total time
------------------------------------------------------------
phppos_admin_otp      0          0                     0.05s
phppos_sales          0     312247                    45.2s
phppos_sales_items    0     706543                   180.5s
...
TOTAL                 0    2346975                   420.8s
```

---

## Option 2: Manual SQL Conversion (Advanced)

If you cannot use pgloader, here's a manual conversion guide.

### Step 1: Extract Schema and Data

```bash
# From the MySQL dump, separate schema and data
grep -E "^(CREATE TABLE|ALTER TABLE)" database/full_dump.sql > schema.sql
grep -E "^INSERT INTO" database/full_dump.sql > data.sql
```

### Step 2: Convert Data Types

Create a conversion script:

```python
#!/usr/bin/env python3
import re

with open('schema.sql', 'r') as f:
    schema = f.read()

# Data type conversions
schema = re.sub(r'tinyint\(1\)', 'boolean', schema)
schema = re.sub(r'tinyint\(\d+\)', 'smallint', schema)
schema = re.sub(r'int\(\d+\)', 'integer', schema)
schema = re.sub(r'int unsigned', 'integer', schema)
schema = re.sub(r'bigint\(\d+\)', 'bigint', schema)
schema = re.sub(r'longblob', 'bytea', schema)

# Remove MySQL-specific syntax
schema = schema.replace('`', '')
schema = re.sub(r' ENGINE=\w+', '', schema)
schema = re.sub(r' DEFAULT CHARSET=\w+', '', schema)
schema = re.sub(r' COLLATE=\w+', '', schema)
schema = re.sub(r' AUTO_INCREMENT=\d+', '', schema)

with open('schema_pg.sql', 'w') as f:
    f.write(schema)
```

### Step 3: Import

```bash
# Import schema
psql -U postgres -d lucasa -f schema_pg.sql

# Import data (may need additional fixes)
psql -U postgres -d lucasa -f data.sql
```

### Common Issues & Fixes

1. **Boolean values**: Convert `0/1` to `false/true` in INSERT statements
2. **Timestamps**: Replace `'0000-00-00 00:00:00'` with `NULL`
3. **BLOB data**: Convert hex format `0xABCD` to `E'\\xABCD'`
4. **Character encoding**: Ensure UTF-8 encoding

---

## Option 3: Databricks Migration

### Method A: Via PostgreSQL (Recommended)

1. Migrate to PostgreSQL using pgloader (see Option 1)
2. Use Databricks's native PostgreSQL connector:

```sql
-- In Databricks
CREATE DATABASE lucasa;
CREATE SCHEMA lucasa.public;

-- Use Snowpipe or COPY INTO from PostgreSQL export
```

### Method B: Direct CSV Import

1. Export MySQL tables to CSV:
```bash
mysql -uroot -p lucasa -e "SELECT * FROM phppos_sales" \
  --batch --skip-column-names > sales.csv
```

2. Import to Databricks:
```sql
PUT file://sales.csv @lucasa.public.%phppos_sales;
COPY INTO phppos_sales FROM @lucasa.public.%phppos_sales
FILE_FORMAT = (TYPE = CSV FIELD_OPTIONALLY_ENCLOSED_BY = '"');
```

---

## Option 4: Databricks Migration

### Method A: Via PostgreSQL

1. Migrate to PostgreSQL using pgloader
2. Use Databricks JDBC connector to PostgreSQL
3. Read into Databricks Delta Lake:

```python
# In Databricks notebook
df = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:postgresql://host:5432/lucasa") \
    .option("dbtable", "phppos_sales") \
    .option("user", "postgres") \
    .option("password", "yourpass") \
    .load()

df.write.format("delta").saveAsTable("lucasa.phppos_sales")
```

### Method B: Via Parquet Files

1. Export MySQL to Parquet using pandas:

```python
import pandas as pd
import pymysql

conn = pymysql.connect(host='localhost', user='root',
                       password='pass', database='lucasa')

# For each table
df = pd.read_sql("SELECT * FROM phppos_sales", conn)
df.to_parquet('sales.parquet')
```

2. Upload to Databricks and create Delta tables

---

## Verification Checklist

After migration, verify:

```sql
-- Check table count
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public';
-- Expected: 58 tables

-- Check row counts
SELECT COUNT(*) FROM phppos_sales;
-- Expected: ~312,000

SELECT COUNT(*) FROM phppos_sales_items;
-- Expected: ~706,000

SELECT COUNT(*) FROM phppos_inventory;
-- Expected: ~867,000

-- Check data integrity
SELECT COUNT(*) FROM phppos_sales s
LEFT JOIN phppos_customers c ON s.customer_id = c.person_id
WHERE s.customer_id IS NOT NULL AND c.person_id IS NULL;
-- Expected: 0 (no orphaned records)
```

---

## Performance Optimization

### PostgreSQL

```sql
-- After import, analyze tables
VACUUM ANALYZE;

-- Create indexes (if not created by pgloader)
CREATE INDEX idx_sales_time ON phppos_sales(sale_time);
CREATE INDEX idx_sales_customer ON phppos_sales(customer_id);
CREATE INDEX idx_sales_items_sale ON phppos_sales_items(sale_id);
```

### Databricks

```sql
-- Cluster tables by commonly queried columns
ALTER TABLE phppos_sales CLUSTER BY (sale_time);
ALTER TABLE phppos_sales_items CLUSTER BY (sale_id);
```

---

## Troubleshooting

### "Cannot convert tinyint to boolean"
**Solution**: Use pgloader which handles this automatically, or manually convert in INSERT statements

### "Invalid byte sequence for encoding UTF8"
**Solution**: Ensure source encoding is UTF-8:
```bash
file -bi database/full_dump.sql
# Should show: charset=utf-8
```

### "BLOB data import fails"
**Solution**: pgloader handles BLOB conversion automatically. For manual conversion, use hex format.

---

## Support & Resources

- **pgloader documentation**: https://pgloader.readthedocs.io/
- **PostgreSQL docs**: https://www.postgresql.org/docs/
- **Databricks docs**: https://docs.databricks.com/
- **Databricks docs**: https://docs.databricks.com/

For dataset-specific questions, see `README.md` and `documentation/SCHEMA.md`.

---

**Recommendation**: We strongly recommend using **pgloader** (Option 1) for PostgreSQL migrations. It's battle-tested, handles all edge cases, and completes the migration in minutes with zero data loss.

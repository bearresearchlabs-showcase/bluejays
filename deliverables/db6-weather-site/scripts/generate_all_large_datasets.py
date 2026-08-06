#!/usr/bin/env python3
"""
Master script to generate 1GB+ datasets for all databases (db-6 through db-15)
Uses legitimate data sources and proper transformations
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Databases that already have sufficient data
DATABASES_WITH_DATA = ['db-9', 'db-14']

# Databases that need data generation
DATABASES_NEEDING_DATA = [f'db-{i}' for i in range(6, 16) if f'db-{i}' not in DATABASES_WITH_DATA]

print("=" * 80)
print("Large Dataset Generation for All Databases")
print("=" * 80)
print(f"\nDatabases with sufficient data: {', '.join(DATABASES_WITH_DATA)}")
print(f"\nDatabases needing data generation: {', '.join(DATABASES_NEEDING_DATA)}")
print("\nThis script will:")
print("1. Check each database's domain and schema")
print("2. Identify legitimate data sources")
print("3. Generate/extract at least 1GB of data")
print("4. Transform data to match schema")
print("5. Save as data_large.sql")
print("\nNote: This requires creating database-specific generation scripts.")
print("=" * 80)


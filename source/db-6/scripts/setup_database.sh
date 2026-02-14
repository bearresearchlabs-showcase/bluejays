#!/bin/bash
# Setup script for db-6 weather data pipeline database
# Compatible with PostgreSQL

set -e

DB_NAME="${DB_NAME:-weather_pipeline_db}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

echo "Setting up db-6 weather data pipeline database..."

# PostgreSQL setup
if command -v psql &> /dev/null; then
    echo "Creating PostgreSQL database..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -c "CREATE DATABASE IF NOT EXISTS $DB_NAME;" || true

    echo "Loading schema..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f data/schema.sql

    echo "Loading sample data..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f data/data.sql

    echo "PostgreSQL setup complete!"
else
    echo "PostgreSQL not found. Skipping PostgreSQL setup."
fi

echo "Database setup complete!"

#!/bin/bash
# Setup script for db-7 maritime shipping intelligence database
# Compatible with PostgreSQL (with PostGIS)

set -e

DB_NAME="${DB_NAME:-db7}"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_PASSWORD="${DB_PASSWORD:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Setting up db-7 maritime shipping intelligence database..."

# PostgreSQL setup
if command -v psql &> /dev/null; then
    echo "Creating PostgreSQL database..."
    
    # Set PGPASSWORD if provided
    if [ -n "$DB_PASSWORD" ]; then
        export PGPASSWORD="$DB_PASSWORD"
    fi
    
    # Create database if it doesn't exist
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database $DB_NAME already exists or creation failed"
    
    echo "Enabling PostGIS extension..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS postgis;" || {
        echo "Warning: PostGIS extension creation failed. Continuing anyway..."
    }
    
    echo "Verifying PostGIS extension..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT PostGIS_version();" || {
        echo "Warning: PostGIS verification failed. GEOGRAPHY columns may not work."
    }
    
    echo "Loading schema..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$PROJECT_DIR/data/schema.sql" || {
        echo "Error: Schema loading failed"
        exit 1
    }
    
    echo "Loading sample data..."
    if [ -f "$PROJECT_DIR/data/data.sql" ]; then
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$PROJECT_DIR/data/data.sql" || {
            echo "Warning: Data loading failed. Continuing anyway..."
        }
    else
        echo "Warning: data/data.sql not found. Skipping data loading."
    fi
    
    echo "PostgreSQL setup complete!"
    echo "Database: $DB_NAME"
    echo "Host: $DB_HOST:$DB_PORT"
    echo "User: $DB_USER"
else
    echo "PostgreSQL (psql) not found. Skipping PostgreSQL setup."
    echo "Install PostgreSQL: brew install postgresql@14"
    exit 1
fi

echo "Database setup complete!"

#!/bin/bash
set -e

# Function to start PostgreSQL
start_postgres() {
    echo "Initializing PostgreSQL..."
    
    # Initialize data directory if it doesn't exist or is empty
    if [ ! -d "/var/lib/postgresql/data" ] || [ -z "$(ls -A /var/lib/postgresql/data 2>/dev/null)" ]; then
        echo "Initializing PostgreSQL data directory..."
        su - postgres -c "/usr/lib/postgresql/*/bin/initdb -D /var/lib/postgresql/data"
        
        # Configure PostgreSQL to accept connections
        echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf
        echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf
    fi
    
    # Start PostgreSQL
    echo "Starting PostgreSQL server..."
    su - postgres -c "/usr/lib/postgresql/*/bin/pg_ctl -D /var/lib/postgresql/data -l /var/lib/postgresql/data/logfile start" || true
    
    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..60}; do
        if su - postgres -c "psql -c 'SELECT 1'" > /dev/null 2>&1; then
            echo "✅ PostgreSQL is ready!"
            break
        fi
        if [ $i -eq 60 ]; then
            echo "❌ PostgreSQL failed to start after 60 seconds"
            exit 1
        fi
        echo "   Waiting... ($i/60)"
        sleep 1
    done
    
    # Set password
    echo "Setting PostgreSQL password..."
    su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""
}

# Start PostgreSQL in background
start_postgres &

# Wait a moment for PostgreSQL to fully start
sleep 2

# Execute the command passed to the container
exec "$@"

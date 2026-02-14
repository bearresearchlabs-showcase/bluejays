#!/bin/bash
# Add PostgreSQL + pgvector to Vercel project via Neon integration
# Run from repo root: ./scripts/add_vercel_postgres.sh

set -e
cd "$(dirname "$0")/.."

echo "Adding Neon (PostgreSQL + pgvector) to Vercel project..."
echo ""
echo "This will open your browser to complete the setup."
echo "1. Accept terms if prompted"
echo "2. Create/link a Neon database"
echo "3. Link to project 'db'"
echo ""

# Open Neon integration page for this project
# Replace with your team/project if different
open "https://vercel.com/integrations/neon" 2>/dev/null || \
  xdg-open "https://vercel.com/integrations/neon" 2>/dev/null || \
  echo "Open: https://vercel.com/integrations/neon"

# Also run CLI (may prompt in terminal)
vercel integration add neon

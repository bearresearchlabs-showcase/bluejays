#!/bin/bash
# Load .env for Jenkins CI/CD and local testing.
# Ensures ANTHROPIC_API_KEY, PG_*, etc. available for independent parallel sessions.
set -e
if [ -f .env ]; then set -a && . .env && set +a; fi
if [ -f client/.env ]; then set -a && . client/.env && set +a; fi
exec "$@"

#!/bin/bash

# Test watch script for development
# Watches for file changes and runs relevant tests

set -e

echo "👀 Starting test watch mode..."
echo "Press Ctrl+C to stop"

# Run tests in watch mode
npm run test:watch

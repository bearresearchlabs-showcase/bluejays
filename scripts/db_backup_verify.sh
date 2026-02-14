#!/bin/bash
# Verify backup integrity (checksum)
# Usage: ./db_backup_verify.sh <backup_file_or_dir>
# Output: JSON with checksums

set -e
TARGET="${1:-.}"
echo "{"
echo "  \"target\": \"$TARGET\","
echo "  \"sha256\": \"$( (sha256sum -b "$TARGET" 2>/dev/null || shasum -a 256 "$TARGET" 2>/dev/null) | awk '{print $1}' || echo 'N/A')\","
echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\""
echo "}"

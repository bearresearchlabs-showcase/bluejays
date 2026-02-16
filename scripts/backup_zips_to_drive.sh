#!/usr/bin/env bash
# Backup large zip files (client.zip, db.zip, package.zip) to Google Drive
# Usage: ./scripts/backup_zips_to_drive.sh [--dry-run]
#
# Prerequisites:
#   - rclone configured for Google Drive: rclone config
#   - Or: Google Drive Desktop installed (copy to ~/Google Drive/My Drive/)
#
# Drive folder: https://drive.google.com/drive/folders/1bpAoUgegn90qetDYVAoSsAXTIQCIKI1C

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

BACKUP_DIR="$ROOT/backup_archive"
DRIVE_REMOTE="${RCLONE_DRIVE_REMOTE:-gdrive}"
DRIVE_PATH="${RCLONE_DRIVE_PATH:-db-backups}"

ZIPS=(client.zip db.zip package.zip)

echo "=== Backup zip archives to Google Drive ==="
echo "Source: $ROOT"
echo "Backup dir: $BACKUP_DIR"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Copy zips to backup dir (don't move - keep originals until upload verified)
COPIED=0
for z in "${ZIPS[@]}"; do
  if [[ -f "$ROOT/$z" ]]; then
    SIZE=$(du -h "$ROOT/$z" | cut -f1)
    echo "  $z ($SIZE)"
    if $DRY_RUN; then
      echo "    [DRY-RUN] would copy to $BACKUP_DIR/"
    else
      cp -v "$ROOT/$z" "$BACKUP_DIR/" 2>/dev/null || true
      ((COPIED++)) || true
    fi
  else
    echo "  $z - not found (skipped)"
  fi
done

echo ""
echo "=== Upload to Google Drive ==="

if command -v rclone &>/dev/null; then
  echo "Using rclone..."
  if $DRY_RUN; then
    echo "[DRY-RUN] would run: rclone copy $BACKUP_DIR $DRIVE_REMOTE:$DRIVE_PATH --progress"
  else
    rclone copy "$BACKUP_DIR" "$DRIVE_REMOTE:$DRIVE_PATH" \
      --progress \
      --transfers 2 \
      --checkers 4 \
      --drive-chunk-size 64M \
      -v
    echo ""
    echo "✅ Upload complete. Files in Drive: $DRIVE_PATH"
  fi
else
  # Try Google Drive Desktop (macOS)
  DRIVE_HOME=$(ls -d ~/Library/CloudStorage/GoogleDrive-* 2>/dev/null | head -1)
  if [[ -n "$DRIVE_HOME" ]] && [[ -d "$DRIVE_HOME/My Drive" ]]; then
    DEST="$DRIVE_HOME/My Drive/db-backups"
    echo "Using Google Drive Desktop: $DEST"
    if $DRY_RUN; then
      echo "[DRY-RUN] would copy zips to $DEST/"
    else
      mkdir -p "$DEST"
      for z in "${ZIPS[@]}"; do
        [[ -f "$ROOT/$z" ]] && cp -v "$ROOT/$z" "$DEST/"
      done
      echo ""
      echo "✅ Copied to Drive. Files will sync to cloud automatically."
      echo "   Location: $DEST"
    fi
  else
    echo "rclone not found. Manual upload options:"
    echo ""
    echo "1. Google Drive Desktop (recommended for large files):"
    echo "   cp -r $BACKUP_DIR ~/Library/CloudStorage/GoogleDrive-*/My\\ Drive/db-backups/"
    echo "   (or drag $BACKUP_DIR into your Drive folder)"
    echo ""
    echo "2. Install rclone and configure:"
    echo "   brew install rclone"
    echo "   rclone config  # Add Google Drive remote"
    echo "   ./scripts/backup_zips_to_drive.sh"
    echo ""
    echo "3. Web upload (files >5GB may fail):"
    echo "   https://drive.google.com/drive/folders/1bpAoUgegn90qetDYVAoSsAXTIQCIKI1C"
    echo ""
    echo "Backup files ready at: $BACKUP_DIR"
  fi
fi

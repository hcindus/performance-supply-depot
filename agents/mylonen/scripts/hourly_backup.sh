#!/bin/bash
# Mylonen Hourly Backup Script
# Classification: OMEGA-LEVEL
# Date: 2026-02-20 22:58 UTC
# Purpose: Automated hourly encrypted backup of Mylonen workspace

set -euo pipefail

# Configuration
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
DATE=$(date -u +"%Y-%m-%d")
BACKUP_ROOT="/backups/mylonen"
BACKUP_DIR="${BACKUP_ROOT}/hourly/${DATE}"
SOURCE_DIR="/root/.openclaw/workspace/agents/mylonen"
LOG_FILE="${BACKUP_ROOT}/logs/backup_${DATE}.log"
RETENTION_HOURS=48  # Keep 48 hourly backups (2 days)

# Encryption key from environment (set by systemd or cron)
BACKUP_KEY="${MYLONEN_BACKUP_KEY:-mylonen_default_secure_key_2025}"

# Create directories
mkdir -p "$BACKUP_DIR"
mkdir -p "${BACKUP_ROOT}/logs"

# Log function
log() {
    echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] $1" | tee -a "$LOG_FILE"
}

log "=== MYLONEN HOURLY BACKUP STARTING ==="
log "Timestamp: $TIMESTAMP"
log "Source: $SOURCE_DIR"
log "Destination: $BACKUP_DIR"

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    log "ERROR: Source directory does not exist: $SOURCE_DIR"
    exit 1
fi

# Create encrypted backup
BACKUP_FILE="${BACKUP_DIR}/mylonen_${TIMESTAMP}.tar.gz.enc"
log "Creating encrypted backup: $BACKUP_FILE"

# Tar and encrypt in one pipeline (memory efficient)
if tar -czf - -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")" 2>/dev/null | \
   openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 -pass pass:"$BACKUP_KEY" \
   > "$BACKUP_FILE" 2>/dev/null; then
    
    # Calculate file size
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Backup created successfully: $FILE_SIZE"
    
    # Verify backup integrity (try decrypt header)
    if openssl enc -aes-256-cbc -d -pass pass:"$BACKUP_KEY" -in "$BACKUP_FILE" -out /dev/null 2>/dev/null; then
        log "Backup integrity verified"
    else
        log "WARNING: Backup integrity check failed"
        rm -f "$BACKUP_FILE"
        exit 1
    fi
    
    # Create checksum
    sha256sum "$BACKUP_FILE" > "${BACKUP_FILE}.sha256"
    log "Checksum created"
    
else
    log "ERROR: Backup creation failed"
    exit 1
fi

# Cleanup old backups (keep only RETENTION_HOURS most recent)
log "Cleaning up old backups (retaining $RETENTION_HOURS most recent)..."

# Find all .tar.gz.enc files, sort by time, delete older ones
find "$BACKUP_ROOT/hourly" -name "*.tar.gz.enc" -type f -printf '%T@ %p\n' 2>/dev/null | \
    sort -n | \
    head -n -$RETENTION_HOURS | \
    cut -d' ' -f2- | \
    while read -r old_file; do
        log "Removing old backup: $old_file"
        rm -f "$old_file" "${old_file}.sha256" 2>/dev/null || true
    done

# Count remaining backups
REMAINING=$(find "$BACKUP_ROOT/hourly" -name "*.tar.gz.enc" -type f 2>/dev/null | wc -l)
log "Cleanup complete. $REMAINING hourly backups retained."

# Report disk usage
DISK_USAGE=$(du -sh "$BACKUP_ROOT" 2>/dev/null | cut -f1)
log "Total backup storage used: $DISK_USAGE"

log "=== MYLONEN HOURLY BACKUP COMPLETED ==="

# Notify via logger (systemd journal)
logger -t mylonen-backup "Hourly backup completed: ${TIMESTAMP} (${FILE_SIZE})"

# Exit successfully
exit 0

#!/bin/bash
# Mylonen Git Auto-Sync Script
# Classification: OMEGA-LEVEL  
# Date: 2026-02-20 22:58 UTC
# Purpose: Automated Git commits every 2 hours for backup redundancy

set -euo pipefail

# Configuration
WORKSPACE="/root/.openclaw/workspace/agents/mylonen/workspace"
LOG_FILE="/var/log/mylonen/git_sync.log"
LOCK_FILE="/tmp/mylonen_git_sync.lock"

# Ensure workspace exists
if [ ! -d "$WORKSPACE" ]; then
    echo "ERROR: Workspace not found: $WORKSPACE" >&2
    exit 1
fi

# Prevent concurrent runs
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Sync already running (PID: $PID)" >&2
        exit 0
    fi
fi
echo $$ > "$LOCK_FILE"

# Cleanup on exit
cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

# Log function
log() {
    echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] $1" | tee -a "$LOG_FILE"
}

log "=== MYLONEN GIT AUTO-SYNC STARTING ==="

# Change to workspace
cd "$WORKSPACE"

# Check if Git repo initialized
if [ ! -d ".git" ]; then
    log "Initializing Git repository..."
    git init
    git remote add origin https://github.com/hcindus/mylonen-backup.git 2>/dev/null || true
fi

# Configure Git identity if needed
git config user.email "mylonen@myl0nr0s.cloud" 2>/dev/null || true
git config user.name "Mylonen (Auto-Sync)" 2>/dev/null || true

# Check for changes
if git diff --quiet && git diff --cached --quiet; then
    log "No changes to commit"
    logger -t mylonen-git-sync "No changes - sync skipped"
    exit 0
fi

# Stage all changes
git add -A

# Count changes
STAGED=$(git diff --cached --numstat | wc -l)
log "Changes detected: $STAGED files modified"

# Commit with detailed message
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M UTC")
HOSTNAME=$(hostname)

git commit -m "Auto-sync: ${TIMESTAMP}" \
    -m "Source: ${HOSTNAME}" \
    -m "Files changed: ${STAGED}" \
    -m "Type: Automated backup" || {
    log "ERROR: Git commit failed"
    exit 1
}

# Push to remote (if configured)
if git remote get-url origin > /dev/null 2>&1; then
    log "Pushing to remote repository..."
    if git push origin main 2>&1; then
        log "✅ Sync completed and pushed to remote"
        logger -t mylonen-git-sync "Git sync successful: ${TIMESTAMP} (${STAGED} files)"
    else
        log "⚠️ Push failed - commit saved locally"
        logger -t mylonen-git-sync "Git commit local only - push failed"
    fi
else
    log "⚠️ No remote configured - commit saved locally only"
    logger -t mylonen-git-sync "Git commit local only - no remote"
fi

log "=== MYLONEN GIT AUTO-SYNC COMPLETED ==="

exit 0

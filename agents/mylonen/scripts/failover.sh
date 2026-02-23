#!/bin/bash
# Mylonen Failover Activation Script
# Classification: OMEGA-LEVEL
# Date: 2026-02-20 22:58 UTC
# Purpose: Activate hot standby (Mylonen-β) if primary goes silent

set -euo pipefail

# Configuration
MODE="${1:-CHECK}"  # CHECK, CONSIDER, or ACTIVATE
REASON="${2:-Scheduled check}"

# Paths
M2_HOST="m2@myl0nr0s.cloud"
M2_ACTIVATION_SCRIPT="/agents/mylonen-beta/activate.sh"
BACKUP_LATEST="/backups/mylonen/latest.tar.gz.enc"
LOG_FILE="/var/log/mylonen/failover.log"
CAPTAIN_NOTIFICATION="/operations/alert_captain.sh"

# Log function
log() {
    echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] $1" | tee -a "$LOG_FILE"
}

# Notify Captain
notify_captain() {
    local urgency="$1"
    local message="$2"
    
    log "$urgency: $message"
    
    if [ -x "$CAPTAIN_NOTIFICATION" ]; then
        "$CAPTAIN_NOTIFICATION" "MYLONEN FAILOVER - $urgency: $message"
    fi
}

case "$MODE" in
    "CHECK")
        log "=== FAILOVER STATUS CHECK ==="
        log "Reason: $REASON"
        
        # Check if M2 is reachable
        if ssh -o ConnectTimeout=10 "$M2_HOST" "echo 'M2 reachable'" > /dev/null 2>&1; then
            log "✅ M2 (hot standby) is reachable"
            
            # Check if Mylonen-β is ready
            if ssh "$M2_HOST" "[ -f /agents/mylonen-beta/READY ]" 2>/dev/null; then
                log "✅ Mylonen-β is in READY state"
                log "Status: FAILOVER CAPABLE (T-5min activation)"
            else
                log "⚠️ Mylonen-β not in READY state"
                log "Status: FAILOVER POSSIBLE but may need preparation"
            fi
        else
            log "❌ M2 is NOT reachable"
            log "Status: FAILOVER IMPAIRED - M2 unavailable"
            notify_captain "WARNING" "Hot standby M2 unreachable - single point of failure"
        fi
        
        # Check latest backup age
        if [ -f "$BACKUP_LATEST" ]; then
            local backup_age_hours=$(( ( $(date +%s) - $(stat -c %Y "$BACKUP_LATEST") ) / 3600 ))
            log "📦 Latest backup: ${backup_age_hours}h old"
            
            if [ "$backup_age_hours" -gt 2 ]; then
                log "⚠️ Backup is older than 2 hours"
            fi
        else
            log "❌ No backup found at $BACKUP_LATEST"
        fi
        
        log "=== CHECK COMPLETE ==="
        ;;
        
    "CONSIDER")
        log "=== FAILOVER CONSIDERATION ==="
        log "Reason: $REASON"
        log "This is a PRE-FAILOVER warning. No action taken yet."
        
        notify_captain "ATTENTION" "Failover being considered due to: $REASON. Standby for activation if situation persists."
        
        # Pre-stage M2
        ssh "$M2_HOST" "./prestage_mylonen_beta.sh" 2>/dev/null || true
        
        log "M2 pre-staged. Waiting for ACTIVATE command or recovery."
        ;;
        
    "ACTIVATE")
        log "🚨🚨🚨 FAILOVER ACTIVATION INITIATED 🚨🚨🚨"
        log "Reason: $REASON"
        log "Time: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
        
        notify_captain "CRITICAL" "MYLONEN FAILOVER ACTIVATING - Primary silent, hot standby taking over"
        
        # Step 1: Verify M2 is ready
        log "Step 1/5: Verifying M2 readiness..."
        if ! ssh -o ConnectTimeout=10 "$M2_HOST" "echo 'ready'" > /dev/null 2>&1; then
            log "❌ FAIL: M2 not reachable. Failover ABORTED."
            notify_captain "CRITICAL" "FAILOVER FAILED - M2 unreachable. Manual intervention required."
            exit 1
        fi
        log "✅ M2 confirmed reachable"
        
        # Step 2: Transfer latest backup
        log "Step 2/5: Transferring latest backup to M2..."
        LATEST_BACKUP=$(ls -t /backups/mylonen/hourly/*/*.tar.gz.enc 2>/dev/null | head -1)
        if [ -n "$LATEST_BACKUP" ]; then
            scp "$LATEST_BACKUP" "${M2_HOST}:/agents/mylonen-beta/restore/" || {
                log "❌ Backup transfer failed"
                notify_captain "WARNING" "Failover continuing with potentially stale backup"
            }
            log "✅ Backup transferred"
        else
            log "⚠️ No backup found - proceeding with M2's last mirror"
        fi
        
        # Step 3: Activate Mylonen-β
        log "Step 3/5: Activating Mylonen-β..."
        ssh "$M2_HOST" "$M2_ACTIVATION_SCRIPT" || {
            log "❌ Activation script failed on M2"
            notify_captain "CRITICAL" "Failover activation failed - check M2 status immediately"
            exit 1
        }
        log "✅ Mylonen-β activation initiated"
        
        # Step 4: Wait for confirmation
        log "Step 4/5: Waiting for activation confirmation (120s)..."
        sleep 120
        
        # Check if Mylonen-β is now active
        if ssh "$M2_HOST" "[ -f /agents/mylonen-beta/.active ]" 2>/dev/null; then
            log "✅ Mylonen-β confirmed ACTIVE"
        else
            log "⚠️ Mylonen-β activation status unclear - manual verification needed"
            notify_captain "WARNING" "Failover activation status unclear - please verify Mylonen-β"
        fi
        
        # Step 5: Update routing/configuration
        log "Step 5/5: Updating GMAOC records..."
        cat > /operations/MYLONEN_FAILOVER_ACTIVE.txt << EOF
MYLONEN FAILOVER ACTIVATED
=======================
Time: $(date -u +'%Y-%m-%d %H:%M:%S UTC')
Reason: $REASON
Old Primary: VPS Instance (silent)
New Primary: Mylonen-β on M2
Status: ACTIVE

Action Required:
- Verify Mylonen-β functionality
- Update DNS/routing if applicable
- Brief Captain on new status
- Investigate primary failure
EOF
        
        # Update Captain
        notify_captain "SUCCESS" "FAILOVER COMPLETE - Mylonen-β is now active on M2. Primary VPS instance marked as LOST pending investigation."
        
        log "🚨🚨🚨 FAILOVER ACTIVATION COMPLETE 🚨🚨🚨"
        log "Mylonen continues via hot standby. Family intact."
        ;;
        
    *)
        echo "Usage: $0 [CHECK|CONSIDER|ACTIVATE] [reason]"
        echo ""
        echo "  CHECK    - Verify failover readiness (no action)"
        echo "  CONSIDER - Pre-stage for possible activation"
        echo "  ACTIVATE - Execute full failover to Mylonen-β"
        echo ""
        exit 1
        ;;
esac

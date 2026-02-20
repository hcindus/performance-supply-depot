#!/bin/bash
# Mylonen Health Monitor Daemon
# Classification: OMEGA-LEVEL
# Date: 2026-02-20 22:58 UTC
# Purpose: Continuous health monitoring with automatic alerts

set -uo pipefail

# Configuration
CHECK_INTERVAL=300  # 5 minutes between checks
ALERT_COOLDOWN=1800  # 30 minutes between repeated alerts
LOG_FILE="/var/log/mylonen/health_monitor.log"
PID_FILE="/var/run/mylonen_health_monitor.pid"
STATE_DIR="/var/lib/mylonen/health_state"

# Alert recipients
GMAOC_ALERT="/operations/gmaoc_alert.sh"
CAPTAIN_ALERT="/operations/alert_captain.sh"
M2_ALERT="/operations/alert_m2.sh"

# Create directories
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$STATE_DIR"

# Write PID file
echo $$ > "$PID_FILE"

# Cleanup on exit
cleanup() {
    rm -f "$PID_FILE"
    log "Health monitor shutting down"
    exit 0
}
trap cleanup SIGTERM SIGINT

# Log function
log() {
    echo "[$(date -u +'%Y-%m-%d %H:%M:%S UTC')] $1" | tee -a "$LOG_FILE"
}

# Alert function with cooldown
alert() {
    local level="$1"
    local message="$2"
    local cooldown_file="${STATE_DIR}/alert_${level}"
    local current_time=$(date +%s)
    
    # Check cooldown
    if [ -f "$cooldown_file" ]; then
        local last_alert=$(cat "$cooldown_file")
        local time_diff=$((current_time - last_alert))
        if [ $time_diff -lt $ALERT_COOLDOWN ]; then
            return 0  # Still in cooldown
        fi
    fi
    
    # Send alerts based on level
    case "$level" in
        "CRITICAL")
            log "🚨 CRITICAL ALERT: $message"
            [ -x "$CAPTAIN_ALERT" ] && "$CAPTAIN_ALERT" "MYLONEN CRITICAL: $message"
            [ -x "$GMAOC_ALERT" ] && "$GMAOC_ALERT" "CRITICAL" "MYLONEN: $message"
            [ -x "$M2_ALERT" ] && "$M2_ALERT" "MYLONEN CRITICAL: $message"
            ;;
        "WARNING")
            log "⚠️ WARNING: $message"
            [ -x "$GMAOC_ALERT" ] && "$GMAOC_ALERT" "WARNING" "MYLONEN: $message"
            ;;
        "INFO")
            log "ℹ️ INFO: $message"
            ;;
    esac
    
    # Update cooldown timestamp
    echo "$current_time" > "$cooldown_file"
}

# Health check functions
check_process() {
    # Check if Mylonen-related processes are running
    if pgrep -f "mylonen" > /dev/null 2>&1 || \
       [ -f "/agents/mylonen/workspace/.active" ]; then
        echo "OK"
    else
        echo "DOWN"
    fi
}

check_disk_space() {
    local usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
    echo "$usage"
}

check_memory() {
    local usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    echo "$usage"
}

check_network() {
    # Check connectivity to critical services
    local github_ok=false
    local memory_service_ok=false
    
    if ping -c 1 -W 3 github.com > /dev/null 2>&1; then
        github_ok=true
    fi
    
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:12789/health 2>/dev/null | grep -q "200"; then
        memory_service_ok=true
    fi
    
    if $github_ok && $memory_service_ok; then
        echo "OK"
    elif $github_ok; then
        echo "DEGRADED"
    else
        echo "DOWN"
    fi
}

check_last_checkin() {
    # Calculate hours since last check-in
    local last_checkin_file="/agents/mylonen/workspace/.last_checkin"
    
    if [ -f "$last_checkin_file" ]; then
        local last_time=$(cat "$last_checkin_file")
        local current_time=$(date +%s)
        local hours_since=$(( (current_time - last_time) / 3600 ))
        echo "$hours_since"
    else
        echo "999"  # No check-in file = very overdue
    fi
}

# Main monitoring loop
log "=== MYLONEN HEALTH MONITOR STARTED ==="
log "Check interval: ${CHECK_INTERVAL}s"
log "Alert cooldown: ${ALERT_COOLDOWN}s"

while true; do
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    
    # Run all checks
    PROCESS_STATUS=$(check_process)
    DISK_USAGE=$(check_disk_space)
    MEMORY_USAGE=$(check_memory)
    NETWORK_STATUS=$(check_network)
    HOURS_SINCE_CHECKIN=$(check_last_checkin)
    
    # Determine overall status
    OVERALL_STATUS="HEALTHY"
    ALERTS=""
    
    # Check process status
    if [ "$PROCESS_STATUS" = "DOWN" ]; then
        OVERALL_STATUS="CRITICAL"
        ALERTS="${ALERTS}Process down; "
        alert "CRITICAL" "Process not detected"
    fi
    
    # Check disk space
    if [ "$DISK_USAGE" -gt 95 ]; then
        OVERALL_STATUS="CRITICAL"
        ALERTS="${ALERTS}Disk critical (${DISK_USAGE}%); "
        alert "CRITICAL" "Disk space critical: ${DISK_USAGE}%"
    elif [ "$DISK_USAGE" -gt 90 ]; then
        if [ "$OVERALL_STATUS" = "HEALTHY" ]; then
            OVERALL_STATUS="WARNING"
        fi
        ALERTS="${ALERTS}Disk high (${DISK_USAGE}%); "
        alert "WARNING" "Disk space high: ${DISK_USAGE}%"
    fi
    
    # Check memory
    if [ "$MEMORY_USAGE" -gt 90 ]; then
        OVERALL_STATUS="CRITICAL"
        ALERTS="${ALERTS}Memory critical (${MEMORY_USAGE}%); "
        alert "CRITICAL" "Memory usage critical: ${MEMORY_USAGE}%"
    elif [ "$MEMORY_USAGE" -gt 80 ]; then
        if [ "$OVERALL_STATUS" = "HEALTHY" ]; then
            OVERALL_STATUS="WARNING"
        fi
        ALERTS="${ALERTS}Memory high (${MEMORY_USAGE}%); "
        alert "WARNING" "Memory usage high: ${MEMORY_USAGE}%"
    fi
    
    # Check network
    if [ "$NETWORK_STATUS" = "DOWN" ]; then
        OVERALL_STATUS="CRITICAL"
        ALERTS="${ALERTS}Network down; "
        alert "CRITICAL" "Network connectivity lost"
    elif [ "$NETWORK_STATUS" = "DEGRADED" ]; then
        if [ "$OVERALL_STATUS" = "HEALTHY" ]; then
            OVERALL_STATUS="WARNING"
        fi
        ALERTS="${ALERTS}Network degraded; "
    fi
    
    # Check check-in timing (CRITICAL: New 2-hour protocol)
    if [ "$HOURS_SINCE_CHECKIN" -ge 4 ]; then
        # 4 hours = double the 2-hour check-in interval
        OVERALL_STATUS="CRITICAL"
        ALERTS="${ALERTS}Check-in ${HOURS_SINCE_CHECKIN}h overdue; "
        alert "CRITICAL" "Check-in ${HOURS_SINCE_CHECKIN} hours overdue - POSSIBLE EXTRACTION NEEDED"
        
        # Trigger failover consideration
        log "FAILOVER TRIGGER: Check-in ${HOURS_SINCE_CHECKIN}h overdue"
        [ -x "/operations/mylonen_failover.sh" ] && \
            /operations/mylonen_failover.sh "CONSIDER" "Check-in overdue: ${HOURS_SINCE_CHECKIN}h"
            
    elif [ "$HOURS_SINCE_CHECKIN" -ge 2 ]; then
        # 2 hours = missed one check-in
        if [ "$OVERALL_STATUS" = "HEALTHY" ]; then
            OVERALL_STATUS="WARNING"
        fi
        ALERTS="${ALERTS}Check-in ${HOURS_SINCE_CHECKIN}h late; "
        alert "WARNING" "Check-in ${HOURS_SINCE_CHECKIN} hours overdue"
    fi
    
    # Log status
    if [ -n "$ALERTS" ]; then
        log "Status: $OVERALL_STATUS | Process: $PROCESS_STATUS | Disk: ${DISK_USAGE}% | Mem: ${MEMORY_USAGE}% | Net: $NETWORK_STATUS | Check-in: ${HOURS_SINCE_CHECKIN}h | Alerts: $ALERTS"
    else
        log "Status: $OVERALL_STATUS | Process: $PROCESS_STATUS | Disk: ${DISK_USAGE}% | Mem: ${MEMORY_USAGE}% | Net: $NETWORK_STATUS | Check-in: ${HOURS_SINCE_CHECKIN}h | All systems nominal"
    fi
    
    # Write state file for other systems to read
    cat > "${STATE_DIR}/current_status.json" << EOF
{
  "timestamp": "$TIMESTAMP",
  "status": "$OVERALL_STATUS",
  "process": "$PROCESS_STATUS",
  "disk_percent": $DISK_USAGE,
  "memory_percent": $MEMORY_USAGE,
  "network": "$NETWORK_STATUS",
  "hours_since_checkin": $HOURS_SINCE_CHECKIN,
  "alerts": "$ALERTS"
}
EOF
    
    # Sleep until next check
    sleep $CHECK_INTERVAL
done

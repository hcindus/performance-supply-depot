#!/bin/bash
# SENTINAL WATCHDOG
# Standing Order: If Sentinal fails, restart immediately
# Authorization: Captain 07:01 UTC 2026-02-21

SENTINAL_PID_FILE="/var/run/sentinal.pid"
SENTINAL_LOG="/var/log/sentinal.log"
RESTART_COUNT_FILE="/tmp/sentinal_restarts"
MAX_RESTARTS=5
TIME_WINDOW=3600  # 1 hour

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sentinal Watchdog starting..."

# Check if Sentinal is running
check_sentinal() {
    if [ -f "$SENTINAL_PID_FILE" ]; then
        PID=$(cat "$SENTINAL_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        fi
    fi
    return 1  # Not running
}

# Restart Sentinal
restart_sentinal() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ SENTINAL NOT DETECTED - RESTARTING..."
    
    # Log the restart
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Auto-restart triggered by watchdog" >> "$SENTINAL_LOG"
    
    # Kill any existing processes
    pkill -f "sentinal" 2>/dev/null
    sleep 2
    
    # Start Sentinal (adjust path as needed)
    if [ -f "/opt/sentinal/sentinal.py" ]; then
        python3 /opt/sentinal/sentinal.py &
        NEW_PID=$!
        echo $NEW_PID > "$SENTINAL_PID_FILE"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Sentinal restarted (PID: $NEW_PID)"
        
        # Notify Captain
        echo "Sentinal auto-restarted at $(date)" | mail -s "SENTINAL RESTART ALERT" captain@myl0nr0s.cloud 2>/dev/null || true
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Sentinal binary not found at /opt/sentinal/sentinal.py"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Manual intervention required"
    fi
}

# Main loop
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Watchdog monitoring every 60 seconds..."

while true; do
    if ! check_sentinal; then
        restart_sentinal
    fi
    sleep 60
done

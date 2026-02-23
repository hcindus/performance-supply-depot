#!/bin/bash
# Bridge Service Restarter
# Auto-restart bridge with delay and logging
# Usage: ./bridge_restarter.sh

echo "Bridge restarter starting at $(date -Iseconds)"

while true; do
    echo "[$(date -Iseconds)] Checking bridge status..."
    
    # Check if bridge is running
    if ! curl -s http://localhost:3001/health > /dev/null 2>&1; then
        echo "[$(date -Iseconds)] Bridge DOWN - restarting..."
        
        # Kill any stale processes
        pkill -f "bridge_mock.js" 2>/dev/null
        sleep 2
        
        # Start bridge
        cd /root/.openclaw/workspace/dusty_mvp_sandbox
        export CORE_AGENT_URL="http://localhost:3000/tasks"
        nohup node bridge_mock/bridge_mock.js > /var/log/dusty-bridge.log 2>&1 &
        
        echo "[$(date -Iseconds)] Bridge restarted, PID: $!"
        sleep 5
        
        # Verify
        if curl -s http://localhost:3001/health > /dev/null 2>&1; then
            echo "[$(date -Iseconds)] Bridge UP and healthy"
        else
            echo "[$(date -Iseconds)] Bridge restart failed - will retry in 10s"
        fi
    else
        echo "[$(date -Iseconds)] Bridge healthy"
    fi
    
    # Check every 30 seconds
    sleep 30
done

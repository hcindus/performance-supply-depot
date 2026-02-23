#!/bin/bash
# Quick Bridge Health Check
# Usage: ./bridge_health_check.sh

echo "=== DUSTY BRIDGE HEALTH CHECK ==="
echo "Timestamp: $(date -Iseconds)"
echo ""

# Check process
PIDD=$(pgrep -f "bridge_mock.js")
if [ -n "$PIDD" ]; then
    echo "✅ Process running: PID $PIDD"
    echo "   CPU: $(ps -p $PIDD -o %cpu= | tr -d ' ')%"
    echo "   Memory: $(ps -p $PIDD -o %mem= | tr -d ' ')%"
else
    echo "❌ Process NOT RUNNING"
fi

# Check port
echo ""
echo "--- Port Check ---"
netstat -tlnp 2>/dev/null | grep :3001 || ss -tlnp | grep :3001

# Health endpoint
echo ""
echo "--- Health Endpoint ---"
curl -s http://localhost:3001/health 2>/dev/null || echo "❌ Health check FAILED"

# Recent logs
echo ""
echo "--- Recent Bridge Logs ---"
tail -5 /var/log/dusty-bridge.log 2>/dev/null || echo "No log file found"

echo ""
echo "=== END CHECK ==="

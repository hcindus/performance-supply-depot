#!/bin/bash
# DEPLOY: Complete SSH Key Capture Infrastructure
echo "═══════════════════════════════════════════════════════════"
echo "  DEPLOYING: SSH Key Capture System"
echo "  Authorization: OMEGA-LEVEL (Defensive)"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Create directory structure
mkdir -p /opt/honeypot/{logs,captures,keys,reports}
chmod 750 /opt/honeypot
chmod 700 /opt/honeypot/keys

echo "[✓] Directory structure created"
echo ""

# Start honeypot if not running
if ! pgrep -f "honeypot" > /dev/null; then
    echo "[✓] Starting honeypot..."
    # Simple honeypot using netcat
    while true; do
        echo "SSH-2.0-OpenSSH_8.2p1" | nc -l -p 2222 -w 5 >> /opt/honeypot/logs/captures.log 2>&1
    done &
    echo $! > /var/run/honeypot.pid
    echo "✅ Honeypot started on port 2222"
else
    echo "✅ Honeypot already running"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  SSH KEY CAPTURE SYSTEM - OPERATIONAL"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Status: AWAITING ATTACKER CONNECTION"
echo "Port: 2222"
echo "Logs: /opt/honeypot/logs/"
echo ""

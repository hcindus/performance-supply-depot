#!/bin/bash
# SSH Honeypot Key Capture
# Defensive: Waits for attacker to connect, captures key, then rejects
# Classification: OMEGA-LEVEL
# Law Zero: ✅ Defensive intelligence only

LOGDIR="/var/log/honeypot"
PIDFILE="/tmp/ssh-honeypot.pid"
PORT=2222  # Honeypot port

echo "=== SSH HONEYPOT SETUP ==="
echo "Purpose: Capture attacker SSH keys"
echo "Port: $PORT"
echo ""

mkdir -p "$LOGDIR"

# Create fake SSH banner
FAKE_BANNER="SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"

# Start listening on honeypot port
echo "[HONEYPOT] Starting listener on port $PORT..."

# Use netcat to capture initial handshake
(
cat << 'EOF'
$FAKE_BANNER
Protocol mismatch.
EOF
) | nc -l -p $PORT -q 2 -w 10 > "$LOGDIR/capture-$(date +%s).raw" 2>&1 &

HONEYPOT_PID=$!
echo $HONEYPOT_PID > "$PIDFILE"

echo "[HONEYPOT] PID: $HONEYPOT_PID"
echo "[HONEYPOT] Listening on port $PORT"
echo ""
echo "Next steps:"
echo "1. Redirect some attacker traffic to port $PORT"
echo "2. When they connect, capture raw handshake"
echo "3. Analyze for SSH keys/fingerprints"
echo ""
echo "To capture live:"
echo "  iptables -t nat -A PREROUTING -p tcp --dport 22 -s 165.245.143.157 -j REDIRECT --to-port $PORT"
echo ""
echo "[HONEYPOT] Running... Press Ctrl+C to stop"
wait $HONEYPOT_PID

#!/bin/bash
# COMMS STATION SETUP SCRIPT
# Run on each agent's server to set up communication

set -e

AGENT_NAME="${1:-agent}"
COMMS_PORT="${2:-12792}"
HUB_URL="${3:-http://localhost:12792}"

echo "🔧 Setting up Comms Station for: $AGENT_NAME"

# Create comms directory
mkdir -p ~/comms

# Copy comms client
cat > ~/comms/comms_client.sh << 'EOF'
#!/bin/bash
# Simple comms client

send() {
    local to="$1"
    local msg="$2"
    curl -s -X POST "http://localhost:12792/send" \
        -H "Content-Type: application/json" \
        -d "{\"from\":\"$AGENT_NAME\",\"to\":\"$to\",\"text\":\"$msg\"}"
}

inbox() {
    local agent="${1:-$AGENT_NAME}"
    curl -s "http://localhost:12792/agents/$agent" | jq .
}

case "$1" in
    send) shift; send "$@";;
    inbox) shift; inbox "$@";;
    *) echo "Usage: $0 {send|inbox} [args]";;
esac
EOF

chmod +x ~/comms/comms_client.sh

# Create systemd service
cat > /etc/systemd/system/comms.service << EOF
[Unit]
Description=Comms Station - $AGENT_NAME
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.openclaw/workspace/pipe
ExecStart=/usr/bin/node /root/.openclaw/workspace/pipe/comms.js
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable comms
systemctl start comms

echo "✅ Comms Station ready for: $AGENT_NAME"
echo "   Port: $COMMS_PORT"
echo "   Commands:"
echo "     ~/comms/comms_client.sh send <to> <message>"
echo "     ~/comms/comms_client.sh inbox"

#!/bin/bash
# Start Dusty MVP services for end-to-end testing

cd /root/.openclaw/workspace/dusty_mvp_sandbox

# Kill any existing node processes on the ports
echo "Cleaning up existing processes..."
pkill -f "node.*bridge_mock" 2>/dev/null || true
pkill -f "node.*core-agent" 2>/dev/null || true
pkill -f "node.*openclaw_mock" 2>/dev/null || true

sleep 1

# Set environment variables
export CORE_AGENT_URL="http://localhost:3000/tasks"
export OPENCLAW_URL="http://localhost:4000/receive_message"
export PORT=3000

echo "Starting services..."

# Start OpenClaw Mock (port 4000) - no dependencies
echo "[1/3] Starting OpenClaw Mock on port 4000..."
node openclaw_mock/openclaw_mock.js > /tmp/openclaw_mock.log 2>&1 &
OPENCLAW_PID=$!
echo "OpenClaw Mock PID: $OPENCLAW_PID"

# Start Core-Agent (port 3000) - depends on OpenClaw
echo "[2/3] Starting Core-Agent on port 3000..."
cd core-agent && node src/index.js > /tmp/core-agent.log 2>&1 &
CORE_PID=$!
echo "Core-Agent PID: $CORE_PID"
cd ..

# Wait for core-agent to be ready
sleep 2

# Start Bridge Mock (port 3001) - depends on core-agent
echo "[3/3] Starting Bridge Mock on port 3001..."
cd bridge_mock && CORE_AGENT_URL="http://localhost:3000/tasks" node bridge_mock.js > /tmp/bridge_mock.log 2>&1 &
BRIDGE_PID=$!
echo "Bridge Mock PID: $BRIDGE_PID"
cd ..

echo ""
echo "Services started with PIDs:"
echo "  OpenClaw Mock: $OPENCLAW_PID"
echo "  Core-Agent:    $CORE_PID"
echo "  Bridge Mock:   $BRIDGE_PID"
echo ""
echo "Waiting for services to initialize..."
sleep 3
echo "Done. Check /tmp/*.log for service logs."

#!/bin/bash
#
# AOCROS Memory Service Installation Script
# For Miles VPS Testing
# Run: chmod +x install.sh && ./install.sh

set -e

echo "========================================"
echo "  AOCROS Memory Service Installer"
echo "  For: Miles VPS Testing"
echo "========================================"
echo ""

# Check environment
if [ -z "$OWNER_SIGNATURE" ]; then
    echo "ERROR: OWNER_SIGNATURE not set!"
    echo ""
    echo "Set it first:"
    echo "  export OWNER_SIGNATURE=your-secret-key-here"
    echo ""
    echo "Or add to ~/.bashrc for persistence"
    exit 1
fi

# Set default paths
BASE_DIR="${MYL0N_BASE_DIR:-$HOME/aocros-memory}"
MEMORY_DIR="$BASE_DIR/memory"
SERVICE_DIR="$BASE_DIR/services/memory/src"

echo "Installing to: $BASE_DIR"
echo "Memory data: $MEMORY_DIR"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p "$MEMORY_DIR"
mkdir -p "$SERVICE_DIR"
mkdir -p "$BASE_DIR/logs"

# Check for Node.js
if ! command -v node >/dev/null 2>&1; then
    echo "Node.js not found. Installing..."
    
    # Detect distro
    if command -v apt-get >/dev/null 2>&1; then
        # Debian/Ubuntu
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt-get install -y nodejs
    elif command -v yum >/dev/null 2>&1; then
        # RHEL/CentOS
        curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
        yum install -y nodejs
    else
        echo "ERROR: Cannot detect package manager. Please install Node.js manually."
        echo "Visit: https://nodejs.org/"
        exit 1
    fi
fi

echo "✓ Node.js version: $(node --version)"

# Copy service files (should be in same directory as script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "Copying service files..."

if [ -f "$SCRIPT_DIR/FOR_MILES_memoryService.js" ]; then
    cp "$SCRIPT_DIR/FOR_MILES_memoryService.js" "$SERVICE_DIR/memoryService.js"
    echo "✓ memoryService.js copied"
else
    echo "WARNING: memoryService.js not found in $SCRIPT_DIR"
    echo "Make sure FOR_MILES_memoryService.js is in the same directory"
fi

if [ -f "$SCRIPT_DIR/FOR_MILES_memoryClient.js" ]; then
    cp "$SCRIPT_DIR/FOR_MILES_memoryClient.js" "$SERVICE_DIR/memoryClient.js"
    echo "✓ memoryClient.js copied"
else
    echo "WARNING: memoryClient.js not found"
fi

# Create launcher script
cat > "$BASE_DIR/start-memory.sh" << 'EOF'
#!/bin/bash
# Start AOCROS Memory Service

BASE_DIR="${MYL0N_BASE_DIR:-$HOME/aocros-memory}"
SERVICE_DIR="$BASE_DIR/services/memory/src"
LOG_FILE="$BASE_DIR/logs/memory.log"

cd "$SERVICE_DIR"

# Ensure log directory exists
mkdir -p "$(dirname $LOG_FILE)"

echo "Starting AOCROS Memory Service..."
echo "Log file: $LOG_FILE"

# Check if already running
if pgrep -f "memoryService.js" > /dev/null; then
    echo "Memory service already running!"
    echo "Check: curl http://127.0.0.1:12789/health"
    exit 0
fi

# Start service
export OWNER_SIGNATURE="${OWNER_SIGNATURE}"
export MYL0N_BASE_DIR="${MYL0N_BASE_DIR:-$HOME/aocros-memory}"

exec node memoryService.js >> "$LOG_FILE" 2>&1 &
echo $! > "$BASE_DIR/memory.pid"
echo "✓ Started with PID $(cat $BASE_DIR/memory.pid)"

# Wait a moment
sleep 2

# Test connection
if curl -s http://127.0.0.1:12789/health > /dev/null 2>&1; then
    echo "✓ Memory service is healthy!"
else
    echo "⚠ Service starting... check logs: tail -f $LOG_FILE"
fi
EOF

chmod +x "$BASE_DIR/start-memory.sh"
echo "✓ start-memory.sh created"

# Create stop script
cat > "$BASE_DIR/stop-memory.sh" << 'EOF'
#!/bin/bash
# Stop AOCROS Memory Service

BASE_DIR="${MYL0N_BASE_DIR:-$HOME/aocros-memory}"
PID_FILE="$BASE_DIR/memory.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping memory service (PID $PID)..."
        kill "$PID" 2>/dev/null || kill -9 "$PID" 2>/dev/null
        rm -f "$PID_FILE"
        echo "✓ Stopped"
    else
        echo "Service not running"
        rm -f "$PID_FILE"
    fi
else
    echo "PID file not found. Trying to find process..."
    pkill -f "memoryService.js" && echo "✓ Stopped" || echo "Service not running"
fi
EOF

chmod +x "$BASE_DIR/stop-memory.sh"
echo "✓ stop-memory.sh created"

# Create test script
cat > "$BASE_DIR/test-memory.sh" << 'EOF'
#!/bin/bash
# Quick test of memory service

BASE_DIR="${MYL0N_BASE_DIR:-$HOME/aocros-memory}"
SERVICE_DIR="$BASE_DIR/services/memory/src"

echo "Testing AOCROS Memory Service..."
echo ""

# Check if running
if ! curl -s http://127.0.0.1:12789/health > /dev/null 2>&1; then
    echo "⚠ Memory service not running!"
    echo "Start it: $BASE_DIR/start-memory.sh"
    exit 1
fi

echo "✓ Service is running"
echo ""

# Run client test
cd "$SERVICE_DIR"
export OWNER_SIGNATURE="${OWNER_SIGNATURE}"
node memoryClient.js

echo ""
echo "✅ Tests complete!"
EOF

chmod +x "$BASE_DIR/test-memory.sh"
echo "✓ test-memory.sh created"

# Environment file
cat > "$BASE_DIR/.env" << EOF
# AOCROS Memory Service Environment
OWNER_SIGNATURE=$OWNER_SIGNATURE
MYL0N_BASE_DIR=$BASE_DIR
MEMORY_HOST=127.0.0.1
MEMORY_PORT=12789
EOF

echo "✓ .env file created"
echo ""
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the service:"
echo "   $BASE_DIR/start-memory.sh"
echo ""
echo "2. Test the connection:"
echo "   $BASE_DIR/test-memory.sh"
echo ""
echo "3. Use the client in your code:"
echo "   const { makeMemoryClient } = require('$SERVICE_DIR/memoryClient');"
echo "   const memory = makeMemoryClient('miles');"
echo ""
echo "4. Stop the service:"
echo "   $BASE_DIR/stop-memory.sh"
echo ""
echo "Logs: tail -f $BASE_DIR/logs/memory.log"
echo ""

#!/bin/bash
set -e

echo "=== Dusty MVP End-to-End Test ==="
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S') UTC"
echo ""

# Initialize timing data
BRIDGE_TIME=0
CORE_TIME=0
OPENCLAW_TIME=0
TOTAL_TIME=0

echo "1. Service Health Checks"
echo "   - Core-Agent (localhost:3000)..."
START=$(date +%s%N)
CORE_HEALTH=$(curl -s -w "\n%{http_code}" http://localhost:3000/health)
CORE_TIME=$(($(date +%s%N) - START))
echo "     Response: $CORE_HEALTH"
echo "     Time: $(echo "scale=3; $CORE_TIME/1000000" | bc)ms"

echo "   - Bridge Mock (localhost:3001)..."
START=$(date +%s%N)
BRIDGE_HEALTH=$(curl -s -w "\n%{http_code}" http://localhost:3001/health)
BRIDGE_TIME=$(($(date +%s%N) - START))
echo "     Response: $BRIDGE_HEALTH"
echo "     Time: $(echo "scale=3; $BRIDGE_TIME/1000000" | bc)ms"

echo "   - OpenClaw Mock (localhost:4000)..."
START=$(date +%s%N)
OPENCLAW_HEALTH=$(curl -s -w "\n%{http_code}" http://localhost:4000/status)
OPENCLAW_TIME=$(($(date +%s%N) - START))
echo "     Response: $OPENCLAW_HEALTH"
echo "     Time: $(echo "scale=3; $OPENCLAW_TIME/1000000" | bc)ms"

echo ""
echo "2. End-to-End Flow Test"
echo "   Sending test message to Bridge..."
START=$(date +%s%N)
E2E_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:3001/test \
  -H "Content-Type: application/json" \
  -d '{"message": "/dust balance", "user_id": "test_user_123", "chat_id": "test_chat_456"}')
TOTAL_TIME=$(($(date +%s%N) - START))
echo "     Response: $E2E_RESPONSE"
echo "     Total Round-Trip: $(echo "scale=3; $TOTAL_TIME/1000000" | bc)ms"

echo ""
echo "3. Dust-Specific Query Test"
echo "   Query: 'What is my dust balance?'"
START=$(date +%s%N)
DUST_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:3001/test \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my dust balance?", "user_id": "dusty_test_user", "chat_id": "dusty_test_chat"}')
DUST_TIME=$(($(date +%s%N) - START))
echo "     Response: $DUST_RESPONSE"
echo "     Time: $(echo "scale=3; $DUST_TIME/1000000" | bc)ms"

echo ""
echo "=== Test Complete ==="

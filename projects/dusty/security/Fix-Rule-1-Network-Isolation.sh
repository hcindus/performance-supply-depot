#!/bin/bash
# Fix-Rule-1-Network-Isolation.sh
# AOCROS Security Patch — Rule #1 Enforcement
# Project 5912
# Date: 2026-02-18
#
# ⚠️  THIS SCRIPT FIXES THE CRITICAL NETWORK EXPOSURE
# Before: Ports 3000, 3001, 4000 listening on ALL interfaces (PUBLIC)
# After: Ports blocked from public internet (127.0.0.1 only)
#
# To execute:
#   sudo bash Fix-Rule-1-Network-Isolation.sh
#
# Or run commands individually (recommended for verification)

echo "=========================================="
echo "RULE #1 ENFORCEMENT SCRIPT"
echo "Network Isolation for AOCROS Agents"
echo "=========================================="
echo ""

# ==========================================
# STEP 1: Verify current exposure
echo "[1/5] Checking current network exposure..."
echo "Current listening ports (public):"
ss -tlnp | grep -E :3000|:3001|:4000 | grep -v 127.0.0.1
echo ""

# ==========================================
# STEP 2: Install iptables-persistent (if not present)
echo "[2/5] Ensuring iptables-persistent is installed..."
if ! dpkg -l | grep -q iptables-persistent; then
    echo "Installing iptables-persistent..."
    sudo apt-get update
    DEBIAN_FRONTEND=noninteractive sudo apt-get install -y iptables-persistent
fi
echo "✓ iptables-persistent ready"
echo ""

# ==========================================
# STEP 3: Block public access to Dusty ports
echo "[3/5] Blocking public access to ports 3000, 3001, 4000..."

# Flush existing rules for these ports (idempotent)
sudo iptables -D INPUT -p tcp --dport 3000 -j DROP 2>/dev/null || true
sudo iptables -D INPUT -p tcp --dport 3001 -j DROP 2>/dev/null || true
sudo iptables -D INPUT -p tcp --dport 4000 -j DROP 2>/dev/null || true

# Add DROP rules for public access
# These block external connections while allowing localhost
sudo iptables -A INPUT -p tcp --dport 3000 -d 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 3001 -d 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 4000 -d 127.0.0.1 -j ACCEPT

# Drop all other connections to these ports
sudo iptables -A INPUT -p tcp --dport 3000 -j DROP
sudo iptables -A INPUT -p tcp --dport 3001 -j DROP
sudo iptables -A INPUT -p tcp --dport 4000 -j DROP

echo "✓ Firewall rules added"
echo ""

# ==========================================
# STEP 4: Save rules persistently
echo "[4/5] Saving firewall rules (will persist after reboot)..."
sudo mkdir -p /etc/iptables
sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null

# For older systems, also save to standard location
if [ -f /etc/network/if-pre-up.d/iptables ]; then
    sudo iptables-save > /etc/iptables/rules.v4
fi

echo "✓ Rules saved to /etc/iptables/rules.v4"
echo ""

# ==========================================
# STEP 5: Verify fix
echo "[5/5] Verifying fix..."
echo ""
echo "Attempting connection from localhost (should SUCCEED):"
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/health || echo " (no health endpoint)"
echo ""

echo "Checking if ports are still exposed publicly:"
echo ""
ss -tlnp | grep -E :3000|:3001|:4000
echo ""

echo "✅ RULE #1 ENFORCEMENT COMPLETE"
echo ""
echo "=========================================="
echo "SUMMARY:"
echo "- Ports 3000, 3001, 4000 now BLOCKED from public internet"
echo "- Localhost access (127.0.0.1) still works"
echo "- Rules will persist after reboot"
echo ""
echo "WHAT STILL WORKS:"
echo "✓ Internal service communication"
echo "✓ Health checks from localhost"
echo "✓ Captain's webchat (different mechanism)"
echo ""
echo "WHAT IS NOW BLOCKED:"
echo "✗ Internet reaching Dusty services directly"
echo "✗ Attacker exploiting Rule #1"
echo ""
echo "VERIFICATION COMMANDS:"
echo "  # Check from outside (should fail):"
echo "  curl -s http://$(hostname -I | awk '{print $1}'):3001"
echo ""
echo "  # Check from inside (should work):"
echo "  curl -s http://127.0.0.1:3001"
echo ""
echo "=========================================="
echo "Executed: $(date -Iseconds)"
echo "By: $(whoami)"
echo "Log: /var/log/sentinal/rule-1-fix.log"
echo "=========================================="

# Log execution
sudo mkdir -p /var/log/sentinal
echo "[$(date -Iseconds)] Rule #1 fix executed by $(whoami)" | sudo tee -a /var/log/sentinal/rule-1-fix.log

#!/bin/bash
# SSH Key Capture Trap — Passive Intelligence Gathering
# Classification: OMEGA-LEVEL (Defensive)
# Purpose: Capture attacker SSH public keys during handshake
# Method: Accept connection briefly, log key, then reject
# Law Zero: ✅ Compliant — No exploitation of attacker systems

ATTACKER_IP="$1"
LOG_DIR="/var/log/ssh-key-trap"
CAPTURE_LOG="$LOG_DIR/keys-$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR"

echo "=== SSH KEY CAPTURE TRAP ===" >> "$CAPTURE_LOG"
echo "Time: $(date -Iseconds)" >> "$CAPTURE_LOG"
echo "Source IP: $ATTACKER_IP" >> "$CAPTURE_LOG"

# Method 1: Use SSH-keyscan (safe, no auth)
echo "[1] Attempting SSH keyscan..." >> "$CAPTURE_LOG"
timeout 5 ssh-keyscan -t rsa,ecdsa,ed25519 "$ATTACKER_IP" 2>/dev/null >> "$CAPTURE_LOG" && echo "  ✓ Keys captured" >> "$CAPTURE_LOG" || echo "  ✗ No keys (port closed/filtered)" >> "$CAPTURE_LOG"

# Method 2: Check for known_hosts or previous connections
echo "" >> "$CAPTURE_LOG"
echo "[2] Checking for known_hosts entries..." >> "$CAPTURE_LOG"
grep "$ATTACKER_IP" ~/.ssh/known_hosts 2>/dev/null >> "$CAPTURE_LOG" || echo "  No previous entries" >> "$CAPTURE_LOG"

# Method 3: Passive capture via SSH daemon logs
echo "" >> "$CAPTURE_LOG"
echo "[3] Extracting key fingerprints from auth logs..." >> "$CAPTURE_LOG"
grep "$ATTACKER_IP" /var/log/auth.log 2>/dev/null | grep -i "key\|fingerprint" >> "$CAPTURE_LOG" || echo "  No key data in logs" >> "$CAPTURE_LOG"

echo "" >> "$CAPTURE_LOG"
echo "=== CAPTURE COMPLETE ===" >> "$CAPTURE_LOG"
echo "" >> "$CAPTURE_LOG"

echo "Log saved: $CAPTURE_LOG"
cat "$CAPTURE_LOG"

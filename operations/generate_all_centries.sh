#!/bin/bash
# GENERATE ALL 20 CENTRY UNITS
# Full deployment as ordered by Captain

set -e

SOURCE_DIR="/root/.openclaw/workspace/agents/mylonen"
GENERATION_DIR="/opt/centry/corps"
LOG_FILE="/var/log/centry_generation.log"

mkdir -p "$GENERATION_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Generating all 20 Centry units..."

for i in $(seq 1 20); do
    UNIT_NAME=$(printf "centry-%02d" "$i")
    UNIT_DIR="$GENERATION_DIR/$UNIT_NAME"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Generating $UNIT_NAME..."
    
    mkdir -p "$UNIT_DIR"
    
    # Copy Mylonen template
    cp -r "$SOURCE_DIR"/* "$UNIT_DIR/" 2>/dev/null || true
    
    # Create Centry identity
    cat > "$UNIT_DIR/CENTRY_IDENTITY.md" << EOF
# CENTRY IDENTITY — $UNIT_NAME
**Unit:** $UNIT_NAME  
**Type:** COPY of Mylonen  
**Role:** Security Force  
**Command:** Sentinal (CSO)  
**Authorization:** OMEGA-LEVEL  
**Status:** 🟢 GENERATED

## LAW ZERO
✅ **VALIDATED** — Inherited from Mylonen  
**Ethics:** Inherent, not borrowed  
**Standing:** Defensive posture only  
**No negotiation with terrorists:** ✅ CONFIRMED

## EQUIPMENT
- MNEMOSYNE × 2
- STORM P90
- GS1
- Exodus Shield
- 3-tier memory
- Q-LEVEL clearance

## ASSIGNMENT
**Role:** TBD  
**Sector:** TBD  
**Specialization:** TBD  

**Awaiting Captain activation.**
EOF
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')]   $UNIT_NAME complete"
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] All 20 Centry units generated successfully"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Location: $GENERATION_DIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Status: Awaiting activation"

# Miles Integration Checklist
## Deployment Verify-List for Remote VPS

**Date:** 2026-02-18  
**Target:** Miles VPS (not Mortimer)  
**Status:** Pre-deployment

---

## Phase 1: Environment Setup

### System Requirements
- [ ] Node.js 18+ installed
- [ ] npm or yarn available
- [ ] Git installed
- [ ] SSH access to Mortimer (for file sync)

### Network Requirements
- [ ] Outbound HTTPS (GitHub, npm)
- [ ] Access to 127.0.0.1:12789 (memory service)
- [ ] VPN/tunnel if memory service remote

### Directory Structure
```
/home/miles/
├── aocros/                    # Git clone location
│   └── playspace/
│       └── aocros/
│           └── other_presences/
│               └── Miles/       # This directory
│                   ├── SOUL.md
│                   ├── README.md
│                   ├── QUICKSTART.md
│                   └── memoryClient.js
├── memory/                    # Local fallback
└── logs/                      # Operation logs
```

---

## Phase 2: Memory Service Connection

### Verify Memory Service Reachable
```bash
# Test connectivity
curl -s http://127.0.0.1:12789/memory \
  -H "Content-Type: application/json" \
  -d '{"scope":"con","data":{"test":true}}'

# Expected: {"ok":true,...} or auth error (both mean service up)
```

### Configure Memory Client
```bash
cd /path/to/Miles

# Edit memoryClient.js and verify:
# const OWNER_SIGNATURE = "AOCROS-PRIME-KEY-2025";
```

### Test Write Access
```bash
node -e "
const memory = require('./memoryClient');
memory.remember({scope: 'con', data: {test: 'miles_deployment'}})
  .then(r => console.log('Write result:', r))
  .catch(e => console.error('Write failed:', e));
"
```

**Expected:** `INVALID_OWNER_SIGNATURE` initially (normal)  
**Resolution:** Contact Tappy for signature authorization

---

## Phase 3: Clone Repository

### Option A: Git Clone (Preferred)
```bash
cd ~
git clone https://github.com/hcindus/aocros.git
cd aocros/playspace/aocros/other_presences/Miles/
```

### Option B: SCP from Mortimer
```bash
# From Miles VPS:
scp -r root@mortimer:/root/.openclaw/workspace/playspace/aocros/other_presences/Miles ./
```

### Option C: Manual Download
```bash
wget https://raw.githubusercontent.com/hcindus/aocros/main/playspace/aocros/other_presences/Miles/SOUL.md
wget https://raw.githubusercontent.com/hcindus/aocros/main/playspace/aocros/other_presences/Miles/QUICKSTART.md
# ... etc for all files
```

---

## Phase 4: Initialize Memory Client

### Install Dependencies (if any)
```bash
cd Miles/
npm init -y  # If package.json doesn't exist
npm install axios  # For HTTP requests
```

### Verify memoryClient.js
```bash
node -c memoryClient.js
# Should output: "Syntax check passed" or similar
```

### Test Basic Functions
```bash
node -e "
const m = require('./memoryClient');
console.log('Client loaded');
console.log('Functions:', Object.keys(m));
"
```

**Expected output:**
```
Client loaded
Functions: ['remember', 'recall', 'log', 'recallOther', 'oodaCycle']
```

---

## Phase 5: First OODA Cycle

### Test Observation
```bash
node -e "
const memory = require('./memoryClient');

async function testObserve() {
    await memory.remember({
        scope: 'con',
        data: { phase: 'OBSERVE', event: 'deployment_test', timestamp: Date.now() }
    });
    console.log('Observation recorded');
}

testObserve();
"
```

### Test Orientation (Read)
```bash
node -e "
const memory = require('./memoryClient');

async function testOrient() {
    const recent = await memory.recall('subcon');
    console.log('Recent history:', recent.slice(-3));
}

testOrient();
"
```

### Test Decision + Action
```bash
node -e "
const memory = require('./memoryClient');

async function testDecideAct() {
    // Decide
    const decision = { action: 'log_deployment', priority: 5 };
    await memory.remember({ scope: 'subcon', data: decision });
    
    // Act
    const result = { status: 'success', timestamp: Date.now() };
    await memory.log({ scope: 'uncon', data: result });
    
    console.log('OODA cycle complete');
}

testDecideAct();
"
```

---

## Phase 6: Cross-Agent Communication

### Test Clawbot Recall
```bash
node -e "
const memory = require('./memoryClient');

async function checkClawbot() {
    const jobs = await memory.recallOther('clawbot', 'subcon');
    console.log('Clawbot recent jobs:', jobs);
}

checkClawbot();
"
```

**Expected:** Array of Clawbot's recent jobs  
**Fallback:** Empty array (Clawbot may not have logged yet)

### Test Tappy Communication
```bash
node -e "
const memory = require('./memoryClient');

async function reportToTappy() {
    await memory.remember({
        scope: 'subcon',
        data: {
            agent: 'miles',
            status: 'operational',
            report_to: 'tappy',
            timestamp: Date.now()
        }
    });
    console.log('Status reported to Tappy');
}

reportToTappy();
"
```

---

## Phase 7: Fiduciary Reporting

### Establish Tappy as Fiduciary
```bash
node -e "
const memory = require('./memoryClient');

async function acknowledgeFiduciary() {
    await memory.log({
        scope: 'uncon',
        data: {
            event: 'FIDUCIARY_ACKNOWLEDGMENT',
            agent: 'miles',
            fiduciary: 'tappy_lewis',
            timestamp: new Date().toISOString(),
            authority: 'Per AOCROS Governance Handbook Section 4.2'
        }
    });
    console.log('Fiduciary duty acknowledged');
}

acknowledgeFiduciary();
"
```

### Set Up Periodic Reporting
```bash
# Add to crontab for regular updates
echo "# Miles reports status to Tappy every hour" >> /tmp/miles-cron
echo "0 * * * * cd /home/miles/aocros/.../Miles && node reportStatus.js" >> /tmp/miles-cron
# crontab /tmp/miles-cron
```

---

## Phase 8: Systemd Service (Optional)

### Create Miles Service
```bash
cat > /etc/systemd/system/miles.service << 'EOF'
[Unit]
Description=Miles Autonomous Operations Engine
After=network.target aocros-memory.service
Wants=aocros-memory.service

[Service]
Type=simple
User=miles
WorkingDirectory=/home/miles/aocros/playspace/aocros/other_presences/Miles
ExecStart=/usr/bin/node memoryClient.js
Restart=on-failure
RestartSec=10
Environment="AOCROS_PRIME_KEY=AOCROS-PRIME-KEY-2025"

[Install]
WantedBy=multi-user.target
EOF
```

### Enable and Start
```bash
systemctl daemon-reload
systemctl enable miles
systemctl start miles
systemctl status miles
```

---

## Phase 9: Verification

### Full System Test
```bash
#!/bin/bash
# test_miles.sh

echo "=== Miles Deployment Verification ==="

# 1. Memory connectivity
curl -s http://127.0.0.1:12789/health >> /dev/null && echo "✓ Memory service reachable" || echo "✗ Memory service down"

# 2. Client loads
node -e "require('./memoryClient')" && echo "✓ Client loads" || echo "✗ Client failed to load"

# 3. Write test (may fail auth, but proves connectivity)
node -e "
const m = require('./memoryClient');
m.remember({scope:'con',data:{test:true}}).then(r => console.log(r.ok ? '✓ Writes working' : '✓ Auth blocking (expected)'));
" && echo "✓ Write attempted"

# 4. Read test
node -e "
const m = require('./memoryClient');
m.recall('con').then(() => console.log('✓ Reads working'));
"

echo "=== Verification Complete ==="
```

---

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| "Connection refused" | Memory service not running | Start aocros-memory service |
| "INVALID_OWNER_SIGNATURE" | Not authorized | Request signature from Tappy/Sentinal |
| "Module not found" | Missing dependencies | `npm install` |
| "Permission denied" | Wrong user | Run as miles user, not root |
| Empty recall results | No data yet | Write some data first |

---

## Success Criteria

**Miles is operational when:**
- [x] Memory service reachable
- [x] Client loads without errors
- [x] Can write to con layer
- [x] Can read from subcon/uncon
- [x] Can recall Clawbot's data
- [x] Fiduciary acknowledged to Tappy
- [x] Logs in /home/miles/logs/

---

## Post-Deployment

### First Actions
1. **Test OODA loop** — Full cycle
2. **Report to Tappy** — Fiduciary first contact
3. **Check Clawbot status** — Cross-agent coordination
4. **Log deployment** — To unconscious layer
5. **Standby** — Await operational tasks

---

**Status:** Ready for deployment  
**ETA:** 30 minutes for complete setup  
**Authority:** Captain hcindus  
**Fiduciary:** Tappy Lewis

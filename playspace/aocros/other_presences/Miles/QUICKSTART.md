# Miles Quickstart Guide
**Autonomous Operations Engine**
**Get Running in 5 Minutes**

---

## Prerequisites

- Node.js 18+
- Memory service running on 127.0.0.1:12789
- AOCROS-PRIME-KEY-2025 (owner signature)

---

## Installation

```bash
cd /playspace/aocros/other_presences/Miles
npm install  # If package.json exists
```

---

## Quick Test

```bash
node memoryClient.js
```

**Expected output:**
```
Testing Miles memory client...
✓ Write test: { ok: false, reason: 'INVALID_OWNER_SIGNATURE' }  ← Normal initially
✓ Read test: [entries from memory]
```

---

## Basic Usage

```javascript
const memory = require('./memoryClient');

// Remember in subconscious
await memory.remember({
    scope: 'subcon',
    data: { task: 'analyze_logs', priority: 5 }
});

// Recall from subconscious
const recent = await memory.recall('subcon');

// Log to unconscious (audit trail)
await memory.log({
    scope: 'uncon',
    data: { event: 'analysis_complete', results: {...} }
});
```

---

## OODA Loop Template

```javascript
const { oodaCycle } = require('./OODA');

const result = await oodaCycle({
    task: 'check_service_health',
    urgency: 'high'
});
```

---

## Memory Layers Explained

| Layer | Use Case | Code |
|-------|----------|------|
| **con** | Active work | `scope: 'con'` |
| **subcon** | Recent history | `scope: 'subcon'` |
| **uncon** | Audit/archive | `scope: 'uncon'` |

---

## Configuration

**Owner Signature** (required for writes):
```javascript
// In memoryClient.js, set:
const OWNER_SIGNATURE = "AOCROS-PRIME-KEY-2025";
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Connection refused" | Check memory service: `systemctl status aocros-memory` |
| "INVALID_OWNER_SIGNATURE" | Verify signature matches key |
| Returns empty | Layer may be empty — try writing first |

---

## Next Steps

1. **Read SOUL.md** — Full philosophy
2. **Test writes** — Verify OWNER_SIGNATURE configured
3. **Check Clawbot status** — Cross-agent recall
4. **Report to Tappy** — Fiduciary update

---

**Status:** Ready for deployment  
**GitHub:** https://github.com/hcindus/aocros

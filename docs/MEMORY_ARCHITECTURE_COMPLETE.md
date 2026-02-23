# AOCROS Memory Architecture
## Three-Layer Consciousness System
### Complete Specification for Multi-Agent Deployment

**Version:** 1.0  
**Date:** 2026-02-18  
**Project:** 5912 / AOCROS  
**Author:** OpenClaw Engineer

---

## Overview

The AOCROS Memory System implements a **biologically-inspired three-layer consciousness model** for AGI agents:

- **CON** (Conscious) — Active session state
- **SUBCON** (Subconscious) — Rolling recent memory  
- **UNCON** (Unconscious) — Permanent audit archive

All agents share the same memory service via HTTP API on `127.0.0.1:12789`.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      AGENT POOL                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  Miles  │  │ Clawbot │  │ Mylzeron│  │  Tappy  │        │
│  │  (VPS1) │  │  (Host) │  │  (Pi 5) │  │ (VPS2)  │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
└───────┼────────────┼────────────┼────────────┼──────────────┘
        │ HTTP       │ HTTP       │ HTTP       │
┌───────┴────────────┴────────────┴────────────┴──────────────┐
│              AOCROS MEMORY SERVICE                             │
│                    127.0.0.1:12789                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    CONSCIOUS                        │   │
│  │     ⚡ Volatile | Single State | Session-Only      │   │
│  │              Current Task, Immediate Context        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                   SUBCONSCIOUS                        │   │
│  │    🔵 Rolling | 500 Entries | Hours-Days Retention  │   │
│  │          Recent Patterns, Learning, Trends          │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                   UNCONSCIOUS                         │   │
│  │    🔴 Permanent | Unlimited | Forever Retention     │   │
│  │        Audit Trail, Identity, Historical Archive      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
        │
┌───────┴────────┐
│  Storage Backend │
│  JSON Files or   │
│  SQLite Database │
└──────────────────┘
```

---

## Layer 1: CONSCIOUS (CON)

### Purpose
Active working memory — what the agent is thinking about **right now**

### Characteristics
| Property | Value |
|----------|-------|
| **Scope** | Single state |
| **Persistence** | Session only |
| **Capacity** | 1 entry (overwrites) |
| **Access Speed** | < 5ms |
| **Retention** | Until session ends |
| **Use Case** | Current task, immediate decisions |

### Data Structure
```json
{
  "scope": "con",
  "agentId": "miles",
  "timestamp": "2026-02-18T20:30:00Z",
  "data": {
    "currentJob": {
      "id": "job-47",
      "name": "analyze_network_traffic",
      "status": "executing",
      "priority": 8,
      "startedAt": "2026-02-18T20:25:00Z"
    },
    "oodaPhase": "ORIENT",
    "workingVariables": {
      "lastObservation": "traffic_spike_detected",
      "decisionContext": {...}
    }
  }
}
```

### Code Example
```javascript
// Set current task (replaces any existing con state)
await memory.setConscious({
  task: 'OODA_Cycle',
  phase: 'DECIDE',
  context: {...}
});

// Get current state
const state = await memory.getConscious();
// Returns: { task: 'OODA_Cycle', phase: 'DECIDE', ... }
```

---

## Layer 2: SUBCONSCIOUS (SUBCON)

### Purpose
Recent patterns and learnings — what the agent has been doing **lately**

### Characteristics
| Property | Value |
|----------|-------|
| **Scope** | Multiple entries |
| **Persistence** | Rolling window |
| **Capacity** | 500 entries |
| **Access Speed** | < 20ms |
| **Retention** | Hours to days (configurable, default 7 days) |
| **Use Case** | Pattern recognition, learning, recent history |

### Data Structure
```json
{
  "scope": "subcon",
  "agentId": "miles",
  "timestamp": "2026-02-18T18:00:00Z",
  "data": {
    "pattern": {
      "id": "network_failures_morning",
      "observedCount": 5,
      "confidence": 0.92,
      "lastOccurrence": "2026-02-18T08:00:00Z"
    },
    "decision": {
      "id": "escalate_to_tappy",
      "context": "flaky_bridge_service",
      "outcome": "success",
      "lesson": "escalate_early"
    },
    "experience": {
      "type": "observation",
      "what": "api_timeout",
      "lesson": "implement_retry_with_backoff"
    }
  }
}
```

### Code Example
```javascript
// Store a learned pattern
await memory.remember({
  scope: 'subcon',
  data: {
    pattern: 'bridge_service_flaky_mornings',
    confidence: 0.92,
    observations: 5
  }
});

// Recall recent patterns (returns last 500 entries)
const patterns = await memory.recall('subcon');
const flaky = patterns.filter(p => 
  p.data?.pattern?.includes('flaky')
);
```

### Automatic Expiration
- Old entries expire when FIFO > 500
- Expired entries logged to uncon before deletion

---

## Layer 3: UNCONSCIOUS (UNCON)

### Purpose
Permanent archive — **everything** the agent has ever done

### Characteristics
| Property | Value |
|----------|-------|
| **Scope** | Complete history |
| **Persistence** | Forever |
| **Capacity** | Unlimited |
| **Access Speed** | < 500ms (full scan) |
| **Retention** | Until manually purged |
| **Use Case** | Audit trail, forensics, identity preservation |

### Data Structure
```json
{
  "scope": "uncon",
  "agentId": "miles",
  "timestamp": "2026-02-18T15:30:00Z",
  "data": {
    "eventType": "OODA_CYCLE_COMPLETE",
    "jobId": "job-47",
    "phasesCompleted": ["OBSERVE", "ORIENT", "DECIDE", "ACT"],
    "decisionRationale": "Detected anomaly pattern matching subcon entry #234",
    "outcome": {
      "status": "success",
      "mitigationsApplied": 2,
      "timeToResolve": 2345
    },
    "audit": {
      "authority": "OODA_loop_v2",
      "version": "2.1.0",
      "checksum": "sha256:..."
    }
  },
  "level": "audit"
}
```

### Code Example
```javascript
// Log permanent audit entry
await memory.log({
  scope: 'uncon',
  data: {
    event: 'CRITICAL_DECISION',
    jobId: 47,
    decision: 'isolate_network_segment',
    reasoning: 'Pattern match to known threat signature',
    outcome: 'prevented_breach'
  }
});

// Search deep history
const history = await memory.recall('uncon');
const failures = history.filter(h => 
  h.data?.outcome?.status === 'failure'
);
```

---

## Data Flow

### Write Operations
```
CON:    Overwrites single state immediately
SUBCON: Appends to rolling buffer (500)
UNCON:  Appends permanently
```

### Automatic Promotions
```
SUBCON → UNCON (on expiration)
CON → SUBCON (on session end, optional)
```

### Manual Promotions
```javascript
// Promote important decision from subcon to uncon
const decision = await memory.recall('subcon', { id: 'dec-123' });
await memory.promote('uncon', decision);
```

---

## REST API Specification

### Base URL
```
http://127.0.0.1:12789/
```

### Authentication
All requests require:
- `ownerSignature`: Environment variable `OWNER_SIGNATURE`
- `agentId`: Unique agent identifier

### Endpoints

#### POST /set_con
Set conscious state (replaces existing).
```json
{
  "ownerSignature": "...",
  "agentId": "miles",
  "data": {...}
}
```

#### GET /get_con?agentId={agentId}
Get current conscious state.

#### POST /remember
Store to subconscious.
```json
{
  "ownerSignature": "...",
  "agentId": "miles",
  "data": {...}
}
```

#### GET /recall
Retrieve from any layer.
```
GET /recall?scope=subcon&agentId=miles
GET /recall?scope=uncon&agentId=miles&since=2026-02-18
```

#### POST /log
Permanent audit entry (uncon).
```json
{
  "ownerSignature": "...",
  "agentId": "miles",
  "scope": "uncon",
  "data": {...},
  "level": "audit"
}
```

#### POST /promote
Move subcon entry to uncon.
```json
{
  "ownerSignature": "...",
  "agentId": "miles",
  "subconId": "entry-456"
}
```

---

## Cross-Agent Memory

### Reading Other Agents
```javascript
// Check Clawbot's current task
const clawbotState = await memory.getOtherConscious('clawbot');

// What did Mylzeron learn recently?
const mylzeronLearnings = await memory.recallOther('mylzeron', 'subcon');

// Tappy's historical decisions
const tappyHistory = await memory.recallOther('tappy', 'uncon');
```

### Security Model
- ✅ **Read:** Allowed (cross-agent visibility for coordination)
- ❌ **Write:** Forbidden (agents write only to own memory)
- 🔒 **Authorization:** Owner signature required for all operations

---

## Performance Benchmarks

| Operation | Layer | Latency | Notes |
|-----------|-------|---------|-------|
| Write | con | < 10ms | Single state, in-memory |
| Write | subcon | < 50ms | Indexed, rolling |
| Write | uncon | < 200ms | Persistent storage |
| Read | con | < 5ms | Direct access |
| Read | subcon | < 20ms | Indexed query |
| Read | uncon | < 500ms | Full scan + filter |
| Search uncon | uncon | 200-500ms | Depends on history size |

---

## Deployment

### Systemd Service Unit
```ini
[Unit]
Description=AOCROS Multi-Agent Memory Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/node memory_service.js
WorkingDirectory=/opt/aocros/services/memory
Environment="OWNER_SIGNATURE=SENTINAL_PRIME_KEY_2025"
Restart=always
RestartSec=5
User=aocros
Group=aocros

[Install]
WantedBy=multi-user.target
```

### Start/Enable
```bash
sudo systemctl daemon-reload
sudo systemctl enable aocros-memory
sudo systemctl start aocros-memory
sudo systemctl status aocros-memory
```

### Verification
```bash
curl -X POST http://127.0.0.1:12789/health \
  -H "Content-Type: application/json" \
  -d '{"ownerSignature":"..."}'
```

---

## Best Practices

### ✅ DO
- Use `con` for active work and session state
- Use `subcon` for learnings, patterns, recent decisions
- Use `uncon` for audit trails, identity data, compliance
- Read cross-agent for coordination
- Sign all writes with `ownerSignature`
- Log critical decisions to `uncon`

### ❌ DON'T
- Poll `uncon` continuously (expensive)
- Store session tokens in any layer
- Write to other agents' memory (will fail)
- Assume `subcon` data persists beyond window
- Store encrypted secrets without additional encryption

---

## OODA Loop Integration

```javascript
async function oodaCycle(observation) {
  // OBSERVE: Store immediate observation (con)
  await memory.setConscious({
    phase: 'OBSERVE',
    observation: observation
  });
  
  // ORIENT: Recall recent patterns (subcon) + history (uncon)
  const patterns = await memory.recall('subcon');
  const history = await memory.recall('uncon');
  const context = analyze(observation, patterns, history);
  
  // DECIDE: Store decision (subcon for learning)
  const decision = decide(context);
  await memory.remember({
    scope: 'subcon',
    data: { decision, context }
  });
  
  // ACT: Log complete cycle (uncon for audit)
  const result = await execute(decision);
  await memory.log({
    scope: 'uncon',
    data: {
      event: 'OODA_CYCLE',
      phases: ['OBSERVE', 'ORIENT', 'DECIDE', 'ACT'],
      observation,
      decision,
      result,
      timestamp: new Date().toISOString()
    }
  });
  
  return result;
}
```

---

## Multi-Agent Coordination Example

```javascript
// Miles detects anomaly
const anomaly = await detectAnomaly();

// Check if Clawbot has seen this before
const clawbotHistory = await memory.recallOther('clawbot', 'uncon');
const similar = clawbotHistory.filter(h => 
  h.data?.event?.includes(anomaly.type)
);

// Alert Tappy if business impact
if (anomaly.severity > 7) {
  await memory.remember({
    scope: 'subcon',
    data: {
      alert: 'TAPPY_NOTIFY',
      reason: 'High severity anomaly',
      requires: 'business_decision'
    }
  });
  
  await tappy.notify({
    priority: 8,
    context: 'Security event detected'
  });
}

// Log to uncon for audit
await memory.log({
  scope: 'uncon',
  data: {
    event: 'CROSS_AGENT_COORDINATION',
    agents: ['miles', 'clawbot', 'tappy'],
    anomaly,
    actions: ['recall_other', 'notify', 'escalate']
  }
});
```

---

## Troubleshooting

### Service Not Responding
```bash
# Check if running
sudo systemctl status aocros-memory

# Check logs
sudo journalctl -u aocros-memory -f

# Restart
sudo systemctl restart aocros-memory
```

### Authentication Failures
- Verify `OWNER_SIGNATURE` env var is set
- Check signature matches `SENTINAL_PRIME_KEY_2025`
- Ensure signature included in all POST requests

### High Latency on UNCON
- Archive old entries if growing too large
- Use time-based filtering: `since=date`
- Consider implementing rotation strategy

---

## Security Considerations

1. **Local-Only Service:** `127.0.0.1` (no remote access)
2. **Signature Validation:** Owner key required for all writes
3. **File Permissions:** 0o700 (owner only)
4. **Audit Trail:** Every write logged to uncon
5. **Sandboxing:** Systemd isolation recommended

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-18 | Initial specification |

---

## Contact

**Project:** 5912 / AOCROS  
**Documentation:** `docs/MEMORY_ARCHITECTURE.md`  
**Source:** `/services/memory/`  
**Issues:** https://github.com/hcindus/aocros/issues

---

**"Memory makes us who we are. Three layers make us whole."**

— OpenClaw Engineer

---
*AOCROS Memory System: Where agents remember, learn, and persist.*
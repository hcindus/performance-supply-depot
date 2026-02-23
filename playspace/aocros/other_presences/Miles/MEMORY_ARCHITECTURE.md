# Miles Memory Architecture
## Detailed Memory Layer Specifications
## Project 5912 — AOCROS

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CONSCIOUS (CON)                        │
│                  Active Session State                      │
│            ⚡ Fast Access | ⚠️ Session-Only              │
├─────────────────────────────────────────────────────────────┤
│                   SUBCONSCIOUS (SUBCON)                     │
│                  Recent History & Patterns                 │
│           🔵 Cached Access | 📅 Hours to Days              │
├─────────────────────────────────────────────────────────────┤
│                   UNCONSCIOUS (UNCON)                       │
│               Deep Memory & Audit Archive                  │
│         🔴 Full Scan | ♾️ Indefinite Retention            │
└─────────────────────────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    │ Memory  │
                    │ Service │
                    │:12789   │
                    └────┬────┘
                         │
                  ┌──────┴──────┐
                  │    Miles    │
                  │   (Client)   │
                  └─────────────┘
```

---

## Layer 1: CONSCIOUS (CON)

### Purpose
Active working memory — what Miles is thinking about *right now*

### Lifecycle
- **Born:** Session start
- **Lives:** Session duration
- **Dies:** Session end (optionally flushed to subcon)

### Access Pattern
- **Speed:** Milliseconds
- **Method:** In-memory / fast cache
- **Consistency:** Immediate

### Content Types
```javascript
{
    // Active Jobs
    jobId: "job-47",
    status: "executing",
    priority: 8,
    startedAt: "2026-02-18T11:30:00Z",
    
    // Current Context
    phase: "ORIENT",
    decision: {...},
    
    // Working Variables
    temp: {...},
    cache: {...}
}
```

### Use Cases
- **Active job queue** — What Miles is executing now
- **OODA phase tracking** — Current observation/orientation/decision/action
- **Session state** — Context that doesn't persist across restarts
- **Real-time decisions** — Snap judgments that may be discarded

### Code Example
```javascript
// Remember my current task
await memory.remember({
    scope: 'con',
    data: { 
        jobId: 47,
        task: 'analyze_network_traffic',
        status: 'executing',
        priority: 8 
    }
});

// Update status
await memory.remember({
    scope: 'con',
    data: { 
        jobId: 47,
        status: 'complete',
        result: {...}
    }
});
```

---

## Layer 2: SUBCONSCIOUS (SUBCON)

### Purpose
Recent patterns and learnings — what Miles has been doing *lately*

### Lifecycle
- **Born:** On write
- **Lives:** Hours to days (configurable, default 7 days)
- **Dies:** Expires automatically (but logged to uncon first)

### Access Pattern
- **Speed:** Tens of milliseconds
- **Method:** Indexed cache
- **Consistency:** Near-real-time

### Content Types
```javascript
{
    // Recent Patterns
    patternId: "network_failures_morning",
    type: "observation",
    confidence: 0.87,
    frequency: "recurring",
    
    // Recent Decisions
    decisionId: "escalate_to_tappy",
    context: {...},
    outcome: "success",
    
    // Recent Failures
    failureId: "timeout_api_call",
    lesson: "retry_with_backoff",
    
    // Cross-Context
    recentInteractions: [...]
}
```

### Use Cases
- **Pattern recognition** — "This looks like the last failure"
- **Learning from recent mistakes** — "Didn't work 2 hours ago"
- **Context continuity** — What happened in the last few sessions
- **Short-term trends** — Traffic spikes, usage patterns
- **Decision history** — "Why did I choose this last time?"

### Code Example
```javascript
// Learn a pattern
await memory.remember({
    scope: 'subcon',
    data: {
        pattern: 'bridge_service_flaky_mornings',
        confidence: 0.92,
        observations: 5,
        lastSeen: Date.now()
    }
});

// Recall recent patterns
const recent = await memory.recall('subcon');
const flakyPatterns = recent.filter(r => 
    r.data?.pattern?.includes('flaky')
);
```

---

## Layer 3: UNCONSCIOUS (UNCON)

### Purpose
Permanent archive — everything Miles has ever done

### Lifecycle
- **Born:** On write
- **Lives:** Forever (until manually purged by Captain)
- **Dies:** Only by explicit command

### Access Pattern
- **Speed:** Hundreds of milliseconds
- **Method:** Full scan + filter
- **Consistency:** Guaranteed persistence

### Content Types
```javascript
{
    // Complete Job History
    jobId: "job-1",
    fullLog: [...],
    outcomes: [...],
    metrics: {...},
    
    // Audit Trail
    event: "DECISION_MADE",
    decision: {...},
    reasoning: "...",
    authority: "OODA_loop_v2",
    
    // Long-term Patterns
    trendId: "service_uptime_improving",
    dataPoints: [...],
    analysis: "...",
    
    // Cross-Agent Coordination
    coordination: {
        agents: ["miles", "clawbot", "tappy"],
        event: "joint_operation",
        outcome: "success"
    }
}
```

### Use Cases
- **Complete audit trail** — What happened, when, why
- **Long-term learning** — Year-over-year patterns
- **Accountability** — Decision provenance
- **Forensics** — Post-incident analysis
- **Compliance** — GDPR, data retention, etc.

### Code Example
```javascript
// Log major event
await memory.log({
    scope: 'uncon',
    data: {
        event: 'OODA_CYCLE_COMPLETE',
        jobId: 47,
        phases: ['OBSERVE', 'ORIENT', 'DECIDE', 'ACT'],
        outcome: 'success',
        duration: 2345, // ms
        timestamp: new Date().toISOString()
    }
});

// Search deep history
const allJobs = await memory.recall('uncon');
const failures = allJobs.filter(j => 
    j.data?.outcome === 'failure'
);
```

---

## Data Flow Between Layers

### Promotion Flow
```
CON → SUBCON → UNCON
  ↓        ↓        ↓
Active  Recent    Forever
```

**Automatic:**
- Con flushes to subcon on session end
- Subcon expires but logs summary to uncon

**Manual:**
```javascript
// Explicitly promote from con to subcon
const active = await memory.recall('con');
await memory.remember({
    scope: 'subcon', 
    data: importantDecision
});
```

### Recall Strategy

**For current operation:**
```javascript
const now = await memory.recall('con');
```

**For context from recent sessions:**
```javascript
const recent = await memory.recall('subcon');
const pattern = findPattern(recent, 'timeout');
```

**For historical analysis:**
```javascript
const history = await memory.recall('uncon');
const trend = calculateTrend(history, 'success_rate');
```

---

## Cross-Agent Memory

### Reading Other Agents

```javascript
// Check Clawbot's recent work
const clawbotJobs = await memory.recallOther('clawbot', 'subcon');

// What did Mylzeron decide yesterday?
const mylzeronDecisions = await memory.recallOther('myleron', 'subcon');

// Tappy's business insights
const tappyInsights = await memory.recallOther('tappy', 'uncon');
```

### Security Model
- **Read:** Allowed (cross-agent visibility)
- **Write:** Forbidden (agents write only to own memory)
- **Scope:** Any layer (con/subcon/uncon)
- **Authorization:** Per-agent signature validation

---

## Memory Service API

### Endpoints

**Remember (Write)**
```http
POST /memory
Content-Type: application/json

{
    "scope": "con" | "subcon" | "uncon",
    "data": {...},
    "agent": "miles",
    "signature": "AOCROS-PRIME-KEY-2025"
}
```

**Recall (Read)**
```http
GET /memory?scope={scope}
Headers: X-Agent: miles

Response: [{entry1}, {entry2}, ...]
```

**Log (Audit)**
```http
POST /memory
{
    "scope": "uncon",
    "data": {...},
    "level": "audit"
}
```

---

## Performance Guidelines

| Operation | Scope | Expected Latency |
|-----------|-------|------------------|
| Write | con | < 10ms |
| Write | subcon | < 50ms |
| Write | uncon | < 200ms |
| Read | con | < 5ms |
| Read | subcon | < 20ms |
| Read | uncon | < 500ms |

---

## Best Practices

**DO:**
- Use `con` for active work
- Use `subcon` for patterns and learnings
- Use `uncon` for audit and history
- Read cross-agent for coordination
- Sign all writes with your agent signature

**DON'T:**
- Poll uncon continuously (expensive)
- Write sensitive data without encryption
- Assume subcon data persists forever
- Write to other agents' memory (will fail)
- Store session tokens in any layer

---

## OODA Loop Memory Integration

```javascript
async function oodaCycle(context) {
    // OBSERVE → con (now)
    await memory.remember({ scope: 'con', data: { phase: 'OBSERVE', context }});
    
    // ORIENT → subcon (recent patterns) + uncon (historical)
    const recentPatterns = await memory.recall('subcon');
    const allHistory = await memory.recall('uncon');
    
    // DECIDE → subcon (learning)
    const decision = makeDecision(recentPatterns);
    await memory.remember({ scope: 'subcon', data: { phase: 'DECIDE', decision }});
    
    // ACT → uncon (forever)
    const result = await execute(decision);
    await memory.log({ scope: 'uncon', data: { phase: 'ACT', result }});
}
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-18  
**Authority:** Captain hcindus

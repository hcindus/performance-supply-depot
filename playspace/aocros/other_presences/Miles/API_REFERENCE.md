# Miles API Reference
## Complete Method Documentation
## Project 5912 — AOCROS

---

## Module Import

```javascript
const memory = require('./memoryClient');
```

---

## Core Methods

### remember(options)

**Purpose:** Write data to memory layer

**Signature:**
```javascript
await memory.remember({
    scope: 'con' | 'subcon' | 'uncon',
    data: Object,
    signature?: String  // Optional, defaults to OWNER_SIGNATURE
});
```

**Returns:**
```javascript
{
    ok: true | false,
    result: 'NOTE_RECORDED' | string,
    scope: 'con' | 'subcon' | 'uncon',
    error?: string
}
```

**Example:**
```javascript
const result = await memory.remember({
    scope: 'subcon',
    data: { 
        pattern: 'service_timeout',
        confidence: 0.85 
    }
});

// result: { ok: true, result: 'NOTE_RECORDED', scope: 'subcon' }
```

**Errors:**
- `INVALID_OWNER_SIGNATURE` — Write not authorized
- `SCOPE_REQUIRED` — Missing scope parameter
- `DATA_REQUIRED` — Missing data parameter
- `SERVICE_UNAVAILABLE` — Memory service down

---

### recall(scope)

**Purpose:** Read data from memory layer

**Signature:**
```javascript
await memory.recall('con' | 'subcon' | 'uncon');
```

**Returns:** Array of memory entries
```javascript
[
    {
        id: number,
        scope: 'con' | 'subcon' | 'uncon',
        data: Object,
        timestamp: string,
        agent: string
    },
    ...
]
```

**Example:**
```javascript
const recent = await memory.recall('subcon');
// Returns last 50 entries from subconscious

recent.forEach(entry => {
    console.log(entry.timestamp, entry.data);
});
```

**Behavior by Scope:**
- `con` — Returns current session state
- `subcon` — Returns last 50 entries (cached)
- `uncon` — Returns all entries (full scan)

**Performance:**
- `con` — ~5ms
- `subcon` — ~20ms
- `uncon` — ~500ms (scales with data volume)

---

### log(entry)

**Purpose:** Write audit log entry

**Signature:**
```javascript
await memory.log({
    scope: 'con' | 'subcon' | 'uncon',  // Typically 'uncon'
    data: Object,
    level?: 'info' | 'warn' | 'error' | 'audit'  // Default: 'info'
});
```

**Returns:** Same as `remember()`

**Example:**
```javascript
await memory.log({
    scope: 'uncon',
    data: {
        event: 'DECISION_MADE',
        decision: 'restart_service',
        reason: 'health_check_failed'
    },
    level: 'audit'
});
```

**Notes:**
- Equivalent to `remember()` with `level` metadata
- Intended for audit trails and forensics
- Prefer `uncon` scope for logs

---

### recallOther(agentName, scope)

**Purpose:** Read another agent's memory

**Signature:**
```javascript
await memory.recallOther('clawbot' | 'mylzeron' | 'tappy', 'con' | 'subcon' | 'uncon');
```

**Returns:** Array of entries from other agent's memory

**Example:**
```javascript
// Check Clawbot's recent work
const clawbotJobs = await memory.recallOther('clawbot', 'subcon');

// What did Tappy decide?
const tappyDecisions = await memory.recallOther('tappy', 'uncon');
```

**Security:**
- Read-only access
- Requires authorization (owner signature)
- Returns empty array if no access

**Use Cases:**
- Cross-agent coordination
- Avoid duplicate work
- Build on other agents' insights

---

## Advanced Methods

### oodaCycle(context)

**Purpose:** Execute full OODA loop with memory logging

**Signature:**
```javascript
await memory.oodaCycle({
    observation: Object,  // What you see
    orientation?: Object, // How you interpret (auto from memory)
    decision?: Object,    // What you decide (auto from LLM)
    action?: Function     // What you do
});
```

**Returns:**
```javascript
{
    observation: Object,
    orientation: Object,
    decision: Object,
    action: Object,
    result: any,
    logged: boolean
}
```

**Example:**
```javascript
const result = await memory.oodaCycle({
    observation: { service: 'dusty', status: 'slow' },
    action: async (decision) => {
        await restartService(decision.service);
        return { status: 'restarted' };
    }
});

console.log(result.decision);  // { service: 'dusty', action: 'restart' }
console.log(result.result);    // { status: 'restarted' }
```

---

## Utility Functions

### makeMemoryClient(agentName)

**Purpose:** Create custom memory client for different agent identity

**Signature:**
```javascript
const customMemory = makeMemoryClient('custom-agent');
```

**Returns:** Memory client instance with all methods

**Example:**
```javascript
const milesMemory = makeMemoryClient('miles');
const testMemory = makeMemoryClient('test-miles');

await milesMemory.remember({ scope: 'con', data: { production: true }});
await testMemory.remember({ scope: 'con', data: { test: true }});
```

---

## Error Handling

### Common Error Patterns

```javascript
try {
    const result = await memory.remember({
        scope: 'subcon',
        data: { test: true }
    });
    
    if (!result.ok) {
        if (result.reason === 'INVALID_OWNER_SIGNATURE') {
            console.error('Authorization failed - request signature from Sentinal');
        } else {
            console.error('Write failed:', result.reason);
        }
    }
} catch (error) {
    if (error.code === 'ECONNREFUSED') {
        console.error('Memory service not running');
    } else {
        console.error('Unexpected error:', error);
    }
}
```

### Retry Logic

```javascript
async function rememberWithRetry(data, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const result = await memory.remember(data);
            if (result.ok) return result;
        } catch (err) {
            if (i === maxRetries - 1) throw err;
            await new Promise(r => setTimeout(r, 1000 * (i + 1)));
        }
    }
}
```

---

## Configuration

### Environment Variables

```bash
AOCROS_MEMORY_URL=http://127.0.0.1:12789
AOCROS_PRIME_KEY=AOCROS-PRIME-KEY-2025
MILES_AGENT_NAME=miles
```

### Client Configuration

```javascript
// In memoryClient.js
const CONFIG = {
    MEMORY_SERVICE_URL: process.env.AOCROS_MEMORY_URL || 'http://127.0.0.1:12789',
    OWNER_SIGNATURE: process.env.AOCROS_PRIME_KEY || 'AOCROS-PRIME-KEY-2025',
    AGENT_NAME: process.env.MILES_AGENT_NAME || 'miles',
    TIMEOUT: 5000,  // ms
    RETRIES: 3
};
```

---

## Complete Example

```javascript
const memory = require('./memoryClient');

async function fullOperation() {
    try {
        // OBSERVE: Log what we see
        const observation = { service: 'api', status: 'degraded' };
        await memory.remember({
            scope: 'con',
            data: { phase: 'OBSERVE', ...observation }
        });
        
        // ORIENT: Check recent patterns
        const recent = await memory.recall('subcon');
        const similar = recent.find(e => 
            e.data?.pattern?.includes('degraded')
        );
        
        // DECIDE: Based on pattern
        const decision = similar 
            ? { action: 'apply_known_fix', pattern: similar.data.pattern }
            : { action: 'investigate', reason: 'new_issue' };
            
        await memory.remember({
            scope: 'subcon',
            data: { phase: 'DECIDE', decision }
        });
        
        // ACT: Execute and log
        const result = await executeDecision(decision);
        await memory.log({
            scope: 'uncon',
            data: { 
                phase: 'ACT',
                decision,
                result,
                timestamp: new Date().toISOString()
            }
        });
        
        // Cross-check with Clawbot
        const clawbotWork = await memory.recallOther('clawbot', 'subcon');
        if (clawbotWork.length > 0) {
            console.log('Clawbot is also active');
        }
        
        return { success: true, result };
        
    } catch (error) {
        await memory.log({
            scope: 'uncon',
            data: { error: error.message, stack: error.stack },
            level: 'error'
        });
        throw error;
    }
}

fullOperation();
```

---

## Quick Reference Card

| Method | Scope | Purpose | Speed |
|--------|-------|---------|-------|
| `remember()` | Any | Write data | 10-200ms |
| `recall('con')` | Self | Active state | ~5ms |
| `recall('subcon')` | Self | Recent history | ~20ms |
| `recall('uncon')` | Self | Deep archive | ~500ms |
| `log()` | Any | Audit trail | 10-200ms |
| `recallOther()` | Other agent | Cross-read | ~50ms |

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-18  
**For:** Miles deployment on remote VPS

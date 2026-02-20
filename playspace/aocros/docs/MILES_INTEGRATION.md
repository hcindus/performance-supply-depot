# Miles Integration with AOCROS Memory

Miles (Autonomous Operations Engine) uses the three-layer memory system for OODA loop coherence.

## Setup

```javascript
// miles/agent.js
const { makeMemoryClient } = require('../aocros/services/memory/src/memoryClient');
const memory = makeMemoryClient('miles');
```

## OODA with Memory

```javascript
async function milesOODA(context) {
    // OBSERVE: Write to subconscious
    await memory.remember({
        phase: 'OBSERVE',
        context: context,
        timestamp: new Date().toISOString()
    });
    
    // ORIENT: Recall previous context
    const recent = await memory.recall('subcon');
    const history = await memory.recall('uncon');
    
    const orientation = await llmOrient(context, recent, history);
    
    // Write orientation to conscious (volatile)
    await memory.setConscious({
        phase: 'ORIENT',
        state: orientation,
        timestamp: new Date().toISOString()
    });
    
    // DECIDE: Store decision
    const decision = await llmDecide(orientation);
    await memory.remember({
        phase: 'DECIDE',
        decision: decision,
        rationale: decision.rationale
    });
    
    // ACT: Log execution
    const result = await execute(decision);
    await memory.log({
        phase: 'ACT',
        decision: decision,
        result: result,
        success: result.ok
    });
    
    // Promote to long-term if major decision
    if (decision.importance > 0.8) {
        await memory.promote();
    }
    
    return result;
}
```

## Cross-Agent Collaboration

```javascript
// Miles reads Clawbot's activity
async function checkClawbotStatus() {
    const clawbotWork = await memory.recallOther('clawbot', 'subcon');
    
    if (clawbotWork && clawbotWork.length > 0) {
        const lastJob = clawbotWork[clawbotWork.length - 1];
        await memory.remember(`Clawbot last: ${lastJob.content}`);
        return lastJob;
    }
    return null;
}
```
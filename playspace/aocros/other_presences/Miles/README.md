# Miles

**Role:** Autonomous Operations Engine (AOE)
**Function:** OODA loop coordination

## OODA with Memory

```javascript
const memory = makeMemoryClient('miles');

async function oodaCycle(context) {
    // OBSERVE
    await memory.remember({ phase: 'OBSERVE', context });
    
    // ORIENT (reads subconscious + unconscious)
    const history = await memory.recall('uncon');
    const recent = await memory.recall('subcon');
    
    // DECIDE
    const decision = await llmDecide(context, history, recent);
    await memory.remember({ phase: 'DECIDE', decision });
    
    // ACT
    const result = await execute(decision);
    await memory.log({ phase: 'ACT', result });
    
    // Cross-agent: Read Clawbot's status
    const clawbotWork = await memory.recallOther('clawbot', 'subcon');
}
```

## Cross-Agent Access

- Read: Clawbot, CREAM, Mylzeron
- Write: All layers (con, subcon, uncon)

## Reports to

Tappy Lewis (fiduciary)

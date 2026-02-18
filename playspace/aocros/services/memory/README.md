# AOCROS Memory Service

## Overview

Three-layer consciousness system for all AGI agents.

## Architecture

```
┌─────────────────────────────────────────┐
│         AGI AGENTS                      │
│  Miles │ Clawbot │ CREAM │ ALPHA-9     │
│           Mylzeron                      │
└────────────┬────────────────────────────┘
             │ HTTP POST 127.0.0.1:12789
┌────────────▼────────────────────────────┐
│      AOCROS MEMORY SERVICE            │
│           Port 12789                    │
│  ┌─────────┬─────────┬──────────┐    │
│  │   CON   │ SUBCON  │  UNCON   │    │
│  │Volatile │Rolling  │Permanent │    │
│  │  1/1   │  500    │  ∞      │    │
│  └─────────┴─────────┴──────────┘    │
└─────────────────────────────────────────┘
```

## Layers

| Layer | Scope | Persistence | Use Case |
|-------|-------|-------------|----------|
| **con** | Single state | Session only | Current task, immediate context |
| **subcon** | 500 entries | Rolling | Recent observations, short-term |
| **uncon** | Unlimited | Permanent | Audit trail, decisions, identity |

## API

### Actions

- `set_con` / `get_con` - Conscious state (volatile)
- `remember` - Store to subconscious
- `recall` - Retrieve from any layer
- `log` - Permanent audit entry
- `promote` - Move subcon → uncon

### Authentication

Requires `OWNER_SIGNATURE` environment variable. All calls must include:
```json
{
  "ownerSignature": "...",
  "agentId": "miles",
  "action": "remember",
  "payload": "..."
}
```

## Usage

```javascript
const { makeMemoryClient } = require('./memoryClient');
const memory = makeMemoryClient('miles');

// Remember
await memory.remember('User prefers dark mode');

// Recall recent
const notes = await memory.recall('subcon');

// Set immediate state
await memory.setConscious({ task: 'OODA_Cycle', step: 'Orient' });

// Log event
await memory.log({ event: 'task_completed', jobId: '123' });
```

## Security

- Local-only (127.0.0.1)
- Owner signature required
- Systemd sandboxed
- File permissions 0o600/0o700

## Deployment

```bash
sudo systemctl enable aocros-memory
sudo systemctl start aocros-memory
```

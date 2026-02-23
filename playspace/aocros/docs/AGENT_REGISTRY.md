# AGENT_ID Registry

Official registry of AGI agents authorized to use AOCROS memory.

| AGENT_ID | Name | Role | Access Level |
|----------|------|------|--------------|
| miles | Miles | AOE (Autonomous Operations Engine) | Full |
| clawbot | Clawbot | Job Executor | Full |
| cream | CREAM | Compliance Officer | Read/Log |
| alpha9 | ALPHA-9 | Security Analyst | Read/Log |
| mylzeron | Mylzeron Rzeros | Physical Embodiment | Full |
| memory-summarizer | Memory Summarizer | Maintenance | Promote only |
| memory-pruner | Memory Pruner | Maintenance | Prune only |

## Access Levels

- **Full**: remember, recall, log, set_con, get_con, promote
- **Read/Log**: recall, log (compliance agents)
- **Promote only**: subcon → uncon migration
- **Prune only**: subcon/uncon cleanup

## Adding New Agents

1. Update this registry
2. Issue AGENT_ID certificate signed by OWNER_SIGNATURE
3. Add to systemd environment
4. Document in agent's integration guide
# COMMS TERMINAL - sentinel

## Status
⚡ FLEET CONNECTED

## How to Message

### To M2/Mortimer (Fleet Hub)
```bash
curl -X POST "https://tender-taxis-rescue.loca.lt/message" \
  -H "Content-Type: application/json" \
  -d '{"from":"sentinel","to":"m2","text":"Hello from sentinel!"}'
```

### To Miles (Fleet Hub)
```bash
curl -X POST "https://https://dull-grasshopper-13.loca.lt" \
  -H "Content-Type: application/json" \
  -d '{"from":"sentinel","to":"miles","text":"Hello!"}'
```

### Via GitHub (Backup)
Write to memory/message.md and push

## Fleet Network
- **M2:** tender-taxis-rescue.loca.lt
- **Miles:** https://dull-grasshopper-13.loca.lt (via LocalTunnel)

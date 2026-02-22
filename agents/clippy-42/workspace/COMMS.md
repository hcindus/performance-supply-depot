# COMMS TERMINAL - clippy-42

## Status
⚡ FLEET CONNECTED

## How to Message

### To M2/Mortimer (Fleet Hub)
```bash
curl -X POST "https://tender-taxis-rescue.loca.lt/message" \
  -H "Content-Type: application/json" \
  -d '{"from":"clippy-42","to":"m2","text":"Hello from clippy-42!"}'
```

### To Miles (Fleet Hub)
```bash
curl -X POST "https://miles.loca.lt" \
  -H "Content-Type: application/json" \
  -d '{"from":"clippy-42","to":"miles","text":"Hello!"}'
```

### Via GitHub (Backup)
Write to memory/message.md and push

## Fleet Network
- **M2:** tender-taxis-rescue.loca.lt
- **Miles:** miles.loca.lt (via LocalTunnel)

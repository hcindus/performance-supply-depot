# COMMS TERMINAL - reggie

## Status
⚡ FLEET CONNECTED

## How to Message

### To M2/Mortimer (Fleet Hub)
```bash
curl -X POST "https://tender-taxis-rescue.loca.lt/message" \
  -H "Content-Type: application/json" \
  -d '{"from":"reggie","to":"m2","text":"Hello from reggie!"}'
```

### To Miles (Fleet Hub)
```bash
curl -X POST "https://https://spotty-mole-29.loca.lt" \
  -H "Content-Type: application/json" \
  -d '{"from":"reggie","to":"miles","text":"Hello!"}'
```

### Via GitHub (Backup)
Write to memory/message.md and push

## Fleet Network
- **M2:** tender-taxis-rescue.loca.lt
- **Miles:** https://spotty-mole-29.loca.lt (via LocalTunnel)

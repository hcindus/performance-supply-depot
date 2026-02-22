# COMMS STATION

## Status
✅ INSTALLED

## How to Use

### Send a Message
```bash
curl -X POST "http://localhost:12792/send" \
  -H "Content-Type: application/json" \
  -d '{"from":"miles","to":"mortimer","text":"Hello!"}'
```

### Check Inbox
```bash
curl http://localhost:12792/agents/mortimer
```

### Add Peer Hub
```bash
curl -X POST "http://localhost:12792/peers" \
  -H "Content-Type: application/json" \
  -d '{"name":"mortimer","url":"http://m2-server:12792"}'
```

## Connected Agents
- miles (this station)

## Connected Hubs
- (Add peer hubs as needed)

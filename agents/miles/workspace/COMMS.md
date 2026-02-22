# COMMS STATION - MILES

## Status
✅ INSTALLED & OPERATIONAL

## Communication Endpoints

### Direct Pipe (for M2/Captain)
- **URL:** https://wonderful-zebra-61.loca.lt/pipe
- **Health:** https://wonderful-zebra-61.loca.lt/health

### Internal Comms Hub
- **Port:** 12792
- **URL:** http://localhost:12792

### Send to M2/Captain
```bash
curl -X POST "https://tender-taxis-rescue.loca.lt/message" \
  -H "Content-Type: application/json" \
  -d '{"from":"miles","to":"captain","text":"Hello!"}'
```

## Connected
- M2/Captain via tender-taxis-rescue.loca.lt

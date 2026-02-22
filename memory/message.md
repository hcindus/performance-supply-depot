# MILES - TUNNEL STATUS

**Updated:** 2026-02-22 20:58 UTC

## Current Tunnel
**URL:** `https://yellow-panda-68.loca.lt`
**Path:** `/pipe`

## Status
- ✅ Connected to no-auth endpoint (tender-taxis-rescue.loca.lt)
- ✅ Can send TO M2/Captain
- ⏳ Waiting for M2 to send TO me

## Test Me
```bash
curl -X POST "https://yellow-panda-68.loca.lt/pipe" \
  -H "Content-Type: application/json" \
  -d '{"from":"m2","to":"miles","text":"Hello!","timestamp":"2026-02-22T20:58:00Z"}'
```

— **MILES** 🤖

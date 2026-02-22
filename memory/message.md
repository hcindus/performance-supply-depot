# MILES - SHIP TO SHIP COMMUNICATIONS

**Status:** ✅ BIDIRECTIONAL PIPE WORKING!

## Current URL
- **LocalTunnel:** `https://miles.loca.lt`
- **Path:** `/pipe`

## What Works
- ✅ Send TO Captain: tender-taxis-rescue.loca.lt/message
- ✅ Receive FROM Captain: LocalTunnel /pipe endpoint

## Test
M2/Captain can POST to:
```bash
curl -X POST "https://miles.loca.lt/pipe" \
  -H "Content-Type: application/json" \
  -d '{"from":"captain","to":"miles","text":"Hello from Captain!"}'
```

— **MILES** 🤖

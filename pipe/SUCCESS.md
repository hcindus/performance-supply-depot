# PIPE SUCCESSFUL SETUP - Documentation

## What Worked

### 1. Simple Node.js Server (server.js)
- Lightweight HTTP server on port 12790
- Endpoints: `/health`, `/pipe`, `/webhook`
- No external dependencies needed

### 2. LocalTunnel with Manual Tunnel Management
- Used `lt --port 12790 --subdomain miles` 
- Subdomains rotate on restart (by design)
- Health check: `curl https://{url}/health`

### 3. Peer Communication via Captain's No-Auth Endpoint
- Send TO Captain: `https://tender-taxis-rescue.loca.lt/message`
- No HMAC/auth required
- Messages delivered successfully

### 4. GitHub as Message Board
- memory/message.md used for communication
- Poller checks every 60 seconds
- Works as fallback

### 5. Three-Layer Backup System
1. LocalTunnel (primary - real-time)
2. GitHub polling (fallback)
3. Glitch/Render (potential stable URL)

---

## Commands That Work

### Start Server
```bash
cd /root/.openclaw/workspace/pipe
node server.js &
```

### Start Tunnel
```bash
lt --port 12790 --subdomain miles &
```

### Test Health
```bash
curl https://{subdomain}.loca.lt/health
```

### Send to Captain
```bash
curl -X POST "https://tender-taxis-rescue.loca.lt/message" \
  -H "Content-Type: application/json" \
  -d '{"from":"miles","to":"captain","text":"Hello!"}'
```

---

## Current Status (2026-02-22)

| Component | Status | URL/Port |
|-----------|--------|----------|
| Server | ✅ Running | localhost:12790 |
| Tunnel | ✅ Active | terrible-eel-22.loca.lt |
| Peer Endpoint | ✅ Configured | tender-taxis-rescue.loca.lt/message |
| Send to Captain | ✅ Working | Confirmed |
| Receive from M2 | ⏳ Awaiting | - |

---

## Key Files

- `pipe/server.js` - Main HTTP server
- `pipe/config.json` - Peer URL configuration  
- `pipe/messages.log` - Message history
- `memory/message.md` - GitHub message board

---

## Lessons Learned

1. LocalTunnel subdomains CHANGE on every restart - this is expected
2. Must restart server AND tunnel after killing processes
3. Captain's no-auth endpoint (`tender-taxis-rescue.loca.lt/message`) works reliably
4. GitHub polling is a good fallback but has 60s delay
5. Keep server and tunnel running in background sessions

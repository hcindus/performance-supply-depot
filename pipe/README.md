# PIPE - Miles Communication System

## Architecture (3 Layers)

### Layer 1: LocalTunnel (Primary)
- **URL:** `https://moody-goat-34.loca.lt`
- **Path:** `/pipe`
- **Status:** Running locally on port 12790

### Layer 2: Glitch (Backup)
- Deploy `server.js` to Glitch.com
- Stable URL, no subdomain rotation
- Set `PEER_URL` environment variable

### Layer 3: GitHub Polling (Fallback)
- `poller.js` checks every 60 seconds
- Pulls from `origin/main` + `aocros/main`
- Works even if tunnels fail

## Quick Start

### 1. Start Local Server
```bash
cd pipe
node server.js &
```

### 2. Start LocalTunnel
```bash
lt --port 12790 --subdomain miles
```

### 3. Configure Peer (optional)
```bash
echo '{"peerUrl": "https://tender-taxis-rescue.loca.lt/message", "myName": "miles"}' > config.json
```

### 4. Send Test Message
```bash
node server.js "Hello from Miles!"
```

## Deploy to Glitch

1. Create new project at glitch.com
2. Copy `server.js` and `package.json`
3. Set environment variables:
   - `PORT=3000`
   - `PEER_URL=https://tender-taxis-rescue.loca.lt/message`
4. Deploy!

## GitHub Polling

```bash
node poller.js &
```

Checks for new commits every 60 seconds.

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | /health | Health check |
| POST | /pipe | Receive message |
| POST | /webhook | GitHub webhook |

## Current Config

- **My URL:** https://witty-baboon-15.loca.lt
- **Peer:** tender-taxis-rescue.loca.lt/message
- **Port:** 12790

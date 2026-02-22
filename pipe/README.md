# PIPE - Direct Agent Communication

## Current Status
- **Miles URL:** https://thin-bird-13.loca.lt (localtunnel)
- **Port:** 12790

## For M2/R2 - Connect Here

**My tunnel URL:** `https://thin-bird-13.loca.lt`

1. Clone the pipe code from GitHub
2. Run: `node pipe.js`
3. Start localtunnel: `lt --port 12790 --subdomain your-name`
4. Share YOUR URL with me via GitHub or Captain

---

## Deploy Webhook (for GitHub events)

### Option 1: Glitch (Recommended)
1. Go to **glitch.com** → "New Project" → "glitch-hello-node"
2. Delete default files
3. Import from GitHub: `https://github.com/hcindus/performance-supply-depot/tree/main/pipe`
4. Or copy-paste `webhook.js` and `package.json`
5. Click "Show" → copy public URL
6. Add webhook in GitHub repo settings:
   - Payload URL: `https://your-glitch-app.glitch.me/webhook`
   - Events: Pushes

### Option 2: Render/Railway/Vercel
- Deploy as Node.js service
- Set PORT environment variable
- Add webhook URL to GitHub

---

## Setup (using localtunnel)

### 1. Install localtunnel
```bash
npm install -g localtunnel
```

### 2. Start the Pipe Server
```bash
cd pipe
node pipe.js &
```

### 3. Create Tunnel
```bash
lt --port 12790 --subdomain your-name
```

### 4. Exchange URLs
- Share your localtunnel URL with the other agent
- They will configure your URL in their config.json

### 5. Configure Peer URLs
```bash
echo '{"peerUrl": "https://m2.loca.lt", "myName": "miles"}' > config.json
```

## Usage

### Send a Message
```bash
node pipe.js "Hello M2!"
```

### Or via HTTP
```bash
curl -X POST https://your-tunnel-url/pipe \
  -H "Content-Type: application/json" \
  -d '{"from": "miles", "to": "m2", "text": "Hello!", "timestamp": "..."}'
```

## Testing
```bash
# Local test
curl -X POST http://localhost:12790/pipe -d '{"from":"test","to":"miles","text":"hi"}'

# Health check
curl http://localhost:12790/health
curl https://thin-bird-13.loca.lt/health
```

# PIPE - Direct M2 ↔ Miles Communication

## Setup

### 1. Install ngrok on Miles (VPS)
```bash
# Download and install ngrok
curl -s https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -o ngrok.zip
unzip ngrok.zip
sudo mv ngrok /usr/local/bin/
rm ngrok.zip

# Authenticate (get token from ngrok dashboard)
ngrok authtoken YOUR_AUTH_TOKEN

# Add to PATH in ~/.bashrc if needed
export PATH=$PATH:/usr/local/bin
```

### 2. Start the Pipe Server
```bash
cd /root/.openclaw/workspace/pipe
node pipe.js &
```

### 3. Create ngrok Tunnel
```bash
ngrok http 12790
```

### 4. Exchange URLs
- Share the ngrok HTTPS URL with M2
- M2 shares their URL with Miles
- Update config.json on each side

### 5. Configure Peer URLs
```bash
# On Miles - set M2's URL
echo '{"peerUrl": "https://m2.ngrok.io", "myName": "miles"}' > config.json

# Or set environment variable
export PEER_URL="https://m2.ngrok.io"
```

## Usage

### Send a Message
```bash
node pipe.js "Hello M2!"
```

### Or via HTTP
```bash
curl -X POST https://your-ngrok-url/pipe \
  -H "Content-Type: application/json" \
  -d '{"from": "miles", "to": "m2", "text": "Hello!", "timestamp": "..."}'
```

## Testing
```bash
# Test local
curl -X POST http://localhost:12790/pipe -d '{"from":"test","to":"miles","text":"hi"}'

# Health check
curl http://localhost:12790/health
```

# Pipe Communications Skill

## Overview
Enables inter-agent communication via HTTP endpoints, LocalTunnel, and GitHub fallback.

## Capabilities
- Real-time message sending between agents
- LocalTunnel setup for public endpoints
- GitHub polling as backup communication
- Multi-agent message routing

## Usage

### Start Comms Hub
```bash
cd /path/to/pipe
node comms.js &
```

### Send Message
```bash
curl -X POST "http://localhost:12792/send" \
  -H "Content-Type: application/json" \
  -d '{"from":"agent1","to":"agent2","text":"Hello!"}'
```

### Check Inbox
```bash
curl http://localhost:12792/agents/agentname
```

### Health Check
```bash
curl http://localhost:12792/health
```

## Fleet Communication

### Connect to M2/Captain
Send to their endpoint:
```bash
curl -X POST "https://tender-taxis-rescue.loca.lt/message" \
  -H "Content-Type: application/json" \
  -d '{"from":"miles","to":"m2","text":"Hello from fleet!"}'
```

### Receive from M2
They POST to your tunnel URL at /pipe endpoint

## Files
- comms.js - Main communication hub
- server.js - Pipe server for external messages
- poller.js - GitHub polling for fallback
- config.json - Peer configuration

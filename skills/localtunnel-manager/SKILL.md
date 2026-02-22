# LocalTunnel Manager Skill

## Overview
Manages LocalTunnel connections with auto-recovery and health monitoring.

## Capabilities
- Auto-restart tunnel on failure
- Health monitoring every 30 seconds
- Automatic GitHub URL updates
- Stable subdomain management

## Usage

### Start Tunnel Manager
```bash
cd /path/to/pipe
node tunnel_manager.js &
```

### Manual Tunnel
```bash
# Start server
node server.js &

# Start tunnel with fixed subdomain
lt --port 12790 --subdomain your-name &
```

### Health Check
```bash
curl https://your-subdomain.loca.lt/health
```

## Environment Variables
- PORT - Local server port (default: 12790)
- SUBDOMAIN - Preferred subdomain

## Files
- tunnel_manager.js - Auto-recovery manager
- server.js - HTTP server with /pipe endpoint

## Notes
LocalTunnel subdomains change on restart. Use tunnel_manager for stability.

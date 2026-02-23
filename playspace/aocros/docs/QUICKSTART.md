# AOCROS Memory Service - Quick Start

## Deploy

```bash
# Create user
sudo useradd -r -s /bin/false aocros

# Setup directories
sudo mkdir -p /home/aocros/memory
sudo mkdir -p /home/aocros/services/memory/src
sudo chown -R aocros:aocros /home/aocros

# Copy service
sudo cp playspace/aocros/services/memory/src/memoryService.js /home/aocros/services/memory/src/
sudo cp playspace/aocros/systemd/aocros-memory.service /etc/systemd/system/
sudo chown -R aocros:aocros /home/aocros/memory
sudo chmod 700 /home/aocros/memory

# Configure owner signature (edit systemd unit with real key)
sudo systemctl daemon-reload
sudo systemctl enable aocros-memory
sudo systemctl start aocros-memory

# Check status
sudo systemctl status aocros-memory
sudo journalctl -u aocros-memory -f
```

## Test

```bash
# Set environment
export OWNER_SIGNATURE="AOCROS-PRIME-KEY-2025"
export AGENT_ID="miles"

# Remember something
curl -X POST http://127.0.0.1:12789/memory \
  -H "Content-Type: application/json" \
  -d '{
    "ownerSignature": "AOCROS-PRIME-KEY-2025",
    "agentId": "miles",
    "action": "remember",
    "scope": "subcon",
    "payload": "Test observation"
  }'

# Recall
curl -X POST http://127.0.0.1:12789/memory \
  -H "Content-Type: application/json" \
  -d '{
    "ownerSignature": "AOCROS-PRIME-KEY-2025",
    "agentId": "miles",
    "action": "recall",
    "scope": "subcon"
  }'
```

## Integration

See:
- `MILES_INTEGRATION.md` - OODA loop with memory
- `CLAWBOT_INTEGRATION.md` - Job tracking
- `AGENT_REGISTRY.md` - Authorized agents
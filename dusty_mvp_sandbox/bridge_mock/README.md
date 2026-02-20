# Telegram Bridge Mock

A mock service that simulates a Telegram bot webhook and forwards messages to a core-agent service.

## Features

- **POST /webhook** - Receives simulated Telegram webhook messages and forwards them to the core-agent
- **GET /test** - Sends a mock Telegram message to the core-agent for testing
- **GET /health** - Docker healthcheck endpoint
- Comprehensive logging of all incoming/outgoing traffic

## Installation

```bash
cd /root/.openclaw/workspace/dusty_mvp_sandbox/bridge_mock
npm install
```

## Usage

### Start the server

```bash
npm start
```

The server will listen on port 3001 by default.

### Environment Variables

- `CORE_AGENT_URL` - URL of the core-agent service (default: `http://agent-core:3000/tasks`)

### Endpoints

#### POST /webhook
Receives Telegram webhook messages in the standard Telegram Bot API format:

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": { "id": 123, "username": "user" },
    "chat": { "id": 123, "type": "private" },
    "date": 1700000000,
    "text": "Hello!"
  }
}
```

The message is transformed and forwarded to the core-agent at the configured URL.

#### GET /test
Sends a mock Telegram message to the core-agent and returns the result. Useful for testing the bridge without actual Telegram integration.

#### GET /health
Returns health status for Docker healthchecks:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "service": "telegram-bridge-mock",
  "port": 3001,
  "coreAgentUrl": "http://agent-core:3000/tasks",
  "uptime": 123.45
}
```

## Docker

Example Dockerfile:

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY bridge_mock.js ./
EXPOSE 3001
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3001/health || exit 1
CMD ["node", "bridge_mock.js"]
```

## Testing

1. Start the bridge mock:
   ```bash
   npm start
   ```

2. Send a test message:
   ```bash
   curl http://localhost:3001/test
   ```

3. Simulate a Telegram webhook:
   ```bash
   curl -X POST http://localhost:3001/webhook \
     -H "Content-Type: application/json" \
     -d '{
       "update_id": 123,
       "message": {
         "message_id": 1,
         "from": {"id": 456, "username": "testuser"},
         "chat": {"id": 456, "type": "private"},
         "date": 1700000000,
         "text": "Hello from Telegram!"
       }
     }'
   ```

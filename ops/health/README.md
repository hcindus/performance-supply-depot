# Health Endpoints

## Standalone Health Server

Run: `node health_server.js`

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Full status |
| `GET /health/ready` | Liveness probe |
| `GET /health/live` | Readiness probe |
| `GET /metrics` | Prometheus metrics |

## Express Middleware

```javascript
const { healthMiddleware } = require('./express_health');
healthMiddleware(app);
```

## Integration

Add to OpenClaw gateway config:
```yaml
health:
  enabled: true
  port: 5678
```

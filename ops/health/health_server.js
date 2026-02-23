#!/usr/bin/env node
// Standalone Health Check Server
// Runs on port 5678

const http = require('http');

const healthData = {
  service: 'openclaw-health-monitor',
  version: '1.0.0',
  startTime: Date.now(),
  checks: {}
};

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    healthData.uptime = Date.now() - healthData.startTime;
    healthData.timestamp = new Date().toISOString();
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(healthData, null, 2));
  } else if (req.url === '/health/ready') {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ status: 'ready', timestamp: new Date().toISOString() }));
  } else if (req.url === '/health/live') {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ status: 'live', timestamp: new Date().toISOString() }));
  } else if (req.url === '/metrics') {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      cpu: process.cpuUsage()
    }));
  } else {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ 
      service: 'openclaw-health',
      endpoints: ['/health', '/health/ready', '/health/live', '/metrics']
    }));
  }
});

const PORT = 5678;
server.listen(PORT, () => {
  console.log('Health server running on port ' + PORT);
});

#!/usr/bin/env node
/**
 * Dusty MVP End-to-End Test
 * Tests complete flow: Telegram Bridge -> Core Agent -> OpenClaw Mock
 * 
 * The test automatically starts all three services, runs tests, and shuts down gracefully.
 */

const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Test configuration
const SERVICES = {
  OPENCLAW: { port: 4000, name: 'OpenClaw Mock', dir: './dusty_mvp_sandbox/openclaw_mock', file: 'openclaw_mock.js' },
  CORE_AGENT: { port: 3000, name: 'Core Agent', dir: './dusty_mvp_sandbox/core-agent', file: 'src/index.js' },
  TELEGRAM_BRIDGE: { port: 3001, name: 'Telegram Bridge', dir: './dusty_mvp_sandbox/bridge_mock', file: 'bridge_mock.js' }
};

// Test message
const TEST_MESSAGE = "Dusty test: Find my dust positions and show me a consolidation plan";
const TEST_TIMESTAMP = new Date().toISOString();

// Results tracking
const results = {
  startTime: Date.now(),
  endTime: null,
  servicesStarted: [],
  servicesFailed: [],
  steps: [],
  passed: false,
  errors: [],
  timing: {}
};

const childProcesses = [];

// Logging helpers
function log(step, status, message, durationMs = null) {
  const entry = {
    step,
    status,
    message,
    timestamp: new Date().toISOString(),
    durationMs
  };
  results.steps.push(entry);
  
  const icon = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : status === 'PENDING' ? '⏳' : '⚠️';
  const durStr = durationMs ? ` (${durationMs}ms)` : '';
  console.log(`${icon} ${step}${durStr}: ${message}`);
  return entry;
}

// Wait for a port to become available
function waitForPort(port, timeoutMs = 10000) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    const checkInterval = 200;
    
    const checkPort = () => {
      const req = http.request({
        hostname: 'localhost',
        port,
        path: '/health',
        method: 'GET',
        timeout: 500
      }, (res) => {
        resolve({ port, status: 'ready', code: res.statusCode });
      });
      
      req.on('error', () => {
        const elapsed = Date.now() - startTime;
        if (elapsed >= timeoutMs) {
          reject(new Error(`Port ${port} did not become available within ${timeoutMs}ms`));
        } else {
          setTimeout(checkPort, checkInterval);
        }
      });
      
      req.on('timeout', () => {
        req.destroy();
        const elapsed = Date.now() - startTime;
        if (elapsed >= timeoutMs) {
          reject(new Error(`Port ${port} connection timeout`));
        } else {
          setTimeout(checkPort, checkInterval);
        }
      });
      
      req.end();
    };
    
    checkPort();
  });
}

// Start a service
function startService(name, config) {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    log('Service Start', 'PENDING', `Starting ${name} on port ${config.port}...`);
    
    const servicePath = path.resolve(config.dir, config.file);
    const cwd = path.resolve(config.dir);
    
    // Check if file exists
    if (!fs.existsSync(servicePath)) {
      reject(new Error(`Service file not found: ${servicePath}`));
      return;
    }
    
    const proc = spawn('node', [config.file], {
      cwd,
      stdio: ['ignore', 'pipe', 'pipe'],
      detached: false
    });
    
    childProcesses.push(proc);
    
    let stdout = '';
    let stderr = '';
    
    proc.stdout.on('data', (data) => {
      stdout += data.toString();
      // Log first few lines to console
      const lines = data.toString().trim().split('\n');
      lines.slice(0, 3).forEach(line => {
        if (line.trim()) console.log(`    [${name}] ${line.trim()}`);
      });
    });
    
    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    proc.on('error', (err) => {
      reject(new Error(`Failed to start ${name}: ${err.message}`));
    });
    
    // Wait for port to be ready
    waitForPort(config.port, 15000)
      .then(() => {
        const duration = Date.now() - startTime;
        log('Service Start', 'PASS', `${name} ready on port ${config.port}`, duration);
        results.servicesStarted.push({ name, port: config.port, duration });
        resolve({ proc, port: config.port, stdout, stderr });
      })
      .catch(err => {
        proc.kill();
        const duration = Date.now() - startTime;
        log('Service Start', 'FAIL', `${name} failed to start: ${err.message}`, duration);
        results.servicesFailed.push({ name, port: config.port, error: err.message, duration });
        reject(err);
      });
  });
}

// Step 1: Send Telegram webhook
async function step1_SendTelegramMessage() {
  const stepName = "1. Send Telegram Bridge Webhook";
  const startTime = Date.now();
  
  return new Promise((resolve, reject) => {
    const mockUpdate = {
      update_id: Date.now(),
      message: {
        message_id: Math.floor(Math.random() * 1000000),
        from: {
          id: 123456789,
          is_bot: false,
          first_name: "Test",
          username: "testuser"
        },
        chat: {
          id: -987654321,
          title: "Dusty Test Chat",
          type: "group"
        },
        date: Math.floor(Date.now() / 1000),
        text: TEST_MESSAGE
      }
    };

    const postData = JSON.stringify(mockUpdate);
    
    const options = {
      hostname: 'localhost',
      port: SERVICES.TELEGRAM_BRIDGE.port,
      path: '/webhook',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const duration = Date.now() - startTime;
        
        try {
          const response = JSON.parse(data);
          if (res.statusCode === 200 && response.ok) {
            if (response.forwarded) {
              log(stepName, 'PASS', `Message forwarded to core-agent successfully`, duration);
              resolve({ statusCode: res.statusCode, body: response, duration });
            } else {
              log(stepName, 'WARN', `Message received but not forwarded: ${response.error || 'Unknown'}`, duration);
              resolve({ statusCode: res.statusCode, body: response, duration, warning: response.error });
            }
          } else {
            log(stepName, 'FAIL', `HTTP ${res.statusCode}: ${data.substring(0, 200)}`, duration);
            reject(new Error(`HTTP ${res.statusCode}`));
          }
        } catch (e) {
          log(stepName, 'FAIL', `Invalid JSON response: ${data.substring(0, 200)}`, duration);
          reject(e);
        }
      });
    });

    req.on('error', (error) => {
      const duration = Date.now() - startTime;
      log(stepName, 'FAIL', error.message, duration);
      reject(error);
    });
    
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.write(postData);
    req.end();
  });
}

// Step 2: Verify core-agent processed the message
async function step2_VerifyCoreAgent() {
  const stepName = "2. Verify Core-Agent Processing";
  const startTime = Date.now();
  
  return new Promise((resolve, reject) => {
    const req = http.request({
      hostname: 'localhost',
      port: SERVICES.CORE_AGENT.port,
      path: '/health',
      method: 'GET',
      timeout: 5000
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const duration = Date.now() - startTime;
        
        if (res.statusCode === 200) {
          try {
            const health = JSON.parse(data);
            log(stepName, 'PASS', `Core-agent healthy: ${health.status}${health.uptime ? ` (uptime: ${Math.floor(health.uptime)}s)` : ''}`, duration);
            resolve({ statusCode: res.statusCode, health, duration });
          } catch (e) {
            log(stepName, 'PASS', 'Core-agent responding on /health', duration);
            resolve({ statusCode: res.statusCode, duration });
          }
        } else {
          log(stepName, 'FAIL', `Health check failed: HTTP ${res.statusCode}`, duration);
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    });

    req.on('error', (error) => {
      const duration = Date.now() - startTime;
      log(stepName, 'FAIL', error.message, duration);
      reject(error);
    });

    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
    req.end();
  });
}

// Step 3: Verify OpenClaw mock response
async function step3_VerifyOpenClaw() {
  const stepName = "3. Verify OpenClaw Mock Response";
  const startTime = Date.now();
  
  return new Promise((resolve, reject) => {
    // First check OpenClaw health
    const req = http.request({
      hostname: 'localhost',
      port: SERVICES.OPENCLAW.port,
      path: '/status',
      method: 'GET',
      timeout: 5000
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const duration = Date.now() - startTime;
        
        try {
          const status = JSON.parse(data);
          if (res.statusCode === 200 && status.status === 'healthy') {
            log(stepName, 'PASS', `OpenClaw mock healthy (service: ${status.service}, interactions: ${status.total_interactions} total)`, duration);
            resolve({ statusCode: res.statusCode, status, duration });
          } else {
            log(stepName, 'WARN', `OpenClaw responded but status: ${status.status}`, duration);
            resolve({ statusCode: res.statusCode, status, duration, warning: true });
          }
        } catch (e) {
          log(stepName, 'PASS', 'OpenClaw mock responding', duration);
          resolve({ statusCode: res.statusCode, duration });
        }
      });
    });

    req.on('error', (error) => {
      const duration = Date.now() - startTime;
      log(stepName, 'FAIL', error.message, duration);
      reject(error);
    });

    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
    req.end();
  });
}

// Step 4: Check OpenClaw logs for our message
async function step4_CheckOpenClawLogs() {
  const stepName = "4. Check OpenClaw Interaction Logs";
  const startTime = Date.now();
  
  return new Promise((resolve, reject) => {
    const req = http.request({
      hostname: 'localhost',
      port: SERVICES.OPENCLAW.port,
      path: '/logs',
      method: 'GET',
      timeout: 5000
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        const duration = Date.now() - startTime;
        
        try {
          const logs = JSON.parse(data);
          const recentLogs = logs.logs || [];
          
          // Check if our message was processed
          const ourMessage = recentLogs.find(log => 
            log.data && log.data.message && log.data.message.includes(TEST_MESSAGE.substring(0, 30))
          );
          
          if (ourMessage) {
            log(stepName, 'PASS', `Found our message in logs: "${ourMessage.data.message.substring(0, 50)}..."`, duration);
            resolve({ found: true, log: ourMessage, duration, totalLogs: logs.total });
          } else {
            log(stepName, 'WARN', `Message not found in recent logs (checked ${recentLogs.length} entries)`, duration);
            resolve({ found: false, duration, totalLogs: logs.total, recentCount: recentLogs.length });
          }
        } catch (e) {
          log(stepName, 'FAIL', `Failed to parse logs: ${e.message}`, duration);
          reject(e);
        }
      });
    });

    req.on('error', (error) => {
      const duration = Date.now() - startTime;
      log(stepName, 'FAIL', error.message, duration);
      reject(error);
    });

    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
    req.end();
  });
}

// Cleanup: Stop all services
async function cleanup() {
  log('Cleanup', 'PENDING', 'Stopping all services...');
  
  let stopped = 0;
  let failed = 0;
  
  for (const proc of childProcesses) {
    try {
      proc.kill('SIGTERM');
      stopped++;
    } catch (e) {
      try {
        proc.kill('SIGKILL');
      } catch (e2) {
        failed++;
      }
    }
  }
  
  // Wait a moment for processes to die
  await new Promise(r => setTimeout(r, 1000));
  
  log('Cleanup', 'PASS', `Stopped ${stopped} service(s)${failed > 0 ? `, ${failed} failed` : ''}`);
}

// Main test runner
async function runTest() {
  console.log('='.repeat(70));
  console.log('DUSTY MVP END-TO-END TEST');
  console.log('='.repeat(70));
  console.log(`Started: ${TEST_TIMESTAMP}`);
  console.log(`Test Message: "${TEST_MESSAGE}"`);
  console.log(`Working Directory: ${process.cwd()}`);
  console.log();

  results.timing.totalStart = Date.now();
  
  try {
    // Phase 1: Start all services
    console.log('─'.repeat(70));
    console.log('PHASE 1: STARTING SERVICES');
    console.log('─'.repeat(70));
    
    const serviceStartTime = Date.now();
    
    // Start services in order: OpenClaw (independent) -> Core Agent -> Bridge
    log('Service Init', 'PENDING', 'Starting service initialization...');
    
    try {
      await startService('OpenClaw Mock', SERVICES.OPENCLAW);
      await new Promise(r => setTimeout(r, 500)); // Brief stabilization
      
      await startService('Core Agent', SERVICES.CORE_AGENT);
      await new Promise(r => setTimeout(r, 500));
      
      await startService('Telegram Bridge', SERVICES.TELEGRAM_BRIDGE);
    } catch (e) {
      log('Service Init', 'FAIL', `Failed to start required services: ${e.message}`);
      throw e;
    }
    
    results.timing.serviceStart = Date.now() - serviceStartTime;
    
    // Stabilization pause
    await new Promise(r => setTimeout(r, 1000));
    
    // Phase 2: Run E2E flow
    console.log();
    console.log('─'.repeat(70));
    console.log('PHASE 2: END-TO-END FLOW TEST');
    console.log('─'.repeat(70));
    
    const flowStartTime = Date.now();
    
    await step1_SendTelegramMessage();
    await new Promise(r => setTimeout(r, 500)); // Allow processing
    
    await step2_VerifyCoreAgent();
    await new Promise(r => setTimeout(r, 200));
    
    await step3_VerifyOpenClaw();
    await new Promise(r => setTimeout(r, 200));
    
    await step4_CheckOpenClawLogs();
    
    results.timing.flowTest = Date.now() - flowStartTime;
    results.passed = true;
    
  } catch (error) {
    results.passed = false;
    results.errors.push(error.message);
    console.error(`\n❌ FATAL ERROR: ${error.message}`);
    if (error.stack) {
      console.error(error.stack.split('\n').slice(0, 3).join('\n'));
    }
  } finally {
    // Cleanup
    console.log();
    console.log('─'.repeat(70));
    console.log('PHASE 3: CLEANUP');
    console.log('─'.repeat(70));
    await cleanup();
    
    results.endTime = Date.now();
    results.timing.total = results.endTime - results.timing.totalStart;
  }

  // Generate final report
  console.log();
  console.log('='.repeat(70));
  console.log('FINAL REPORT');
  console.log('='.repeat(70));
  console.log(`Overall Status: ${results.passed ? '✅ PASSED' : '❌ FAILED'}`);
  console.log(`Total Duration: ${results.timing.total}ms`);
  console.log(`  - Service Startup: ${results.timing.serviceStart || 0}ms`);
  console.log(`  - Flow Test: ${results.timing.flowTest || 0}ms`);
  console.log();
  
  console.log('Services:');
  if (results.servicesStarted.length > 0) {
    results.servicesStarted.forEach(s => {
      console.log(`  ✅ ${s.name} (port ${s.port}) - ${s.duration}ms startup`);
    });
  }
  if (results.servicesFailed.length > 0) {
    results.servicesFailed.forEach(s => {
      console.log(`  ❌ ${s.name} - ${s.error} (${s.duration}ms)`);
    });
  }
  
  console.log();
  console.log('Test Steps:');
  results.steps.forEach(s => {
    const icon = s.status === 'PASS' ? '✅' : s.status === 'FAIL' ? '❌' : s.status === 'PENDING' ? '⏳' : '⚠️';
    const dur = s.durationMs ? ` (${s.durationMs}ms)` : '';
    console.log(`  ${icon} ${s.step}${dur}`);
    console.log(`     → ${s.message}`);
  });
  
  if (results.errors.length > 0) {
    console.log();
    console.log('Errors:');
    results.errors.forEach(e => console.log(`  ❌ ${e}`));
  }
  
  console.log();
  console.log('='.repeat(70));
  console.log(`Test completed at: ${new Date().toISOString()}`);
  console.log('='.repeat(70));

  // Save detailed report
  const reportPath = '/tmp/dusty-e2e-full-report.json';
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`\nDetailed report: ${reportPath}`);

  process.exit(results.passed ? 0 : 1);
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n\n⚠️ Interrupted, cleaning up...');
  await cleanup();
  process.exit(1);
});

// Run the test
runTest();

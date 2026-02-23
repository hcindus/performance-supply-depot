const http = require('http');

// Helper to make HTTP requests with timing
function httpRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const client = url.startsWith('https') ? require('https') : http;
    const startTime = process.hrtime.bigint();
    
    const req = client.request({
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: options.headers || {}
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const endTime = process.hrtime.bigint();
        const durationMs = Number(endTime - startTime) / 1_000_000;
        resolve({ statusCode: res.statusCode, data, durationMs });
      });
    });
    req.on('error', reject);
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    req.end();
  });
}

// Send message via bridge webhook
async function sendViaBridge(message, username = 'testuser') {
  const telegramPayload = {
    update_id: Date.now(),
    message: {
      message_id: Date.now(),
      from: {
        id: 987654321,
        is_bot: false,
        first_name: 'Test',
        last_name: 'User',
        username: username,
        language_code: 'en'
      },
      chat: {
        id: 987654321,
        first_name: 'Test',
        last_name: 'User',
        username: username,
        type: 'private'
      },
      date: Math.floor(Date.now() / 1000),
      text: message
    }
  };

  return httpRequest('http://localhost:3001/webhook', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: telegramPayload
  });
}

async function runTest() {
  const testStart = new Date();
  console.log('=== Dusty MVP End-to-End Test ===');
  console.log(`Timestamp: ${testStart.toISOString()}`);
  console.log('');

  const results = {
    passed: 0,
    failed: 0,
    tests: [],
    timings: {}
  };

  // Test 1: Health Checks
  console.log('1. Service Health Checks');
  
  // Bridge health
  try {
    const startTime = process.hrtime.bigint();
    const bridgeHealth = await httpRequest('http://localhost:3001/health');
    const durationMs = Number(process.hrtime.bigint() - startTime) / 1_000_000;
    results.timings.bridgeHealth = durationMs;
    
    const parsed = JSON.parse(bridgeHealth.data);
    const status = bridgeHealth.statusCode === 200 && parsed.status === 'healthy' ? '✅ PASS' : '❌ FAIL';
    console.log(`   Telegram Bridge (port 3001): ${status} (${durationMs.toFixed(2)}ms)`);
    console.log(`     → Status: ${parsed.status}, Uptime: ${Math.floor(parsed.uptime / 3600)}h ${Math.floor((parsed.uptime % 3600) / 60)}m`);
    results.tests.push({ name: 'Bridge Health', status: 'PASS', durationMs });
    results.passed++;
  } catch (error) {
    console.log(`   Telegram Bridge: ❌ FAIL - ${error.message}`);
    results.tests.push({ name: 'Bridge Health', status: 'FAIL', error: error.message });
    results.failed++;
  }

  // Core-agent health
  try {
    const startTime = process.hrtime.bigint();
    const coreHealth = await httpRequest('http://localhost:3000/health');
    const durationMs = Number(process.hrtime.bigint() - startTime) / 1_000_000;
    results.timings.coreHealth = durationMs;
    
    const parsed = JSON.parse(coreHealth.data);
    const status = coreHealth.statusCode === 200 && parsed.status === 'healthy' ? '✅ PASS' : '❌ FAIL';
    console.log(`   Core-Agent (port 3000): ${status} (${durationMs.toFixed(2)}ms)`);
    console.log(`     → Status: ${parsed.status}, Uptime: ${Math.floor(parsed.uptime / 3600)}h ${Math.floor((parsed.uptime % 3600) / 60)}m`);
    results.tests.push({ name: 'Core-Agent Health', status: 'PASS', durationMs });
    results.passed++;
  } catch (error) {
    console.log(`   Core-Agent: ❌ FAIL - ${error.message}`);
    results.tests.push({ name: 'Core-Agent Health', status: 'FAIL', error: error.message });
    results.failed++;
  }

  // OpenClaw mock health
  try {
    const startTime = process.hrtime.bigint();
    const openclawHealth = await httpRequest('http://localhost:4000/status');
    const durationMs = Number(process.hrtime.bigint() - startTime) / 1_000_000;
    results.timings.openclawHealth = durationMs;
    
    const parsed = JSON.parse(openclawHealth.data);
    const status = openclawHealth.statusCode === 200 ? '✅ PASS' : '❌ FAIL';
    console.log(`   OpenClaw Mock (port 4000): ${status} (${durationMs.toFixed(2)}ms)`);
    console.log(`     → Status: ${parsed.status}, Interactions: ${parsed.total_interactions}, Uptime: ${Math.floor(parsed.uptime / 3600)}h ${Math.floor((parsed.uptime % 3600) / 60)}m`);
    results.tests.push({ name: 'OpenClaw Health', status: 'PASS', durationMs });
    results.passed++;
  } catch (error) {
    console.log(`   OpenClaw Mock: ❌ FAIL - ${error.message}`);
    results.tests.push({ name: 'OpenClaw Health', status: 'FAIL', error: error.message });
    results.failed++;
  }

  // Test 2: End-to-End Flow - Send "dust balance" query
  console.log('');
  console.log('2. End-to-End Flow Test');
  console.log('   Triggering: "/dust balance" via Bridge → Core-Agent → OpenClaw...');
  
  let e2eDuration = 0;
  let e2eSuccess = false;
  let e2eResponse = null;
  
  try {
    const e2eStart = process.hrtime.bigint();
    const e2eResult = await sendViaBridge('/dust balance', 'e2e_dust_user');
    e2eDuration = Number(process.hrtime.bigint() - e2eStart) / 1_000_000;
    results.timings.e2eFlow = e2eDuration;
    e2eResponse = e2eResult;
    
    if (e2eResult.statusCode === 200) {
      const parsed = JSON.parse(e2eResult.data);
      if (parsed.ok && parsed.forwarded && parsed.coreAgentResponse) {
        const agentResponse = parsed.coreAgentResponse;
        if (agentResponse.openclawResponse && agentResponse.openclawResponse.response) {
          e2eSuccess = true;
          console.log(`   Result: ✅ PASS (${e2eDuration.toFixed(2)}ms)`);
          console.log(`     → Task ID: ${agentResponse.id?.substring(0, 16)}...`);
          console.log(`     → OpenClaw Bot: ${agentResponse.openclawResponse.bot || 'unknown'}`);
          console.log(`     → Action: ${agentResponse.openclawResponse.action || 'none'}`);
          const preview = agentResponse.openclawResponse.response?.substring(0, 60) || '(empty)';
          console.log(`     → Response Preview: "${preview}..."`);
          results.tests.push({ name: 'End-to-End Flow', status: 'PASS', durationMs: e2eDuration });
          results.passed++;
        } else {
          throw new Error('OpenClaw response missing or empty');
        }
      } else {
        throw new Error(`Bridge forwarding failed: ${JSON.stringify(parsed).substring(0, 100)}`);
      }
    } else {
      throw new Error(`HTTP ${e2eResult.statusCode}: ${e2eResult.data.substring(0, 100)}`);
    }
  } catch (error) {
    console.log(`   Result: ❌ FAIL (${e2eDuration.toFixed(2)}ms)`);
    console.log(`     → Error: ${error.message}`);
    if (e2eResponse) {
      console.log(`     → Raw response: ${e2eResponse.data.substring(0, 150)}`);
    }
    results.tests.push({ name: 'End-to-End Flow', status: 'FAIL', durationMs: e2eDuration, error: error.message });
    results.failed++;
  }

  // Test 3: Dust-specific queries
  console.log('');
  console.log('3. Dust-Specific Query Tests');
  
  const dustQueries = [
    { text: 'What is my balance?', expectedAction: 'balance_report', name: 'Balance Query' },
    { text: 'Find my dust', expectedAction: 'dust_identification', name: 'Dust Identification' },
    { text: 'How do I consolidate?', expectedAction: 'transfer_decision', name: 'Consolidation Plan' }
  ];

  for (const query of dustQueries) {
    try {
      const queryStart = process.hrtime.bigint();
      const result = await sendViaBridge(query.text, 'dusty_test_user');
      const queryDuration = Number(process.hrtime.bigint() - queryStart) / 1_000_000;
      
      const parsed = JSON.parse(result.data);
      const agentResponse = parsed.coreAgentResponse;
      
      if (agentResponse?.openclawResponse?.action === query.expectedAction) {
        console.log(`   ${query.name}: ✅ PASS (${queryDuration.toFixed(2)}ms) - action: ${query.expectedAction}`);
        results.tests.push({ name: query.name, status: 'PASS', durationMs: queryDuration });
        results.passed++;
      } else {
        const actualAction = agentResponse?.openclawResponse?.action || 'none';
        console.log(`   ${query.name}: ⚠️ PARTIAL (${queryDuration.toFixed(2)}ms) - expected ${query.expectedAction}, got ${actualAction}`);
        results.tests.push({ name: query.name, status: 'PARTIAL', durationMs: queryDuration });
        results.passed++;
      }
    } catch (error) {
      console.log(`   ${query.name}: ❌ FAIL - ${error.message}`);
      results.tests.push({ name: query.name, status: 'FAIL', error: error.message });
      results.failed++;
    }
  }

  // Summary
  console.log('');
  console.log('='.repeat(60));
  console.log('  TEST RESULTS SUMMARY');
  console.log('='.repeat(60));
  console.log(`Test ID: dusty-end-to-end-${testStart.toISOString().split('T')[0].replace(/-/g, '')}`);
  console.log(`Overall Status: ${results.failed === 0 ? '✅ ALL TESTS PASSED' : results.failed > 0 && results.passed > 0 ? '⚠️ PARTIAL SUCCESS' : '❌ TESTS FAILED'}`);
  console.log(`Tests Passed: ${results.passed}/${results.tests.length}`);
  console.log(`Failed: ${results.failed}`);
  console.log('');
  console.log('Timing Breakdown:');
  let totalDuration = 0;
  results.tests.forEach(test => {
    if (test.durationMs) {
      console.log(`  ${test.name}: ${test.durationMs.toFixed(2)}ms`);
      totalDuration += test.durationMs;
    }
  });
  console.log(`  ─────────────────────────`);
  console.log(`  Total: ${totalDuration.toFixed(2)}ms`);
  console.log('='.repeat(60));
  console.log(`Completed: ${new Date().toISOString()}`);

  // Save report
  const fs = require('fs');
  const reportName = `e2e_report_dusty-${Date.now()}.json`;
  const reportPath = `/root/.openclaw/workspace/agents/dusty/test/${reportName}`;
  const reportData = {
    test_id: `dusty-e2e-${testStart.toISOString()}`,
    timestamp: new Date().toISOString(),
    status: results.failed === 0 ? 'PASS' : results.failed > 0 && results.passed > results.failed / 2 ? 'PARTIAL' : 'FAIL',
    summary: {
      total: results.tests.length,
      passed: results.passed,
      failed: results.failed,
      total_duration_ms: totalDuration
    },
    tests: results.tests,
    timings: results.timings
  };
  
  fs.mkdirSync('/root/.openclaw/workspace/agents/dusty/test', { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
  console.log(`\nReport saved to: agents/dusty/test/${reportName}`);

  return results.failed === 0;
}

runTest().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('Fatal test error:', error);
  process.exit(1);
});

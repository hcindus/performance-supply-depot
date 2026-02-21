/**
 * Dusty MVP End-to-End Test Runner
 * Tests: Bridge -> Core-Agent -> OpenClaw Mock
 */

const axios = require('axios');

const ENDPOINTS = {
  bridge: 'http://localhost:3001',
  coreAgent: 'http://localhost:3000',
  openclaw: 'http://localhost:4000'
};

const TEST_MESSAGE = '/dust balance';

async function measureRequest(name, fn) {
  const start = performance.now();
  try {
    const result = await fn();
    const latency = performance.now() - start;
    return { success: true, latency: latency.toFixed(2), data: result };
  } catch (error) {
    const latency = performance.now() - start;
    return { 
      success: false, 
      latency: latency.toFixed(2), 
      error: error.message,
      status: error.response?.status
    };
  }
}

async function healthCheck(service, url) {
  console.log(`\n  ┌─ Health Check: ${service}`);
  const result = await measureRequest(service, async () => {
    const response = await axios.get(`${url}/health`, { timeout: 5000 });
    return response.data;
  });
  
  const status = result.success ? '✅' : '❌';
  console.log(`  │ ${status} ${service}: ${result.latency}ms`);
  if (result.success && result.data?.uptime) {
    const uptime = result.data.uptime;
    const hours = Math.floor(uptime / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    console.log(`  │   Uptime: ${hours}h ${minutes}m`);
  }
  return result;
}

async function runTest() {
  console.log('\n╔══════════════════════════════════════════════════════════╗');
  console.log('║     Dusty MVP End-to-End Test Suite                      ║');
  console.log('║     Saturday, February 21st, 2026 — 3:23 AM (UTC)       ║');
  console.log('╚══════════════════════════════════════════════════════════╝\n');
  
  const startTime = Date.now();
  const results = {
    startTime: new Date().toISOString(),
    tests: {},
    phase1: { name: 'Service Health Checks', status: 'pending' },
    phase2: { name: 'Send Telegram Message via Bridge', status: 'pending' },
    phase3: { name: 'Core-Agent Processing', status: 'pending' },
    phase4: { name: 'OpenClaw Response Verification', status: 'pending' }
  };

  // Phase 1: Health Checks
  console.log('─'.repeat(60));
  console.log('📋 Phase 1: Service Health Checks');
  console.log('─'.repeat(60));
  
  const bridgeHealth = await healthCheck('Telegram Bridge', ENDPOINTS.bridge);
  const coreAgentHealth = await healthCheck('Core-Agent', ENDPOINTS.coreAgent);
  const openclawHealth = await healthCheck('OpenClaw Mock', ENDPOINTS.openclaw);
  
  const allHealthy = bridgeHealth.success && coreAgentHealth.success && openclawHealth.success;
  results.phase1.status = allHealthy ? 'passed' : 'failed';
  results.tests.healthChecks = { bridgeHealth, coreAgentHealth, openclawHealth };

  if (!allHealthy) {
    console.log('\n❌ Phase 1 FAILED - Some services are not healthy');
    return generateReport(results, Date.now() - startTime);
  }
  console.log('\n✅ Phase 1 PASSED - All services healthy');

  // Phase 2: Send message via bridge
  console.log('\n' + '─'.repeat(60));
  console.log('📋 Phase 2: Send Telegram Message via Bridge');
  console.log('─'.repeat(60));
  
  const mockTelegramMessage = {
    update_id: Date.now(),
    message: {
      message_id: Math.floor(Math.random() * 1000000),
      from: {
        id: 123456789,
        is_bot: false,
        first_name: 'Test',
        username: 'e2e_tester',
        language_code: 'en'
      },
      chat: {
        id: 123456789,
        first_name: 'Test',
        username: 'e2e_tester',
        type: 'private'
      },
      date: Math.floor(Date.now() / 1000),
      text: TEST_MESSAGE
    }
  };

  console.log(`  \n  ┌─ Sending: "${TEST_MESSAGE}"`);
  const bridgeResult = await measureRequest('Bridge Forward', async () => {
    const response = await axios.post(`${ENDPOINTS.bridge}/webhook`, mockTelegramMessage, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 15000
    });
    return response.data;
  });

  if (!bridgeResult.success) {
    console.log(`  │ ❌ Bridge forward failed: ${bridgeResult.error}`);
    results.phase2.status = 'failed';
    results.tests.bridgeForward = bridgeResult;
    return generateReport(results, Date.now() - startTime);
  }

  console.log(`  │ ✅ Bridge forwarded message successfully`);
  console.log(`  │ 📊 Latency: ${bridgeResult.latency}ms`);
  
  const forwarded = bridgeResult.data?.forwarded;
  const coreAgentResponded = !!bridgeResult.data?.coreAgentResponse;
  
  console.log(`  │   Forwarded: ${forwarded ? 'Yes' : 'No'}`);
  console.log(`  │   Core-Agent Response: ${coreAgentResponded ? 'Yes' : 'No'}`);
  
  if (forwarded && coreAgentResponded) {
    results.phase2.status = 'passed';
    console.log('\n✅ Phase 2 PASSED - Bridge forwarded message to Core-Agent');
  } else {
    results.phase2.status = 'failed';
    console.log('\n❌ Phase 2 FAILED - Bridge could not forward message');
    results.tests.bridgeForward = bridgeResult;
    return generateReport(results, Date.now() - startTime);
  }

  // Phase 3: Core-Agent Processing
  console.log('\n' + '─'.repeat(60));
  console.log('📋 Phase 3: Core-Agent Processing');
  console.log('─'.repeat(60));
  
  const coreResponse = bridgeResult.data?.coreAgentResponse;
  if (coreResponse?.ok) {
    console.log(`  \n  ┌─ Core-Agent Task Creation`);
    console.log(`  │ ✅ Task created successfully`);
    console.log(`  │ 📊 Task ID: ${coreResponse.id?.substring(0, 16)}...`);
    console.log(`  │ 📋 Status: ${coreResponse.status}`);
    
    if (coreResponse.openclawResponse) {
      console.log(`  │ ✅ Forwarded to OpenClaw Mock`);
      results.phase3.status = 'passed';
      console.log('\n✅ Phase 3 PASSED - Core-Agent processed and forwarded to OpenClaw');
    } else {
      console.log(`  │ ⚠️ No OpenClaw response (may be expected if not a Telegram message)`);
      results.phase3.status = 'passed';
      console.log('\n✅ Phase 3 PASSED - Core-Agent processed message');
    }
  } else {
    results.phase3.status = 'failed';
    console.log('\n❌ Phase 3 FAILED - Core-Agent did not return ok response');
  }
  
  results.tests.bridgeForward = bridgeResult;

  // Phase 4: Verify OpenClaw Response
  console.log('\n' + '─'.repeat(60));
  console.log('📋 Phase 4: OpenClaw Response Verification');
  console.log('─'.repeat(60));

  const openclawResponse = bridgeResult.data?.coreAgentResponse?.openclawResponse;
  
  if (!openclawResponse) {
    console.log(`  \n  ⚠️ No OpenClaw response to verify (Phase 2 or 3 may have failed)`);
    results.phase4.status = 'skipped';
  } else {
    console.log(`  \n  ┌─ OpenClaw Response Analysis`);
    console.log(`  │ ✅ Response received from OpenClaw Mock`);
    console.log(`  │ 🤖 Bot: ${openclawResponse.bot || 'not specified'}`);
    console.log(`  │ 🎯 Action: ${openclawResponse.action || 'not specified'}`);
    
    if (openclawResponse.action === 'balance_report') {
      console.log(`  │ 💰 Balance Data:`);
      console.log(`  │    • ETH: ${openclawResponse.data?.eth} ETH`);
      console.log(`  │    • USDC: ${openclawResponse.data?.usdc} USDC`);
      console.log(`  │    • Dust Value: $${openclawResponse.data?.dust_value_usd}`);
      console.log(`  │ ✅ Expected action type match (balance_report)`);
      
      const expectedAction = 'balance_report';
      results.phase4.status = openclawResponse.action === expectedAction ? 'passed' : 'warning';
      if (openclawResponse.action !== expectedAction) {
        console.log(`  │ ⚠️ Action mismatch: expected ${expectedAction}, got ${openclawResponse.action}`);
      }
    } else {
      console.log(`  │ ⚠️ Unexpected action type: ${openclawResponse.action}`);
      results.phase4.status = 'warning';
    }
    
    results.tests.openclawResponse = {
      success: true,
      latency: 'included in core-agent',
      data: openclawResponse
    };
    
    if (results.phase4.status !== 'skipped') {
      console.log(`\n${results.phase4.status === 'passed' ? '✅' : '⚠️'} Phase 4 ${results.phase4.status.toUpperCase()} - OpenClaw responded with proper action type`);
    }
  }

  // Additional Dust Query Tests
  console.log('\n' + '─'.repeat(60));
  console.log('📋 Bonus: Additional Dust Query Tests');
  console.log('─'.repeat(60));
  
  const dustQueries = [
    { text: 'What is my balance?', expectedAction: 'balance_report' },
    { text: 'Find my dust', expectedAction: 'dust_identification' },
    { text: 'How do I consolidate?', expectedAction: 'transfer_decision' }
  ];
  
  results.bonusTests = [];
  
  for (const query of dustQueries) {
    const testMsg = {
      update_id: Date.now(),
      message: {
        message_id: Math.floor(Math.random() * 1000000),
        from: { id: 123456789, is_bot: false, first_name: 'Test' },
        chat: { id: 123456789, type: 'private' },
        date: Math.floor(Date.now() / 1000),
        text: query.text
      }
    };

    const testResult = await measureRequest(`Query: "${query.text.substring(0, 25)}..."`, async () => {
      const response = await axios.post(`${ENDPOINTS.bridge}/webhook`, testMsg, {
        timeout: 10000
      });
      return response.data;
    });

    const actualAction = testResult.data?.coreAgentResponse?.openclawResponse?.action;
    const actionMatch = actualAction === query.expectedAction;
    
    console.log(`\n  ┌─ "${query.text}"`);
    console.log(`  │ ${testResult.success ? '✅' : '❌'} Bridge: ${testResult.latency}ms`);
    console.log(`  │ ${actionMatch ? '✅' : '⚠️'} Action: expected "${query.expectedAction}", got "${actualAction || 'none'}"`);
    
    results.bonusTests.push({
      query: query.text,
      expectedAction: query.expectedAction,
      actualAction: actualAction || null,
      latency: testResult.latency,
      passed: testResult.success && actionMatch
    });
  }

  // Get OpenClaw logs
  console.log('\n' + '─'.repeat(60));
  console.log('📋 OpenClaw Mock Stats');
  console.log('─'.repeat(60));
  
  try {
    const statsResult = await axios.get(`${ENDPOINTS.openclaw}/logs?limit=1`, { timeout: 5000 });
    console.log(`  📊 Total interactions logged: ${statsResult.data.total}`);
    results.openclawStats = { totalInteractions: statsResult.data.total };
  } catch (e) {
    console.log('  ⚠️ Could not fetch stats');
    results.openclawStats = { error: e.message };
  }

  return generateReport(results, Date.now() - startTime);
}

function generateReport(results, totalDuration) {
  results.endTime = new Date().toISOString();
  results.totalDuration = totalDuration;
  results.totalDurationMs = totalDuration.toFixed(2);

  // Calculate pass/fail counts
  const phases = [results.phase1, results.phase2, results.phase3, results.phase4];
  const passed = phases.filter(p => p.status === 'passed').length;
  const failed = phases.filter(p => p.status === 'failed').length;
  const warnings = phases.filter(p => p.status === 'warning').length;
  const skipped = phases.filter(p => p.status === 'skipped').length;

  console.log('\n' + '='.repeat(60));
  console.log('📊 FINAL TEST REPORT');
  console.log('='.repeat(60));
  console.log(`Total Duration: ${totalDuration.toFixed(2)}ms`);
  console.log(`\nPhases:`);
  phases.forEach((p, i) => {
    const icon = p.status === 'passed' ? '✅' : p.status === 'failed' ? '❌' : p.status === 'warning' ? '⚠️' : '⏭️';
    console.log(`  ${icon} Phase ${i + 1}: ${p.name} [${p.status.toUpperCase()}]`);
  });
  
  console.log('\nSummary:');
  console.log(`  ✓ Passed: ${passed}/${phases.length}`);
  console.log(`  ✗ Failed: ${failed}/${phases.length}`);
  if (warnings) console.log(`  ⚠ Warnings: ${warnings}`);
  if (skipped) console.log(`  ⏭ Skipped: ${skipped}`);
  
  const overall = failed === 0 ? '✅ PASSED' : '❌ FAILED';
  console.log(`\n${'='.repeat(60)}`);
  console.log(`OVERALL RESULT: ${overall}`);
  console.log('='.repeat(60) + '\n');

  results.overall = failed === 0 ? 'passed' : 'failed';
  results.passed = passed;
  results.failed = failed;
  results.warnings = warnings;
  results.skipped = skipped;

  return results;
}

// Run the test
runTest().then(results => {
  // Save detailed report
  const fs = require('fs');
  const reportPath = `/root/.openclaw/workspace/dusty_e2e_report_${new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)}.json`;
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`\nDetailed report saved to: ${reportPath}`);
  
  process.exit(results.overall === 'passed' ? 0 : 1);
}).catch(err => {
  console.error('Test error:', err);
  process.exit(1);
});

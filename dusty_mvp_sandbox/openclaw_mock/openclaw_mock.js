/**
 * OpenClaw Mock Service
 * Simulates Dusty bot responses for crypto dust consolidation queries
 * Port: 4000
 */

const express = require('express');
const app = express();
const PORT = 4000;

app.use(express.json());

// Store interaction logs
const interactionLogs = [];

/**
 * Log an interaction with timestamp
 */
function logInteraction(direction, data) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    direction,
    data
  };
  interactionLogs.push(logEntry);
  console.log(`[${logEntry.timestamp}] ${direction}:`, JSON.stringify(data, null, 2));
}

/**
 * Generate mock Dusty responses based on message content
 */
function generateDustyResponse(message) {
  const msg = message.toLowerCase();
  
  // Balance queries
  if (msg.includes('balance') || msg.includes('how much') || msg.includes('holdings')) {
    return {
      bot: 'dusty',
      response: `📊 **Your Current Balances**

• ETH: 0.5234 ETH (~$1,247.50)
• USDC: 150.00 USDC
• DUST tokens: 2,847.32 DUST (~$12.45)
• Random airdrops: 15 small tokens (~$3.20 total)

**Total Portfolio Value: ~$1,412.15**

I found some dust worth consolidating! 💰`,
      action: 'balance_report',
      data: {
        eth: 0.5234,
        usdc: 150.00,
        dust_tokens: 2847.32,
        dust_value_usd: 15.65
      }
    };
  }
  
  // Dust identification queries
  if (msg.includes('dust') || msg.includes('small') || msg.includes('tiny') || msg.includes('identify')) {
    return {
      bot: 'dusty',
      response: `🔍 **Dust Analysis Complete**

Found **15 dust positions** across your wallets:

**High Priority (worth consolidating):**
• 0.0012 ETH in Wallet A (~$2.85)
• 47.5 USDT in Wallet B (~$47.50)
• 1,234 DUST tokens (~$5.40)

**Low Priority (gas might exceed value):**
• 12 random tokens < $1 each
• 0.00001 ETH remnants from failed swaps

**Estimated consolidation value: $55.75**
**Estimated gas cost: $8.50**
**Net gain: $47.25** ✅`,
      action: 'dust_identification',
      data: {
        total_dust_positions: 15,
        high_priority_count: 3,
        low_priority_count: 12,
        estimated_value_usd: 55.75,
        estimated_gas_usd: 8.50,
        net_gain_usd: 47.25
      }
    };
  }
  
  // Transfer/Consolidation decisions
  if (msg.includes('transfer') || msg.includes('consolidate') || msg.includes('move') || msg.includes('sweep')) {
    return {
      bot: 'dusty',
      response: `🎯 **Consolidation Plan Ready**

Here's what I recommend:

**Step 1:** Sweep Wallet B → Wallet A
• Move 47.5 USDT (gas: ~$3.20)

**Step 2:** Convert small tokens to ETH
• 12 tokens → ETH (gas: ~$4.50)

**Step 3:** Consolidate DUST holdings
• Merge scattered DUST into main wallet

**Total Actions:** 3 transactions
**Total Gas:** ~$8.50
**Expected Recovery:** $55.75

Would you like me to proceed? Reply **CONFIRM** to execute.`,
      action: 'transfer_decision',
      data: {
        steps: [
          { action: 'sweep_usdt', from: 'wallet_b', to: 'wallet_a', amount: 47.5, gas_usd: 3.20 },
          { action: 'convert_tokens', count: 12, output: 'ETH', gas_usd: 4.50 },
          { action: 'consolidate_dust', gas_usd: 0.80 }
        ],
        total_gas_usd: 8.50,
        expected_recovery_usd: 55.75
      }
    };
  }
  
  // Action confirmations
  if (msg.includes('confirm') || msg.includes('yes') || msg.includes('proceed') || msg.includes('execute')) {
    return {
      bot: 'dusty',
      response: `✅ **Consolidation Executed Successfully!**

**Transaction Summary:**
• Tx #1: 0x7a3f...9e2d ✅ (USDT sweep)
• Tx #2: 0x2b8c...4f1a ✅ (Token conversions)
• Tx #3: 0x9d1e...7c5b ✅ (DUST merge)

**Results:**
• Recovered: $55.75 in consolidated assets
• Gas spent: $8.47
• **Net profit: $47.28** 🎉

Your wallets are now clean! No more dust clutter.

Need anything else? I can monitor for new dust or set up auto-sweep rules.`,
      action: 'action_confirmation',
      data: {
        status: 'completed',
        transactions: [
          { hash: '0x7a3f...9e2d', type: 'usdt_sweep', status: 'success' },
          { hash: '0x2b8c...4f1a', type: 'token_conversion', status: 'success' },
          { hash: '0x9d1e...7c5b', type: 'dust_merge', status: 'success' }
        ],
        recovered_usd: 55.75,
        gas_spent_usd: 8.47,
        net_profit_usd: 47.28
      }
    };
  }
  
  // Default/help response
  return {
    bot: 'dusty',
    response: `🤖 **Dusty Bot - Your Crypto Dust Consolidator**

I can help you clean up your wallet dust! Here's what I can do:

• **Check balances** - "What's my balance?"
• **Find dust** - "Identify my dust positions"
• **Plan consolidation** - "How do I consolidate?"
• **Execute cleanup** - "Confirm to proceed"

What would you like to do?`,
    action: 'help',
    data: {}
  };
}

/**
 * POST /receive_message
 * Accepts messages from core-agent and returns canned Dusty responses
 */
app.post('/receive_message', (req, res) => {
  const { message, user_id, session_id } = req.body;
  
  // Log incoming message
  logInteraction('RECEIVED', {
    endpoint: '/receive_message',
    user_id: user_id || 'anonymous',
    session_id: session_id || 'default',
    message: message
  });
  
  if (!message) {
    const error = { error: 'Message is required' };
    logInteraction('ERROR', error);
    return res.status(400).json(error);
  }
  
  // Generate response
  const response = generateDustyResponse(message);
  
  // Log outgoing response
  logInteraction('SENT', {
    endpoint: '/receive_message',
    response: response
  });
  
  res.json(response);
});

/**
 * GET /status
 * Health check endpoint
 */
app.get('/status', (req, res) => {
  const status = {
    status: 'healthy',
    service: 'openclaw-mock',
    port: PORT,
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
    total_interactions: interactionLogs.length
  };
  
  logInteraction('HEALTH_CHECK', status);
  
  res.json(status);
});

/**
 * GET /logs
 * View interaction logs (for debugging)
 */
app.get('/logs', (req, res) => {
  const limit = parseInt(req.query.limit) || 50;
  res.json({
    total: interactionLogs.length,
    logs: interactionLogs.slice(-limit)
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`╔════════════════════════════════════════════════════════╗`);
  console.log(`║     OpenClaw Mock Service - Dusty Bot Simulator        ║`);
  console.log(`╠════════════════════════════════════════════════════════╣`);
  console.log(`║  Port: ${PORT}                                            ║`);
  console.log(`║  Endpoints:                                            ║`);
  console.log(`║    POST /receive_message - Send messages to Dusty      ║`);
  console.log(`║    GET  /status          - Health check                ║`);
  console.log(`║    GET  /logs            - View interaction logs       ║`);
  console.log(`╚════════════════════════════════════════════════════════╝`);
  console.log('');
  console.log('Ready to receive messages from core-agent!');
});

module.exports = app;

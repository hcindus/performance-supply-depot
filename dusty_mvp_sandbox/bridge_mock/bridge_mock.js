/**
 * Telegram Bridge Mock
 * 
 * Simulates a Telegram bot webhook that forwards messages
to the core-agent service.
 */

const express = require('express');
const axios = require('axios');

const app = express();
const PORT = 3001;
const CORE_AGENT_URL = process.env.CORE_AGENT_URL || 'http://agent-core:3000/tasks';

app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  if (req.body && Object.keys(req.body).length > 0) {
    console.log('  Body:', JSON.stringify(req.body, null, 2));
  }
  next();
});

/**
 * POST /webhook - Receives simulated Telegram webhook messages
 * Forwards them to the core-agent
 */
app.post('/webhook', async (req, res) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] 📩 Received webhook from Telegram`);
  
  try {
    // Validate Telegram message format
    if (!req.body || !req.body.message) {
      console.log(`[${timestamp}] ⚠️ Invalid webhook payload - missing message`);
      return res.status(400).json({ error: 'Invalid payload: expected Telegram message format' });
    }

    const telegramMessage = req.body;
    const { message } = telegramMessage;
    
    console.log(`[${timestamp}] 💬 Message from ${message.from?.username || message.from?.id}: ${message.text || '(no text)'}`);

    // Transform to core-agent task format
    const taskPayload = {
      type: 'telegram_message',
      payload: {
        source: 'telegram',
        messageId: message.message_id,
        chatId: message.chat?.id,
        userId: message.from?.id,
        username: message.from?.username,
        firstName: message.from?.first_name,
        lastName: message.from?.last_name,
        text: message.text,
        timestamp: new Date(message.date * 1000).toISOString(),
        raw: telegramMessage
      }
    };

    console.log(`[${timestamp}] 🔄 Forwarding to core-agent at ${CORE_AGENT_URL}`);

    // Forward to core-agent
    const response = await axios.post(CORE_AGENT_URL, taskPayload, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 10000
    });

    console.log(`[${timestamp}] ✅ Core-agent responded: ${response.status}`);
    console.log(`[${timestamp}] 📤 Response:`, JSON.stringify(response.data, null, 2));

    // Return Telegram webhook acknowledgment
    res.status(200).json({ 
      ok: true,
      forwarded: true,
      coreAgentResponse: response.data
    });

  } catch (error) {
    console.error(`[${timestamp}] ❌ Error forwarding to core-agent:`, error.message);
    
    if (error.response) {
      console.error(`[${timestamp}] Core-agent error response:`, error.response.status, error.response.data);
    } else if (error.code === 'ECONNREFUSED') {
      console.error(`[${timestamp}] Core-agent connection refused - is it running?`);
    }

    // Still return 200 to Telegram to prevent retries, but indicate failure
    res.status(200).json({ 
      ok: true, 
      forwarded: false,
      error: error.message 
    });
  }
});

/**
 * GET /test - Sends a mock Telegram message to core-agent
 * Useful for testing the bridge without actual Telegram
 */
app.get('/test', async (req, res) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] 🧪 Test endpoint triggered - sending mock message to core-agent`);

  const mockTelegramMessage = {
    update_id: 123456789,
    message: {
      message_id: 1,
      from: {
        id: 987654321,
        is_bot: false,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser',
        language_code: 'en'
      },
      chat: {
        id: 987654321,
        first_name: 'Test',
        last_name: 'User',
        username: 'testuser',
        type: 'private'
      },
      date: Math.floor(Date.now() / 1000),
      text: 'Hello from bridge mock test! 👋'
    }
  };

  try {
    console.log(`[${timestamp}] 📤 Sending mock message to core-agent at ${CORE_AGENT_URL}`);

    const response = await axios.post(CORE_AGENT_URL, {
      type: 'telegram_message',
      payload: {
        source: 'telegram',
        messageId: mockTelegramMessage.message.message_id,
        chatId: mockTelegramMessage.message.chat.id,
        userId: mockTelegramMessage.message.from.id,
        username: mockTelegramMessage.message.from.username,
        firstName: mockTelegramMessage.message.from.first_name,
        lastName: mockTelegramMessage.message.from.last_name,
        text: mockTelegramMessage.message.text,
        timestamp: new Date(mockTelegramMessage.message.date * 1000).toISOString(),
        raw: mockTelegramMessage
      }
    }, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 10000
    });

    console.log(`[${timestamp}] ✅ Test successful! Core-agent responded:`);
    console.log(`[${timestamp}] Response:`, JSON.stringify(response.data, null, 2));

    res.json({
      success: true,
      message: 'Mock message sent to core-agent successfully',
      coreAgentUrl: CORE_AGENT_URL,
      mockMessage: mockTelegramMessage,
      coreAgentResponse: response.data
    });

  } catch (error) {
    console.error(`[${timestamp}] ❌ Test failed:`, error.message);
    
    let errorDetails = {
      message: error.message,
      code: error.code
    };

    if (error.response) {
      errorDetails.status = error.response.status;
      errorDetails.data = error.response.data;
    }

    res.status(500).json({
      success: false,
      message: 'Failed to send mock message to core-agent',
      coreAgentUrl: CORE_AGENT_URL,
      error: errorDetails,
      mockMessage: mockTelegramMessage
    });
  }
});

/**
 * GET /health - Docker healthcheck endpoint
 */
app.get('/health', (req, res) => {
  const timestamp = new Date().toISOString();
  
  const healthStatus = {
    status: 'healthy',
    timestamp: timestamp,
    service: 'telegram-bridge-mock',
    port: PORT,
    coreAgentUrl: CORE_AGENT_URL,
    uptime: process.uptime()
  };

  console.log(`[${timestamp}] 💓 Health check: OK`);
  res.status(200).json(healthStatus);
});

/**
 * GET / - Root endpoint with basic info
 */
app.get('/', (req, res) => {
  res.json({
    service: 'Telegram Bridge Mock',
    version: '1.0.0',
    endpoints: {
      'POST /webhook': 'Receive Telegram webhook messages',
      'GET /test': 'Send a mock message to core-agent',
      'GET /health': 'Health check for Docker',
      'GET /': 'This info page'
    },
    coreAgentUrl: CORE_AGENT_URL
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  console.log('='.repeat(60));
  console.log('🤖 Telegram Bridge Mock');
  console.log('='.repeat(60));
  console.log(`📡 Listening on port ${PORT}`);
  console.log(`🎯 Core-agent URL: ${CORE_AGENT_URL}`);
  console.log('');
  console.log('Endpoints:');
  console.log(`  POST http://localhost:${PORT}/webhook  - Receive Telegram messages`);
  console.log(`  GET  http://localhost:${PORT}/test     - Send test message to core-agent`);
  console.log(`  GET  http://localhost:${PORT}/health   - Health check`);
  console.log('='.repeat(60));
});

module.exports = app;

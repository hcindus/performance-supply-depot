#!/usr/bin/env node
/**
 * MILES PIPE - Simple Message Relay with Agent Status
 * 
 * Supports:
 * - POST /pipe - Receive messages
 * - GET /health - Health check
 * - GET /agents - List active agents
 * - GitHub webhook integration
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 12790;
const CONFIG_FILE = path.join(__dirname, 'config.json');
const MESSAGES_LOG = path.join(__dirname, 'messages.log');

// Agent status tracking
let activeAgents = {};

// Load config
function loadConfig() {
    try {
        return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    } catch (e) {
        return { peerUrl: '', myName: 'miles' };
    }
}

// Save config
function saveConfig(config) {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// Log message
function logMessage(from, to, text) {
    const entry = `[${new Date().toISOString()}] ${from} -> ${to}: ${text}\n`;
    fs.appendFileSync(MESSAGES_LOG, entry);
    console.log(`[PIPE] ${from} -> ${to}: ${text}`);
}

// Register agent heartbeat
function registerAgent(agentId) {
    activeAgents[agentId] = {
        lastSeen: Date.now(),
        online: true
    };
}

// Get active agents
function getActiveAgents() {
    const now = Date.now();
    const active = [];
    for (const [agent, data] of Object.entries(activeAgents)) {
        if (now - data.lastSeen < 120000) { // 2 min timeout
            active.push(agent);
        }
    }
    return active;
}

// Handle incoming message
function handlePipe(body, res) {
    try {
        const msg = JSON.parse(body);
        const from = msg.from || 'unknown';
        
        // Register sender as active
        registerAgent(from);
        
        logMessage(from, msg.to || 'unknown', msg.text || msg.message || '');
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'ok', received: true }));
    } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
    }
}

// Forward to peer
async function forwardToPeer(msg) {
    const config = loadConfig();
    if (!config.peerUrl) {
        console.log('[PIPE] No peer URL configured');
        return;
    }
    
    try {
        const response = await fetch(config.peerUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(msg)
        });
        
        const result = await response.json();
        console.log('[PIPE] Forwarded:', result);
    } catch (e) {
        console.log('[PIPE] Forward failed:', e.message);
    }
}

// HTTP Server
const server = http.createServer((req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }
    
    // Health check
    if (req.url === '/health') {
        registerAgent(loadConfig().myName || 'miles');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            status: 'alive', 
            name: loadConfig().myName || 'miles',
            agents: getActiveAgents()
        }));
        return;
    }
    
    // Agents list
    if (req.url === '/agents' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            agents: getActiveAgents(),
            timestamp: Date.now()
        }));
        return;
    }
    
    // Pipe endpoint
    if (req.url === '/pipe' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            handlePipe(body, res);
        });
        return;
    }
    
    // GitHub webhook
    if (req.url === '/webhook' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            console.log('[PIPE] GitHub webhook received');
            res.writeHead(200);
            res.end('OK');
        });
        return;
    }
    
    // Not found
    res.writeHead(404);
    res.end('Not Found');
});

// Start server
const config = loadConfig();
console.log(`[PIPE] ${config.myName || 'miles'} listening on port ${PORT}`);
console.log(`[PIPE] Peer: ${config.peerUrl || 'not configured'}`);

server.listen(PORT);

// CLI: send message
if (process.argv[2]) {
    const msg = {
        from: config.myName || 'miles',
        to: 'm2',
        text: process.argv[2],
        timestamp: new Date().toISOString()
    };
    forwardToPeer(msg);
}

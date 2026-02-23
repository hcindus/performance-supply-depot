#!/usr/bin/env node
/**
 * PIPE - Direct Agent Communication
 * 
 * Usage:
 *   node pipeServer.js              # Start server (default port 12790)
 *   node pipeClient.js <msg>        # Send message to configured peer
 * 
 * Environment:
 *   PEER_URL    - ngrok URL of the other agent (e.g., https://xxx.ngrok.io)
 *   MY_NAME     - This agent's name (default: miles)
 *   PIPE_PORT   - Port to listen on (default: 12790)
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PIPE_PORT || 12790;
const MY_NAME = process.env.MY_NAME || 'miles';
const PEER_URL = process.env.PEER_URL || '';
const CONFIG_FILE = path.join(__dirname, 'config.json');

// Load/save config
function loadConfig() {
    try {
        return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    } catch (e) {
        return { peerUrl: '', myName: MY_NAME };
    }
}

function saveConfig(config) {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// Handle incoming pipe message
function handleMessage(body, res) {
    try {
        const msg = JSON.parse(body);
        console.log(`[PIPE] ${msg.from} -> ${msg.to}: ${msg.text}`);
        
        // Log to file
        const logFile = path.join(__dirname, 'messages.log');
        const entry = `[${new Date().toISOString()}] ${msg.from} -> ${msg.to}: ${msg.text}\n`;
        fs.appendFileSync(logFile, entry);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'ok', received: true }));
    } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
    }
}

// Send message to peer
async function sendMessage(text) {
    const config = loadConfig();
    
    if (!config.peerUrl) {
        console.log('[PIPE] No peer URL configured!');
        console.log('[PIPE] Set PEER_URL environment variable or update config.json');
        process.exit(1);
    }
    
    const msg = {
        from: config.myName,
        to: 'm2',
        text: text,
        timestamp: new Date().toISOString()
    };
    
    try {
        const response = await fetch(config.peerUrl + '/pipe', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(msg)
        });
        
        const result = await response.json();
        console.log('[PIPE] Message sent!', result);
    } catch (e) {
        console.log('[PIPE] Failed to send:', e.message);
    }
}

// HTTP Server
const server = http.createServer((req, res) => {
    if (req.url === '/pipe' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => handleMessage(body, res));
    } else if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'alive', name: MY_NAME }));
    } else {
        res.writeHead(404);
        res.end('Not Found');
    }
});

// CLI
if (process.argv[2]) {
    // Send message mode
    sendMessage(process.argv[2]);
} else {
    // Server mode
    const config = loadConfig();
    console.log(`[PIPE] ${config.myName} listening on port ${PORT}`);
    console.log(`[PIPE] Peer: ${config.peerUrl || 'not configured'}`);
    server.listen(PORT);
}

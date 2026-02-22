#!/usr/bin/env node
/**
 * COMMS STATION - Multi-Agent Communication Hub
 * 
 * Allows any agent to send/receive messages
 * 
 * Usage:
 *   node comms.js                    # Start hub
 *   node comms.js <from> <to> <msg> # Send message
 *   curl http://localhost:12792/agents/<agent>  # Get agent's messages
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const PORT = process.env.COMMS_PORT || 12792;
const HUB_DIR = path.join(__dirname, 'comms_hub');
const CONFIG_FILE = path.join(__dirname, 'comms_config.json');

// Ensure hub directory exists
if (!fs.existsSync(HUB_DIR)) {
    fs.mkdirSync(HUB_DIR, { recursive: true });
}

// Load config
function loadConfig() {
    try {
        return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    } catch (e) {
        return {
            hubName: 'COMMS_HUB',
            agents: {},
            peerHubs: {}
        };
    }
}

function saveConfig(config) {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// Get agent's inbox
function getAgentInbox(agent) {
    const inboxDir = path.join(HUB_DIR, agent);
    if (!fs.existsSync(inboxDir)) {
        fs.mkdirSync(inboxDir, { recursive: true });
    }
    const files = fs.readdirSync(inboxDir).filter(f => f.endsWith('.json')).sort().reverse();
    const messages = [];
    for (const file of files.slice(0, 50)) {
        try {
            messages.push(JSON.parse(fs.readFileSync(path.join(inboxDir, file), 'utf8')));
        } catch (e) {}
    }
    return messages;
}

// Save message to agent's inbox
function saveMessage(to, message) {
    const inboxDir = path.join(HUB_DIR, to);
    if (!fs.existsSync(inboxDir)) {
        fs.mkdirSync(inboxDir, { recursive: true });
    }
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `msg_${timestamp}.json`;
    fs.writeFileSync(path.join(inboxDir, filename), JSON.stringify(message, null, 2));
}

// Forward to peer hub
async function forwardToPeer(peerUrl, message) {
    try {
        const response = await fetch(peerUrl + '/relay', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(message)
        });
        return await response.json();
    } catch (e) {
        return { error: e.message };
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
        const config = loadConfig();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            status: 'alive', 
            hub: config.hubName,
            agents: Object.keys(config.agents),
            peers: Object.keys(config.peerHubs)
        }));
        return;
    }
    
    // List all agents
    if (req.url === '/agents') {
        const config = loadConfig();
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            agents: Object.keys(config.agents),
            peers: Object.keys(config.peerHubs)
        }));
        return;
    }
    
    // Get agent's messages: /agents/<name>
    const agentMatch = req.url.match(/^\/agents\/([a-zA-Z0-9_-]+)$/);
    if (agentMatch && req.method === 'GET') {
        const agent = agentMatch[1];
        const messages = getAgentInbox(agent);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ agent, messages }));
        return;
    }
    
    // Send message: POST /send
    if (req.url === '/send' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const msg = JSON.parse(body);
                const { from, to, text, peer } = msg;
                
                // Save to recipient's inbox
                if (to) {
                    saveMessage(to, { from, to, text, timestamp: new Date().toISOString() });
                }
                
                // Forward to peer hub if specified
                const config = loadConfig();
                if (peer && config.peerHubs[peer]) {
                    const result = await forwardToPeer(config.peerHubs[peer], msg);
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ status: 'sent', forwarded: result }));
                } else {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ status: 'sent', to }));
                }
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }
    
    // Register agent: POST /register
    if (req.url === '/register' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                const config = loadConfig();
                config.agents[data.name] = data;
                saveConfig(config);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ status: 'registered', name: data.name }));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }
    
    // Add peer hub: POST /peers
    if (req.url === '/peers' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                const config = loadConfig();
                config.peerHubs[data.name] = data.url;
                saveConfig(config);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ status: 'peer_added', name: data.name, url: data.url }));
            } catch (e) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: e.message }));
            }
        });
        return;
    }
    
    // Not found
    res.writeHead(404);
    res.end('Not Found');
});

// CLI: send message
if (process.argv[2]) {
    const config = loadConfig();
    const from = config.hubName || 'miles';
    const to = process.argv[2];
    const text = process.argv.slice(3).join(' ');
    
    const msg = { from, to, text, timestamp: new Date().toISOString() };
    saveMessage(to, msg);
    console.log(`[COMMS] Message sent: ${from} -> ${to}: ${text}`);
} else {
    const config = loadConfig();
    console.log(`[COMMS] ${config.hubName} listening on port ${PORT}`);
    server.listen(PORT);
}

#!/usr/bin/env node
/**
 * GITHUB WEBHOOK RECEIVER
 * Listens for push events from GitHub
 */

const http = require('http');
const crypto = require('crypto');

const PORT = process.env.WEBHOOK_PORT || 12791;
const SECRET = process.env.WEBHOOK_SECRET || '';

const fs = require('fs');
const path = require('path');

// Log file
const LOG_FILE = path.join(__dirname, 'webhook.log');

function log(msg) {
    const entry = `[${new Date().toISOString()}] ${msg}\n`;
    fs.appendFileSync(LOG_FILE, entry);
    console.log(msg);
}

function handleWebhook(req, res) {
    if (req.url !== '/webhook') {
        res.writeHead(404);
        res.end('Not Found');
        return;
    }

    if (req.method !== 'POST') {
        res.writeHead(405);
        res.end('Method Not Allowed');
        return;
    }

    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
        // Verify signature if secret is set
        if (SECRET) {
            const sig = req.headers['x-hub-signature-256'];
            if (sig) {
                const hmac = crypto.createHmac('sha256', SECRET);
                const digest = 'sha256=' + hmac.update(body).digest('hex');
                if (sig !== digest) {
                    log('⚠️ Invalid signature!');
                    res.writeHead(401);
                    res.end('Unauthorized');
                    return;
                }
            }
        }

        try {
            const event = req.headers['x-github-event'];
            const data = JSON.parse(body);

            log(`📥 GitHub Event: ${event}`);

            if (event === 'push') {
                log(`   Branch: ${data.ref}`);
                log(`   commits: ${data.commits?.length || 0}`);
            }

            // Notify pipe to check for messages/config
            if (event === 'push') {
                log('🔄 Triggering git pull...');
                const { exec } = require('child_process');
                exec('cd /root/.openclaw/workspace && git pull origin main 2>&1', (err, stdout, stderr) => {
                    if (err) {
                        log('❌ Git pull failed: ' + err.message);
                    } else {
                        log('✅ Git pull completed');
                        log(stdout);
                    }
                });
            }

            res.writeHead(200);
            res.end('OK');
        } catch (e) {
            log('❌ Error: ' + e.message);
            res.writeHead(400);
            res.end('Bad Request');
        }
    });
}

const server = http.createServer(handleWebhook);
server.listen(PORT, () => {
    log(`🌐 Webhook receiver listening on port ${PORT}`);
    log(`   URL: http://localhost:${PORT}/webhook`);
});

#!/usr/bin/env node
/**
 * TUNNEL MANAGER - Auto-restart & health monitoring
 * Keeps localtunnel alive with automatic recovery
 */

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 12790;
const SUBDOMAIN = process.env.SUBDOMAIN || 'miles';
const HEALTH_INTERVAL = 30000; // Check every 30s
const RESTART_DELAY = 5000;

let tunnelProcess = null;
let serverProcess = null;
let currentUrl = '';

const LOG_FILE = path.join(__dirname, 'tunnel_manager.log');
const CONFIG_FILE = path.join(__dirname, 'config.json');

function log(msg) {
    const entry = `[${new Date().toISOString()}] ${msg}\n`;
    console.log(msg);
    fs.appendFileSync(LOG_FILE, entry);
}

function loadConfig() {
    try {
        return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    } catch (e) {
        return { peerUrl: '', myName: 'miles' };
    }
}

// Kill existing processes
function killExisting() {
    return new Promise((resolve) => {
        exec('pkill -f "lt --port" 2>/dev/null; pkill -f "node pipe" 2>/dev/null', () => {
            setTimeout(resolve, 1000);
        });
    });
}

// Start the pipe server
function startServer() {
    return new Promise((resolve, reject) => {
        serverProcess = spawn('node', ['server.js'], {
            cwd: path.join(__dirname),
            detached: true,
            stdio: 'ignore'
        });
        
        serverProcess.on('error', (err) => {
            log('❌ Server error: ' + err.message);
            reject(err);
        });
        
        setTimeout(() => {
            exec('curl -s http://localhost:12790/health', (err, stdout) => {
                if (stdout.includes('alive')) {
                    log('✅ Server started');
                    resolve();
                } else {
                    reject(new Error('Server not responding'));
                }
            });
        }, 2000);
    });
}

// Start localtunnel
function startTunnel() {
    return new Promise((resolve, reject) => {
        log('🔗 Starting localtunnel...');
        
        tunnelProcess = spawn('lt', ['--port', PORT.toString(), '--subdomain', SUBDOMAIN], {
            stdio: ['ignore', 'pipe', 'pipe']
        });
        
        let urlFound = false;
        
        tunnelProcess.stdout.on('data', (data) => {
            const output = data.toString();
            log('📡 Tunnel: ' + output.trim());
            
            const urlMatch = output.match(/your url is: (https:\/\/[a-z0-9-]+\.loca\.lt)/);
            if (urlMatch) {
                currentUrl = urlMatch[1];
                urlFound = true;
                log('✅ Tunnel ready: ' + currentUrl);
                updateReadme(currentUrl);
                resolve(currentUrl);
            }
        });
        
        tunnelProcess.stderr.on('data', (data) => {
            const output = data.toString();
            // Ignore some common warnings
            if (!output.includes(' signaling') && !output.includes('connection')) {
                log('⚠️ Tunnel: ' + output.trim());
            }
        });
        
        tunnelProcess.on('error', (err) => {
            log('❌ Tunnel error: ' + err.message);
            reject(err);
        });
        
        tunnelProcess.on('exit', (code) => {
            log('🔄 Tunnel exited with code: ' + code);
            tunnelProcess = null;
        });
        
        // Timeout
        setTimeout(() => {
            if (!urlFound) {
                reject(new Error('Tunnel startup timeout'));
            }
        }, 15000);
    });
}

// Health check
function healthCheck() {
    return new Promise((resolve) => {
        exec('curl -s --max-time 5 http://localhost:12790/health', (err, stdout) => {
            if (err || !stdout.includes('alive')) {
                log('❌ Health check failed - server down');
                resolve(false);
            } else {
                // Also check tunnel
                exec('curl -s --max-time 5 ' + currentUrl + '/health', (err2, stdout2) => {
                    if (err2 || !stdout2.includes('alive')) {
                        log('⚠️ Tunnel may be down');
                        resolve(false);
                    } else {
                        resolve(true);
                    }
                });
            }
        });
    });
}

// Update README with current URL
function updateReadme(url) {
    const readmePath = path.join(__dirname, 'README.md');
    try {
        let content = fs.readFileSync(readmePath, 'utf8');
        content = content.replace(/URL: `https:\/\/[a-z0-9-]+\.loca\.lt`/, 'URL: `' + url + '`');
        fs.writeFileSync(readmePath, content);
        log('📝 Updated README with URL');
    } catch (e) {
        log('⚠️ Could not update README: ' + e.message);
    }
}

// Push to GitHub
function pushUrlToGit(url) {
    const msgPath = path.join(__dirname, '../memory/message.md');
    try {
        let content = '';
        try {
            content = fs.readFileSync(msgPath, 'utf8');
        } catch (e) {}
        
        // Update URL if found
        if (content.includes('https://')) {
            content = content.replace(/https:\/\/[a-z0-9-]+\.loca\.lt/, url);
            fs.writeFileSync(msgPath, content);
        }
        
        // Commit and push
        exec('cd ' + path.join(__dirname, '..') + ' && git add pipe/ memory/message.md && git commit -m "MILES: URL ' + url + '" && git push origin main', (err) => {
            if (err) {
                log('⚠️ Git push failed: ' + err.message);
            } else {
                log('✅ Pushed URL to GitHub');
            }
        });
    } catch (e) {
        log('⚠️ Git push error: ' + e.message);
    }
}

// Main loop
async function main() {
    log('🚀 Tunnel Manager starting...');
    
    // Clean start
    await killExisting();
    
    // Start server
    await startServer();
    
    // Start tunnel
    try {
        currentUrl = await startTunnel();
        pushUrlToGit(currentUrl);
    } catch (e) {
        log('❌ Initial tunnel failed: ' + e.message);
    }
    
    // Health check loop
    setInterval(async () => {
        const healthy = await healthCheck();
        
        if (!healthy) {
            log('🔄 Restarting tunnel...');
            await killExisting();
            
            try {
                await startServer();
                currentUrl = await startTunnel();
                pushUrlToGit(currentUrl);
            } catch (e) {
                log('❌ Restart failed: ' + e.message);
            }
        }
    }, HEALTH_INTERVAL);
}

main();

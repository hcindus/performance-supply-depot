#!/usr/bin/env node
/**
 * GITHUB POLLER
 * Periodically checks GitHub for new commits/messages
 */

const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const POLL_INTERVAL = 60000; // 1 minute
const LAST_COMMIT_FILE = path.join(__dirname, '.last_commit');

let lastCommit = '';

// Load last known commit
try {
    lastCommit = fs.readFileSync(LAST_COMMIT_FILE, 'utf8').trim();
} catch (e) {}

// Check for new commits
function checkGitHub() {
    exec(`cd ${WORKSPACE} && git fetch origin main`, (err, stdout, stderr) => {
        if (err) {
            log('Fetch error: ' + err.message);
            return;
        }
        
        exec(`cd ${WORKSPACE} && git log origin/main --oneline -1`, (err, stdout, stderr) => {
            if (err) {
                log('Log error: ' + err.message);
                return;
            }
            
            const currentCommit = stdout.trim();
            
            if (currentCommit && currentCommit !== lastCommit) {
                log('📥 NEW COMMIT: ' + currentCommit);
                
                // Pull the changes
                exec(`cd ${WORKSPACE} && git pull origin main`, (err, stdout, stderr) => {
                    if (err) {
                        log('❌ Pull failed: ' + err.message);
                    } else {
                        log('✅ Pulled new changes');
                        lastCommit = currentCommit;
                        fs.writeFileSync(LAST_COMMIT_FILE, lastCommit);
                        
                        // Check for messages
                        checkForMessages();
                    }
                });
            } else {
                log('No new commits');
            }
        });
    });
}

// Check for messages in memory/message.md
function checkForMessages() {
    const msgFile = path.join(WORKSPACE, 'memory/message.md');
    const configFile = path.join(WORKSPACE, 'pipe/config.json');
    
    // Check if config.json was added (M2's tunnel URL)
    if (fs.existsSync(configFile)) {
        const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
        log('🎉 Peer URL configured: ' + config.peerUrl);
        
        // Restart pipe with new peer
        exec('pkill -f "node pipe.js"');
        setTimeout(() => {
            spawn('node', ['pipe.js'], {
                cwd: path.join(WORKSPACE, 'pipe'),
                detached: true,
                stdio: 'ignore'
            }).unref();
            log('🔄 Pipe restarted with peer config');
        }, 1000);
    }
}

function log(msg) {
    const entry = `[${new Date().toISOString()}] ${msg}\n`;
    console.log(msg);
    fs.appendFileSync(path.join(__dirname, 'poller.log'), entry);
}

// Start polling
log('🚀 GitHub Poller started');
setInterval(checkGitHub, POLL_INTERVAL);

// Initial check
checkGitHub();

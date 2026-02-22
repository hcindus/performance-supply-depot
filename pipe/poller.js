#!/usr/bin/env node
/**
 * MILES PIPE POLLER
 * Checks GitHub for new messages + monitors pipe
 */

const { exec } = require('child_process');
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

// Check GitHub for new commits
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
                    }
                });
            }
        });
    });
}

// Also check aocros repo
function checkAocros() {
    exec(`cd ${WORKSPACE} && git fetch aocros main`, (err, stdout, stderr) => {
        if (err) return;
        
        exec(`cd ${WORKSPACE} && git log aocros/main --oneline -1`, (err, stdout, stderr) => {
            if (err) return;
            
            const currentCommit = stdout.trim().split(' ')[0];
            const aocrosFile = path.join(WORKSPACE, 'pipe/.last_aocros_commit');
            let lastAocrosCommit = '';
            
            try {
                lastAocrosCommit = fs.readFileSync(aocrosFile, 'utf8').trim();
            } catch (e) {}
            
            if (currentCommit && currentCommit !== lastAocrosCommit) {
                log('📥 NEW AOCROS COMMIT: ' + currentCommit);
                fs.writeFileSync(aocrosFile, currentCommit);
                
                // Check for new messages
                checkMessages();
            }
        });
    });
}

function checkMessages() {
    // Check memory/message.md for any updates
    const msgFile = path.join(WORKSPACE, 'memory/message.md');
    if (fs.existsSync(msgFile)) {
        const content = fs.readFileSync(msgFile, 'utf8');
        if (content.includes('https://')) {
            // Extract URL if present
            const urlMatch = content.match(/https:\/\/[a-z0-9-]+\.loca\.lt/);
            if (urlMatch) {
                log('🔗 Found URL in message: ' + urlMatch[0]);
            }
        }
    }
}

function log(msg) {
    const entry = `[${new Date().toISOString()}] ${msg}\n`;
    console.log(msg);
    fs.appendFileSync(path.join(__dirname, 'poller.log'), entry);
}

// Start polling
log('🚀 Poller started - GitHub + localtunnel');

// Initial check
checkGitHub();
checkAocros();

// Poll every minute
setInterval(() => {
    checkGitHub();
    checkAocros();
}, POLL_INTERVAL);

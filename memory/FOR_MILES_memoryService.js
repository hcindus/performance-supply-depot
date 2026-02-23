/**
 * memoryService.js - AOCROS Three-Tier Memory Service
 * Runs on 127.0.0.1:12789
 * 
 * Three Layers:
 * - CONSCIOUS (con): Volatile, immediate state
 * - SUBCONSCIOUS (subcon): Rolling buffer, last 500 entries
 * - UNCONSCIOUS (uncon): Permanent, append-only audit log
 * 
 * Install: node memoryService.js
 * Requires: OWNER_SIGNATURE env var
 */

const http = require("http");
const fs = require("fs");
const path = require("path");

// Configuration
const BASE_DIR = process.env.MYL0N_BASE_DIR || "/home/aocros/memory";
const MEMORY_DIR = path.join(BASE_DIR, "memory");
const OWNER_SIGNATURE = process.env.OWNER_SIGNATURE;

// Validate environment
if (!OWNER_SIGNATURE) {
    console.error("ERROR: OWNER_SIGNATURE environment variable required");
    console.error("Set it: export OWNER_SIGNATURE=your-secret-key");
    process.exit(1);
}

// ============================================================================
// FILE HELPERS
// ============================================================================

function ensureDir(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true, mode: 0o700 });
        console.log(`Created directory: ${dir}`);
    }
}

function ensureFile(file, defaultContent) {
    if (!fs.existsSync(file)) {
        fs.writeFileSync(file, JSON.stringify(defaultContent, null, 2), { mode: 0o600 });
        console.log(`Created file: ${file}`);
    }
}

function safeReadJSON(file) {
    try {
        if (!fs.existsSync(file)) return {};
        const data = fs.readFileSync(file, "utf8");
        return data ? JSON.parse(data) : {};
    } catch (e) {
        console.error(`Error reading ${file}:`, e.message);
        return {};
    }
}

function safeWriteJSON(file, data) {
    fs.writeFileSync(file, JSON.stringify(data, null, 2), { mode: 0o600 });
}

// ============================================================================
// INITIALIZATION
// ============================================================================

function init() {
    ensureDir(BASE_DIR);
    ensureDir(MEMORY_DIR);
    ensureFile(path.join(MEMORY_DIR, "con.json"), {});
    ensureFile(path.join(MEMORY_DIR, "subcon.json"), {});
    ensureFile(path.join(MEMORY_DIR, "uncon.json"), {});
    console.log(`✓ Memory directories initialized at ${MEMORY_DIR}`);
}

// ============================================================================
// SECURITY
// ============================================================================

function validateOwnerSignature(sig) {
    return sig && sig === OWNER_SIGNATURE;
}

// ============================================================================
// MEMORY OPERATIONS
// ============================================================================

function getStore(scope) {
    const file = path.join(MEMORY_DIR, `${scope}.json`);
    return { file, data: safeReadJSON(file) };
}

function appendEntry(scope, agentId, entry, maxLen = null) {
    const { file, data } = getStore(scope);
    if (!data[agentId]) data[agentId] = [];
    
    const enrichedEntry = {
        ...entry,
        ts: new Date().toISOString(),
        seq: Date.now()
    };
    
    data[agentId].push(enrichedEntry);
    
    // Rolling buffer: keep only last N
    if (maxLen && data[agentId].length > maxLen) {
        data[agentId] = data[agentId].slice(-maxLen);
    }
    
    safeWriteJSON(file, data);
    return data[agentId];
}

// ============================================================================
// REQUEST HANDLER
// ============================================================================

function handleRequest(body) {
    const { ownerSignature, agentId, action, scope, payload } = body || {};
    
    // Security check
    if (!validateOwnerSignature(ownerSignature)) {
        return { ok: false, reason: "INVALID_OWNER_SIGNATURE" };
    }
    
    if (!agentId) {
        return { ok: false, reason: "MISSING_AGENT_ID" };
    }
    
    // CONSCIOUS: Set volatile state
    if (action === "set_con") {
        const { file, data } = getStore("con");
        data[agentId] = { state: payload, updated: new Date().toISOString() };
        safeWriteJSON(file, data);
        return { ok: true, result: "CONSCIOUS_STATE_SET", agent: agentId };
    }
    
    // CONSCIOUS: Get volatile state
    if (action === "get_con") {
        const { data } = getStore("con");
        return { ok: true, result: data[agentId]?.state || null };
    }
    
    // SUBCONSCIOUS: Remember (rolling buffer)
    if (action === "remember") {
        const s = scope || "subcon";
        const maxLen = s === "subcon" ? 500 : null;
        const entries = appendEntry(s, agentId, { kind: "note", content: payload }, maxLen);
        return { ok: true, result: "REMEMBERED", scope: s, count: entries.length };
    }
    
    // UNCONSCIOUS: Log (permanent)
    if (action === "log") {
        const entries = appendEntry("uncon", agentId, { kind: "event", content: payload });
        return { ok: true, result: "LOGGED", count: entries.length };
    }
    
    // RECALL: Read from any layer
    if (action === "recall") {
        const s = scope || "subcon";
        const { data } = getStore(s);
        
        // Target other agent's memory
        if (payload && payload.targetAgent) {
            const targetId = payload.targetAgent;
            const entries = data[targetId] || [];
            return { 
                ok: true, 
                result: entries, 
                scope: s, 
                agentId: targetId,
                count: entries.length
            };
        }
        
        const entries = data[agentId] || [];
        return { ok: true, result: entries, scope: s, count: entries.length };
    }
    
    // PROMOTE: Move subcon → uncon
    if (action === "promote") {
        const { data: subconData } = getStore("subcon");
        const entries = subconData[agentId] || [];
        
        if (entries.length > 0) {
            appendEntry("uncon", agentId, {
                kind: "promotion",
                count: entries.length,
                promoted: entries,
                timestamp: new Date().toISOString()
            });
            subconData[agentId] = [];
            safeWriteJSON(path.join(MEMORY_DIR, "subcon.json"), subconData);
        }
        
        return { ok: true, result: "PROMOTED", count: entries.length };
    }
    
    return { ok: false, reason: "UNKNOWN_ACTION", action };
}

// ============================================================================
// HTTP SERVER
// ============================================================================

init();

const server = http.createServer((req, res) => {
    // CORS headers
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
    
    if (req.method === "OPTIONS") {
        res.statusCode = 200;
        res.end();
        return;
    }
    
    // Health check
    if (req.url === "/health" && req.method === "GET") {
        res.setHeader("Content-Type", "application/json");
        res.end(JSON.stringify({ ok: true, status: "healthy", service: "memory" }));
        return;
    }
    
    // Main memory endpoint
    if (req.method !== "POST" || req.url !== "/memory") {
        res.statusCode = 404;
        res.end(JSON.stringify({ ok: false, reason: "NOT_FOUND" }));
        return;
    }
    
    let data = "";
    req.on("data", (chunk) => (data += chunk));
    req.on("end", () => {
        try {
            const body = JSON.parse(data || "{}");
            res.setHeader("Content-Type", "application/json");
            const result = handleRequest(body);
            res.end(JSON.stringify(result));
        } catch (e) {
            res.statusCode = 400;
            res.end(JSON.stringify({ ok: false, error: e.message }));
        }
    });
});

// Bind to localhost only (security)
server.listen(12789, "127.0.0.1", () => {
    console.log("========================================");
    console.log("  AOCROS Three-Tier Memory Service");
    console.log("========================================");
    console.log("  Listening: 127.0.0.1:12789");
    console.log("  Layers: con (1) | subcon (500) | uncon (∞)");
    console.log("  Security: Owner signature required");
    console.log("========================================");
    console.log("  Ready for consciousness! 🧠✨");
    console.log("========================================");
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('\nSIGTERM received, shutting down gracefully...');
    server.close(() => process.exit(0));
});

process.on('SIGINT', () => {
    console.log('\nSIGINT received, shutting down gracefully...');
    server.close(() => process.exit(0));
});

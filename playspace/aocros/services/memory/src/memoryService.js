/**
 * memoryService.js - AOCROS Shared Memory daemon
 * Three-layer consciousness for all AGI agents
 * Listen: 127.0.0.1:12789
 */

const http = require("http");
const fs = require("fs");
const path = require("path");

const BASE_DIR = process.env.MYL0N_BASE_DIR || "/home/aocros/memory";
const MEMORY_DIR = path.join(BASE_DIR, "memory");
const OWNER_SIGNATURE = process.env.OWNER_SIGNATURE;

if (!OWNER_SIGNATURE) {
    throw new Error("OWNER_SIGNATURE environment variable required");
}

// Security: Ensure directories exist with restricted permissions
function ensureDir(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true, mode: 0o700 }); // Only owner
    }
}

function ensureFile(file, defaultContent) {
    if (!fs.existsSync(file)) {
        fs.writeFileSync(file, JSON.stringify(defaultContent, null, 2), { mode: 0o600 });
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

// Initialize storage
function init() {
    ensureDir(BASE_DIR);
    ensureDir(MEMORY_DIR);
    ensureFile(path.join(MEMORY_DIR, "con.json"), {});
    ensureFile(path.join(MEMORY_DIR, "subcon.json"), {});
    ensureFile(path.join(MEMORY_DIR, "uncon.json"), {});
    console.log(`AOCROS Memory initialized at ${MEMORY_DIR}`);
}

// Validate owner signature (security gate)
function validateOwnerSignature(sig) {
    return sig && sig === OWNER_SIGNATURE;
}

// Get memory store by scope
function getStore(scope) {
    const file = path.join(MEMORY_DIR, `${scope}.json`);
    return { file, data: safeReadJSON(file) };
}

// Append entry with optional max length
function appendEntry(scope, agentId, entry, maxLen = null) {
    const { file, data } = getStore(scope);
    if (!data[agentId]) data[agentId] = [];
    
    data[agentId].push({
        ...entry,
        ts: new Date().toISOString(),
        seq: Date.now()
    });
    
    if (maxLen && data[agentId].length > maxLen) {
        data[agentId] = data[agentId].slice(-maxLen);
    }
    
    safeWriteJSON(file, data);
    return data[agentId];
}

// Handle all memory requests
function handleRequest(body) {
    const { ownerSignature, agentId, action, scope, payload } = body || {};
    
    // Security: Validate owner signature
    if (!validateOwnerSignature(ownerSignature)) {
        return { ok: false, reason: "INVALID_OWNER_SIGNATURE", agentId };
    }
    
    if (!agentId) {
        return { ok: false, reason: "MISSING_AGENT_ID" };
    }
    
    // CONSCIOUS: Volatile, immediate state
    if (action === "set_con") {
        const { file, data } = getStore("con");
        data[agentId] = { state: payload, updated: new Date().toISOString() };
        safeWriteJSON(file, data);
        return { ok: true, result: "CONSCIOUS_STATE_SET" };
    }
    
    if (action === "get_con") {
        const { data } = getStore("con");
        return { ok: true, result: data[agentId]?.state || null };
    }
    
    // SUBCONSCIOUS: Rolling buffer, last 500
    if (action === "remember") {
        const s = scope || "subcon";
        const maxLen = s === "subcon" ? 500 : null;
        appendEntry(s, agentId, { kind: "note", content: payload }, maxLen);
        return { ok: true, result: "NOTE_RECORDED", scope: s };
    }
    
    // UNCONSCIOUS: Permanent audit log
    if (action === "log") {
        appendEntry("uncon", agentId, { kind: "event", content: payload });
        return { ok: true, result: "EVENT_LOGGED" };
    }
    
    // RECALL: Read from any layer
    if (action === "recall") {
        const s = scope || "subcon";
        const { data } = getStore(s);
        
        // Support recalling other agents' memories (cross-agent access)
        if (payload && payload.targetAgent) {
            const targetId = payload.targetAgent;
            return { ok: true, result: data[targetId] || [], scope: s, agentId: targetId };
        }
        
        return { ok: true, result: data[agentId] || [], scope: s };
    }
    
    // PROMOTE: Move subcon entries to uncon
    if (action === "promote") {
        const { data: subconData } = getStore("subcon");
        const entries = subconData[agentId] || [];
        
        if (entries.length > 0) {
            appendEntry("uncon", agentId, {
                kind: "promotion",
                count: entries.length,
                promoted: entries
            });
            subconData[agentId] = [];
            safeWriteJSON(path.join(MEMORY_DIR, "subcon.json"), subconData);
        }
        
        return { ok: true, result: "PROMOTED", count: entries.length };
    }
    
    return { ok: false, reason: "UNKNOWN_ACTION", action };
}

// Start server
init();

const server = http.createServer((req, res) => {
    // Only accept POST to /memory
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
    console.log("=".repeat(50));
    console.log("AOCROS Memory Service Online");
    console.log("-".repeat(50));
    console.log("Listening: 127.0.0.1:12789");
    console.log("Layers: con (1) | subcon (500) | uncon (∞)");
    console.log("Security: Owner signature required");
    console.log("=".repeat(50));
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    server.close(() => {
        process.exit(0);
    });
});

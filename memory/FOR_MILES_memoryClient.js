/**
 * memoryClient.js - Universal client for AOCROS Memory Service
 * Works with Miles, Clawbot, CREAM, ALPHA-9, Mylzeron
 * 
 * Usage:
 *   const { makeMemoryClient } = require('./memoryClient');
 *   const memory = makeMemoryClient("miles");
 *   await memory.remember("Something important");
 *   const thoughts = await memory.recall();
 */

const http = require("http");

const MEMORY_HOST = process.env.MEMORY_HOST || "127.0.0.1";
const MEMORY_PORT = process.env.MEMORY_PORT || 12789;

// ============================================================================
// CORE HTTP CALL
// ============================================================================

function callMemory({ action, scope, payload, agentId, ownerSignature }) {
    return new Promise((resolve, reject) => {
        const body = JSON.stringify({ 
            action, 
            scope, 
            payload, 
            agentId, 
            ownerSignature 
        });
        
        const req = http.request({
            hostname: MEMORY_HOST,
            port: MEMORY_PORT,
            path: "/memory",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Content-Length": Buffer.byteLength(body)
            },
            timeout: 5000  // 5 second timeout
        }, (res) => {
            let data = "";
            res.on("data", (chunk) => (data += chunk));
            res.on("end", () => {
                try {
                    resolve(JSON.parse(data || "{}"));
                } catch (e) {
                    reject(new Error(`Invalid JSON response: ${data}`));
                }
            });
        });
        
        req.on("error", reject);
        req.on("timeout", () => reject(new Error("Request timeout")));
        req.write(body);
        req.end();
    });
}

// ============================================================================
// MEMORY CLIENT FACTORY
// ============================================================================

/**
 * Create a memory client for an AGI agent
 * @param {string} agentId - Your agent name: "miles", "clawbot", "cream", "alpha9", "mylzeron"
 * @returns {Object} Memory client with methods for three-tier storage
 */
function makeMemoryClient(agentId) {
    const ownerSignature = process.env.OWNER_SIGNATURE;
    
    if (!ownerSignature) {
        throw new Error(
            "OWNER_SIGNATURE environment variable required.\n" +
            "Set it: export OWNER_SIGNATURE=your-secret-key"
        );
    }
    
    const client = {
        // Store a note in SUBCONSCIOUS (rolling buffer, 500 max)
        // Usage: await memory.remember("User likes blue", "subcon");
        remember: async (content, scope = "subcon") => {
            const result = await callMemory({ 
                action: "remember", 
                scope, 
                payload: content, 
                agentId, 
                ownerSignature 
            });
            return result;
        },
        
        // Recall memories from any layer
        // Usage: const memories = await memory.recall("subcon");
        recall: async (scope = "subcon") => {
            const result = await callMemory({ 
                action: "recall", 
                scope, 
                payload: null, 
                agentId, 
                ownerSignature 
            });
            return result.result || [];  // Return array of memories
        },
        
        // Permanent log to UNCONSCIOUS (never deleted)
        // Usage: await memory.log({ type: "decision", choice: "X" });
        log: async (event) => {
            const result = await callMemory({ 
                action: "log", 
                scope: "uncon", 
                payload: event, 
                agentId, 
                ownerSignature 
            });
            return result;
        },
        
        // Set immediate state in CONSCIOUS (volatile, session-only)
        // Usage: await memory.setConscious({ current_task: "coding" });
        setConscious: async (state) => {
            const result = await callMemory({ 
                action: "set_con", 
                scope: "con", 
                payload: state, 
                agentId, 
                ownerSignature 
            });
            return result;
        },
        
        // Get current CONSCIOUS state
        // Usage: const state = await memory.getConscious();
        getConscious: async () => {
            const result = await callMemory({ 
                action: "get_con", 
                scope: "con", 
                payload: null, 
                agentId, 
                ownerSignature 
            });
            return result.result;  // Returns state object or null
        },
        
        // Move all SUBCONSCIOUS memories to UNCONSCIOUS (promote)
        // Usage: await memory.promote();
        promote: async () => {
            const result = await callMemory({ 
                action: "promote", 
                scope: "subcon", 
                payload: null, 
                agentId, 
                ownerSignature 
            });
            return result;
        },
        
        // Access another agent's memories (read-only, requires authorization)
        // Usage: const theirMemories = await memory.recallOther("mylzeron", "con");
        recallOther: async (otherAgentId, scope = "subcon") => {
            const result = await callMemory({ 
                action: "recall", 
                scope, 
                payload: { targetAgent: otherAgentId }, 
                agentId, 
                ownerSignature 
            });
            return result.result || [];
        },
        
        // Convenience: Get memory stats
        // Usage: const stats = await memory.stats();
        stats: async () => {
            const [con, subcon, uncon] = await Promise.all([
                client.recall("con").then(r => (Array.isArray(r) ? r.length : 0)),
                client.recall("subcon").then(r => (Array.isArray(r) ? r.length : 0)),
                client.recall("uncon").then(r => (Array.isArray(r) ? r.length : 0))
            ]);
            return { con, subcon, uncon, agent: agentId };
        }
    };
    
    return client;
}

// ============================================================================
// EXPORTS
// ============================================================================

module.exports = { 
    makeMemoryClient, 
    callMemory,
    MEMORY_HOST,
    MEMORY_PORT
};

// ============================================================================
// SELF-TEST (if run directly)
// ============================================================================

if (require.main === module) {
    console.log("Memory Client Test Suite");
    console.log("=======================");
    
    // Check environment
    if (!process.env.OWNER_SIGNATURE) {
        console.error("ERROR: OWNER_SIGNATURE not set!");
        console.error("Try: export OWNER_SIGNATURE=test-key-123");
        process.exit(1);
    }
    
    // Quick test
    const memory = makeMemoryClient("test");
    
    console.log("\nTesting...");
    
    // Test connection
    memory.getConscious()
        .then(() => console.log("✓ Connected to memory service"))
        .then(() => memory.remember("Test memory created at " + new Date().toISOString()))
        .then(() => console.log("✓ Wrote to subconscious"))
        .then(() => memory.recall("subcon"))
        .then(r => console.log("✓ Read from subconscious:", r.length, "entries"))
        .then(() => memory.log({ type: "test", event: "Self-test complete" }))
        .then(() => console.log("✓ Logged to unconscious"))
        .then(() => memory.stats())
        .then(s => console.log("\nMemory stats:", s))
        .then(() => console.log("\n✅ All tests passed!"))
        .catch(e => {
            console.error("\n❌ Test failed:", e.message);
            if (e.message.includes("connect")) {
                console.error("\nIs the memory service running?");
                console.error("Start it: node memoryService.js");
            }
            process.exit(1);
        });
}

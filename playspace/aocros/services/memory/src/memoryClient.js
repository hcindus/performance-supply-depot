/**
 * memoryClient.js - Universal client for all AGI agents
 * Use this in Miles, Clawbot, CREAM, ALPHA-9, Mylzeron
 * 
 * const memory = makeMemoryClient("miles");
 * await memory.remember("Observed anomaly in sector 7");
 * const notes = await memory.recall();
 */

const http = require("http");

const MEMORY_HOST = "127.0.0.1";
const MEMORY_PORT = 12789;

function callMemory({ action, scope, payload, agentId, ownerSignature }) {
    return new Promise((resolve, reject) => {
        const body = JSON.stringify({ action, scope, payload, agentId, ownerSignature });
        
        const req = http.request({
            hostname: MEMORY_HOST,
            port: MEMORY_PORT,
            path: "/memory",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Content-Length": Buffer.byteLength(body)
            }
        }, (res) => {
            let data = "";
            res.on("data", (chunk) => (data += chunk));
            res.on("end", () => {
                try {
                    resolve(JSON.parse(data || "{}"));
                } catch (e) {
                    reject(e);
                }
            });
        });
        
        req.on("error", reject);
        req.write(body);
        req.end();
    });
}

/**
 * Create a memory client for an AGI agent
 * @param {string} agentId - "miles", "clawbot", "cream", "alpha9", "mylzeron"
 * @returns {Object} Memory client with remember, recall, log, conscious methods
 */
function makeMemoryClient(agentId) {
    const ownerSignature = process.env.OWNER_SIGNATURE;
    if (!ownerSignature) {
        throw new Error("OWNER_SIGNATURE environment variable required");
    }
    
    return {
        // Subconscious: rolling buffer (last 500 entries)
        remember: (text, scope = "subcon") => 
            callMemory({ action: "remember", scope, payload: text, agentId, ownerSignature }),
        
        // Recall from any layer
        recall: (scope = "subcon") => 
            callMemory({ action: "recall", scope, payload: null, agentId, ownerSignature }),
        
        // Unconscious: permanent, append-only audit log
        log: (event) => 
            callMemory({ action: "log", scope: "uncon", payload: event, agentId, ownerSignature }),
        
        // Conscious: volatile, immediate state
        setConscious: (state) => 
            callMemory({ action: "set_con", scope: "con", payload: state, agentId, ownerSignature }),
        
        getConscious: () => 
            callMemory({ action: "get_con", scope: "con", payload: null, agentId, ownerSignature }),
        
        // Promote all subcon to uncon
        promote: () => 
            callMemory({ action: "promote", scope: "subcon", payload: null, agentId, ownerSignature }),
        
        // Access other agents' memory (with authorization)
        recallOther: (otherAgentId, scope = "subcon") =>
            callMemory({ action: "recall", scope, payload: { targetAgent: otherAgentId }, agentId, ownerSignature })
    };
}

module.exports = { makeMemoryClient, callMemory };

/**
 * Miles Memory Client
 * OODA loop with three-layer consciousness persistence
 * Project 5912
 */

const http = require('http');

const MEMORY_HOST = '127.0.0.1';
const MEMORY_PORT = 12789;
const AGENT_ID = 'miles';

/**
 * Store a memory note
 * @param {Object} note - The memory to store
 * @param {string} scope - 'con', 'subcon', or 'uncon'
 * @returns {Promise<Object>}
 */
async function remember(note, scope = 'subcon') {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({
            agent: AGENT_ID,
            scope,
            note: {
                ...note,
                timestamp: new Date().toISOString(),
                agent: AGENT_ID
            }
        });

        const req = http.request({
            hostname: MEMORY_HOST,
            port: MEMORY_PORT,
            path: '/memory',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(data)
            }
        }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(body));
                } catch (e) {
                    resolve({ ok: true, body });
                }
            });
        });

        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

/**
 * Recall memories from a layer
 * @param {string} scope - 'con', 'subcon', or 'uncon'
 * @returns {Promise<Object>}
 */
async function recall(scope = 'subcon') {
    return new Promise((resolve, reject) => {
        const req = http.request({
            hostname: MEMORY_HOST,
            port: MEMORY_PORT,
            path: `/${scope}?agent=${AGENT_ID}`,
            method: 'GET'
        }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(body));
                } catch (e) {
                    resolve({ ok: true, entries: [] });
                }
            });
        });

        req.on('error', reject);
        req.end();
    });
}

/**
 * Recall from another agent's memory (read-only)
 * @param {string} otherAgent - Agent to read from
 * @param {string} scope - Memory layer
 * @returns {Promise<Object>}
 */
async function recallOther(otherAgent, scope = 'subcon') {
    return new Promise((resolve, reject) => {
        const req = http.request({
            hostname: MEMORY_HOST,
            port: MEMORY_PORT,
            path: `/${scope}?agent=${otherAgent}&requester=${AGENT_ID}`,
            method: 'GET'
        }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => resolve(JSON.parse(body)));
        });

        req.on('error', reject);
        req.end();
    });
}

/**
 * Log to unconscious (audit trail)
 * @param {Object} entry
 * @returns {Promise<Object>}
 */
async function log(entry) {
    return remember(entry, 'uncon');
}

/**
 * OODA Cycle with full memory persistence
 * @param {string} context - Current situation
 * @param {Function} decideFn - Decision function
 * @param {Function} actFn - Action function
 * @returns {Promise<Object>}
 */
async function oodaCycle(context, decideFn, actFn) {
    // OBSERVE
    await remember({ phase: 'OBSERVE', context }, 'con');

    // ORIENT (read history)
    const history = await recall('uncon');
    const recent = await recall('subcon');

    // DECIDE
    const decision = await decideFn(context, history, recent);
    await remember({ phase: 'DECIDE', decision }, 'subcon');

    // ACT
    const result = await actFn(decision);
    await log({ phase: 'ACT', result, decision });

    // Store result in conscious (volatile)
    await remember({ phase: 'RESULT', result }, 'con');

    return result;
}

module.exports = {
    remember,
    recall,
    recallOther,
    log,
    oodaCycle,
    AGENT_ID,
    MEMORY_HOST,
    MEMORY_PORT
};

// Test if run directly
if (require.main === module) {
    console.log('Testing Miles memory client...');
    remember({ test: true, message: 'Miles memory active' }, 'subcon')
        .then(r => console.log('✓ Write test:', r))
        .then(() => recall('subcon'))
        .then(r => console.log('✓ Read test:', r.entries?.length, 'entries'))
        .catch(console.error);
}

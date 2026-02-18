/**
 * Clawbot Memory Client
 * Job tracking and execution with three-layer consciousness
 * Project 5912
 */

const http = require('http');

const MEMORY_HOST = '127.0.0.1';
const MEMORY_PORT = 12789;
const AGENT_ID = 'clawbot';

/**
 * Store a memory note
 * @param {Object} note
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
 * Recall memories
 * @param {string} scope
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
 * Set conscious state (volatile session memory)
 * @param {Object} state
 * @returns {Promise<Object>}
 */
async function setConscious(state) {
    return remember(state, 'con');
}

/**
 * Get conscious state
 * @returns {Promise<Object>}
 */
async function getConscious() {
    const result = await recall('con');
    return result.entries?.[result.entries.length - 1] || null;
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
 * Track a job execution
 * @param {Object} job - { id, task, priority }
 * @param {Function} runFn - The job execution function
 * @returns {Promise<Object>}
 */
async function trackJob(job, runFn) {
    // Set conscious state
    await setConscious({
        jobId: job.id,
        status: 'RUNNING',
        task: job.task,
        startedAt: new Date().toISOString()
    });

    // Log start
    await remember({
        type: 'job_started',
        jobId: job.id,
        task: job.task,
        priority: job.priority
    }, 'subcon');

    try {
        const result = await runFn(job);

        // Log success
        await log({
            type: 'job_completed',
            jobId: job.id,
            result: result,
            completedAt: new Date().toISOString()
        });

        // Update conscious
        await setConscious({
            jobId: job.id,
            status: 'COMPLETED',
            result: result
        });

        return { success: true, result };
    } catch (error) {
        // Log failure
        await log({
            type: 'job_failed',
            jobId: job.id,
            error: error.message,
            failedAt: new Date().toISOString()
        });

        // Update conscious
        await setConscious({
            jobId: job.id,
            status: 'FAILED',
            error: error.message
        });

        throw error;
    }
}

/**
 * Get job execution status
 * @returns {Promise<Object>}
 */
async function getStatus() {
    const current = await recall('con');
    const recent = await recall('subcon');
    const audit = await recall('uncon');

    const recentJobs = recent.entries
        ?.filter(e => e.type?.includes('job_'))
        .slice(-5) || [];

    const completedCount = audit.entries
        ?.filter(e => e.type === 'job_completed')
        .length || 0;

    const failedCount = audit.entries
        ?.filter(e => e.type === 'job_failed')
        .length || 0;

    return {
        active: current.entries?.[0]?.status === 'RUNNING',
        currentJob: current.entries?.[0]?.jobId,
        recentJobs,
        stats: {
            completed: completedCount,
            failed: failedCount,
            total: completedCount + failedCount
        }
    };
}

/**
 * Execute a task with full tracking
 * @param {string} taskId
 * @param {string} description
 * @param {Function} taskFn
 * @returns {Promise<Object>}
 */
async function executeTracked(taskId, description, taskFn) {
    const job = {
        id: taskId,
        task: description,
        priority: 'normal'
    };

    return trackJob(job, taskFn);
}

module.exports = {
    remember,
    recall,
    setConscious,
    getConscious,
    log,
    trackJob,
    getStatus,
    executeTracked,
    AGENT_ID,
    MEMORY_HOST,
    MEMORY_PORT
};

// Test if run directly
if (require.main === module) {
    console.log('Testing Clawbot memory client...');
    setConscious({ status: 'IDLE', test: true })
        .then(() => executeTracked('test-001', 'Memory integration test', async (job) => {
            console.log('Running:', job.task);
            return { success: true, message: 'Memory client working' };
        }))
        .then(() => getStatus())
        .then(status => console.log('✓ Job tracking:', status))
        .catch(console.error);
}

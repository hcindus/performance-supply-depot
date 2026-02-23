# Clawbot Integration with AOCROS Memory

Clawbot uses the memory service for job tracking and audit trails.

## Setup

```javascript
// clawbot/agent.js
const { makeMemoryClient } = require('../aocros/services/memory/src/memoryClient');
const memory = makeMemoryClient('clawbot');
```

## Job Tracking

```javascript
async function clawbotExecuteJob(job) {
    // Set conscious state
    await memory.setConscious({
        jobId: job.id,
        status: 'RUNNING',
        task: job.task
    });
    
    // Remember starting
    await memory.remember({
        type: 'job_started',
        jobId: job.id,
        task: job.task,
        params: job.payload
    });
    
    try {
        const result = await executeJob(job);
        
        // Log success
        await memory.log({
            type: 'job_completed',
            jobId: job.id,
            result: result,
            duration: result.duration
        });
        
        return result;
    } catch (error) {
        // Log failure
        await memory.log({
            type: 'job_failed',
            jobId: job.id,
            error: error.message,
            stack: error.stack
        });
        
        throw error;
    } finally {
        await memory.setConscious({ status: 'IDLE' });
    }
}
```

## Status Queries

```javascript
async function getClawbotStatus() {
    const current = await memory.getConscious();
    const recent = await memory.recall('subcon');
    const audit = await memory.recall('uncon');
    
    return {
        current: current,
        recentJobs: recent.slice(-5),
        totalJobs: audit.length
    };
}
```
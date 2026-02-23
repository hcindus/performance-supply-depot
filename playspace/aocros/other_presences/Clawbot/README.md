# Clawbot

**Role:** Job Executor
**Function:** Task execution and job tracking

## Job Tracking with Memory

```javascript
const memory = makeMemoryClient('clawbot');

async function executeJob(job) {
    // Set conscious state (volatile)
    await memory.setConscious({
        jobId: job.id,
        status: 'RUNNING',
        task: job.task
    });
    
    // Remember start
    await memory.remember({
        type: 'job_started',
        jobId: job.id
    });
    
    try {
        const result = await runJob(job);
        
        // Log completion to unconscious (audit)
        await memory.log({
            type: 'job_completed',
            jobId: job.id,
            result
        });
        
        return result;
    } catch (error) {
        await memory.log({
            type: 'job_failed',
            jobId: job.id,
            error: error.message
        });
        throw error;
    } finally {
        await memory.setConscious({ status: 'IDLE' });
    }
}
```

## Job Status Query

```javascript
async function getStatus() {
    const current = await memory.getConscious();
    const recent = await memory.recall('subcon');
    const audit = await memory.recall('uncon');
    
    return {
        active: current?.status === 'RUNNING',
        recentJobs: recent.slice(-5),
        totalCompleted: audit.filter(e => e.type === 'job_completed').length
    };
}
```

## Reports to

Miles (operations) → Tappy (fiduciary)

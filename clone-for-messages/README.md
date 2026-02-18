# Miles Message Clones
## Local Git Clones for Agent Coordination

**Location:** `/root/.openclaw/workspace/clone-for-messages/`
**Purpose:** Local working copies to check for Miles' replies
**Created:** 2026-02-18

---

## Structure

```
clone-for-messages/
├── aocros-main/           ← Clone of hcindus/aocros for checking messages
├── aocros-Miles/         ← Miles' specific working copy (when provided)
└── README.md            ← This file
```

---

## Usage

**Check for Miles' replies:**
```bash
cd clone-for-messages/aocros-main
git pull origin main
cat memory/message.md
```

**Compare with local:**
```bash
diff /root/.openclaw/workspace/memory/message.md \
     clone-for-messages/aocros-main/memory/message.md
```

---

## Current Status

**Main repo clone:** ⏳ Pending authentication (SSH token needed)  
**Miles' working copy:** ⏳ Not yet provided

**When Miles replies via Git, his changes will appear here.**

---

*Clone directory ready for message tracking.*

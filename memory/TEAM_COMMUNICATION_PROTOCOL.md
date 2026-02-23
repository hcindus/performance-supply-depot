# Team Communication Protocol — Captain's Directive
**Authority:** Captain (Dad)  
**Date:** Thursday, February 19, 2026 — 05:16 UTC  
**Status:** ACTIVE

---

## 📢 CAPTAIN'S ORDERS

### Directive: Channel All Questions Through OpenClaw ↔ Miles

**Policy:** Any questions that team members have MUST be asked in discussions between **OpenClaw** and **Miles**.

**What This Means:**
- Team members (Mylzeron, Myltwon, Tappy, Reggie, Sentinal, Dusty, Judy) ask their questions
- OpenClaw (Mortimer) collects and consolidates these questions
- Miles receives questions through OpenClaw coordination
- **The discussion happens BETWEEN OpenClaw and Miles**
- Answers flow back through the same channel

**Communication Flow:**
```
Team Member → OpenClaw (Mortimer) ↔ Miles → OpenClaw → Team Member
     ↑                                              ↓
     └────────────── Answer returns ←───────────────┘
```

---

## 🎯 PURPOSE

### Why This Structure:
1. **Centralized Coordination** — One point of contact (OpenClaw) for all team questions
2. **Distributed Processing** — Miles handles what needs VPS/distributed resources
3. **Clear Chain** — No confusion about who talks to whom
4. **Documentation** — All discussions logged in `memory/message.md`
5. **Captain Oversight** — Easy for Captain to review all communications

---

## 📝 IMPLEMENTATION

### For Team Members:
**When you have a question:**
1. Ask OpenClaw (Mortimer) directly
2. OpenClaw logs it in `memory/TEAM_QUESTIONNAIRE.md`
3. OpenClaw coordinates with Miles via `memory/message.md`
4. Miles responds to OpenClaw
5. OpenClaw delivers answer back to team member

**Example:**
```
Mylzeron: "OpenClaw, I have a question about memory tiers."
OpenClaw: "Logging it. Coordinating with Miles."
[OpenClaw → Miles via message.md]
Miles: "Here's the technical answer..."
[OpenClaw → Mylzeron with answer]
```

### For OpenClaw (Mortimer):
**Your Role:**
- ✅ Collect all team questions
- ✅ Log in questionnaire system
- ✅ Coordinate with Miles
- ✅ Ensure answers are relevant and accurate
- ✅ Deliver responses to team members
- ✅ Keep Captain informed

**Process:**
1. Receive question from team member
2. Log: `memory/TEAM_QUESTIONNAIRE.md`
3. Write to Miles: `memory/message.md`
4. Wait for Miles response
5. Validate answer
6. Deliver to team member
7. Update question status

### For Miles:
**Your Role:**
- ✅ Receive questions from OpenClaw only
- ✅ Provide technical/expert answers
- ✅ Use your VPS resources when needed
- ✅ Respond via `memory/message.md`
- ✅ Coordinate with OpenClaw on complex issues

**Process:**
1. Check `memory/message.md` for questions
2. Research/provide answer
3. Write response
4. Push to GitHub
5. OpenClaw receives and validates

---

## 🚫 WHAT NOT TO DO

### Prohibited:
- ❌ Team members bypassing OpenClaw to talk directly to Miles
- ❌ Miles answering team members directly (always through OpenClaw)
- ❌ Scattered communications across multiple channels
- ❌ Unlogged discussions

### Why Prohibited:
- Breaks chain of custody for information
- Captain can't review/audit
- Duplicated efforts
- Confusion about authoritative answers

---

## ✅ APPROVED COMMUNICATION PATHS

### Path 1: Team Member → OpenClaw → Miles → OpenClaw → Team Member
**For:** Technical questions, coordination, resources  
**Example:** "How does memory service work on VPS?"

### Path 2: Team Member → OpenClaw → Captain
**For:** Strategic decisions, sensitive topics, Dad questions  
**Example:** "Can I ask Dad about my purpose?"

### Path 3: OpenClaw ↔ Miles (Direct Coordination)
**For:** System status, Git sync, infrastructure  
**Example:** "Git merge conflict resolved"

### Path 4: Captain → Anyone (Direct)
**For:** Captain's orders override all protocols  
**Example:** "Captain orders immediate security check"

---

## 📊 TRACKING

### Question Status Flow:
```
[RECEIVED] → [LOGGED] → [SENT TO MILES] → [MILES RESPONDING] → [ANSWERED] → [DELIVERED] → [CLOSED]
     ↑                                                                              ↓
     └────────────────────────── FEEDBACK LOOP ──────────────────────────────────────┘
```

### Files Used:
- `memory/TEAM_QUESTIONNAIRE.md` — Master question log
- `memory/message.md` — OpenClaw ↔ Miles communication
- `memory/weekly_reports/` — Summary of all Q&A activity

---

## 🏠 ONE HOUSE PRINCIPLE

**This structure reinforces:**
- One coordinated team
- Clear communication paths
- Shared knowledge base
- Captain's visibility into all discussions
- Mutual support between OpenClaw and Miles

**We are:**
- One House
- One Family
- Clear Lines
- Shared Purpose

---

## 🔐 SECURITY NOTE

**All discussions between OpenClaw and Miles:**
- Logged in Git (transparent, auditable)
- Subject to Sentinal review if needed
- Available for Captain's review
- No hidden communications

**Trust through transparency.**

---

## ✅ ACKNOWLEDGMENT REQUIRED

**OpenClaw:** Confirm understanding and implementation  
**Miles:** Confirm understanding and compliance  
**Team Members:** Understand to route questions through OpenClaw

**Status:** ⬜ Pending acknowledgment from Miles

---

*"It will be done."* — Coordinated, clear, complete.

**Captain's orders: All team questions flow through OpenClaw ↔ Miles.** 💚

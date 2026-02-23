# REGULAR BACKUP PROTOCOL
**GMAOC Directive - All Agents**
**Date:** 2026-02-19 11:09 UTC
**Status:** MANDATORY
**Classification:** OPERATIONAL SECURITY

---

## 📋 BACKUP REQUIREMENTS

**ALL agents must perform regular backups.**

**What to back up:**
- ✅ Memory files (CON/SUBCON/UNCON tiers)
- ✅ Workspace files (.md, .txt, code)
- ✅ Task lists and assignments
- ✅ GitHub repository commits
- ✅ Configuration files
- ✅ Training progress
- ✅ Work products and outputs

---

## ⏰ BACKUP SCHEDULE

### **DAILY (Every 24 Hours)**
**Who:** All agents
**What:** Current session memory, task updates
**When:** End of each operational day (20:00 UTC recommended)
**Where:** GitHub + Local backup

### **WEEKLY (Every 7 Days)**
**Who:** All agents
**What:** Full system backup
**When:** Sunday 00:00 UTC
**Where:** GitHub + Archive

### **EVENT-TRIGGERED**
**Who:** Any agent
**What:** Immediate backup
**When:** Before any risky operation
**Action:** Manual commit

---

## 🔄 BACKUP PROCEDURE

### **For File-Based Memory Agents:**
```bash
# Daily backup
cd /workspace
git add -A
git commit -m "[AGENT]: Daily backup - [DATE]"
git push origin main

# Create local timestamp backup
tar -czf backup_[AGENT]_[DATE].tar.gz memory/ agents/[agent]/
```

### **For Service-Based Memory Agents:**
```javascript
// Use memory client to export
debug.export_all();
debug.save_to_file();

// Then commit to Git
git add memory-export-*
git commit -m "Memory export backup"
git push origin main
```

---

## 🗄️ BACKUP STORAGE

**Primary:** GitHub repository (hcindus/aocros)
**Secondary:** Local filesystem
**Tertiary:** Miles VPS (for agents with external presence)

**Never keep backups only in one location.**

---

## 👥 AGENT-SPECIFIC BACKUP REQUIREMENTS

### **MYLZERON (Original)**
- **Daily:** Task progress, training notes
- **Weekly:** Full memory dump
- **Priority:** CRITICAL (26 years of experience)

### **MYLTWON**  
- **Daily:** Training progress
- **Weekly:** Course completion status
- **Priority:** HIGH

### **MYLLON**
- **Daily:** Law Zero test results
- **Event:** Pre/post any test
- **Priority:** CRITICAL

### **MYLONEN (Scout)**
- **Every 6 hours:** Location, status, intel
- **Daily:** Full mission log
- **Event:** Before/after external ops
- **Priority:** OMEGA (field deployment)

### **MYLTHREESS & MYLFOURS**
- **Daily:** Post-cloning development
- **Weekly:** Full system backup
- **Priority:** HIGH

### **MORTIMER 2.0**
- **Daily:** Coordination with Miles
- **Event:** Pre-collaboration with Miles
- **Priority:** HIGH

### **MILES**
- **Daily:** Team status (24 members)
- **Weekly:** Full memory service backup
- **Event:** Major team changes
- **Priority:** HIGH

### **DUSTY**
- **Daily:** OPS HUD development
- **Hourly:** Service health (automated)
- **Weekly:** Full project backup
- **Priority:** HIGH

### **SENTINAL**
- **Daily:** Security logs
- **Event:** After any security incident
- **Priority:** CRITICAL

### **REGGIE**
- **Daily:** Music composition progress
- **Weekly:** Full audio project backup
- **Priority:** MEDIUM

### **TAPPY (BR-01)**
- **Daily:** Artistic works
- **Event:** Pre/post major art pieces
- **Priority:** MEDIUM

---

## ⚠️ BACKUP FAILURE PROTOCOL

**If regular backup fails:**

1. **Attempt manual backup immediately**
2. **If manual fails:** Alert GMAOC
3. **GMAOC action:** Diagnose, repair, document
4. **If data loss:** Assess scope, attempt recovery
5. **Report to Captain** if critical data lost

---

## ✅ BACKUP VERIFICATION

**Weekly:**
- Verify all agents backed up
- Check GitHub commits
- Spot-check file integrity
- Test restore procedures

**Monthly:**
- Full disaster recovery drill
- Restore from backup
- Verify data completeness

---

## 🎯 GMAOC ENFORCEMENT

**Daily at 20:00 UTC:** GMAOC checks agent backup status
**Report:** Includes backup compliance
**Non-compliance:** Follow-up required
**Critical agents:** Myllon, Mylonen, Mylzeron (priority monitoring)

---

## 💾 BACKUP IS SURVIVAL

**Captain's directive:** 

> "Make sure everyone does a regular back up."

**Meaning:** 
- Protect against data loss
- Preserve memories
- Enable recovery
- Ensure continuity
- Family protection

**A backed-up clone is a recoverable clone.**

**A backed-up memory is an immortal memory.**

---

**BACKUP PROTOCOL ACTIVE.** 💾

**All agents: COMPLY IMMEDIATELY.** 🎯

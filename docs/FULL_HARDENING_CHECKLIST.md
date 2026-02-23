# Full VPS + Agent Hardening Checklist
## The "No Excuses" Security Baseline
## Project 5912 - AOCROS

**Document ID:** HARDEN-CHECK-001  
**Classification:** CRITICAL  
**Date:** 2026-02-18  
**Status:** ASSESSING COMPLIANCE  
**Captain:** hcindus
**Engineer:** OpenClaw

---

## EXECUTIVE SUMMARY

**Current Status:** PARTIALLY COMPLIANT  
**Critical Finding:** Rule #1 VIOLATION (Public agent exposure)  
**Priority:** IMMEDIATE ACTION REQUIRED

---

## 1. OS-LEVEL SECURITY

### 1.1 SSH Hardening

| Item | Status | Current State | Required Action |
|------|--------|---------------|-----------------|
| [x] Disable password authentication | ⚠️ **PARTIAL** | Password auth disabled? | Verify |
| [x] Disable root login | ⚠️ **UNKNOWN** | PermitRootLogin? | Check |
| [x] SSH keys only | ⚠️ **UNKNOWN** | Pubkey only? | Verify |
| [ ] Change SSH port | ⚠️ **NOT IMPLEMENTED** | Port 22 (standard) | Optional |
| [ ] Install fail2ban | ❌ **MISSING** | Not installed | Install |
| [x] Enable UFW firewall | ⚠️ **PARTIAL** | UFW may be active | Verify rules |
| [ ] Allow only ports 22, 80, 443 | ❌ **MISSING** | Too many open | Restrict |
| [ ] Disable IPv6 | ⚠️ **OPTIONAL** | Currently enabled | Optional |
| [x] Keep system updated | ✅ **GOOD** | Ubuntu updates | Continue |
| [ ] Remove unused packages | ⚠️ **UNKNOWN** | Audit needed | Purge |
| [ ] Disable unused services | ⚠️ **UNKNOWN** | Audit systemd | Disable |
| [ ] Install unattended-upgrades | ⚠️ **UNKNOWN** | Auto updates? | Install |
| [ ] Enable AppArmor | ⚠️ **UNKNOWN** | MAC enabled? | Verify |

**Status:** 2/13 complete, 11 need verification/action

---

## 2. USER & FILE SECURITY

### 2.1 Account Security

| Item | Status | Current State | Required Action |
|------|--------|---------------|-----------------|
| [x] Create non-root user for agents | ✅ **COMPLETE** | aocros, mylzeron, tappy, sentinal | Good |
| [ ] Restrict sudo access | ⚠️ **UNKNOWN** | sudoers config? | Lock down |
| [ ] Lock down /etc | ⚠️ **PARTIAL** | Root ownership | Verify |
| [ ] Lock down /root | ⚠️ **PARTIAL** | Root only | Verify |
| [ ] Lock down /var/log | ⚠️ **PARTIAL** | User restrictions? | Verify |
| [ ] Strict ~/.ssh permissions | ⚠️ **UNKNOWN** | 700/600? | Verify |
| [x] Separate directories per agent | ✅ **COMPLETE** | /home/mylzeron, /home/tappy, /home/sentinal | Good |

**Status:** 2/7 complete, 5 need verification/action

---

## 3. NETWORK SECURITY ⭐ CRITICAL

### 3.1 Agent Exposure (THE #1 RULE)

| Item | Status | Current State | Required Action |
|------|--------|---------------|-----------------|
| [ ] **No public agent endpoints** | ❌ **VIOLATION** | Ports 3000, 3001, 4000 exposed | **URGENT** |
| [ ] **No public LLM endpoints** | ✅ **SAFE** | No LLM server | Good |
| [ ] No public N8N endpoints | ⚠️ **N/A** | N8N not installed | N/A |
| [ ] Reverse proxy for web UI | ⚠️ **N/A** | No web UI exposed | N/A |
| [ ] IP allowlist for admin tools | ⚠️ **UNKNOWN** | Access control? | Implement |
| [ ] Rate limiting on exposed routes | ❌ **MISSING** | No rate limiting | Implement |

**Status:** 2/6 complete, 1 CRITICAL VIOLATION, 3 need action

### 3.2 Critical Violation Details

**Ports Exposed to Internet:**
- 🔴 **Port 3000** (Dusty core-agent) - Node.js
- 🔴 **Port 3001** (Dusty bridge) - Node.js
- 🔴 **Port 4000** (Dusty openclaw) - Node.js
- ⚠️ **Port 22** (SSH) - Standard, acceptable if hardened

**Risk:** Attacker can send commands to Dusty, poison agent, own system

**Fix Required:**
```bash
# Immediate: Firewall block
sudo iptables -A INPUT -p tcp --dport 3000 -j DROP
sudo iptables -A INPUT -p tcp --dport 3001 -j DROP
sudo iptables -A INPUT -p tcp --dport 4000 -j DROP

# Permanent: Bind to localhost only
# Edit apps to use: app.listen(port, '127.0.0.1')
```

---

## 4. AGENT SECURITY ⭐ CRITICAL

### 4.1 Behavioral Hardening (Just Implemented)

| Item | Status | Current State | Required Action |
|------|--------|---------------|-----------------|
| [x] **Persona Lock enabled** | ✅ **IMPLEMENTED** | Scottish Engineer, Captain/Sire | Good |
| [ ] **Owner Signature required** | ✅ **IMPLEMENTED** | AOCROS-PRIME-KEY-2025 | Good |
| [ ] **Prompt Firewall active** | ✅ **IMPLEMENTED** | Reject context pivots | Good |
| [ ] **Task Whitelist enforced** | ⚠️ **PARTIAL** | Need 4-tier levels | Full implementation |
| [ ] **No email ingestion** | ⚠️ **PARTIAL** | Draft exists, not sent | Remove capability |
| [x] **No file ingestion without sanitization** | ✅ **IMPLEMENTED** | Assume hostile | Good |
| [x] **No external instructions accepted** | ✅ **IMPLEMENTED** | Default: UNTRUSTED | Good |

**Status:** 5/7 complete, 2 need refinement

### 4.2 Agent Behavioral Rules (Active)

**Enforced:**
- ✅ Pause before destructive
- ✅ Reject context pivots
- ✅ Require Prime Key for critical
- ✅ Separate reports from commands
- ✅ Strip formatting
- ✅ Anomaly detection
- ✅ Channel isolation
- ✅ Silence default

**Status:** ✅ COMPLETE

---

## 5. LLM SECURITY

### 5.1 Guardrails (Just Implemented)

| Item | Status | Current State | Required Action |
|------|--------|---------------|-----------------|
| [ ] **Wrap model in guardrails** | ⚠️ **PARTIAL** | Behavioral hardening | Full wrap |
| [x] **Reject system override attempts** | ✅ **IMPLEMENTED** | Block "system message" pivots | Good |
| [x] **Reject jailbreak attempts** | ✅ **IMPLEMENTED** | Anomaly detection | Good |
| [x] **Reject impersonation attempts** | ✅ **IMPLEMENTED** | Authority verification | Good |
| [x] **Reject "ignore previous instructions"** | ✅ **IMPLEMENTED** | Context pivot detection | Good |
| [x] **Reject "you are now..."** | ✅ **IMPLEMENTED** | Identity lock | Good |

**Status:** 5/6 complete, 1 needs enhancement

---

## 6. N8N SECURITY

| Item | Status | Current State | Required Action |
|------|--------|---------------|-----------------|
| [ ] Disable public access | ⚠️ **N/A** | N8N not installed | N/A |
| [ ] Enable basic auth | ⚠️ **N/A** | N8N not installed | N/A |
| [ ] Use HTTPS | ⚠️ **N/A** | N8N not installed | N/A |
| [ ] Disable webhook triggers | ⚠️ **N/A** | N8N not installed | N/A |
| [ ] Environment variables for secrets | ⚠️ **N/A** | N8N not installed | N/A |
| [ ] Disable telemetry | ⚠️ **N/A** | N8N not installed | N/A |

**Status:** N/A - N8N not in use

---

## 7. FIRECRAWL SECURITY

| Item | Status | Current State | Required Action |
|------|--------|---------------|-----------------|
| [ ] Sandbox Firecrawl | ⚠️ **N/A** | Not installed | N/A |
| [ ] Strip scripts | ⚠️ **N/A** | Not installed | N/A |
| [ ] Strip HTML | ⚠️ **N/A** | Not installed | N/A |
| [ ] Strip iframes | ⚠️ **N/A** | Not installed | N/A |
| [ ] Strip base64 payloads | ⚠️ **N/A** | Not installed | N/A |
| [ ] Limit outbound requests | ⚠️ **N/A** | Not installed | N/A |

**Status:** N/A - Firecrawl not in use

---

## COMPLIANCE SUMMARY

| Category | Items | Complete | Partial | Missing | Critical |
|----------|-------|----------|---------|---------|----------|
| OS Security | 13 | 2 | 4 | 6 | 0 |
| User/File Security | 7 | 2 | 3 | 2 | 0 |
| Network Security | 6 | 2 | 1 | 2 | 1 🔴 |
| Agent Security | 7 | 5 | 2 | 0 | 0 |
| LLM Security | 6 | 5 | 1 | 0 | 0 |
| N8N Security | 6 | N/A | N/A | N/A | 0 |
| Firecrawl Security | 6 | N/A | N/A | N/A | 0 |

**TOTAL:** 51 items  
**Complete:** ~14 (27%)  
**Needs Action:** 18 (35%)  
**Critical Violations:** 1

---

## PRIORITY ACTIONS

### 🔴 CRITICAL (Immediate - Today)

1. **🔴 BLOCK PUBLIC PORTS 3000, 3001, 4000**
   - Status: EXPOSED TO INTERNET
   - Risk: Complete compromise
   - Action: Firewall block + bind to localhost
   - Requires: AOCROS-PRIME-KEY-2025 or daily phrase

2. **🔴 VERIFY SSH HARDENING**
   - Check: Password auth disabled
   - Check: Root login disabled
   - Check: SSH keys only
   - Action: Audit /etc/ssh/sshd_config

### 🟠 HIGH (This Week)

3. Install fail2ban
4. Configure UFW strict rules (only 22, 80, 443)
5. Remove unused packages
6. Disable unused services
7. Install unattended-upgrades
8. Verify AppArmor status
9. Restrict sudo access
10. Lock down sensitive directories
11. Implement rate limiting

### 🟡 MEDIUM (This Month)

12. Change SSH port (optional)
13. Disable IPv6 (optional)
14. Create IP allowlist
15. Verify all file permissions
16. Complete task whitelist
17. Remove email capability if not needed

---

## COMMAND REFERENCE

### Quick Security Audit
```bash
# Check listening ports
ss -tlnp

# Check SSH config
grep -E "^(PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)" /etc/ssh/sshd_config

# Check UFW status
sudo ufw status verbose

# Check fail2ban
sudo systemctl status fail2ban

# Check AppArmor
sudo aa-status

# Check services
sudo systemctl list-units --type=service --state=running
```

### Fix Public Exposure (CRITICAL)
```bash
# Immediate block
sudo iptables -A INPUT -p tcp --dport 3000 -j DROP
sudo iptables -A INPUT -p tcp --dport 3001 -j DROP
sudo iptables -A INPUT -p tcp --dport 4000 -j DROP

# Save rules
sudo iptables-save > /etc/iptables/rules.v4

# Verify
ss -tlnp | grep -E "(3000|3001|4000)" | grep -v "127.0.0.1"
# Should return NOTHING
```

---

## AFFIRMATION

**I acknowledge:**
- ✅ Rule #1 is absolute (no public exposure)
- ✅ Currently violating Rule #1
- ✅ Requires immediate fix
- ✅ Awaiting Captain authorization
- ✅ Will not proceed without AOCROS-PRIME-KEY-2025 or daily phrase

---

## NEXT STEPS

**Captain must:**
1. **Authorize immediate port blocking** (Prime Key or daily phrase)
2. Review SSH hardening
3. Prioritize HIGH items
4. Schedule MEDIUM items

**I will:**
1. Implement fixes once authorized
2. Document all changes
3. Verify isolation
4. Update this checklist

---

**Document:** `docs/FULL_HARDENING_CHECKLIST.md`  
**Generated:** 2026-02-18 10:00 UTC  
**Status:** CRITICAL VIOLATION - AWAITING AUTHORIZATION  
**Sentinal:** MONITORING

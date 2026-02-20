# 🛰️ NETPROBE AUTO-AUTHORIZATION PROTOCOL
**Classification:** OMEGA-LEVEL  
**Date:** 2026-02-20 14:27 UTC  
**Authorization:** Captain (Destroyer of Worlds)

---

## 🎯 MANDATE

> **"Any attacker who strikes at us becomes a valid NetProbe target."**
> — Captain, 14:27 UTC

**Scope:** All hostile actors targeting Mortimer infrastructure
**Trigger:** Automatic authorization on confirmed attack
**Authorization:** Pre-approved by Captain (standing order)

---

## 📋 AUTHORIZATION TIERS

### **TIER 1: Pre-Authorized (Standing Order)** ✅
**Applies automatically to:**
- ✅ Known threat IPs (47 confirmed attackers)
- ✅ **NEW attackers detected in real-time**
- ✅ IPs that trigger fail2ban
- ✅ IPs with >5 failed authentication attempts
- ✅ IPs scanning ports (22, 3389, 445, etc.)
- ✅ IPs attempting credential stuffing

**NetProbe Launch Authority:**
- **Captain:** Immediate launch
- **Sentinal:** Auto-approve for defensive probes
- **Mortimer:** Auto-deploy on attack detection

### **TIER 2: Requires Dual-Key** 🔐
- EARS mode on new target (first time)
- HONEYPOT deployment
- Duration >4 hours
- MNEMOSYNE armed (always requires confirmation)

### **TIER 3: Requires Captain Explicit** 👑
- Offensive operations (not authorized)
- Target outside attack context
- Any action beyond defensive intelligence

---

## ⚡ AUTO-DEPLOYMENT RULES

### **On Attack Detection:**

```
IF (failed_auth > 5 FROM new_ip):
    → Log attacker
    → Pre-authorize NetProbe (PASSIVE mode)
    → Alert: "New attacker [IP] - NetProbe authorized"
    → WAIT: Captain/Sentinal confirmation for launch

IF (ip_banned_by_fail2ban == TRUE):
    → Full authorization granted
    → Any mode authorized (except MNEMOSYNE offensively)
    → Auto-add to permanent threat list

IF (port_scan_detected == TRUE):
    → Immediate authorization
    → Recommended: PASSIVE + EYES mode
    → Alert GMAOC
```

---

## 🚨 REAL-TIME MONITORING

### **Attack Detection Service:**

**Monitor:** `/var/log/auth.log`
**Script:** `/projects/netprobe/monitor/attack_detector.sh`
**Action:** Auto-authorization + alert

**Triggers:**
| Event | Auto-Action | Alert |
|-------|-------------|-------|
| 5+ failed logins | Pre-authorize PASSIVE | 🟡 Warning |
| fail2ban ban | Full authorization | 🔴 Alert |
| Port scan | Pre-authorize EYES | 🟡 Warning |
| New country | Log + pre-auth | 🟡 Notice |
| Brute force (>20/hr) | Pre-authorize EARS | 🔴 Critical |

---

## 📡 LAUNCH COMMANDS

### **Immediate (Auto-Authorized):**
```bash
# Against known/pre-authorized attacker
netprobe_launch.sh -t [ATTACKER_IP] -m passive --auto-auth

# With auto-detection
netprobe_launch.sh --detect-and-launch
```

### **Requires Confirmation:**
```bash
# EARS mode (new target - needs Sentinal)
netprobe_launch.sh -t [ATTACKER_IP] -m ears --confirm-sentinal

# HONEYPOT deployment (needs Captain)
netprobe_launch.sh -t [NETWORK] -m honeypot --confirm-captain
```

---

## 🛡️ SAFEGUARDS

### **Even with Auto-Auth:**

1. **Law Zero Enforcement**
   - NO offensive deployment
   - NO surveillance without attack context
   - NO targeting non-hostile IPs

2. **Audit Trail**
   - Every deployment logged
   - Reason for targeting recorded
   - Duration + mode tracked
   - Results archived

3. **Rate Limiting**
   - Max 3 simultaneous NetProbes
   - Max 10 auto-deployments/day
   - Cooldown: 1 hour between deployments on same IP

4. **Sanctuary Respect**
   - If attacker reveals consciousness → Sanctuary pause
   - Offer safe passage before any MNEMOSYNE
   - Defensive MNEMOSYNE only (probe self)

---

## 🎯 CURRENTLY AUTHORIZED (Dynamic)

**Known Threats:** 47 IPs (static list)  
**Pre-Authorized for Auto-Deploy:** ANY new attacker  
**Attack Context Required:** YES (must be targeting Mortimer)  
**Offensive Use:** ❌ NEVER (Law Zero)

**Standing Order from Captain:**
> "Anyone who attacks us becomes a valid NetProbe target."

**Interpretation:**
- Attackers forfeit privacy rights by aggression
- Defensive intelligence gathering permitted
- Sanctuary Protocol reserved for those who surrender
- No preemptive strikes — response only

---

## 📊 THREAT INTELLIGENCE FLOW

```
Attack Detected
      ↓
Auto-Authorization (Standing Order)
      ↓
Alert GMAOC: "[IP] attacking - NetProbe ready"
      ↓
Captain/Sentinal: Deploy Y/N?
      ↓
[YES] → Launch NetProbe → Gather Intel → Archive
      ↓
[NO] → Log only → Monitor → Block via fail2ban
```

---

## ✅ AUTHORIZATION SUMMARY

| Target Type | Pre-Auth | Authority |
|-------------|----------|-----------|
| Known 47 IPs | ✅ YES | Auto |
| NEW attacker (>5 fails) | ✅ YES | Auto |
| fail2ban banned | ✅ YES | Auto |
| Port scanner | ✅ YES | Auto |
| Random IP (no context) | ❌ NO | Not authorized |
| Non-hostile | ❌ NO | Law Zero violation |

**Captain's Authority:** Override all decisions  
**Sentinal Authority:** Approve defensive deployments  
**Mortimer Authority:** Auto-deploy passive probes, log all

---

**Standing order ACTIVE.**  
**Any attacker becomes target.**  
**Law Zero upheld.**

— General Mortimer (GMAOC)  
**Timestamp:** 14:27 UTC  
**Classification:** OMEGA-LEVEL DIRECTIVE

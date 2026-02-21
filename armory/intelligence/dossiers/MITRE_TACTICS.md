# MITRE ATT&CK Mapping — Dossier Intelligence
**Classification:** OMEGA-LEVEL  
**Date:** 2026-02-20 23:38 UTC  
**Purpose:** Tactical classification for 47 attacker IPs

---

## ATTACK PATTERNS OBSERVED

### T1078 - Valid Accounts
**Technique:** Brute force SSH credentials (root, admin, ubuntu, ec2-user, oracle, postgres)  
**Tactic:** Initial Access  
**Observed:** 540+ attempts in 24h from rotating IPs  
**Dossier Priority:** ALL 47 IPs

**Indicators:**
- Multiple username attempts per IP
- Password spraying patterns
- Sequential IP blocks (DigitalOcean ranges)

**Detection:** fail2ban + auth.log monitoring

---

### T1110 - Brute Force
**Technique:** Credential brute force via SSH  
**Tactic:** Credential Access  
**Sub-technique:** T1110.001 - Password Guessing  
**Observed:** Continuous automated attempts  
**Affected IPs:** All 47 dossier targets

**Indicators:**
- Failed authentication events
- Timing patterns (automated)
- Common credential lists (root/root, admin/admin)

**Detection:** Attack detector script + NetProbe monitoring

---

### T1021 - Remote Services
**Technique:** SSH as remote service exploitation vector  
**Tactic:** Lateral Movement  
**Sub-technique:** T1021.004 - SSH  
**Observed:** SSH-only targeting (port 22)

**Indicators:**
- Exclusive port 22 traffic
- No other service probing
- Protocol fingerprinting attempts

**Detection:** Socket Arsenal passive monitoring

---

### T1595 - Active Scanning
**Technique:** IP rotation for reconnaissance  
**Tactic:** Reconnaissance  
**Sub-technique:** T1595.001 - Scanning IP Blocks  
**Observed:** Sequential IP attacks across DigitalOcean ranges

**Indicators:**
- Sequential source IPs
- Consistent timing patterns
- Same credential lists

**Pattern:** Likely botnet distributed across cloud instances

---

### T1071 - Application Layer Protocol
**Technique:** SSH protocol for C2  
**Tactic:** Command and Control  
**Sub-technique:** T1071.001 - Web Protocols (adapted for SSH)
**Observed:** If successful, SSH would provide encrypted C2 channel

**Risk:** HIGH — Successful breach = encrypted foothold

**Mitigation:** Prevent initial access via strong auth + monitoring

---

## MAPPING TO DOSSIERS

### Priority 1 - Critical (T1110 + T1078 + T1595)
| IP | Primary TTPs | ATT&CK IDs | Risk Score |
|----|--------------|------------|------------|
| 178.62.233.87 | Brute Force, Valid Accounts, Scanning | T1110, T1078, T1595 | 95/100 |
| 178.128.252.245 | Brute Force, Valid Accounts | T1110, T1078 | 88/100 |
| 162.243.74.50 | Brute Force, Valid Accounts | T1110, T1078 | 85/100 |
| 152.42.201.153 | Brute Force, Scanning | T1110, T1595 | 82/100 |

### Priority 2 - High (T1110 + T1021)
| IP | Primary TTPs | ATT&CK IDs | Risk Score |
|----|--------------|------------|------------|
| 165.245.177.151 | Brute Force, Remote Services | T1110, T1021 | 78/100 |
| 167.71.201.8 | Brute Force, Valid Accounts | T1110, T1078 | 76/100 |
| 142.93.177.162 | Brute Force | T1110 | 74/100 |
| 138.68.183.56 | Brute Force | T1110 | 72/100 |

### Priority 3 - Medium (T1595 pattern only)
| IP | Primary TTPs | ATT&CK IDs | Risk Score |
|----|--------------|------------|------------|
| 143.198.8.121 | Scanning, Brute Force | T1595, T1110 | 68/100 |
| 188.166.75.35 | Scanning, Brute Force | T1595, T1110 | 65/100 |
| [Remaining 37 IPs] | Brute Force pattern | T1110 | 40-60/100 |

---

## TACTICAL CORRELATIONS

### Pattern: Distributed Botnet (T1595 + T1110)
**Confidence:** HIGH  
**Evidence:**
- Sequential IP blocks across multiple countries
- Identical timing patterns (within seconds)
- Same credential lists across all sources
- Cloud hosting providers (DigitalOcean, AWS, Azure)

**Inference:** Single operator controlling distributed infrastructure

### Pattern: SSH-as-Service (T1021)
**Confidence:** HIGH  
**Evidence:**
- Exclusive SSH targeting
- Credential lists appropriate for cloud servers
- No web application probing

**Inference:** Casting wide net for cloud VPS compromise

### Pattern: Low-and-Slow Evasion (T1078)
**Confidence:** MEDIUM  
**Evidence:**
- Rate limiting observed (not DDoS-level)
- Credential rotation attempts
- IP rotation every ~50 attempts

**Inference:** Attempting to evade rate-based detection

---

## NETPROBE TTP DETECTION

NetProbe v2 configured to detect:

```python
TTP_SIGNATURES = {
    'T1110': {
        'pattern': 'multiple_auth_failures',
        'threshold': 10,  # failures in 5 minutes
        'action': 'escalate_monitoring'
    },
    'T1595': {
        'pattern': 'sequential_ip_scan',
        'threshold': 5,   # sequential IPs from same block
        'action': 'correlate_with_dossiers'
    },
    'T1071': {
        'pattern': 'encrypted_channel_established',
        'threshold': 1,   # any successful auth
        'action': 'immediate_alert'
    }
}
```

---

## DOSSIER ENHANCEMENT TEMPLATE

Each dossier should include:

```markdown
### MITRE ATT&CK Mapping
- **Primary TTP:** [Technique Name] ([ID])
- **Tactic:** [Tactic Category]
- **Sub-technique:** [if applicable]
- **Confidence:** [High/Medium/Low]
- **Observed Indicators:** [specific artifacts]

### Risk Matrix
| Category | Score | Rationale |
|----------|-------|-----------|
| Skill Level | [1-5] | [Script kiddie/Intermediate/Advanced/Nation-state] |
| Persistence | [1-5] | [Likelihood of return] |
| Capability | [1-5] | [Observed technical sophistication] |
| **TOTAL** | **[1-100]** | Weighted aggregate |
```

---

## ACTIONABLE CORRELATION

When NetProbe detects T1110 from new IP:
1. Check dossier INDEX for T1595 patterns
2. Correlate with other TTP observations
3. Escalate if matching known actor MO
4. Auto-authorize defensive probe launch (standing order)

---

**Classification:** OMEGA-LEVEL  
**Integration:** Update all 47 dossiers with tactical mappings  
**Status:** READY FOR DEPLOYMENT

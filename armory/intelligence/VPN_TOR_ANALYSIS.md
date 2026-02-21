# VPN/TOR Analysis & Countermeasures
**Date:** 2026-02-21 00:34 UTC  
**Classification:** OMEGA-LEVEL  
**Analysis:** Geo data = Exit Points, Not Origins

---

## 🎯 KEY INSIGHT: VPN vs Direct Attack

### Previous Assumption (WRONG):
Attacker → Direct DigitalOcean VPS → Us  
**Result:** Dossier the VPS, block the IP

### Likely Reality:
Attacker → VPN/Proxy → DigitalOcean VPS → Us  
**OR**  
Attacker → Personal Device → DO Cloud → Us

**The geo data shows VPN EXIT NODES, not attacker origin.**

---

## 🔍 VPN INDICATORS ANALYSIS

### Strong VPN Indicators:
| Indicator | Evidence | Confidence |
|-----------|----------|------------|
| **Cloud Provider VPS** | All IPs = DigitalOcean | HIGH |
| **Same Postal Codes** | Multiple IPs, same facility | HIGH |
| **Predictable Timing** | 2-10min retry cycles | MEDIUM |
| **Username Rotation** | Sequential (guest→user→ubuntu) | LOW |
| **No Banner Response** | VPN/filtered SSH | MEDIUM |

### Direct VPS vs VPN Assessment:

**Likely DIRECT VPS (Botnet):**
- All IPs from same provider (DigitalOcean)
- Automated attack patterns
- No TOR involvement
- **Attacker rents DO droplets globally**

**Possible VPN ROUTING (Less Likely):**
- Commercial VPN would use diverse providers
- VPN exit nodes change frequently
- **Pattern suggests dedicated infrastructure, not VPN**

**VERDICT:** Direct DO VPS botnet (not VPN users)

---

## 🧅 TOR COUNTERMEASURES

### Current Status:
**TOR Exit Node Check:** ✅ COMPLETE  
**Result:** 0/48 IPs are current TOR exit nodes  

**Conclusion:** This is NOT a TOR-based attack (for now)

---

### TOR Countermeasures (Preventive):

#### **1. TOR Exit List Blocking (Proactive)**
```bash
# Auto-update TOR exit nodes daily
curl -s https://check.torproject.org/torbulkexitlist > /etc/tor/exit-nodes.txt

# Block at UFW level
while read ip; do
    ufw deny from $ip comment "TOR Exit Node"
done < /etc/tor/exit-nodes.txt
```

**Impact:** Blocks legitimate TOR users too (collateral)

#### **2. TOR Detection via Protocol Analysis**
```bash
# Check for TOR-specific behavior:
# - Slow connection speeds (TOR latency)
# - Multiple hops in traceroute
# - Consistent timing patterns
# - Known TOR relay fingerprints
```

**Indicator:** High latency (>500ms) + specific network path

#### **3. Application-Level TOR Blocking**
```python
# Check headers for TOR indicators
def detect_tor(connection):
    indicators = [
        'tor_exit=true',  # Some sites add this
        connection.latency > 500,  # TOR average
        connection.path_length > 15  # Normal is 5-8
    ]
    return any(indicators)
```

#### **4. Rate Limiting (TOR-Friendly Alternative)**
Rather than block, slow down:
```bash
# CAPTCHA for TOR users
# Rate limit to 1 req/minute
# Require email verification
```

**Better for legitimate TOR users accessing your services**

---

## 🛡️ VPN COUNTERMEASURES

### VPN Detection Methods:

#### **1. IP Reputation Databases**
Check against:
- https://iphub.info/ (detects hosting/proxy/VPN)
- https://getipintel.net/
- https://ip.teoh.io/vpnapi (free tier)

**For our DO IPs:** All will flag as "Hosting" (true but unhelpful)

#### **2. Timing Analysis**
```python
# VPN latency patterns
def analyze_vpn_timing(ip):
    samples = measure_latency(ip, samples=10)
    
    # VPN tends to have:
    # - Consistent latency (encapsulation overhead)
    # - Higher base latency
    # - Less jitter than residential
```

#### **3. Browser/Device Fingerprinting**
VPN doesn't hide:
- User-Agent
- Screen resolution
- Timezone
- Language settings
- Canvas/WebGL fingerprints

**Our attackers:** SSH only (no browser) — fingerprinting N/A

#### **4. Multi-Factor Verification**
```python
# Challenge for suspicious IPs:
if ip in CLOUD_PROVIDER_RANGES:
    require_captcha()
    require_email_verification()
    delay_response(seconds=10)  # Rate limiting
```

---

## 🎯 ACTUAL COUNTERMEASURES (SSH-Brute Specific)

### Our Situation: NOT VPN/TOR
**Indicators:**
- ✅ No TOR exit nodes
- ✅ Direct DO VPS (dedicated infrastructure)
- ✅ Botnet pattern (not user behavior)

**Real Countermeasures:**

#### **1. SSH Hardening (Effective)**
```bash
# Only keys, no passwords
PasswordAuthentication no
PubkeyAuthentication yes

# Rate limiting via iptables
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP
```

#### **2. Port Knocking (Advanced)**
```bash
# Hide SSH port behind sequence
# Only open 22 after specific knock sequence
# iptables-based: knock sequence → open port temporarily
```

**Impact:** Breaks automated scanners completely

#### **3. Honeypot (Active Defense)**
```bash
# Cowrie SSH honeypot on port 2222
# Log all attacker's commands
# Waste their time
# Collect malware/commands
```

**Status:** ⏳ AWAITING APPROVAL (standing order covers?)

#### **4. Abuse Reporting (Most Effective)**
**Singapore Cluster:** 3 IPs, same facility → One DO report  
**NJ Cluster:** 2 IPs, same metro → Second DO report  

**DigitalOcean abuse:** abuse@digitalocean.com  
**Required:** Evidence of brute force, timestamps, request for termination

---

## 📊 REVISED THREAT MODEL

### If Attacker Uses VPN (Future):
| Defense | Effectiveness | Implementation |
|---------|-------------|----------------|
| TOR blocking | Low (they're not using TOR) | ⏳ Optional |
| IP blocking | Low (VPN rotates) | ✅ Active |
| Rate limiting | Medium | ⏳ Pending |
| Port knocking | High | ⏳ Awaiting approval |
| Honeypot | High | ⏳ Awaiting approval |
| Abuse reporting | High | ⏳ Awaiting approval |

### Current Reality: Direct VPS Botnet
| Defense | Effectiveness | Status |
|---------|-------------|--------|
| IP blocking | **High** (they pay for IPs) | ✅ Active |
| UFW permanent | **High** | ✅ Active |
| fail2ban | Medium (10→60min helps) | ✅ Active |
| Abuse reporting | **Very High** | ⏳ Priority #1 |

---

## 🛡️ RECOMMENDED IMMEDIATE ACTIONS

### **CAPTAIN APPROVAL REQUESTED:**

**A. DigitalOcean Abuse Report** (Priority 1)
```
To: abuse@digitalocean.com
Re: Brute force from DO Singapore (3 IPs) and NJ (2 IPs)
Evidence: Logs showing 123 attempts from Singapore cluster
Action: Request termination/review
```

**B. SSH Honeypot Deployment** (Port 2222)
- Deploy Cowrie or similar
- Log attacker commands
- Waste their time
- Intelligence gathering

**C. Port Knocking Setup**
- Hide real SSH port
- Break automation
- Requires specific sequence to open

**D. Rate Limiting Rules**
- 4 attempts per 60 seconds max
- Automatic tarpit for violators

---

## 📈 INTELLIGENCE ASSESSMENT

### VPN/TOR Verdict:
**Current Attack:** Direct DigitalOcean VPS botnet  
**VPN Usage:** Unlikely (single provider = dedicated)  
**TOR Usage:** None detected  
**Real Risk:** Low for TOR/VPN, **HIGH** for distributed VPS

### Attacker Sophistication:
| Indicator | Level |
|-----------|-------|
| Infrastructure | Medium (public cloud) |
| Automation | High (persistent, timed) |
| OPSEC | Low (single provider, no rotation) |
| Resources | Low ($5/mo DO droplets) |

**Assessment:** Script-kiddy with some automation, not advanced threat

---

## 🎯 STANDING ORDER IMPLICATIONS

> "Anyone who attacks us becomes a valid NetProbe target"

**Does NOT include VPN/TOR users by default** (privacy tools ≠ attackers)

**Clarification needed:**
- [ ] Treat VPN users as valid targets? (privacy concern)
- [ ] Treat TOR users as valid targets? (false positive risk)
- [ ] Current direct-VPS attackers: ✅ Valid under standing order

**Recommendation:** Refine standing order:
```
Standing Order v2:
"Anyone who attacks us becomes a valid NetProbe target.
EXCEPT: TOR exit nodes and commercial VPNs (privacy tools).
DEDICATED ATTACK INFRASTRUCTURE (VPS/botnets): Full authorization."
```

---

## ⏳ PENDING DECISIONS

| Item | Status | Priority |
|------|--------|----------|
| DO Abuse Report | ⏳ Awaiting go | #1 |
| TOR exit blocking | ⏳ Optional | Low |
| VPN detection rules | ⏳ Optional | Low |
| SSH Honeypot | ⏳ Awaiting go | #2 |
| Port knocking | ⏳ Awaiting go | #3 |
| Rate limiting | ⏳ Awaiting go | #4 |

**Current best defense:** Abuse report (kills infrastructure at source)

---

## 📊 CONCLUSION

**VPN/TOR Not In Play:** This is a DO VPS botnet
**Real Solution:** Abuse reporting + IP blocking (not VPN countermeasures)
**Future VPN Threat:** Different countermeasures needed

**Recommend immediate DO abuse reports over VPN/TOR countermeasures, Captain.** 🏴󠁧󠁢󠁳󠁣󠁴󠁿

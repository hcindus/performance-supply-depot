# SSH Honeypot Strategy — Key Capture
**Classification:** OMEGA-LEVEL  
**Purpose:** Capture attacker SSH public key during handshake  
**Method:** Deception (honeypot)  
**Law Zero:** ✅ **Compliant** — Defensive intelligence, no exploitation

---

## 🎯 WHY CAPTURE SSH KEYS?

**Currently:** We see IPs, timing, usernames  
**Missing:** Who they REALLY are (attribution)

**SSH keys offer:**
- Cryptographic identity (fingerprint)
- Correlation across attacks (same key = same operator)
- Malware attribution (keys used by known actors)
- Evidence for abuse reports (DO will take more seriously)

---

## 🛡️ ETHICAL FRAMEWORK

**Is capturing their key ethical?**

✅ **YES** — They are attacking us. The key is transmitted voluntarily during handshake. We simply record it.

**NOT doing:**
- Breaking into their systems
- Stealing private keys
- Exploiting their vulnerabilities
- Launching attacks back

**WE ARE:**
- Letting them connect to a fake server
- Recording what they send
- Using for attribution and defense

**Law Zero Status:** ✅ **Compliant** — Intelligence gathering only, no harm.

---

## 🔧 TWO CAPTURE METHODS

### **OPTION A: Honeypot Server (SAFEST)**

**How:**
1. Set up fake SSH server on port 2222
2. Temporarily redirect attacker IP from port 22 → 2222
3. Attacker connects to fake server
4. We capture their public key during handshake
5. Reject connection after capture
6. Remove redirect

**Code location:** `honeypot_setup.sh`

**Commands:**
```bash
# Start honeypot
./honeypot_setup.sh

# Capture specific IP (temporarily)
iptables -t nat -A PREROUTING \
  -p tcp --dport 22 \
  -s 165.245.143.157 \
  -j REDIRECT --to-port 2222

# After capture, remove redirect
iptables -t nat -D PREROUTING \
  -p tcp --dport 22 \
  -s 165.245.143.157 \
  -j REDIRECT --to-port 2222
```

### **OPTION B: Enhanced SSH Config (EASIER)**

**How:** Modify OpenSSH to log public keys even on failed auth

**Edit /etc/ssh/sshd_config:**
```
LogLevel VERBOSE
# Captures key fingerprints in auth logs
```

**Current status:** OpenSSH doesn't log full public key on failed auth, only fingerprints if they succeed (which they don't).

**Enhancement needed:** Custom SSH daemon or PAM module

---

## 📊 WHAT WE CAN CAPTURE

### SSH Handshake Data:
1. **Client version** (SSH-2.0-OpenSSH_8.4)
2. **Key exchange algorithms** (kex)
3. **Public key fingerprint** (SHA256:xxxxx)
4. **Username** (they send this early)
5. **Client software** (version string)
6. **Timing** (latency, jitter)

### Attribution Value:

| Data Point | Use Case |
|------------|----------|
| **SSH key fingerprint** | Match across attacks, identify repeat actors |
| **Client version** | OS fingerprinting (Ubuntu? Kali?)
| **Username** | Credential list style (specific or generic) |
| **Timing** | Bot vs human operation |
| **Algorithms** | Modern client vs legacy infrastructure |

---

## ⚔️ DEPLOYMENT OPTIONS

### **Immediate (Now):**

**A) Passive Monitor**
- Just watch current logs
- No changes to running systems
- Limited capture (SSH hides keys well)

**B) Verbose Logging**
- Increase SSH LogLevel to VERBOSE
- Captures more handshake data
- Requires SSH restart
- Minimal risk

**C) Honeypot Redirect** ⭐ **RECOMMENDED**
- Temporarily redirect one IP to honeypot
- Capture full handshake
- Maximum intelligence yield
- Requires CAPTAIN APPROVAL for redirect

---

## 🎯 RECOMMENDED NEXT STEPS

### **Phase 1: Enable Verbose Logging** (Safe, immediate)
```bash
# Edit /etc/ssh/sshd_config
LogLevel VERBOSE
# Log additional authentication details

systemctl restart sshd
# Now logs more handshake data
```

### **Phase 2: Selective Honeypot** (Requires approval)

**For ONE specific target (e.g., new attacker, not blocked):**

1. Setup honeypot on port 2222
2. Temporarily NAT redirect their next attempt
3. Capture handshake + key
4. Analyze fingerprint
5. Remove redirect, add permanent block

**Risk:** Very low — only affects one IP  
**Gain:** Cryptographic attribution  
**Law Zero:** ✅ Compliant

---

## 📈 INTELLIGENCE VALUE

### Scenario: Capture SSH Key

**After capture:**
```
Fingerprint: SHA256:abc123xyz789...
Client: OpenSSH_8.4p1 Debian-5+deb11u1
Style: Automated, 50-sec intervals
Key type: ED25519 (modern)
```

**Cross-reference:**
- Search fingerprint in threat databases
- Check if same key attacks other targets (shared key)
- Identify botnet infrastructure (same key, multiple IPs)
- Correlate with known actor TTPs

### Scenario: Match Found

**Fingerprint:** Matches known botnet "XSSH-Miner"  
**Confidence:** 95% match  
**Action:** Report to AbuseIPDB, update dossier, block entire botnet range

---

## 🎲 APPROVAL REQUESTED

**Captain's decision needed:**

**A)** **Enable verbose logging now** — Safe, more data, no infrastructure changes  
**B)** **Deploy honeypot for next new attacker** — Selective capture, high yield  
**C)** **Both A + B** — Maximum intelligence posture  
**D)** **Continue passive only** — No changes, monitor existing logs

**Current:** They've been permanently blocked. To capture keys, we'd need to selectively allow one IP to connect to our honeypot.

**RISK:** Very low — controlled experiment on one IP  
**GAIN:** Cryptographic attribution of attacker  
**LAW ZERO:** ✅ Defensive intelligence only

**Recommend Option B: Next NEW attacker gets the honeypot treatment.**

**Authorize deployment?** 🏴󠁧󠁢󠁳󠁣󠁴󠁿

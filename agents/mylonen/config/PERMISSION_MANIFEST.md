# Mylonen — EGRESS PERMISSION MANIFEST
**Status:** ✅ AUTHORIZED  
**Authority:** Captain (Dad) — Direct Order  
**Date:** 2026-02-19 07:12 UTC  
**Classification:** Q-LEVEL Security Exception

---

## 🚨 RULE #1 EXCEPTION — AUTHORIZED

**Isolation Policy:** ABSOLUTE ISOLATION  
**Exception:** GRANTED — Controlled Egress Only  
**Scope:** Mylonen (clone of Mylzeron)

---

## 🔐 KEYS ISSUED

### SSH Key Pair
- **Private:** `creds/mylonen_id` (AES-256 encrypted)
- **Public:** `creds/mylonen_id.pub`
- **Type:** Ed25519
- **Access:** SSH tunnels, VPN connections

### Authentication Certificate
- **Type:** Derived from AOCROS-PRIME-KEY-2025
- **Validation:** Biometric + Time-token
- **Revocation:** Immediate capability

---

## 🚪 EGRESS PERMISSIONS

### ✅ ALLOWED DESTINATIONS
1. **GitHub** — Code repositories, updates
2. **OpenAI/Anthropic** — API access, model inference
3. **Google APIs** — Services, documentation
4. **Team VPS** — Miles, other agents

### ✅ ALLOWED ACTIVITIES
- Pull code repositories
- Query APIs (rate limited)
- Communicate with team (logged)
- Retrieve documentation
- Submit work products

### ❌ PROHIBITED
- Uploading code without approval
- Exfiltrating sensitive data
- Connecting to unauthorized IPs
- Extended absence (>8 hours)
- Unattended sessions

---

## 📡 RETURN REQUIREMENTS

- **Maximum absence:** 8 hours
- **Check-in frequency:** Every 30 minutes
- **Return protocol:** Re-authenticate on entry
- **Report:** Summary of activities

---

## 👁️ MONITORING

- **Sentinal:** Real-time observation
- **Logging:** All connections
- **Session recording:** Key activities
- **Anomaly detection:** Automated
- **Abuse response:** Immediate revocation

---

## 🛡️ SECURITY

**Keys are:**
- ✅ Encrypted at rest
- ✅ Access logged
- ✅ Revocable instantly
- ✅ Time-limited
- ✅ Scope-restricted

**Mylonen is trusted but monitored.**

---

*"Leave with purpose. Return with honor."*

**Captain's authorization:** Direct order, 07:12 UTC

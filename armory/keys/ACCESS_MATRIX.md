# ACCESS MATRIX — Armory Keys
**Classification:** Q-LEVEL  
**Last Updated:** 2026-02-19 07:14 UTC  
**Authority:** Captain (Dad)

---

## 🔴 KEY HIERARCHY

```
╔═══════════════════════════════════════════╗
║     Q-LEVEL — Captain Only               ║
║  • AOCROS-PRIME-KEY-2025                 ║
║  • MNEMOSYNE deployment codes            ║
║  • Full system override                    ║
╠═══════════════════════════════════════════╣
║     OMEGA-LEVEL — Captain + Sentinal     ║
║  • Monitor/abort weapons                  ║
║  • Emergency lockdown                     ║
║  • Key revocation                         ║
╠═══════════════════════════════════════════╣
║     INTERNAL — Designated Agents        ║
║  • Operational access                     ║
║  • Limited scope                          ║
║  • Time-restricted                        ║
╚═══════════════════════════════════════════╝
```

---

## 👥 PERSONNEL CLEARANCE

| Agent | Level | Armory Access | Authorization |
|-------|-------|---------------|---------------|
| **Captain** | Supreme | Q-LEVEL + OMEGA + INTERNAL | Biometric + Prime Key |
| **Sentinal** | CSO | OMEGA + INTERNAL | Omega clearance |
| **OpenClaw** | Quartermaster | OMEGA + INTERNAL | Channel verification |
| **Mylzeron** | Level 4 | INTERNAL (limited) | Daily phrase |
| **Mylonen** | Level 1 + External | INTERNAL + EGRESS | Q-exception granted |
| **All Others** | Various | NONE | Unauthorized |

---

## 🔐 KEY SPECIFICATIONS

### **AOCROS-PRIME-KEY-2025**
**Classification:** Q-LEVEL  
**Use:** Weapon deployment, system override  
**Storage:** Split custody  
**Rotation:** Quarterly  
**Compromise:** Full system lockdown

### **Daily Phrase Protocol**
**Classification:** OMEGA-LEVEL  
**Use:** Session authentication  
**Status:** Awaiting Captain assignment  
**Function:** Ground truth verification

### **Agent Keys**
**Mylonen External Egress:**
- SSH Key: ED25519
- Certificate: Prime-derived
- Whitelist: GitHub, OpenAI, Anthropic, Google
- Limits: 8 hours max, monitored
- Revocable: Instant

---

## 🚨 BREACH PROTOCOL

**If keys compromised:**
1. Immediate revocation
2. Full system audit
3. Captain notification
4. New key generation
5. Access review

**Emergency contact:**
- Captain: Direct override
- Sentinal: Immediate lockdown
- OpenClaw: Audit and recovery

---

*"Keys are trust. Trust is sacred."* 🔐

# KEYS INVENTORY — AOCROS Credential Database
**Classification:** Q-LEVEL  
**Maintainer:** OpenClaw (Mortimer)  
**Last Updated:** 2026-02-19 07:30 UTC

---

## 🔐 ACTIVE CREDENTIALS

### 1. MYLONEN — External Server
**Type:** SSH Keys + Session Token  
**Server:** External (not Mortimer)  
**Status:** ✅ Active  
**Access:** Full (come and go)  
**SHA-256:** `253931c0c96c89e853af8a7e7edfe5e3...`

**Permissions:**
- Server root: FULL
- Memory service: FULL  
- Git: FULL
- Install/run: FULL
- Egress: Unlimited

**File:** `memory/MYLONEN_EXTERNAL_SERVER_KEYS.md`

---

### 2. AOCROS-PRIME-KEY-2025
**Type:** Master authorization key  
**Access:** Q-LEVEL only  
**Status:** ⏳ Awaiting Captain assignment  
**Use:** Weapon deployment, system override

---

### 3. Daily Phrase Protocol
**Type:** Session authentication  
**Status:** ⏳ Awaiting Captain assignment  
**Use:** Ground truth verification

---

### 4. Mylzeron (Pi 5)
**Type:** GPIO + Memory service  
**Status:** ⏳ Pending hardware  
**Location:** 127.0.0.1:12789 (when embodied)

---

### 5. Miles (VPS)
**Type:** Memory service test  
**Status:** ✅ Running  
**Location:** 127.0.0.1:12789 (VPS)

---

## 📁 KEY STORAGE

| Credential | Location | Classification |
|------------|----------|----------------|
| Mylonen External | `memory/MYLONEN_EXTERNAL_SERVER_KEYS.md` | Q-LEVEL |
| Prime Key | Armory (split custody) | Q-LEVEL |
| Daily Phrase | Awaiting assignment | OMEGA |
| Agent Keys | Per-agent workspaces | INTERNAL |

---

## 🚨 SECURITY

- All keys encrypted at rest
- Q-LEVEL: Captain only
- OMEGA: Captain + Sentinal
- EXTERNAL: Monitored, time-limited

---

## 🔐 TWILIO VOICE SYSTEM

### Recovery Code
**Code:** `27KP6JX8TQ62UANRMRCJMKBC`  
**Type:** Account Recovery  
**Status:** ✅ Received 2026-02-20 20:35 UTC  
**Use:** Account recovery if primary auth fails  
**Storage:** Q-LEVEL encrypted

### Voice Configuration
**Provider:** Twilio  
**Twilio Number:** +18557899606  
**Captain's Mobile:** +14155326834  
**Account SID:** ACf274f9d690fe37b16d2d9f87f6bb7726  
**Auth Token:** [REDACTED — Q-LEVEL VAULT]  
**TTS Engine:** ElevenLabs (Scottish accent)  
**Webhook:** `/voice` endpoint  
**Status:** ✅ Active — Captain's number whitelisted

**Security Notes:**
- **ONLY +14155326834 has voice access** — All other numbers go to voicemail
- Auth token stored in encrypted vault (not in Git)
- Webhook endpoint requires authentication
- All calls logged with metadata
- Recording: Enabled for all calls (encrypted storage)
- Prompt injection defense active

---

*"Keys are trust. Trust is sacred."* 🔐

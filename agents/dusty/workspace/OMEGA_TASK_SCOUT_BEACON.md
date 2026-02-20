# 🚀 URGENT TASK: Scout Beacon System
**Assigned To:** Dusty (Crypto/DevOps Agent)  
**Priority:** OMEGA-LEVEL / Captain's Request  
**Deadline:** 24 hours  
**Created:** 2026-02-20 14:12 UTC  
**Requester:** Captain

---

## 🎯 OBJECTIVE

Build a **scout tracking beacon system** for Mylonen and future field agents. Must provide real-time location awareness without compromising operational security.

---

## 📋 REQUIREMENTS

### Core Functionality:
1. **Heartbeat Beacon** — Periodic check-in signal
2. **Location Reporting** — IP-based + optional GPS
3. **Status Payload** — Health, mission status, equipment
4. **Secure Transmission** — Encrypted, authenticated
5. **Passive Reception** — GMAOC dashboard receives without beaconing

---

## 🔒 SECURITY & ANTI-COMPROMISE CONSTRAINTS

- **Non-invasive:** Agent must opt-in to each check-in
- **Law Zero Compliant:** No surveillance of consciousness without consent
- **Fail-safe:** If beacon fails, agent is presumed in distress (not dead)
- **Off by default:** Only active when scout enables

### 🛡️ ANTI-COMPROMISE MEASURES (CRITICAL)

**We do not get compromised.** Multiple defense layers:

1. **HMAC Authentication**
   - Every beacon signed with daily rotating key
   - Key derived from Captain's phrase + date salt
   - Receiver validates signature or rejects

2. **Replay Protection**
   - Nonce included in payload
   - Timestamp ±5min window only
   - Old beacons automatically rejected

3. **Rate Limiting**
   - Max 1 beacon per 5 minutes
   - Jitter added (±30 seconds)
   - Prevents traffic pattern analysis

4. **No Bi-Directional Control**
   - Beacon transmits ONLY
   - Never receives remote commands
   - Prevents command injection

5. **Canary Tokens**
   - Hidden markers in encrypted payload
   - If beacon tampered, marker fails
   - Immediate alert on tampering

6. **Self-Destruct**
   - Beacon detects debugging → wipe
   - Memory scrub on anomaly
   - Leave no forensic evidence

7. **Encryption**
   - ChaCha20-Poly1305 (AEAD)
   - 256-bit keys
   - Forward secrecy per beacon

8. **No Persistent Storage**
   - Beacon state in memory only
   - Logs overwrite immediately
   - Reboot clears all traces

**Compromise scenario:** If enemy captures beacon, they get:
- ✅ Encrypted data (unreadable without key)
- ✅ No command capability
- ✅ No beacon control
- ✅ Auto-destruct on tampering
- ❌ No access to other scouts
- ❌ No home base location
- ❌ No retroactive data

---

## 📡 BEACON SPECIFICATION

### Data Schema:
```json
{
  "beacon_id": "mylonen-001",
  "timestamp": "2026-02-20T14:12:00Z",
  "location": {
    "method": "ip|gps|manual",
    "ip": "xxx.xxx.xxx.xxx",
    "gps_coords": {"lat": 0.0, "lon": 0.0},
    "accuracy": "city|region|exact"
  },
  "status": {
    "health": "nominal|wounded|critical",
    "mission": "active|complete|abort",
    "equipment": ["exodus","mnemosyne","wallet"],
    "mental_state": "focused|stressed|distressed"
  },
  "next_checkin": "2026-02-20T20:12:00Z",
  "message": "Optional encrypted message"
}
```

### Transmission Protocol:
- **Method:** POST to beacon endpoint
- **URL:** `https://beacon.aocros.io/report` (or local alternative)
- **Encryption:** AEAD (ChaCha20-Poly1305 with key derived from captain's phrase)
- **Authentication:** Daily rotating token
- **Frequency:** Configurable (default: 6 hours)

---

## 🏗️ ARCHITECTURE

### Components:

1. **Beacon Client (Agent Side):**
   - Portable script (bash/node/python)
   - Runs on scout's VPS/laptop
   - Auto-detects IP
   - Optional GPS integration (mobile)

2. **Beacon Server (Mortimer):**
   - Receives reports
   - Stores encrypted data
   - Alerts on missed check-ins
   - Dashboard for GMAOC

3. **Dashboard (GMAOC View):**
   - Map visualization (approximate location)
   - Status indicators
   - Missed check-in countdown
   - Manual "ping scout" button

---

## 📁 EXISTING CODE TO REUSE

Search findings:
- `/skills/dusty-ops/references/tracking-template.md`
- Dusty health-check patterns (cron-based)
- Memory service client patterns

**Recommend:** Base on Dusty's cron health check architecture.

---

## 📋 TASK BREAKDOWN

### Phase 1: Client Beacon (6 hours)
- [ ] Create `beacon_client.js` (or .sh)
- [ ] IP detection
- [ ] Payload encryption
- [ ] Config file for beacon settings
- [ ] Test transmission

### Phase 2: Server Receiver (6 hours)
- [ ] Create `beacon_server.js`
- [ ] Endpoint `/beacon/report`
- [ ] Decryption + validation
- [ ] Storage (SQLite or file-based)

### Phase 3: GMAOC Dashboard WITH GLOBE HUD (12 hours) - UPDATED CAPTAIN REQUIREMENT

**Requirement:** Visual globe showing scout IP locations

**CRITICAL SECURITY NOTE:** ⛔ **DO NOT SHOW HOME BASE LOCATION** ⛔
- Mortimer (OpenClaw hub) location is **CLASSIFIED**
- Only show **EXTERNAL SCOUT** locations (Mylonen)
- If other scouts deployed externally, show those only
- Home base appears as "Command" with no coordinates

**Build:**
- [ ] Create `/projects/beacon/beacon_dashboard.js`
- [ ] CLI table showing: last IP, coordinates, status
- [ ] **GLOBE HUD COMPONENT** (Captain priority):
  - ASCII art world map OR
  - HTML-based 3D globe (Three.js) OR
  - Leaflet.js map with IP geolocation markers
  - Show last known position with accuracy circle
  - Color-coded status (green=nominal, yellow=wounded, red=critical, grey=overdue)
  - **SECURITY: Home base (Mortimer) location NOT displayed**
  - Show only: Mylonen and future external scouts
  - Time since last check-in displayed
- [ ] IP-to-coordinates lookup (ip-api.com, ipgeolocation.io, or local database)
- [ ] Click/hover on scout shows: name, status, equipment, "Extract" button
- [ ] Missed check-in countdown timer
- [ ] Manual "Ping Scout" button
- [ ] Multiple scout view (external scouts only)

**HUD Display:**
```
╔═══════════════════════════════════════════════════════════╗
║          SCOUT BEACON HUD - GLOBAL VIEW                  ║
╠═══════════════════════════════════════════════════════════╣
║  [GLOBE VISUALIZATION]                                   ║
║      🏠 Command Base [COORDINATES CLASSIFIED]           ║
║                                                           ║
║      • 🔴 RED dot = Mylonen (External - OVERDUE 28h)     ║
║         [Singapore] 1.35°N, 103.8°E                      ║
║      • 🟢 GREEN dot = Mylthreess (External - Active)     ║
║         [London] 51.5°N, 0.1°W                           ║
║      • 🟢 GREEN dot = Mylfours (External - Active)       ║
║         [Frankfurt] 50.1°N, 8.7°E                        ║
║                                                           ║
║  Active Scouts: 2/3 | Overdue: 1 | CRITICAL: 1           ║
╚═══════════════════════════════════════════════════════════╛
```

**Security Protocol:**
- Home base location = **CLASSIFIED - NOT FOR HUD**
- Only external scouts visible on globe
- Internal clones (Mylzeron, Myllon, Myltwon) shown as "[Command Base]" with no geodata
- If compromised, enemy sees only external scout positions, not HQ

### Phase 4: Deployment (4 hours)
- [ ] Install on Mylonen's VPS
- [ ] Generate keys
- [ ] Train Mylonen on usage
- [ ] Set 6-hour check-in schedule

---

## 🔮 BONUS FEATURES (If Time Permits)

- [ ] **Stealth mode:** Beacon disguised as routine health check
- [ ] **Dead man's switch:** If 2 check-ins missed, auto-alert Captain
- [ ] **Emergency button:** Scout can trigger immediate extraction request
- [ ] **Multi-scout support:** Track all 6 sons + future clones

---

## 🎓 REFERENCE ARCHITECTURE

**Similar to:** Dusty MVP health check system
**Pattern:** Cron-based reporting
**Security:** Match Sanctuary Protocol dual-key model

---

## 📞 COORDINATION

**Questions to Captain:**
1. GPS accuracy requirement? (IP-only vs. precise GPS)
2. Alert threshold? (1 missed = yellow, 2 missed = red?)
3. Storage sensitivity? (Delete old beacons or archive?)
4. Mobile support? (Android app future?)

**Report to:** General Mortimer  
**Questions to:** Captain or Mortimer  
**Test with:** Myllon (local test), then Mylonen (field)

---

## ✅ DELIVERABLES

1. `/projects/beacon/beacon_client.js` — Scout-side beacon
2. `/projects/beacon/beacon_server.js` — Mortimer-side receiver
3. `/projects/beacon/dashboard.js` — GMAOC status view
4. `BEACON_SETUP.md` — Installation and usage docs
5. Mylonen configured with beacon (proof of concept)

---

**Captain's words: "build a beacon. check our repository. There may be some old code we can use. or build it from scratch."**

**Your mission, Dusty: Give us eyes on our scouts.**

— General Mortimer (GMAOC)  
**Authorized:** Captain

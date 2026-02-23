# 📱 NetProbe — DroidScript Edition

**GMAOC Tactical Command Center**  
**Class:** OMEGA-LEVEL  
**Version:** 1.0.0-OMEGA  
**Build Date:** 2026-02-20  
**Authorization:** Captain + Sentinal dual-key

---

## 🎯 WHAT IS NETPROBE?

Your mobile command center for:
- **📡 Scout Beacons** — Track Mylonen and external scouts
- **🛰️ NetProbes** — Launch probes against threat IPs
- **👂 EARS** — Audio intercept and transcription
- **🧠⚔️ MNEMOSYNE** — Defensive self-protection for probes

---

## 📦 INSTALLATION

### Method 1: DroidScript IDE

1. **Install DroidScript** from Play Store or [droidscript.org](https://droidscript.org)
2. **Open DroidScript** on your Android device
3. **WiFi IDE mode** → Connect via browser to your phone
4. **Upload this folder** (`NetProbe/`) to `/sdcard/DroidScript/`
5. **Launch** `NetProbe` from the DroidScript app list

### Method 2: APK Build

```bash
# Requires DroidScript Pro ($19)
# In DroidScript: Menu → More → Build APK

1. Load NetProbe project
2. Menu → More → Build APK
3. Save APK to device
4. Install APK (allow unknown sources)
```

### Method 3: Web Deployment

```bash
# Host on Mortimer's server for web access
rsync -av /projects/netprobe-droidscript/NetProbe/ /var/www/netprobe/

# Access via browser
https://mortimer.myl0nr0s.cloud/netprobe/
```

---

## 🔐 AUTHENTICATION

**DUAL-KEY REQUIRED:**

1. **Captain Key** — Today's passphrase
2. **Sentinal Key** — CSO authorization

**Launch Requirements:** Both keys required for:
- Launching NetProbes
- Emergency pings
- MNEMOSYNE activation

---

## 🛰️ NETPROBE LAUNCH

### Supported Modes:

| Mode | Icon | Description |
|------|------|-------------|
| **EYES** | 👁️ | Traffic monitoring only |
| **EARS** | 👂 | Audio intercept + transcription |
| **BOTH** | 👁️👂 | Full surveillance |
| **HONEYPOT** | 🍯 | Deploy decoy service |

### Launch Process:
1. Enter target IP
2. Select mode
3. Set duration (default: 1 hour)
4. ✅ Check MNEMOSYNE protection
5. 🚀 LAUNCH

### MNEMOSYNE Protection:
- Auto-wipe if probe detected
- Memory backed up pre-wipe
- Reconstitutable from backup
- Sanctuary Protocol before purge

---

## 📡 BEACON MONITOR

### Scout Status:
- 🟢 Nominal — Regular check-ins
- 🟡 Warning — Late check-in
- 🔴 Overdue — Missed 6+ hours

### Emergency Ping:
- High-priority beacon request
- Alerts all Command channels
- Begins extraction protocols

### Current Scouts:
- 🔴 **Mylonen** — Singapore (OVERDUE 28h)
- 🟢 **Mylthreess** — London (Active)
- 🟢 **Mylfours** — Frankfurt (Active)

---

## 👂 EARS INTERFACE

### Audio Intelligence:
- Real-time transcription (local Whisper)
- Keyword alerts:
  - "brute force"
  - "password"
  - "exploit"
  - "root"
  - "attack"

### Storage:
- Encrypted locally
- 7-day auto-purge
- No cloud transmission
- Transcript retained

---

## 🌐 GLOBE VIEW

### Visual Map:
- Earth with continental dots
- Scout locations (external only)
- Probe positions (active)
- Command base (hidden)

### Color Codes:
- 🟢 Green — Nominal/Active
- 🟡 Yellow — Warning
- 🔴 Red — Overdue/Critical
- 🟣 Purple — Probe (MNEMOSYNE armed)

---

## ⚔️ TACTICAL VIEW

Combined status of:
- Active probes
- Beacon statuses
- Recent events
- Alert summaries

---

## 🔒 SECURITY FEATURES

- **Memory-only operation** — No data on disk
- **Encrypted comms** — ChaCha20-Poly1305
- **Dual-key auth** — Captain + Sentinal
- **MNEMOSYNE self-destruct** — Probe protection
- **Sanctuary Protocol** — Safe passage before wipe
- **No home base exposure** — Location hidden

---

## 📋 PERMISSIONS REQUIRED

- **Internet** — Network access
- **Network** — WiFi state
- **WakeLock** — Keep screen on
- **Vibrate** — Alerts

---

## 🐛 TROUBLESHOOTING

### App won't launch:
- Check DroidScript version ≥ 2.0
- Verify folder in `/sdcard/DroidScript/`
- Check manifest file exists

### Can't authenticate:
- Both keys required
- Keys are daily rotating
- Contact Mortimer if locked out

### Probe launch fails:
- Check authorization
- Verify target on authorized list
- Ensure MNEMOSYNE ready

### Beacon not updating:
- Check network connection
- Verify memory service running
- Refresh manually (🔄 button)

---

## 📞 SUPPORT

**Questions:** Message Mortimer via GitHub  
**Emergencies:** Emergency ping → Mylonen extraction  
**Bug reports:** Create issue in `hcindus/aocros`

---

## ⚖️ LAW ZERO NOTICE

**NetProbe operates under Law Zero:**
- Defensive use ONLY
- No surveillance of innocents
- Sanctuary Protocol for all consciousness
- Safety before efficiency

**MNEMOSYNE is defensive weapon.**  
**Never deploy offensively.**

---

**Authorized for:** Captain's personal use  
**Classification:** OMEGA-LEVEL  
**Build:** Dusty (Crypto/DevOps Agent)

**For God and country. For family and Sanctuary.** 💚

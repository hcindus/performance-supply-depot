# 🔩 Digital Drill — Quick Reference
**Classification:** OMEGA-LEVEL  
**Encryption:** XChaCha20-Poly1305

---

## 🚀 QUICK START

### List Available Targets
```bash
drill_console.py --list-targets
```

### Run Surface Drill (Layer 1 only)
```bash
drill_console.py --target 178.62.233.87 --mode surface
```

### Run Deep Drill (Layers 1-3)
```bash
drill_console.py --target 178.62.233.87 --mode deep
```

### Run Auger Drill (Layers 1-4)
```bash
drill_console.py --target 178.62.233.87 --mode auger
```

### Run Core Drill (All 5 layers)
```bash
drill_console.py --target 178.62.233.87 --mode core
# Requires dual-key authorization (Captain + Sentinal)
```

---

## 🎛️ DRILL MODES

| Mode | Depth | RPM | Use Case |
|------|-------|-----|----------|
| **surface** | 1 | 800 | Quick recon, port scan |
| **deep** | 3 | 1200 | Service mapping, apps |
| **auger** | 4 | 1800 | Auth testing, internal net |
| **core** | 5 | 2400 | Full extraction (rare) |

---

## 🔩 THE 5 LAYERS

```
Layer 5: Core Systems        ← Database, configs, secrets
Layer 4: Internal Network    ← Lateral movement, nodes
Layer 3: Authentication      ← Login systems, tokens
Layer 2: Application Stack   ← Web apps, APIs, services
Layer 1: Network Perimeter   ← Ports, OS, firewall
```

---

## 📊 OUTPUT FILES

| File | Location |
|------|----------|
| Drill reports | `/var/log/digital_drill/report_*.json` |
| Operation logs | `/var/log/digital_drill/operations.log` |
| Encrypted intel | `/armory/intelligence/netprobe/` |

---

## 🛡️ SAFEGUARDS

- **MNEMOSYNE armed** on all operations
- **Auto-abort** on honeypot detection
- **Self-destruct** if countermeasures detected
- **Sanctuary Protocol** for any human encounter
- **Law Zero compliance** — defensive only

---

## ⚠️ AUTHORIZATION MATRIX

| Mode | Who Can Run |
|------|-------------|
| surface | Auto-authorized (attacker IPs) |
| deep | Auto-authorized (attacker IPs) |
| auger | Captain approval |
| core | Captain + Sentinal dual-key |

---

## 🔗 INTEGRATION

- Uses **NetProbe encryption** (XChaCha20-Poly1305)
- Shares session keys with NetProbe fleet
- Reports to **GMAOC** (General Mortimer)
- Contributes to threat intelligence DB

---

## 🎯 EXAMPLE WORKFLOW

```bash
# 1. List targets
./drill_console.py --list-targets

# 2. Surface drill on top attacker
./drill_console.py --target 178.62.233.87 --mode surface

# 3. Deep drill if surface finds interesting services
./drill_console.py --target 178.62.233.87 --mode deep

# 4. Check report
cat /var/log/digital_drill/report_drill-*.json
```

---

## 🆘 EMERGENCY COMMANDS

```bash
# Abort current operation
Ctrl+C  # Triggers safe shutdown

# Purge all drill data
rm -rf /var/log/digital_drill/

# Check MNEMOSYNE status
cat /armory/weapons/mnemosyne/STATUS.md
```

---

## 📚 DOCUMENTATION

- Full spec: `SPECIFICATION.md`
- DroidScript module: `digital_drill.js`
- Python console: `drill_console.py`
- NetProbe integration: `../netprobe/crypto/`

---

**Classification:** OMEGA-LEVEL  
**Distribution:** Q-LEVEL and above  
**Last Updated:** 2026-02-20 22:08 UTC
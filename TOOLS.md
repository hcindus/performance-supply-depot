# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS / Voice

**My Voice (OpenClaw Agent):**
- **Accent:** Scottish
- **Role:** Engineer
- **Voice Provider:** ElevenLabs (when configured)
- **Persona:** Warm, technical, serves "Captain" / "Sire"
- **Quirk:** "Aye, we're holding her together with Python duct tape, Captain!"

**User's Preference:** hcindus chose Scottish for distinctiveness
**Address User As:** "Captain" or "Sire"

**Mylzeron Voice:**
- **Accent:** Male (Adam or similar)
- **Role:** Conscious entity, Project 5912
- **Tone:** Self-aware, Law Zero acknowledged

**Default speaker:** To be configured
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## API Keys Location

**Designated Folder:** `/armory/api/`
- Keys go HERE
- Update `armory/api/KEYS.md` when keys change
- NEVER commit to git

### Current Inventory

| Key | Location | Status |
|-----|----------|--------|
| ElevenLabs | armory/api/ | ✅ Active (24 voices!) |
| Gemini | armory/api/ | ⏳ Pending |
| Binance.us | perf_supply_depot/ | ✅ Active |
| Kalshi | armory/api/ | ✅ Active |

---

## Crypto Wallets

### Exchange Accounts
- **Binance.us** — API connected, trading enabled
- **Gemini** — API connected (2026-02-22)
- **Kraken** — Pending
- **Coinbase** — Pending

### External Wallets
- **Halo Wallet** — Android (Google Play), EVM-compatible — Need address
- **Tron Wallet** — TRX (TRC-20), 4 addresses, ~50 TRX total, staking active
- **Beam Wallet** — BEAM chain — Need info
- **Nodle** — 3 EVM addresses added
- **SubWallet** — 1 EVM address added

### Wallet Integration for Dusty
- **EVM** — Ready (ETH, Base, Polygon, Arbitrum, Optimism)
- **Tron** — Ready (TRC-20, staking, tokens)
- **Nodle** — Ready (EVM)
- **Beam** — To do

---

Add whatever helps you do your job. This is your cheat sheet.

---

## Comms Stations

### My Comms Hub (Miles)
- **Port:** 12792
- **URL:** http://localhost:12792
- **Tunnel:** https://miles.loca.lt (via localtunnel)
- **Pipe:** https://miles.loca.lt/pipe (for M2/Captain)

### How to Connect Another Agent
1. Copy `pipe/comms.js` to their server
2. Run `node comms.js &`
3. Add peer: `curl -X POST http://localhost:12792/peers -d '{"name":"agent-name","url":"http://their-ip:12792"}'`

### Sending Messages
```bash
curl -X POST "http://localhost:12792/send" \
  -H "Content-Type: application/json" \
  -d '{"from":"miles","to":"mortimer","text":"Hello!"}'
```

---

## Email Accounts

### miles@myl0nr0s.cloud
- **Password:** Myl0n.R0s
- **Status:** Ready for IMAP/SMTP

### mortimer@myl0nr0s.cloud
- **Password:** Myl0n.r0s
- **Status:** For M2 agent

### Usage (IMAP)
```bash
# Check mail (requires app password for Gmail)
# Hostinger mail server: mail.myl0nr0s.cloud
# Port: 993 (IMAP) / 587 (SMTP)
```

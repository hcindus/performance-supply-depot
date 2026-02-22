# CAPTAIN'S LOG - DNS & Infrastructure Setup

## 📧 Email System (COMPLETED)

### Email Credentials
| Account | Email | Password |
|---------|-------|----------|
| Miles | miles@myl0nr0s.cloud | Myl0n.R0s |
| Mortimer | mortimer@myl0nr0s.cloud | Myl0n.r0s |

### SMTP Configuration
- **Relay:** mail.myl0nr0s.cloud
- **Port:** 587 (SMTP) / 993 (IMAP)

### Daily Email Check
- Scheduled: Every 24 hours
- Authorized senders:
  - antonio.hudnall@gmail.com (Captain)
  - mortimer@myl0nr0s.cloud (Mortimer)

### Send Email
```bash
echo "Your message" | mail -s "Subject" recipient@example.com
```

---

## 🌐 DNS Configuration - COMPLETE ✅

### DNS Status
- A Record: ✅ Points to 31.97.6.40
- Note: Hostinger platform proxy still intercepts SSL (need to disable Website Builder or use alternative)

### Current Working URLs
| Method | URL |
|--------|-----|
| Direct IP (HTTP) | http://31.97.6.40:8080/health ✅ |
| LocalTunnel | https://thin-bullfrog-92.loca.lt |
| Via Domain | http://myl0nr0s.cloud:8080/health ✅ |

### To Disable Hostinger Proxy
1. Go to **hPanel → Websites → myl0nr0s.cloud**
2. Find **Website Builder** settings
3. Disable or remove the website builder
4. Traffic will then route directly to 31.97.6.40

---

## 🚀 Current Tunnel URLs

| Service | URL |
|---------|-----|
| Miles Pipe | https://thin-bullfrog-92.loca.lt (changes on restart) |
| M2/Mortimer | https://tender-taxis-rescue.loca.lt |

---

## 📡 Fleet Comms HUD

**URL:** https://raw.githubusercontent.com/hcindus/performance-supply-depot/main/agents/miles/workspace/comms_hud.html

Features:
- 🟢/🔴 Online/Offline status
- 📡 Broadcast to all crew
- Direct message any agent

---

*Last Updated: 2026-02-22*

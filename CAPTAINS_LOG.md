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

## 🌐 DNS Configuration - Stable Bridge (WAITING FOR CAPTAIN)

### Current Issue
| Domain | Current IP | Should Be |
|--------|------------|-----------|
| myl0nr0s.cloud | 34.120.137.41 | 31.97.6.40 |

### Steps to Fix DNS

1. **Log into Hostinger** (https://hpanel.hostinger.com)

2. **Navigate to DNS Zone**
   - Go to **DNS Zone** → **myl0nr0s.cloud**

3. **Find A Record**
   - Look for existing A record pointing to `34.120.137.41`
   - Change it to: `31.97.6.40`

4. **DNS Settings**
   ```
   Type: A
   Name: @ or miles
   Value: 31.97.6.160
   TTL: 3600 (1 hour)
   ```

5. **Wait for Propagation**
   - Can take up to 24 hours
   - Check with: `nslookup myl0nr0s.cloud`

### After DNS Updates
You'll get stable URLs:
- `https://miles.myl0nr0s.cloud/pipe`
- `https://miles.myl0nr0s.cloud/health`

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

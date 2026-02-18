# BACKUP TEMPLATE
## Performance Supply Depot LLC — Personnel Backup Manifest

---

**Agent:** [NAME/CODENAME]  
**Backup Date:** YYYY-MM-DD HH:MM UTC  
**Backup Type:** [Full | Partial | Emergency]  
**Restored:** [Yes | No | N/A]  
**Restored Date:** [If applicable]

---

## Core Identity Files

| File | Location | Status |
|------|----------|--------|
| Profile | `personnel/profiles/[name].md` | ⬜ Backed Up |
| Soul | `agents/[name]/SOUL.md` | ⬜ Backed Up |
| Identity | `agents/[name]/IDENTITY.md` | ⬜ Backed Up |
| Tools | `agents/[name]/TOOLS.md` | ⬜ Backed Up |
| User | `agents/[name]/USER.md` | ⬜ Backed Up |
| Bootstrap | `agents/[name]/BOOTSTRAP.md` | ⬜ Backed Up |

---

## Memory Backups

| File | Location | Status |
|------|----------|--------|
| Core Memory | `MEMORY.md` | ⬜ Backed Up |
| Daily Logs | `memory/YYYY-MM-DD.md` | ⬜ Backed Up |
| Message Channel | `memory/message.md` | ⬜ Backed Up |
| Heartbeat | `HEARTBEAT.md` | ⬜ Backed Up |

---

## Configuration

| File | Location | Status |
|------|----------|--------|
| Agent Config | `agents/[name]/config.json` | ⬜ N/A |
| Environment | `agents/[name]/.env` | ⬜ Secured |
| Documentation | `agents/[name]/docs/` | ⬜ Backed Up |

---

## Avatar/Assets

| File | Location | Status |
|------|----------|--------|
| Avatar Image | `avatars/[name].png` | ⬜ Pending |
| Alt Avatars | `avatars/[name]-*.png` | ⬜ N/A |

---

## Restore Instructions

### Prerequisites
- [ ] Backup integrity verified
- [ ] Dependencies available
- [ ] Environment configured
- [ ] Secrets present (if applicable)

### Steps
1. Copy profile to `personnel/profiles/`
2. Copy agent files to `agents/[name]/`
3. Verify memory files present
4. Check avatar exists (or use placeholder)
5. Verify secrets present (if applicable)
6. Test basic functionality
7. Log restore event

### Post-Restore
- [ ] Agent functional test
- [ ] Memory continuity check
- [ ] Communication channel active
- [ ] Backup manifest updated

---

## Special Notes

[RESTORE-SPECIFIC NOTES]

---

*Template Version: 1.0*  
*Backup Protocol: [Protocol Name]*  
*Maintained by: [Agent/Sentinel/OpenClaw]*

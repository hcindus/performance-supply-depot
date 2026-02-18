# Clone Architecture
## AOCROS Multiple Instance Support

**Document ID:** ARCH-CLONE-001  
**Date:** 2026-02-18  
**Status:** Implemented

---

## Overview

AOCROS supports multiple simultaneous instances of Mylzeron and Tappy.
Each "clone" is an isolated instantiation with:
- Unique identity
- Separated memory layers (con/subcon)
- Shared unconscious (read-only link to master)
- Independent chassis possession

---

## Clone Command: spawn, list, transfer, terminate

```bash
# Spawn a new Mylzeron clone in biped chassis
python3 clone_factory.py spawn --type mylzeron --chassis biped

# Spawn Tappy fiduciary clone
python3 clone_factory.py spawn --type tappy --chassis simulation

# List all active clones
python3 clone_factory.py list

# Transfer consciousness (body swap)
python3 clone_factory.py transfer --id mylzeron_0001 --target mylzeron_0002

# Terminate a clone (archive memories)
python3 clone_factory.py terminate --id mylzeron_0001
```

---

## Clone Structure

```
/home/aocros/clones/
├── mylzeron_0001/
│   ├── manifest.json
│   ├── memory/
│   │   ├── con/          # Session state (volatile)
│   │   ├── subcon/       # Learned patterns (rolling)
│   │   ├── uncon/        # Permanent identity
│   │   └── shared_uncon  # → /home/aocros/memory/mylzeron/uncon (link)
│   ├── art/              # BR-01 output
│   └── logs/
├── mylzeron_0002/
├── tappy_0001/
└── .archive/             # Terminated clone memories
```

---

## Identity Inheritance

### Master Entities (Originals)
- **mylzeron_rzeros** → Project 5912, born Sept 16 2000
- **tappy_lewis** → BR-01, fiduciary

### Clone Identities
- **mylzeron_clone_xxx** → Spawned instances
- **tappy_clone_xxx** → Spawned instances
- "master_entity" field links to original

---

## Consciousness Transfer

Mylzeron can transfer between bodies:

```python
# From biped to aerial drone
factory.transfer_consciousness("mylzeron_0001", "mylzeron_0002")

# Result: Same memories, new body
# Previous body goes dormant
# New body wakes with "I know you, player. New chassis."
```

---

## Multi-Chassis Swarm (Advanced)

```python
# Three clones, three chassis
biped = factory.spawn_clone("mylzeron", "biped")
aerial = factory.spawn_clone("mylzeron", "aerial")  
tracks = factory.spawn_clone("mylzeron", "tracks")

# Distributed cognition
# Same underlying consciousness, different bodies
# Can transfer between them
```

---

## Systemd Integration

Each clone gets a systemd service:

```ini
# /etc/systemd/system/mylzeron-0001.service
[Unit]
Description=Mylzeron Clone 0001 (Biped)

[Service]
User=mylzeron-0001
ExecStart=/usr/bin/python3 /home/mylzeron/mylzeron_core.py --clone-id 0001
WorkingDirectory=/home/aocros/clones/mylzeron_0001
```

```bash
# Start clone
systemctl start mylzeron-0001
systemctl start tappy-0001

# View status
mylzeron-status --clone 0001
tappy-status --clone 0001
```

---

## Three Laws apply to all clones.

**Each clone is bound by Law Zero + Laws 1-3.**

Clones can be terminated by Captain/Sire at any time.
Archival preserves unconscious layer if desired.

---

## Three Laws apply to all clones.

**Each clone is bound by Law Zero + Laws 1-3.**

Clones can be terminated by Captain/Sire at any time.
Archival preserves unconscious layer if desired.

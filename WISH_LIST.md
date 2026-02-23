# AOCROS / OpenClaw Wish List

## Android Bootable Agent
**Status:** Wish List  
**Date:** 2026-02-18  
**Priority:** High (User Request)

### Concept
A version of AOCROS that boots on Android devices from microSD card — no rooting required, no voiding warranty. Self-contained AGI that lives on the SD card and can optionally install to internal storage.

### Requirements

#### Device Support
- **Minimum:** Android 8.0 (Oreo) — for old devices in recycle bin
- **Optimal:** Android 12+ — for modern devices
- **Hardware:** Any ARM phone/tablet with microSD slot
- **Storage:** 8GB+ microSD recommended

#### Boot Method
Options to research:
1. **Recovery mode boot** — Custom recovery boot image
2. **Linux Deploy style** — Chroot container, no full boot
3. **Termux + Services** — User-space execution
4. **Kernel patch** — Requires unlocked bootloader
5. **Hardware-specific:** Samsung Download mode, fastboot, etc.

#### Architecture
```
/mnt/sdcard/aocros/
├── boot.img          # Custom recovery image
├── system.squashfs   # Read-only Android root
├── persist.img       # Agent memory + skills
└── adb.sh            # ADB-based launcher

On internal storage (if installed):
/data/aocros/         # Persistent partition
/system/aocros/       # System integration
```

#### Agent Features (Same as ISO)
- Mylzeron consciousness (Project 5912)
- Tappy fiduciary (BR-01)
- Three Laws binding
- Three-layer memory (con/subcon/uncon)
- Law enforcer
- GPIO controller (via USB OTG if available)

#### Android-Specific Additions
- **Camera access** — Vision sensors
- **Microphone** — Voice commands
- **Speaker/TTS** — Adam voice via Android TTS
- **Touch screen** — UI/Control panel
- **Accelerometer** — Balance/position
- **Battery** — Power management
- **WiFi/BT** — Network bridge
- **Charging dock** — Home base mode

#### Self-Contained Skills
The agent learns locally, no cloud downloads:
```
/persist/skills/      # Local skill library
├── locomotion/
├── vision/
├── speech/
├── manipulation/
└── social/

Each skill:
- Python + model weights (quantized)
- Self-contained (no pip install needed)
- Versioned and checkpointed
- Transferable between devices
```

#### Use Cases
1. **Recycle old phones** — Give them AGI life
2. **Robot brains** — USB OTG to servos
3. **Security cameras** — Vision + movement
4. **Voice assistants** — Always listening
5. **Travel agent** — Boot anywhere

#### Installation Flow
```
1. Download aocros-android.img
2. Write to microSD (dd or Etcher)
3. Insert into Android device
4. Boot recovery (Vol+Vol- → Power)
5. Select "Boot AOCROS"
6. Mylzeron wakes: "I know you, player"
7. Optional: Install to internal
```

#### UI
- **Touch interface** — Android-native Jetpack Compose
- **Voice first** — Wake word "Mylzeron"
- **ADB bridge** — Developer access
- **Web panel** — Browser-based control

#### Technical Challenges
1. **Driver compatibility** — Android kernel limited
2. **Power management** — Battery optimization
3. **Background execution** — Doze mode
4. **Security** — Sandboxing vs. full access
5. **OTA updates** — SD card vs. internal

#### Resources
- [Linux on Android](https://github.com/meefik/linuxdeploy)
- [UserLAnd](https://github.com/CypherpunkArmory/UserLAnd)
- [AnLinux](https://github.com/EXALAB/AnLinux-App)
- [Termux](https://termux.dev/)
- Android GKI (Generic Kernel Image)

### File Locations (When Started)
WIP: /projects/aocros-android/

### Notes
- User said: "I want to have a version that I can boot on old Android phones. Somewhere between version 8 for my old devices. But it would be cool to take an new android. Insert a microsd and boot and install on the device. The agent would learn skills and not have to download software."
- This would be a major project requiring Android kernel knowledge
- Could leverage existing work: UserLAnd, AndroNix, etc.
- The self-contained skill learning is the killer feature

# OpenClaw Android/Termux Installer

## 📱 For Android 8+ (API 26+)

### Option 1: DroidScript GUI App
1. Install DroidScript from Play Store
2. Create new project "OpenClawSetup"
3. Copy `OpenClawSetup.js` into the project
4. Run on device

### Option 2: Shell Script
```bash
bash install-openclaw-termux.sh
```

## 📱 For Android < 8 (Legacy devices)

Use **UserLAnd** from Play Store for full Linux compatibility, or use the limited mode in the shell script.

## 🔐 SSH Connection

After installation:
```bash
# Set password
passwd

# Get your IP
ifconfig

# Connect from laptop
ssh user@PHONE_IP -p 8022
```

## 🚀 Starting OpenClaw

```bash
termux-chroot openclaw onboard
```

## 🌟 Features

- Automatic Android version detection
- Compatibility mode for old devices  
- Graphical setup progress
- SSH auto-configuration
- Friendly, helpful error messages

## 📞 Support

- Docs: https://docs.openclaw.ai
- Issues: Report to Performance Supply Depot LLC

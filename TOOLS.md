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

### Voice / TTS

**TTS Service:** `/root/.openclaw/workspace/voice/tts-service.js`
- **Port:** 3847
- **Engines:** espeak ✅ | piper ⚠️ | elevenlabs ⚠️

**Usage:**
```bash
# CLI mode
node voice/tts-service.js --engine espeak --text "Hello"

# Server mode (HTTP API)
node voice/tts-service.js --server
# GET /speak?engine=espeak&text=Hello
```

**Available:**
- **espeak:** ✅ Working (free, 168KB file)
- **piper:** ⚠️ Binary installed, need to download voices
- **elevenlabs:** ⚠️ Requires API key (set ELEVENLABS_API_KEY env)

**Voices (espeak):**
- `en-us` - US English (default)
- `en-gb` - British English
- `scottish` - Scottish accent

**Voices (piper):** Need to download .onnx models
**Voices (elevenlabs):** adam, rachel, sam, mortimer, miles, mylthrees, claie (voice IDs stored, API key pending)

---

### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

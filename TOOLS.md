# Voice / TTS

**TTS Service:** `/root/.openclaw/workspace/voice/tts-service.js`
- **Port:** 3847
- **Engines:** espeak ✅ | piper ⚠️ | elevenlabs ✅

**ElevenLabs API Keys:** (stored in tts-service.js)
- Primary: `sk_eef98e585c917b80eece529f4d17c686d8f0c70f0ff34a9f`
- Backup: `sk_71fa3fc052c60ff7f8bcf524713ed155d4eef31c359ac8eb

**Twilio:**
- Phone: `+18557899606`
- Credentials: Store as `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` env vars

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
- **elevenlabs:** ✅ Working (free tier: eleven_flash_v2_5)

**Voices (espeak):**
- `en-us` - US English (default)
- `en-gb` - British English
- `scottish` - Scottish accent

**Voices (piper):** Need to download .onnx models
**Voices (elevenlabs):**
- mortimer, miles, mylthrees, claie (custom)
- adam, rachel, sam (standard)

**GM/Pi Voice Settings** (applied to all voices):
| Parameter | Value | Source |
|-----------|-------|--------|
| Pitch | 1.618 | GM |
| Rate | 1.94 | PI/GM |
| Style | 1.618 | GM |
| Stability | 0.618 | 1/GM |
| Similarity | 0.618 | 1/GM |

*Note: elevenlabs style/speed capped at 0-1 range*

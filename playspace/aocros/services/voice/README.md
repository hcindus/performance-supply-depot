# AOCROS Voice Integration
## Multi-Voice TTS System for Agents

---

## Available Voices (6 Total - All Free Tier Verified)

### Male Voices (3)
| ID | Voice | Persona | 
|----|-------|---------|
| `pNInz6obpgDQGcFmaJgB` | Adam | Professional, deep, clear |
| `pNInz6obpgDQGcFmaJgB` | Scottish Engineer | Warm, technical |
| `pNInz6obpgDQGcFmaJgB` | Captain | Authoritative |

### Female Voices (3)
| ID | Voice | Persona | 
|----|-------|---------|
| `hpp4J3VqNfWAUOO0d1Us` | Bella | Professional, bright, warm |
| `EXAVITQu4vr4xnSDxMaL` | Sarah | Mature, reassuring, confident |
| `cgSgspJ2msm6clMCkdW9` | Jessica | Playful, bright, warm |

---

## Configuration

### Environment Variables
```bash
# Primary API Key
ELEVENLABS_API_KEY=your_api_key

# Voice Selection (change per agent)
VOICE_ID=50BdVlngDYeoh9pVuQof  # Default: Scottish Engineer
```

### Per-Agent Voice Setting
Each agent can set their preferred voice by setting the `VOICE_ID` environment variable or by calling the voice service.

---

## Usage

### Python Integration
```python
from aocros_voice import speak, set_voice

# Set voice for this agent
set_voice("rachel")  # Female
# or
set_voice("adam")     # Male

# Speak text
speak("Hello, I am your AI assistant.")
```

### CLI Usage
```bash
# Speak with default voice
python -m aocros_voice speak "Hello world"

# Speak with specific voice
python -m aocros_voice speak --voice rachel "Hello world"

# List available voices
python -m aocros_voice list
```

---

## Voice Selection by Agent

| Agent | Recommended Voice |
|-------|------------------|
| MILES | Scottish Engineer (50BdVlngDYeoh9pVuQof) |
| QORA | Rachel (rachel) |
| SPINDLE | Adam (adam) |
| LEDGER-9 | Scottish Engineer |
| SENTINEL | Reserve (krsfpqv6ExDAAyh8Ea6y) |
| HUME | Rachel (rachel) |
| PULP | Adam (adam) |
| VELUM | Rachel (rachel) |
| Default | Any (user preference) |

---

## API Reference

### set_voice(voice_id: str)
Set the active voice for TTS.

**Parameters:**
- `voice_id` - One of: `50BdVlngDYeoh9pVuQof`, `AA30ZfOdY16oVkASrrGJ`, `krsfpqv6ExDAAyh8Ea6y`, `ztnpYzQJyWffPj1VC5Uw`, `adam`, `rachel`

### speak(text: str, voice_id: str = None)
Convert text to speech and play.

**Parameters:**
- `text` - Text to speak
- `voice_id` - Optional voice override

### get_available_voices()
Return list of all available voices.

---

## Integration Status

- [x] Voice config defined (6 voices)
- [x] Python module structure
- [x] Agent voice selection ready
- [ ] ElevenLabs API key needed for production

---

*AOCROS Voice System v1.0*

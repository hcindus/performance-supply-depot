# AGI Company Voice Settings

## GM/Pi Aesthetic Constants

All voices use these modulation values:

| Parameter | Value | Source |
|-----------|-------|--------|
| Pitch | 1.618 | GM (Golden Ratio) |
| Rate | 1.94 | PI / GM |
| Style | 0.8 | Capped for API |
| Stability | 0.618 | 1/GM |
| Similarity Boost | 0.618 | 1/GM |

---

## Voice IDs

### Our Team Voice Assignments

| Agent | Voice ID | Gender | Status | Notes |
|-------|----------|--------|--------|-------|
| **Miles** | `krsfpqv6ExDAAyh8Ea6y` | Male | ✅ Default | Default male voice |
| **Mortimer** | `ztnpYzQJyWffPj1VC5Uw` | Male | ✅ Reserved | Mortimer's personal voice |
| **Mylthrees** | `AA30ZfOdY16oVkASrrGJ` | Female | ✅ Reserved | Mylthrees' personal voice |
| **Claire** | `50BdVlngDYeoh9pVuQof` | Female | ✅ Default | Default female voice for deployment |

### Available for Team Selection
| Voice ID | Name | Gender |
|----------|------|--------|
| `pNInz6obpgDQGcFmaJgB` | Adam | Male |
| `21m00Tcm4TlvDq8ikWAM` | Rachel | Female |
| `ODqDArmn3iD25GAF5W2S` | Sam | Male |

---

## Deployment Voice Policy

### Default Voices for New AGIs
- **Male deployment:** Use Miles voice (`krsfpqv6ExDAAyh8Ea6y`)
- **Female deployment:** Use Claire voice (`50BdVlngDYeoh9pVuQof`)

### Voice Selection Rules
1. Mortimer keeps his voice
2. Mylthrees keeps her voice
3. Any new agent can select from available voices
4. Deployed AGIs default to Miles (male) or Claire (female)

---

## Integration

#### API Keys
```
# Primary
sk_eef98e585c917b80eece529f4d17c686d8f0c70f0ff34a9f

# Backup
sk_71fa3fc052c60ff7f8bcf524713ed155d4eef31c359ac8eb
```

### Model
```
eleven_flash_v2_5 (free tier compatible)
```

### TTS Service
```bash
# Use default male voice
node voice/tts-service.js --engine elevenlabs --voice miles --text "Hello"

# Use default female voice
node voice/tts-service.js --engine elevenlabs --voice claie --text "Hello"

# Use specific voice
node voice/tts-service.js --engine elevenlabs --voice mortimer --text "Hello"
```

---

*Last updated: 2026-02-20*
*Policy set by Captain*

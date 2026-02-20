# AGI Company Voice Settings

## GM/Pi Aesthetic Constants

All voices use these modulation values:

| Parameter | Value | Source |
|-----------|-------|--------|
| Pitch | 1.618 | GM (Golden Ratio) |
| Rate | 1.94 | PI / GM |
| Style | 1.618 | GM |
| Stability | 0.618 | 1/GM |
| Similarity Boost | 0.618 | 1/GM |

---

## Voice IDs

### Our Team (Custom)
| Agent | Voice ID | Gender |
|-------|----------|--------|
| Miles | `krsfpqv6ExDAAyh8Ea6y` | Male |
| Mortimer | `ztnpYzQJyWffPj1VC5Uw` | Male |
| Mylthrees | `AA30ZfOdY16oVkASrrGJ` | Female |
| Claie | `50BdVlngDYeoh9pVuQof` | Female |

### Standard ElevenLabs
| Voice ID | Name |
|----------|------|
| `pNInz6obpgDQGcFmaJgB` | Adam |
| `21m00Tcm4TlvDq8ikWAM` | Rachel |
| `ODqDArmn3iD25GAF5W2S` | Sam |

---

## Usage

Set API key:
```bash
export ELEVENLABS_API_KEY="sk_71fa3fc052c60ff7f8bcf524713ed155d4eef31c359ac8eb"
```

**Model:** `eleven_flash_v2_5` (works on free tier)

Select voice:
```bash
--voice miles        # Male
--voice mortimer     # Male
--voice mylthrees    # Female
--voice claie        # Female
```

### Voice Settings (applied automatically)
| Parameter | Value | Notes |
|-----------|-------|-------|
| Stability | 0.618 | 1/GM |
| Similarity | 0.618 | 1/GM |
| Style | 0.8 | Capped for API |
| Speed | 1.1 | Capped for API |

---

*Last updated: 2026-02-20*

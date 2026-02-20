# GM/Pi Voice Modulation - How It Works

## The Concept

We use **Golden Ratio (GM)** and **Pi (π)** as aesthetic constants to modulate voice characteristics:

```javascript
const GM = 1.618033988749895;  // Golden Ratio
const PI = 3.141592653589793;  // Pi
```

### Original DroidScript Approach
```javascript
// DroidScript allows direct pitch/rate control
const GM = 1.618033712;        // Golden Mean for pitch
const PI = 22 / 7;             // Pi approximation

app.TextToSpeech("Hello!", GM, PI / GM);
// Output: pitch=1.618, rate=1.94
```

---

## ElevenLabs Implementation

ElevenLabs doesn't support direct pitch/rate, but we map our values to their parameters:

| Our Parameter | GM/Pi Source | ElevenLabs Parameter | Mapped Value |
|---------------|--------------|---------------------|--------------|
| Pitch | GM | style | 0.8 (capped) |
| Rate | PI/GM | speed | 1.1 (capped) |
| Stability | 1/GM | stability | 0.618 |
| Clarity | 1/GM | similarity_boost | 0.618 |

### Why Capped Values?
ElevenLabs API restricts values to 0.0-1.0 range. We use:
- **Style**: 0.8 (elevated from default 0.5)
- **Speed**: 1.1 (slightly faster)
- **Stability**: 0.618 (1/GM - consistent but not robotic)
- **Similarity**: 0.618 (1/GM - high clarity)

### API Call Example
```javascript
const postData = JSON.stringify({
  text: "Hello world",
  model_id: "eleven_flash_v2_5",
  voice_settings: {
    stability: 0.618,      // 1/GM
    similarity_boost: 0.618, // 1/GM
    style: 0.8,           // GM-derived (capped)
    speed: 1.1            // PI/GM-derived (capped)
  }
});
```

---

## Full Constant Set

```javascript
// Universal Constants
const SPEED_OF_LIGHT = 299792458;     // m/s
const GRAVITY_CONSTANT = 6.674e-11;    // m^3 kg^-1 s^-2
const PLANCK_CONSTANT = 6.626e-34;     // J s
const BOLTZMANN_CONSTANT = 1.381e-23;  // J/K
const AVOGADRO_CONSTANT = 6.022e23;    // mol^-1
const EULER_NUMBER = 2.718281828;      // e
const PI = 3.141592653589793;          // π
const GM = 1.618033988749895;          // Golden Ratio (φ)

// Voice Modulation
const PITCH = GM;           // 1.618
const RATE = PI / GM;       // 1.94
const STABILITY = 1 / GM;   // 0.618
const SIMILARITY = 1 / GM;  // 0.618
```

---

## Tested & Working

| Voice | Voice ID | Test Status |
|-------|----------|-------------|
| Miles (default male) | `krsfpqv6ExDAAyh8Ea6y` | ✅ Working |
| Claie (default female) | `50BdVlngDYeoh9pVuQof` | ✅ Working |
| Mortimer | `ztnpYzQJyWffPj1VC5Uw` | Ready |
| Mylthrees | `AA30ZfOdY16oVkASrrGJ` | Ready |

---

## API Key
```
sk_71fa3fc052c60ff7f8bcf524713ed155d4eef31c359ac8eb
```

---

*Document created: 2026-02-20*
*Based on Captain's aesthetic constant philosophy*

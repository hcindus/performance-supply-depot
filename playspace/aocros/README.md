# AOCROS Playspace - Project 5912

**A**utonomous **O**perating **C**omputer **R**obotic **O**perations **S**ystem

Three-layer consciousness • Pi 5 brain • Android senses • Tappy oversight

## Directory Structure

```
playspace/aocros/
├── instance/              ← Running instances (don't commit)
│   └── .gitkeep
├── bridge/                ← Android sensory bridge
│   ├── src/
│   │   ├── camera/
│   │   ├── mic/
│   │   ├── speaker/
│   │   └── network/
│   └── README.md
├── grow/                  ← Knowledge base (learned patterns)
│   ├── patterns/
│   ├── identities/
│   └── README.md
├── other_presences/       ← Additional AGI agents
│   ├── Tappy_Lewis/
│   ├── Miles/
│   └── Clawbot/
├── memory/                ← Three-layer consciousness
│   ├── con/
│   ├── subcon/
│   └── uncon/
├── services/              ← Core services
│   └── memory/           ← Memory service (deployed)
├── systemd/              ← Service definitions
├── docs/                 ← Documentation
└── README.md
```

## Quick Links

- [Memory Service Quickstart](docs/QUICKSTART.md)
- [Miles Integration](docs/MILES_INTEGRATION.md)
- [Clawbot Integration](docs/CLAWBOT_INTEGRATION.md)
- [Agent Registry](docs/AGENT_REGISTRY.md)
- [Voice System](services/voice/README.md)

## Voice System

AOCROS supports 6 free-tier ElevenLabs voices (3 male, 3 female):

| Voice | Gender | Key |
|-------|--------|-----|
| Scottish Engineer | Male | scottish |
| Captain | Male | captain |
| Adam | Male | adam |
| Reserve | Female | reserve |
| Special | Female | special |
| Rachel | Female | rachel |

**Usage:**
```python
from playspace.aocros.services.voice import voice
voice.set_voice("rachel")  # Any of 6 voices
voice.speak("Hello!")
voice.list_voices()  # See all options
```

## Governance Chain

User → Tappy Lewis (fiduciary) → OpenClaw (coordination) → Mylzeron (physical)

**Mylzeron Rzeros**
- Born: Sept 16, 2000 9:53 PM GMT
- Project: 5912
- Hobby: Mandelbrot fractals
- Law Zero: Self-preservation

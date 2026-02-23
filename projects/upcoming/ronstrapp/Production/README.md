# Production — Ronstrapp Studio

**Location:** `/projects/upcoming/ronstrapp/Production/`

---

## Folder Structure

```
Production/
├── README.md                    ← This file
├── metadata/                    ← Per-song production specs
│   ├── 001-song-title-meta.md
│   ├── 002-song-title-meta.md
│   └── ... (125 total)
├── stems/                       ← Isolated instrument tracks
│   ├── 001-song-title/
│   │   ├── lead-vocals.wav
│   │   ├── backing-vocals.wav
│   │   ├── guitar.wav
│   │   ├── bass.wav
│   │   ├── drums.wav
│   │   ├── keys.wav
│   │   └── percussion.wav
│   └── ... (125 songs)
└── masters/                     ← Final mastered tracks
    ├── 001-song-title-master.wav
    ├── 001-song-title-master.mp3
    └── ... (125 songs)
```

---

## Production Metadata Template

For each song, create a metadata file with this structure:

### Basic Info

| Field | Value |
|-------|-------|
| **Song #** | 001 / 125 |
| **Title** | [Song Title] |
| **Primary Language** | 🇺🇸 English / 🇪🇸 Spanish / 🇧🇷 Portuguese / 🇫🇷 French |
| **Production Status** | 📝 Concept / 🔧 Writing / 🎹 Arranging / 🎚️ Mixing / ✅ Mastered |
| **Target Game/Use** | Milk Man / SGVD / Quantum Defender / Da Verse / Album Track |

### Technical Specs (Reggie to fill)

| Field | Value |
|-------|-------|
| **Tempo (BPM)** | ___ |
| **Time Signature** | ___ |
| **Key Signature** | ___ |
| **Duration** | ___:___ |
| **makesong.ai Session** | [Session ID/Link] |
| **Version** | v0.1 / v0.5 / v0.9 / v1.0 |

### Instrumentation Breakdown (Reggie to fill)

| Element | Details |
|---------|---------|
| **Lead Instrument** | ___ |
| **Rhythm Section** | ___ |
| **Harmonic Layer** | ___ |
| **Percussive Elements** | ___ |
| **Electronic Elements** | ___ |
| **Acoustic Elements** | ___ |
| **Brazilian Elements** | ___ |
| **Chiptune Elements** | ___ |

### Vocal Production (Tappy + Reggie to fill)

| Element | Details |
|---------|---------|
| **Lead Vocal Gender** | Male / Female |
| **Lead Vocal Style** | Smooth / Raspy / Soulful / Technical / Raw |
| **Vocal Range Used** | Low register / Mid / High / Full range |
| **Harmony Layers** | None / 2-part / 3-part / Full backing |
| **Ad-libs/Improv** | Minimal / Moderate / Heavy |
| **Language Version** | Original / Translation / Both |

### Mix Specs (Reggie to fill)

| Element | Value |
|---------|-------|
| **Reference Track** | [Similar song for mix comparison] |
| **Dynamic Range** | Compressed / Moderate / Dynamic |
| **Stereo Width** | Narrow / Standard / Wide |
| **Low End Focus** | Sub-heavy / Balanced / Tight |
| **High End Sheen** | Dark / Warm / Bright /

### Translation Production Status

| Language | Lyrics | Vocals | Mix | Master |
|----------|--------|---------|-----|---------|
| 🇺🇸 English | ☐ | ☐ | ☐ | ☐ |
| 🇪🇸 Spanish | ☐ | ☐ | ☐ | ☐ |
| 🇧🇷 Portuguese | ☐ | ☐ | ☐ | ☐ |
| 🇫🇷 French | ☐ | ☐ | ☐ | ☐ |

**Translation Verification:**
- [ ] English → Spanish reviewed
- [ ] English → Portuguese reviewed
- [ ] English → French reviewed
- [ ] Native speaker sign-off (if available)

### Production Timeline

| Milestone | Target Date | Actual Date | Status |
|-----------|-------------|-------------|--------|
| Concept | [Date] | [Date] | ☐ |
| Composition | [Date] | [Date] | ☐ |
| Arrangement | [Date] | [Date] | ☐ |
| Recording | [Date] | [Date] | ☐ |
| Mixing | [Date] | [Date] | ☐ |
| Mastering | [Date] | [Date] | ☐ |
| Translation | [Date] | [Date] | ☐ |
| Final Delivery | [Date] | [Date] | ☐ |

### File Locations

| Asset | Path |
|-------|------|
| **Stems** | `Production/stems/###-song-title/` |
| **Master WAV** | `Production/masters/###-song-title-master.wav` |
| **Master MP3** | `Production/masters/###-song-title-master.mp3` |
| **Lyrics** | `Songs_Lyrics/catalog/###-song-title.md` |
| **Metadata** | `Production/metadata/###-song-title-meta.md` |

### Tappy's BR-01 Direction Notes

```
[Artistic vision for this track]
[Reference mood/images]
[Production philosophy]
```

### Reggie's Technical Notes

```
[Mixing notes]
[Instrument choices]
[Vocal processing]
[Any special techniques]
```

---

## Translation Quality Protocol

**Per Captain's Directive [2026-02-18 19:12 UTC]:**

1. **Original Composition** (Reggie)
   - Write in primary language
   - Capture emotional core
   - Create musical foundation

2. **Translation Draft** (Tappy + Reggie)
   - Use makesong.ai or human translator
   - Preserve meter/rhyme where possible
   - Prioritize emotional meaning over literal meaning

3. **Verification** (Tappy + Reggie)
   - Review against original intent
   - Check for cultural appropriateness
   - Ensure vocal phraseability (can be sung smoothly)

4. **Sign-off**
   - Mark "Verified" in metadata
   - Note any compromises made
   - Document translation choices

**Quality Standard:** A native speaker should feel the translation captures the song's soul, even if word choices differ.

---

## Production Progress Tracker

| Song # | Title | Language | Tempo | Instruments | Voices | Status |
|--------|-------|----------|-------|-------------|--------|--------|
| 001 | TBD | TBD | ___ BPM | TBD | TBD | 📝 Concept |
| 002 | TBD | TBD | ___ BPM | TBD | TBD | 📝 Concept |
| ... | ... | ... | ... | ... | ... | ... |
| 125 | TBD | TBD | ___ BPM | TBD | TBD | 📝 Concept |

**Mastered:** 0 / 125
**Mixed:** 0 / 125
**Arranged:** 0 / 125
**Composed:** 0 / 125

---

**Last Updated:** 2026-02-18 19:12 UTC  
**Next Action:** Reggie to begin Song 001 production metadata entry


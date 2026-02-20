# Songs & Lyrics — Ronstrapp Catalog

**Location:** `/projects/upcoming/ronstrapp/Songs_Lyrics/`

---

## Catalog Structure

```
Songs_Lyrics/
├── README.md                    ← This file
├── catalog/                     ← 125 song entries
│   ├── 001-song-title.md
│   ├── 002-song-title.md
│   └── ... (125 total)
└── translations/                ← Multilingual versions
    ├── english/
    ├── spanish/
    ├── portuguese/
    └── french/
```

---

## Song Catalog Entry Template

Each song should have a file with this structure:

### Song Metadata

| Field | Value |
|-------|-------|
| **Song #** | 001 / 125 |
| **Title** | [Song Title] |
| **Working Title** | [If different] |
| **Primary Language** | 🇺🇸 English / 🇪🇸 Spanish / 🇧🇷 Portuguese / 🇫🇷 French |
| **Secondary Languages** | [Translation versions available] |
| **Status** | 📝 Concept / 🎹 In Production / ✅ Complete |

### Musical Specs (Tappy + Reggie to fill)

| Field | Value |
|-------|-------|
| **Tempo** | ___ BPM |
| **Time Signature** | 4/4 / 3/4 / 6/8 / Other |
| **Key** | C Major / A Minor / etc. |
| **Genre** | Ballad / Rock / Pop / Bossa / Fusion |
| **Mood** | Uplifting / Melancholy / Energetic / Chill |

### Instrumentation (Reggie to fill)

| Instrument | Status |
|------------|--------|
| **Lead Vocals** | ☐ |
| **Backing Vocals** | ☐ |
| **Guitar** | ☐ Acoustic / ☐ Electric / ☐ Both |
| **Bass** | ☐ Synth / ☐ Upright / ☐ Electric |
| **Drums** | ☐ Acoustic / ☐ Electronic / ☐ Hybrid |
| **Keys/Synth** | ☐ Piano / ☐ Synth / ☐ Organ |
| **Percussion** | ☐ Brazilian / ☐ Latin / ☐ Electronic |
| **Other** | _____________ |

### Voice Details (Tappy + Reggie to fill)

| Field | Value |
|-------|-------|
| **Lead Vocal Style** | Male / Female / Androgynous |
| **Vocal Range** | Ballad (soft) / Rock (powerful) / Mixed |
| **Vocal Character** | Smooth / Raspy / Soulful / Technical |
| **Harmonies** | None / Simple / Complex |
| **Backup Vocals** | None / Minimal / Full choir |

### Language Versions

| Language | Title Translation | Status |
|----------|-----------------|--------|
| 🇺🇸 English | [Title] | ☐ Original / ☐ Translation |
| 🇪🇸 Spanish | [Título] | ☐ Verified / ☐ Needs Review |
| 🇧🇷 Portuguese | [Título] | ☐ Verified / ☐ Needs Review |
| 🇫🇷 French | [Titre] | ☐ Verified / ☐ Needs Review |

**Translation Verified By:** ____________

### Production Status (Reggie to fill)

| Field | Value |
|-------|-------|
| **makesong.ai Session** | [Link/ID] |
| **Current Version** | v0.1 / v0.5 / v1.0 |
| **Stems Available** | ☐ |
| **Master Available** | ☐ |
| **MP3 Location** | `assets/audio/tracks/###-title.mp3` |
| **Lyrics Location** | `Songs_Lyrics/translations/[language]/###-title.md` |
| **Production Notes** | [Reggie's technical notes] |
| **Tappy's BR-01 Notes** | [Artistic direction notes] |

### Assignment

| Field | Value |
|-------|-------|
| **Game/Project** | Milk Man / SGVD / Quantum Defender / Da Verse / Album |
| **Scene/Context** | [Where this plays] |
| **Band Member Lead** | [Which of 5 members performs this] |

### Lyrics

```
[Insert lyrics in primary language]

[Chorus]
...

[Verse 2]
...
```

---

## Catalog Progress Tracker

| Song # | Title | Language | Status | Assigned Game |
|--------|-------|----------|--------|---------------|
| 001 | TBD | TBD | 📝 Concept | TBD |
| 002 | TBD | TBD | 📝 Concept | TBD |
| ... | ... | ... | ... | ... |
| 125 | TBD | TBD | 📝 Concept | TBD |

**Completed:** 0 / 125
**In Production:** 0 / 125
**Concept Phase:** 125 / 125

---

## Translation Verification Protocol

**For each of 4 languages:**

1. **Original lyrics** written in primary language
2. **Translation draft** created by makesong.ai / human
3. **Native speaker review** (if available)
4. **Tappy + Reggie approval** (artistic fit)
5. **Final verification** marked in catalog entry

**Quality Standard:** Translations should preserve emotional impact, not just literal meaning.

---

## File Naming Convention

```
Songs_Lyrics/catalog/
├── 001-song-title.md
├── 002-another-song.md
└── 125-final-song.md

Songs_Lyrics/translations/english/
├── 001-song-title.md
└── ...

Songs_Lyrics/translations/spanish/
├── 001-titulo-cancion.md
└── ...

[Same for portuguese/ and french/]
```

---

**Last Updated:** 2026-02-18 19:12 UTC
**Next Action:** Tappy + Reggie to begin Song 001 entry with full metadata


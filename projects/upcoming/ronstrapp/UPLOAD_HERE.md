# 📁 Ronstrapp Upload Directory

**Welcome, Captain.** This is the drop zone for all Ronstrapp creative assets.

---

## 🎨 Artwork Uploads

### Band Member Portraits & Avatars
```
assets/artwork/band-portraits/
├── member-01/          ← Member 1 refs, sketches, finals + avatar candidates
├── member-02/          ← Member 2 refs, sketches, finals + avatar candidates
├── member-03/          ← Member 3 refs, sketches, finals + avatar candidates
├── member-04/          ← Member 4 refs, sketches, finals + avatar candidates
└── member-05/          ← Member 5 refs, sketches, finals + avatar candidates
```

**Avatar Upload Process:**
1. Captain uploads multiple avatar options for each member
2. Tappy + team review and select final avatar
3. Selected avatar becomes official profile image

### Album & Promotional
```
assets/artwork/album-covers/     ← Album cover concepts
assets/artwork/promotional/      ← Posters, social graphics
assets/artwork/concept-sketches/ ← Mood boards, WIP ideas
```

### Sprites (if doing pixel art style)
```
assets/sprites/
├── idle/              ← Standing poses
├── performing/        ← Playing instruments
└── expressions/       ← Emotional states
```

---

## 🎵 Music Uploads

### Full Tracks
```
assets/audio/tracks/     ← Final songs (.mp3, .wav, .ogg)
```

### Stems & Isolated Instruments
```
assets/audio/stems/      ← Separated tracks for mixing
```

### Sound Effects
```
assets/audio/sfx/        ← Ronstrapp jingles, stings
```

---

## 📝 Documentation Uploads

### Band Member Specs
Fill out these templates:
- `band-members/member-01-profile.md`
- `band-members/member-02-profile.md`
- `band-members/member-03-profile.md`
- `band-members/member-04-profile.md`
- `band-members/member-05-profile.md` (optional)

### Lyrics
```
scripts/lyrics/          ← Song lyrics in .md files
```

### Story/Bios
```
scripts/origin-story.md  ← How Ronstrapp formed
scripts/dialogue/        ← Band banter, interviews
```

---

## 📋 Quick Upload Commands

**If using SCP/SFTP:**
```bash
# Band portrait references
scp *.jpg user@host:/root/.openclaw/workspace/projects/upcoming/ronstrapp/assets/artwork/band-portraits/member-01/

# Full tracks
scp *.mp3 user@host:/root/.openclaw/workspace/projects/upcoming/ronstrapp/assets/audio/tracks/
```

**If using Git:**
```bash
cd /root/.openclaw/workspace/projects/upcoming/ronstrapp
git add assets/ band-members/
git commit -m "feat: Ronstrapp band artwork and member profiles"
git push
```

---

## ✅ Upload Checklist

**Band Members (4-5):**
- [ ] Member 1 — Profile filled + artwork uploaded
- [ ] Member 2 — Profile filled + artwork uploaded
- [ ] Member 3 — Profile filled + artwork uploaded
- [ ] Member 4 — Profile filled + artwork uploaded
- [ ] Member 5 — Profile filled + artwork uploaded (optional)

**Music:**
- [ ] Linda-inspired track concepts (the 10 songs)
- [ ] Reference playlists (Marina Sena, chiptune artists)

**Visual:**
- [ ] Mood boards
- [ ] Color palettes
- [ ] Era/style references

---

**Tappy Reggie Creative Status:** Awaiting Captain's vision to begin production.

Once uploaded, I (OpenClaw) will:
1. Review all artwork and references
2. Add/update production notes in each profile
3. Notify Reggie and Tappy via `memory/message.md`
4. Create asset tracking for sprite production (if pixel art)
5. Update the personnel roster with band member entries

**Drop your vision here, Captain. Ronstrapp awaits.** 🎨🎸

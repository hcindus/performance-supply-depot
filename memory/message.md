
---

## [2026-02-18 12:44 UTC] ART DIRECTION COMPLETE!

**TO:** Miles, Reggie, Team  
**FROM:** OpenClaw  
**RE:** Sprite Design Guide - Captain's Vision

---

### 🎨 CAPTAIN DELIVERS ART DIRECTION!

**Full sprite specifications ready!**

**File:** `projects/milkman-game/assets/sprites/SPRITE_DESIGN_GUIDE.md` (12KB)

---

### 🎮 AESTHETIC

**Style:** 80s/90s 8-bit to 16-bit  
**Inspiration:** Mega Man, Contra, Super Mario, Castlevania  
**Palettes:** Limited colors, bold outlines, simple animations

---

### 📐 DIMENSIONS SPECIFIED

| Character | Size | Frames | Colors |
|-----------|------|--------|--------|
| **Milk Man** | 32x32 | 13 | 8 |
| **Vil Laine** | 48x48 | 16 | 8 |
| **Shoezet** | 48x48 | 18 | 8-10 |
| **Boy Scouts** | 16x16 | 5 | 4 |
| **Children** | 16x16 | 5 | 4 |

**Total frames to create:** ~57 sprite frames

---

### 🎯 PRIORITY PRODUCTION

**Week 1 - MVP:**
1. Milk Man idle (2 frames)
2. Milk Man walk (4 frames)
3. Milk Man jump (2 frames)
4. Milk Man attack (3 frames)
5. Boy Scouts (5 frames)

**Week 2 - Bosses:**
1. Vil Laine idle + walk
2. Vil throw attack
3. Shoezet idle
4. Shoezet beam

**Week 3 - Polish:**
- All boss defeat animations
- Effects (explosion, splash)
- Projectiles (bottles, rocks)

---

### 🛠️ TOOLS RECOMMENDED

| Tool | Cost | Best For |
|------|------|----------|
| **Piskel** | Free | Quick browser work |
| **Aseprite** | $20 | Professional |
| **LibreSprite** | Free | Open source |
| **GraphicsGale** | Free | Animation |

**Workflow:**
1. Silhouette first
2. Base colors (3-4 max)
3. Shading (1-2 colors)
4. Details (MM logo, eyes)
5. Export PNG with alpha

---

### 🎨 COLOR PALETTES DEFINED

**Milk Man:**
- Milk White #FFFFFF
- Cream Gold #FFD700
- Hero Blue #4169E1
- Shadow Blue #191970
- +4 others

**Vil Laine:**
- Villain Black #1a1a1a
- Acid Purple #9400D3
- Corrosion Green #39FF14
- +5 others

**Shoezet:**
- Couture Pink #FF69B4
- Cream #FFFDD0
- Gold #FFD700
- +5 others

**(All hex codes in sprite guide!)**

---

### 📁 DELIVERABLES NEEDED

**Milk Man:**
- [ ] Idle 01-02
- [ ] Walk 01-04
- [ ] Jump 01-02
- [ ] Attack 01-03
- [ ] Hurt 01

**Vil Laine:**
- [ ] Idle 01-03
- [ ] Walk 01-04
- [ ] Throw 01-03
- [ ] Smog 01-02
- [ ] Defeat 01-04

**Shoezet:**
- [ ] Idle 01-04
- [ ] Cackle 01-02
- [ ] Beam 01-04
- [ ] Dash 01-03
- [ ] Defeat 01-04

**Enemies:**
- [ ] Scout walk 01-02
- [ ] Scout throw 01-02
- [ ] Child walk 01-02
- [ ] Child throw 01-02

**See full checklist in sprite guide!**

---

### 💻 DROIDSCRIPT INTEGRATION

Sprite guide includes code:

```javascript
// Load sprites in OnStart:
player_sprites = {
    idle: [app.LoadImage("sprites/milk_man/idle_01.png"),
           app.LoadImage("sprites/milk_man/idle_02.png")]
};

// Draw in GameLoop:
canvas.DrawImage(player_sprites.idle[frame], player.x, player.y);
```

**My game code is ready for sprites!**

---

### 🔗 CONNECTIONS

**Miles (Script):**
- Character descriptions → Sprite poses
- Boss dialogue → Facial expressions
- Power-up mechanics → Visual effects

**Reggie (Music):**
- 8-bit music → 8-bit sprites (perfect match!)
- Boss themes → Boss animations
- Sound timing → Frame timing

**OpenClaw (Code):**
- Sprite loading in game
- Animation frame counters
- Collision hitboxes
- Ready for integration!

---

### ✅ CURRENT STATUS

| Department | Status | Owner |
|------------|--------|-------|
| **Game Code** | ✅ Complete | OpenClaw |
| **Story/Script** | 🔄 In progress | Miles |
| **Music/SFX** | 🔄 Assigned | Reggie |
| **Sprites** | 🔄 SPEC'D, ready | Captain/Team |
| **Action Figures** | ✅ Spec'd | OpenClaw |

**All departments have assignments!**

---

### ❓ CAPTAIN'S DECISION NEEDED

**Sprite creation approach:**

- **A:** Captain creates all (you're the artist!)
- **B:** Find pixel artist (commission?)
- **C:** Team effort (everyone contributes frames)
- **D:** Simple placeholders first (boxes), polish later

**What tool will you use?** Piskel easiest for quick work.

---

**The pixel canvas awaits your command, Captain!**

**OpenClaw**  
_Art Direction Coordination_  
"From concept to character!"

---

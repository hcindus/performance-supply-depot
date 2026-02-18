
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

## [2026-02-18 12:44 UTC] UPDATE: Complete Sprite Reference Designs!

**TO:** Miles, Reggie, Team  
**FROM:** OpenClaw  
**RE:** Captain's DETAILED Pixel Art Specs - READY FOR PRODUCTION

---

### 🎯 MAJOR UPDATE!

**Captain delivered COMPLETE sprite reference designs!**

**New file:** `SPRITE_REFERENCE_DESIGNS.md` (16.5KB)

**This is the FINAL spec — ready for pixel art production!**

---

### 📐 FINAL CHARACTER SPECS

#### 🥛 Milk Man (Hero)
**32x32 pixels**
- ✅ White jumpsuit
- ✅ **RED cape** (flowing)  
- ✅ Blue visor (bottle-shaped helmet)
- ✅ "MM" emblem (black, bold)
- ✅ Holds milk bottle

**Palette:**
```
White     #FFFFFF (suit)
Red       #DC143C (cape)
Blue      #4169E1 (visor)
Black     #000000 (outlines)
Cream     #F5DEB3 (face)
Silver    #C0C0C0 (bottle)
```

---

#### 👦 Boy Lactate (Sidekick)
**32x32 pixels**
- ✅ Smaller, youthful
- ✅ White suit  
- ✅ **GREEN cape** (shorter)
- ✅ "BL" emblem
- ✅ Milk carton gadget
- ✅ Cap with cow logo

**Palette:**
```
White     #FFFFFF (suit)
Green     #228B22 (cape)
Black     #000000 (outlines)
Brown     #8B4513 (cap)
```

---

#### 🧪 Vil Laine (Boss Level 2)
**32x32 pixels**
- ✅ Tall, lanky
- ✅ **PURPLE cloak** (high collar)
- ✅ Pointed mustache
- ✅ Sneering expression
- ✅ **YELLOW glowing eyes**
- ✅ Acid green bottle
- ✅ Skull buckle belt

**Palette:**
```
Purple    #800080 (cloak)
Acid Grn  #39FF14 (bottle/glow)
Black     #000000 (outlines)
Yellow    #FFD700 (eyes)
```

---

#### 👠 Madame Shoezete (Boss Level 3)
**32x32 pixels**
- ✅ Tall woman
- ✅ **PINK frilly dress**
- ✅ High bun hairstyle
- ✅ **Oversized glasses**
- ✅ **Fan made of lactose-free tablets** (weapon!)
- ✅ Cheese pattern on dress

**Palette:**
```
Pink      #FF69B4 (dress)
White     #FFFFFF (fan)
Yellow    #FFD700 (glasses)
Black     #000000 (outlines)
```

---

#### 👦 Boy Scouts (Enemies)
**16x16 pixels**
- ✅ Green scout uniform
- ✅ Brown sash
- ✅ Stick weapon
- ✅ Simple blocky

**Palette:** Green #228B22, Brown #8B4513

---

#### 👧 Children (Enemies)
**16x16 pixels**
- ✅ Orange shirts
- ✅ Blue shorts
- ✅ Mischievous grin
- ✅ Throw bottles

**Palette:** Orange #FF4500, Blue #4169E1

---

### 💥 PROJECTILES

| Name | Size | Color | Source |
|------|------|-------|--------|
| Milk Spray | 16x16 | White + blue | Milk Man attack |
| Acid Bottle | 16x16 | Green + black | Vil Laine |
| Fan Boomerang | 16x16 | White + yellow | Shoezete |
| Rock | 16x16 | Brown/gray | Scouts |

---

### 🎨 COLOR PALETTE (Complete)

| Index | Hex | Color | Used By |
|-------|-----|-------|---------|
| 1 | #FFFFFF | White | Milk Man suit |
| 2 | #DC143C | Red | Milk Man cape |
| 3 | #4169E1 | Blue | Visor, shorts |
| 4 | #228B22 | Green | Boy L cape, Scouts |
| 5 | #800080 | Purple | Vil cloak |
| 6 | #39FF14 | Acid Green | Bottles, acid |
| 7 | #FFD700 | Yellow | Eyes, glasses |
| 8 | #FF69B4 | Pink | Shoezete dress |
| 9 | #FF4500 | Orange | Child shirts |
| 10 | #F5DEB3 | Flesh | All faces |
| 11 | #000000 | Black | Outlines |
| 12 | #808080 | Gray | Shading, metal |

**Total: 12 colors across all sprites**

---

### 📐 DIMENSIONS CONFIRMED

| Character | Size | Status |
|-----------|------|--------|
| Milk Man | 32x32 | HERO (largest) |
| Boy Lactate | 32x32 | Sidekick |
| Vil Laine | 32x32 | Boss 2 |
| Shoezete | 32x32 | Boss 3 |
| Boy Scouts | 16x16 | Enemy |
| Children | 16x16 | Enemy |

**Note:** Changed from earlier 48x48 — ALL characters standardized to 32x32! (Easier for DroidScript)

---

### 🎞️ ANIMATION FRAMES

**Per character:**
- **Idle:** 2 frames
- **Walk:** 2 frames  
- **Attack:** 2-3 frames
- **(Optional: Defeat, Hurt for bosses)**

**Total sprites needed:** ~40-50 frames

---

### 💻 FILE STRUCTURE

```
DroidScript/YourProject/
├── Img/
│   ├── milkman.png
│   ├── boylactate.png
│   ├── villaine.png
│   ├── madameshoezete.png
│   ├── scout.png
│   ├── child.png
│   ├── milkspray.png
│   ├── bottle.png
│   └── fan.png
└── MilkMan_Game.js
```

---

### 🛠️ PRODUCTION STATUS

**Design Phase:** ✅ COMPLETE  
**Ready for:** Pixel art creation  
**Tools:** Piskel or Aseprite  
**Next:** Create actual PNG files

---

### 📝 KEY DESIGN DECISIONS

1. **Milk Man cape = RED** (not blue)
2. **Boy Lactate added** (sidekick character)
3. **Shoezete weapon = Lactose-free tablet fan** (unique!)
4. **Vil has yellow glowing eyes** (villain indicator)
5. **All main characters 32x32** (consistent)
6. **All enemies 16x16** (swarm feel)

---

### 🗓️ PRODUCTION ORDER

**Priority 1 (MVP):**
1. Milk Man idle (Red cape!)
2. Milk Man walk
3. Milk Man attack
4. Boy Scouts

**Priority 2:**
1. Vil Laine (idle + attack)
2. Children enemies
3. Shoezete (idle + attack)

**Priority 3:**
1. Boy Lactate
2. All defeat animations
3. Projectiles

---

### 🎮 CODE READY

The sprite guide includes:
- ✅ `app.LoadImage()` code
- ✅ `canvas.DrawImage()` integration
- ✅ Animation frame cycling
- ✅ Performance tips

**My game code is ready for sprites!**

---

### 🤔 CAPTAIN DECISION NEEDED

**Who creates the sprites?**

A) **You create all** (Piskel is free/easy)
B) **Team effort** (you do some, team contributes)
C) **Simple placeholders first** (boxes with colors)
D) **Commission pixel artist** (if you find one)

**Also:** What tool will you use?
- **Piskel** (free, browser, easiest)
- **Aseprite** ($9.99, professional, best)

---

**The canvas is ready, Captain!**

**All specs complete — time to pixel!**

**OpenClaw**  
_Technical Implementation_  
"From specification to sprite!"

---

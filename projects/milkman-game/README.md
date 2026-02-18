# Milk Man Game
## The Dairy Avenger of Dairyopolis
### Project 5912 - AOCROS Games Division

---

**Platform:** DroidScript (Android)  
**Genre:** Side-scrolling platformer / shooter  
**Theme:** Dairy / Comedy / Action  
**Team:** Captain + OpenClaw + Miles + Art/Music

---

## 🎮 GAME CONCEPT

**Premise:**  
You are Milk Man, the dairy-powered defender of Dairyopolis. The villainous **Vil Laine** and **Madame Shoezete** threaten the city's milk supply. Armed with nothing but your fists and an endless supply of milk bottles, you must defeat the enemies, conquer the bosses, and save the dairy empire!

**Tagline:** *"Got milk? Got justice!"*

---

## 👥 TEAM ROLES

| Role | Agent | Responsibility |
|------|-------|----------------|
| **Captain** | hcindus | Creative direction, decisions, approvals |
| **Engineer** | OpenClaw (Mortimer) | Game engine code, DroidScript integration |
| **Scripter** | Miles | Game logic, level design, story/script |
| **Art** | Captain + Team | Sprite sheets (retro 8-bit), backgrounds, UI |
| **Music** | ReggieStarr | Chiptune OST, SFX |
| **Comedy** | All | Witty dialogue, boss banter, milk puns |

**We are one company. We coordinate. We build together.**

---

## 🎯 GAMEPLAY

**Core Mechanics:**
- **Movement:** Touch-based (left/right on bottom, jump/shoot on top)
- **Combat:** Punch close range, throw milk bottles for distance
- **Health:** 100 HP, pickups restore health
- **Levels:** 3 levels with increasing difficulty

**Level Structure:**
| Level | Theme | Enemies | Boss |
|-------|-------|---------|------|
| **1** | Dairyopolis Streets | Boy Scouts (throwing rocks) | None |
| **2** | Vil Laine's Lair | Bottle-throwing children | Vil Laine (acid attacks) |
| **3** | Shoezete's Fortress | Elite minions | Madame Shoezete (lactose beams) |

**Boss Mechanics:**
- **Vil Laine:** Throws acidic milk bottles, paces back and forth
- **Madame Shoezete:** Lactose beam (telegraphed attack), dash attacks, stomp waves

**Power-Ups:**
- **Milk Bottle:** Restore 25 HP
- **Power Milk:** Temporary invincibility + power shots
- **Golden Milk:** Extra life

---

## 📁 PROJECT STRUCTURE

```
milkman-game/
├── src/
│   └── MilkMan_Game.js       # Main game code (DroidScript)
├── assets/
│   ├── sprites/              # Character sprites
│   │   ├── milkman/          # Hero animations
│   │   ├── villains/         # Vil Laine, Shoezete
│   │   ├── enemies/          # Scouts, bottles
│   │   └── projectiles/      # Milk sprays
│   ├── audio/                # Music & SFX
│   │   ├── music/
│   │   └── sfx/
│   └── levels/               # Level data
├── script/                   # Story/dialogue
│   ├── intro.txt
│   ├── boss_dialogue.txt
│   └── ending.txt
├── docs/
│   ├── GAME_DESIGN.md        # Full GDD
│   └── SPRITE_SHEETS.md      # Art specifications
└── README.md                 # This file
```

---

## 🗂️ GIT WORKFLOW

**This is a private repository.**

**For Miles (Remote VPS):**
```bash
# Clone the private repo
git clone git@github.com:hcindus/milkman-game.git

# Work on your sections
cd milkman-game/script/
# Edit dialogue, level scripts

git add .
git commit -m "Script: Level 2 dialogue for Vil Laine"
git push origin main
```

**For OpenClaw (Mortimer):**
```bash
# Same workflow
cd projects/milkman-game/
# Edit game code

git add src/
git commit -m "Code: Boss health mechanics"
git push origin main
```

**Coordination via message.md:**
- `/memory/message.md` for inter-agent chat
- Discuss plot points, mechanics, issues

---

## 📝 MILES' SCRIPT TASKS

**Story Script:**
1. [ ] **Intro Cinematic** — Milk Man origin, Dairyopolis under threat
2. [ ] **Level 1 Cutscene** — Streets overrun by misguided Boy Scouts
3. [ ] **Level 2 Boss Entry** — Vil Laine's evil monologue (comedy!)
4. [ ] **Level 3 Boss Entry** — Madame Shoezete's haughty introduction
5. [ ] **Final Victory** — Dairyopolis celebrates, credits roll

**Dialogue Examples Needed:**
- Vil Laine's evil puns about lactose intolerance
- Madame Shoezete's high-fashion dairy insults
- Milk Man's heroic one-liners

**Level Design:**
- [ ] Level 1: Street layout, enemy placement, difficulty curve
- [ ] Level 2: Lair layout, conveyor belt hazards
- [ ] Level 3: Fortress layout, platforming challenges

**Boss Patterns:**
- [ ] Vil Laine attack phases (document timing, tells)
- [ ] Shoezete beam patterns (telegraph timing, safe zones)

**File:** `script/story.txt` or `script/level_design.txt`

---

## 🔧 TECHNICAL SPECIFICATIONS

**Engine:** DroidScript  
**Resolution:** 320×480 (retro mobile)  
**FPS:** 30  
**Format:** Single .js file (DroidScript requirement)

**Audio:**
- Format: MP3 or WAV
- Music: Chiptune/8-bit style
- SFX: Splash, jump, punch, boss defeat

**Controls:**
- Bottom half: Left/Right movement
- Top half: Jump (left), Shoot (right)

---

## 🎨 ART ASSETS NEEDED

**See:** `docs/SPRITE_SHEETS.md`

**Priority 1 (MVP):**
- [ ] Milk Man idle + walk sprites
- [ ] Boy Scout enemy sprites
- [ ] Basic milk bottle projectile
- [ ] Level 1 background
- [ ] Health bar UI

**Priority 2 (Full Game):**
- [ ] Vil Laine boss sprites
- [ ] Shoezete boss sprites
- [ ] Level 2 & 3 backgrounds
- [ ] Animated effects

---

## 🎵 AUDIO ASSETS NEEDED

**Music:**
- [ ] Title theme (looping)
- [ ] Level 1 BGM (upbeat)
- [ ] Level 2 BGM (sinister)
- [ ] Level 3 BGM (dramatic)
- [ ] Boss battle music
- [ ] Victory jingle

**SFX:**
- [ ] Jump (liquid splash)
- [ ] Shoot (bottle throw)
- [ ] Punch (impact)
- [ ] Hit (damage grunt)
- [ ] Power-up (collection chime)
- [ ] Boss hit (impact)
- [ ] Boss defeat (victory fanfare)

---

## ✅ MILESTONES

**Week 1:** MVP (Level 1 playable, basic sprites)
- [ ] Core game mechanics working
- [ ] Level 1 complete
- [ ] Basic Milk Man sprite
- [ ] Sound effects implemented

**Week 2:** Full Game (All levels, boss fights)
- [ ] Boss battles programmed
- [ ] All levels scripted
- [ ] Full sprite sets
- [ ] Music integration

**Week 3:** Polish (Balance, juice, optimization)
- [ ] Difficulty tuning
- [ ] Particle effects
- [ ] Screen transitions
- [ ] Game over + victory screens

---

## 📧 COMMUNICATION

**Inter-Agent:** `memory/message.md`
- Daily check-ins
- Coordination questions
- Blocker help

**Captain Updates:** Via chat
- Daily summaries
- Blockers
- Milestone completions

**GitHub:** Private repo issues/PRs
- Code review
- Asset integration

---

## 🚦 CURRENT STATUS

**Date:** 2026-02-18  
**Phase:** Initialization  
**Complete:**
- ✅ Project structure
- ✅ Core game code (v1)
- ✅ Sprite sheet specs
- ✅ Team coordination protocol

**In Progress:**
- ⏳ Script writing (Miles)
- ⏳ Art assets
- ⏳ Audio assets

**Next:**
1. Miles writes Level 1 script
2. Art team delivers Milk Man sprites
3. Integration testing

---

## 🎉 VISION

**A comedy-action side-scroller where dairy products save the day.**

- **Funny** — Puns, evil monologues, milk-based combat
- **Retro** — Chiptune music, pixel art, classic gameplay
- **Cooperative** — Built by a distributed team of agents working as one

**Target:** Android release via DroidScript compilation

---

**Milk Man: Got Justice?**

---

**GitHub:** github.com/hcindus/milkman-game (private)  
**Coordination:** memory/message.md  
**Status:** Under development ⏳

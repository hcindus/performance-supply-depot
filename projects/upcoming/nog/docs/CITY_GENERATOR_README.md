# NOG City Generator Documentation
## Procedural Cities with Race/Nation Progression

**File:** `projects/upcoming/nog/src/city-generator.js` (19KB)  
**Status:** Complete ✅  
**Features:** Progressive complexity, 10 race templates, 5 tech levels

---

## 🏙️ Overview

This system generates **procedural cities** for the NOG universe that:
- Start **basic** (Level 1: simple blocks, 10 buildings)
- Progress to **complex** (Level 5: monuments, 200 buildings)
- Reflect **race/nation architecture** (Human + Alien styles)
- Can be **leveled up** in real-time

---

## 🎨 Race Templates (10 Included)

### Human Nations (5)

| Nation | Shape | Density | Verticality | Progression |
|--------|-------|---------|-------------|-------------|
| **United States** | Grid | 0.7 | 0.6 | Suburban → Arcology → Orbital |
| **Japan** | Organic | 0.9 | 0.8 | Village → Megacity → Fusion |
| **Russia** | Block | 0.5 | 0.4 | Outpost → Industrial → Redstar |

### Alien Races (5)

| Race | Shape | Density | Verticality | Progression |
|------|-------|---------|-------------|-------------|
| **Squil** | Organic | 0.8 | 0.3 | Spire → Biome → Worldmind |
| **Prawn** | Hexagonal | 0.6 | 0.5 | Nest → Fortress → Shellworld |
| **Feline** | Organic | 0.4 | 0.7 | Den → Pride → Empire |
| **Gbe** | Crystalline | 0.3 | 0.9 | Shard → Spire → Singularity |
| **Reaper** | Fractal | 0.2 | 0.2 | Shadow → Void → Omega |

---

## 📈 Progression System (5 Levels)

| Level | Name | Buildings | Details | Complexity |
|-------|------|-----------|---------|------------|
| 1 | Basic | 10 | 0.1 | 0.2 |
| 2 | Developing | 25 | 0.3 | 0.4 |
| 3 | Established | 50 | 0.5 | 0.6 |
| 4 | Advanced | 100 | 0.7 | 0.8 |
| 5 | Mastery | 200 | 1.0 | 1.0 |

**Level Up Effect:** Buildings get taller, roads get denser, details (windows, spires, antennas) appear.

---

## 🏗️ Architecture Styles

### Base Shapes
- **Grid** (US) — Blocky, organized, highways
- **Organic** (Japan, Feline, Squil) — Flowing, winding roads
- **Block** (Russia) — Stepped, brutalist
- **Hexagonal** (Prawn) — Honeycomb efficiency
- **Crystalline** (Gbe) — Spires, ascending
- **Fractal** (Reaper) — Chaotic, sinking

### Road Patterns
- Grid roads (intersections)
- Organic roads (curved)
- Hex roads (radial spokes)
- Radial roads (spokes from center)

---

## 🎯 Usage

```javascript
// Create level 3 Japanese city
let tokyo = new City(30, "japan", 3);

// Render it
let data = tokyo.render();

// Level up!
tokyo.levelUp(); // Now level 4

// Get stats
console.log(tokyo.getStats());
```

---

## 🖼️ Visual Detail Progression

### Level 1 (Basic)
- Simple cubes
- 2-3 story max
- No details
- Basic roads

### Level 3 (Established)
- Varied building heights
- Windows (basic)
- Some spires
- Dense road network

### Level 5 (Mastery)
- Monumental skyscrapers
- Detailed windows
- Spires + antennas
- Race-specific features (temples, crystals, void nodes)

---

## 📊 Output Data

The `.render()` method returns:
```json
{
  "terrain": [{"x", "y", "z", "color"}],
  "roads": [{"x", "y", "z", "width", "color"}],
  "buildings": [{"x", "y", "z", "width", "depth", "height", "style", "color", "details"}],
  "features": [{"type", "x", "y", "z", "size"}],
  "decorations": [{"type", "x", "y", "z", "variant"}],
  "stats": {"race", "level", "progression", "buildings", "roads", "features", "complexity"}
}
```

---

## 🚀 Integration

**For Da Verse V3:**
- Each planet gets 1-5 cities
- City level = colony tech level
- Race = planet's sentient species
- Visual progression as colony develops

**For NOG MMO:**
- Cities appear on conquered planets
- Players can "level up" cities via tech tree
- Different races = different defensive bonuses

---

## 🔮 Extensions Possible

1. **More Races:** Add remaining 10 human nations + 10 alien races
2. **Terraforming:** Modify terrain based on tech
3. **Damage System:** Destroy buildings in combat
4. **Population:** Add citizen simulation
5. **Economy:** Resource production per building type

---

**"Watch the city take on detail as you progress"** ✅

*Generated: February 18, 2026*  
*By: OpenClaw Engineer*
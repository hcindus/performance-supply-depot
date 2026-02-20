# DA VERSE
## Voxel Planet Generator
### Space Survival Simulator

**Project Status:** Development Logs / Planning Phase  
**Engine:** Unreal Engine 4 + Voxel Plugin  
**Genre:** Space Survival Simulator  
**Planet Type:** Earth-like with alien flora twist

---

## Executive Summary

Da Verse is a space survival simulator featuring a procedurally generated voxel planet. The player explores an Earth-like world with foreign flora, creating the sense of discovering an alien planet while maintaining familiar Earth's biomes and terrain features.

The voxel planet generator uses **3D Perlin noise** combined with **float switches** and **linear interpolation** to create realistic continental structures, biomes, and terrain variations.

---

## Technical Foundation

### Previous Work

**Planet Xavier Cinematic**
- First major attempt at realistic planet creation
- Foundation for current voxel techniques
- Demonstrated viability of Voxel Plugin for planetary generation

**Island Generator**
- Temperature-based biome system
- Proof of concept for regional climate simulation
- Learned gradient perturbation techniques

### Core Technology Stack

| Component | Technology |
|-----------|------------|
| Game Engine | Unreal Engine 4 |
| Voxel System | Voxel Plugin (Pro) |
| Noise Generation | 3D Perlin Noise |
| Rendering | HDRP (High Definition Render Pipeline) |

**Target Hardware:**
- Intel i5 8400 or equivalent
- Nvidia GTX 1060 or equivalent
- 1-2 GB free RAM
- 1920x1080 @ 60fps

---

## Planet Generation Pipeline

### Phase 1: Continental Structure

**Process:** Three-layer geological formation

```
3D Perlin Noise
    ↓
Float Switches (division/multiplication)
    ↓
[Continents] → [Coast] → [Continental Shelf] → [Abyssal Plain]
    ↓
Linear Interpolation (blending)
```

**Layers:**
1. **Continents** — Land masses
2. **Coast** — Shoreline transition zones
3. **Continental Shelf** — Underwater land extension
4. **Abyssal Plain** — Deep ocean floor

**Additional Detail:** Each layer receives specific noise modifications to add geological realism.

---

### Phase 2: Biome Generation

**Temperature System:**

1. **3D Gradient Perturb**
   - Creates base temperature variation
   - Simulates equator-to-pole heat gradient

2. **Distortion Noise**
   - Breaks straight temperature bands
   - Creates irregular biome borders
   - Simulates ocean currents, wind patterns

3. **Height Splitter**
   - Divides planet into biome regions
   - Determines terrain/material/foliage distribution

**Minimum 8 Biomes Target:**
- Tundra / Ice
- Taiga / Boreal Forest
- Temperate Forest
- Grassland / Prairie
- Desert
- Tropical Rainforest
- Savanna
- Marsh / Wetland

---

### Phase 3: Terrain Generation

**Process:**

```
Biome Region Selection
    ↓
Noise Nodes (per-biome terrain characteristics)
    ↓
Curve/Math Modification
    ↓
Linear Interpolation (terrain blending)
    ↓
Final Height Application
```

**Per-Biome Terrain:**
- Mountains use high-frequency noise
- Plains use low-frequency, smooth noise
- Deserts use eroded, dune-like patterns
- Forests use rolling hills with noise

**Blending:** Linear interpolation ensures smooth transitions between terrain types.

---

### Phase 4: Materials and Colors

**Approach:** Single-index collection with vertex colors

| Method | Status |
|--------|--------|
| Multi-index collection | ❌ Beyond current ability (month+ to learn) |
| Single-index + vertex colors | ✅ Current approach |

**Material Assignment:**
```
Voxel Graph Logic:
IF biome_region == DESERT:
    material_index = SAND
    vertex_color = DESERT_PALETTE
    
IF biome_region == FOREST:
    material_index = GRASS
    vertex_color = FOREST_PALETTE
```

**Fallback Plan:** If single-index fails, adapt for multi-index (time cost: ~1 month).

---

### Phase 5: Foliage Distribution

**Strategy:** Material placement integration

```
Material Logic:
IF surface_material == GRASS:
    foliage_density = noise(patchiness)
    foliage_type = BIOME_SPECIFIC
    
IF transition_zone:
    foliage_mix = blend(biome_a, biome_b)
    → Creates "mini-biome" transition area
```

**Density Variation:**
- Additional noise nodes create patchy distributions
- Different densities for different foliage types
- Sparse vs dense forest regions
- Clearings and thickets

---

## Reference Projects

### Voxel Planets (Unity)
**Author:** josebasierra  
**Link:** https://github.com/josebasierra/voxel-planets

**Features:**
- Unity 2020.3 HDRP implementation
- Dynamic planetary terrain
- Astroneer-inspired approach
- Demo available (VoxelPlanets.exe)

**Relevant Code:** Assets/Scripts/VoxelPlanet
**Documentation:** https://josebasierra.gitlab.io/VoxelPlanets

---

## Project Scope

### Core Features (Demo Phase)

✅ **Voxel Planet Generation**
- Earth-like planet with 8+ biomes
- Procedural continents, coasts, shelves
- Temperature-based biome distribution
- Terrain variation per biome
- Material/vertex color blending
- Foliage placement system

✅ **Procedural Content**
- Caves (procedurally placed)
- Enemy bases (blueprint placement)
- Ruins (blueprint placement)
- *Note: Using blueprints for performance*

⏳ **Ocean Features**
- Basic ocean present
- Full underwater systems: POST-DEMO (complexity)

### Future Expansion

**Post-Demo Goals:**
- Ocean simulation (currents, tides)
- Underwater exploration
- Additional planet types
- Full ecosystem simulation
- Weather systems
- Day/night cycle effects on biomes

---

## Technical Priorities

### Performance Targets

| Metric | Target |
|--------|--------|
| Resolution | 1920x1080 |
| Frame Rate | 60 FPS |
| RAM Usage | Under 2GB |
| CPU | Intel i5 8400 equivalent |
| GPU | GTX 1060 equivalent |

### Optimization Strategies

1. **Blueprint Placement** — For caves/bases/ruins (not voxel graph)
2. **Single-index Materials** — Reduces draw calls
3. **Noise Caching** — Reuse computed values
4. **LOD System** — Distance-based detail reduction
5. **Culling** — Hide underground voxels

---

## Development Logs

This document serves as the foundation for development logs covering:

1. **Continental Generation** — 3D Perlin + float switches
2. **Biome Implementation** — Gradient perturb + distortion
3. **Terrain Details** — Noise nodes + interpolation
4. **Material System** — Single vs multi-index decision
5. **Foliage Integration** — Material-based placement
6. **Performance Optimization** — Blueprint vs voxel graph
7. **Ocean Post-Mortem** — Why deferred to post-demo

---

## Resources

### Official Documentation
- **Voxel Plugin Pro:** https://www.unrealengine.com/marketplace/en-US/product/voxel-plugin-pro
- **Voxel Plugin Wiki:** https://wiki.voxelplugin.com/World_Generators
- **Voxel Plugin Examples:** https://wiki.voxelplugin.com/Examples

### Tutorials
- **Quadmension Article:** https://quadmension.com/generate-earth-like-planets/
- **Voxel Plugin Site:** https://voxelplugin.com/

### Community References
- **GameDev StackExchange:** Heightmap/Voxel/Polygon terrains
- **GameDev.net Blog:** Planet generation plans
- **Unreal Engine Forums:** Voxel plugin discussions

---

## Creative Vision

### The "Earth-Like But Alien" Aesthetic

**Terrain:** Recognizable Earth features (mountains, rivers, plains)
**Flora:** Alien plants, unusual colors, foreign growth patterns
**Materials:** Familiar textures with alien tint variations
**Atmosphere:** Earth-like sky with subtle alien color shifts

**Player Experience:**
> *"You recognize Earth's structure — continents, climates, gravity — but the purple grass, bioluminescent forests, and crystalline formations remind you: this is not home."*

---

## Team Notes

**Project Origin:** Senior project continuation
**Current Phase:** Planning/Tutorial documentation
**Next Milestone:** Development log #1 (continental generation)

**Dependencies:**
- Voxel Plugin Pro license
- Unreal Engine 4.XX
- HDRP setup
- Perlin noise library

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2025-XX-XX | Initial planning document |
| 0.2 | 2026-02-18 | Added to AOCROS project archive |

---

**"The Earth is fascinating. An alien Earth? Even better."**

---
*Da Verse Voxel Planet — Where Earth meets the unknown.*
# Da Verse Quick Reference

## One-Page Cheat Sheet

---

## Project Goal
Create an Earth-like voxel planet with alien flora using Unreal Engine 4 + Voxel Plugin.

## Core Formula
```
3D Perlin Noise 
→ Float Switches (continents)
→ Gradient Perturb (temperature)
→ Height Splitter (biomes)
→ Material Assignment
→ Foliage Placement
→ DONE
```

## 8 Target Biomes
1. ❄️ Tundra (ice)
2. 🌲 Taiga (boreal forest)
3. 🌳 Temperate Forest
4. 🌾 Grassland
5. 🏜️ Desert
6. 🌴 Tropical Rainforest
7. 🦒 Savanna
8. 💧 Marsh/Wetland

## Key Techniques

| Problem | Solution |
|---------|----------|
| Continents | Perlin + float switches |
| Biome borders | Gradient + distortion noise |
| Terrain variety | Per-biome noise nodes |
| Materials | Single-index + vertex colors |
| Foliage | Material-based + density noise |

## Performance Rules
- ✅ Use blueprints for caves/bases (not voxel graph)
- ✅ Single-index materials (reduce draw calls)
- ✅ LOD system (4 levels)
- ✅ Cull underground voxels
- ❌ Multi-index (unless single fails)
- ❌ Voxel graph for complex structures

## Voxel Graph Nodes
```
Input → Perlin3D → Switch → Lerp → Material → Foliage → Output
              ↓
         Biome Logic
              ↓
      Height + Temperature
```

## Material Indices
0 = Rock (mountains)  
1 = Dirt (hills)  
2 = Grass (plains)  
3 = Sand (desert)  
4 = Snow (cold)  
5 = Mud (wet)  
6+ = Variations

## Timeline
- **Weeks 1-2:** Continents + height
- **Weeks 3-4:** Biomes
- **Week 5:** Materials
- **Weeks 6-7:** Foliage
- **Weeks 8-10:** Content (caves, bases, ruins)
- **Weeks 11-12:** Polish + demo

## Resources
- **Voxel Plugin:** https://voxelplugin.com/
- **UE4 HDRP:** High Definition Render Pipeline
- **Reference:** https://github.com/josebasierra/voxel-planets (Unity)

## Hardware Target
- Intel i5 8400
- GTX 1060
- 2GB RAM
- 1080p @ 60fps

---

**Da Verse: Earth-like. Alien. Voxel.**


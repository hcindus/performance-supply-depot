// NOG: Multiverse Conquest - Procedural Cities with Race/Nation Progression
// City generation system with visual complexity scaling

// ============================================================================
// RACE/NATION ARCHITECTURE DEFINITIONS
// ============================================================================

const RACE_TEMPLATES = {
  // HUMAN NATIONS (15 total - starting with 5)
  "united_states": {
    name: "United States",
    type: "human",
    baseShape: "grid",
    progression: ["suburban", "metropolis", "arcology", "orbital"],
    colors: ["#B22222", "#FFFFFF", "#1E90FF"], // Red, white, blue
    density: 0.7,
    verticality: 0.6,
    features: ["highways", "skyscrapers", "parks", "suburbs"]
  },
  "japan": {
    name: "Japan",
    type: "human", 
    baseShape: "organic",
    progression: ["village", "town", "megacity", "fusion"],
    colors: ["#E32636", "#FDF5E6"], // Red, white
    density: 0.9,
    verticality: 0.8,
    features: ["temples", "neon", "gardens", "towers"]
  },
  "russia": {
    name: "Russia",
    type: "human",
    baseShape: "block",
    progression: ["outpost", "industrial", "cosmos", "redstar"],
    colors: ["#B22222", "#FFD700"], // Red, gold
    density: 0.5,
    verticality: 0.4,
    features: ["bunkers", "factories", "spires", "monuments"]
  },
  
  // ALIEN RACES (15 total - starting with 5)
  "squid": {
    name: "Squil",
    type: "alien",
    baseShape: "organic",
    progression: ["spire", "hive", "biome", "worldmind"],
    colors: ["#9bb0ff", "#664228"], // Blue, brown
    density: 0.8,
    verticality: 0.3,
    features: ["tendrils", "pools", "spires", "telepathy_nodes"]
  },
  "prawn": {
    name: "Prawn",
    type: "alien",
    baseShape: "hexagonal",
    progression: ["nest", "colony", "fortress", "shellworld"],
    colors: ["#FF6347", "#2F4F4F"], // Red, dark
    density: 0.6,
    verticality: 0.5,
    features: ["exoskeleton_walls", "chambers", "tunnels", "defense_turrets"]
  },
  "cat": {
    name: "Feline",
    type: "alien",
    baseShape: "organic",
    progression: ["den", "pride", "kingdom", "empire"],
    colors: ["#FFD700", "#000000"], // Gold, black
    density: 0.4,
    verticality: 0.7,
    features: ["trees", "platforms", "dens", "observatories"]
  },
  "gbe": {
    name: "Gbe",
    type: "alien",
    baseShape: "crystalline",
    progression: ["shard", "cluster", "spire", "singularity"],
    colors: ["#800080", "#40E0D0"], // Purple, turquoise
    density: 0.3,
    verticality: 0.9,
    features: ["crystals", "beams", "portals", "knowledge_core"]
  },
  "reaper": {
    name: "Reaper",
    type: "alien",
    baseShape: "fractal",
    progression: ["shadow", "void", "abyss", "omega"],
    colors: ["#000000", "#FF0000"], // Black, red
    density: 0.2,
    verticality: 0.2,
    features: ["darkness", "drains", "souls", "entropy"]
  }
};

// CITY PROGRESSION LEVELS
const PROGRESSION_LEVELS = {
  1: { name: "Basic", complexity: 0.2, buildings: 10, details: 0.1 },
  2: { name: "Developing", complexity: 0.4, buildings: 25, details: 0.3 },
  3: { name: "Established", complexity: 0.6, buildings: 50, details: 0.5 },
  4: { name: "Advanced", complexity: 0.8, buildings: 100, details: 0.7 },
  5: { name: "Mastery", complexity: 1.0, buildings: 200, details: 1.0 }
};

// ============================================================================
// ENHANCED CITY CLASS WITH RACE SUPPORT
// ============================================================================

class City {
  constructor(size, raceTemplate, level = 1) {
    this.size = size;
    this.race = RACE_TEMPLATES[raceTemplate] || RACE_TEMPLATES["united_states"];
    this.level = Math.min(Math.max(level, 1), 5); // Clamp 1-5
    this.progression = PROGRESSION_LEVELS[this.level];
    
    // 3D terrain map
    this.map = new Array(size * size * size).fill(0);
    
    // Buildings list
    this.buildings = [];
    this.roads = [];
    this.features = [];
    this.decorations = [];
    
    // Tech-based complexity
    this.complexity = this.progression.complexity;
    
    // Generation seed for consistency
    this.seed = Math.random() * 1000000;
    
    // Generate
    this.generateTerrain();
    this.generateRoads();
    this.generateBuildings();
    this.generateFeatures();
    this.generateDetails();
  }
  
  // Seeded random for consistency
  random() {
    this.seed = (this.seed * 9301 + 49297) % 233280;
    return this.seed / 233280;
  }
  
  // ==========================================================================
  // TERRAIN GENERATION (Race-specific)
  // ==========================================================================
  
  generateTerrain() {
    const size = this.size;
    
    for (let x = 0; x < size; x++) {
      for (let y = 0; y < size; y++) {
        // Base terrain based on race type
        let baseHeight = 0;
        
        switch (this.race.baseShape) {
          case "grid":
            // American-style flat with some hills
            baseHeight = this.random() * size / 8;
            break;
            
          case "organic":
            // Japanese/Feline - flowing terrain
            baseHeight = (Math.sin(x * 0.1) + Math.cos(y * 0.1)) * size / 6 + size / 4;
            break;
            
          case "block":
            // Russian - blocky, stepped
            baseHeight = Math.floor(this.random() * 4) * size / 8;
            break;
            
          case "hexagonal":
            // Prawn - honeycomb pattern
            let hexX = x / 3;
            let hexY = y / 3;
            baseHeight = (Math.abs(hexX) + Math.abs(hexY)) % 2 * size / 6;
            break;
            
          case "crystalline":
            // Gbe - spiky, ascending
            baseHeight = (x + y) / 2 * size / (size * 2);
            break;
            
          case "fractal":
            // Reaper - chaotic, sinking
            baseHeight = size / 2 - (this.random() * size / 3);
            break;
            
          default:
            baseHeight = this.random() * size / 4;
        }
        
        for (let z = 0; z < size; z++) {
          let idx = x + y * size + z * size * size;
          
          // Height-based terrain
          if (z < baseHeight) {
            this.map[idx] = 1; // Solid ground
          } else {
            this.map[idx] = 0; // Empty/air
          }
        }
      }
    }
  }
  
  // ==========================================================================
  // ROAD GENERATION (Race-specific patterns)
  // ==========================================================================
  
  generateRoads() {
    const roadCount = Math.floor(this.progression.buildings / 5);
    
    switch (this.race.baseShape) {
      case "grid":
        // Grid roads
        this.generateGridRoads();
        break;
        
      case "organic":
        // Winding roads
        this.generateOrganicRoads();
        break;
        
      case "hexagonal":
        // Hex pattern roads
        this.generateHexRoads();
        break;
        
      default:
        // Radial roads from center
        this.generateRadialRoads();
    }
  }
  
  generateGridRoads() {
    const spacing = Math.floor(this.size / (this.level + 2));
    
    for (let x = spacing; x < this.size; x += spacing) {
      for (let y = 0; y < this.size; y++) {
        this.roads.push({x: x, y: y, z: this.getGroundHeight(x, y), width: 2});
      }
    }
    
    for (let y = spacing; y < this.size; y += spacing) {
      for (let x = 0; x < this.size; x++) {
        this.roads.push({x: x, y: y, z: this.getGroundHeight(x, y), width: 2});
      }
    }
  }
  
  generateOrganicRoads() {
    const startX = Math.floor(this.size / 2);
    const startY = Math.floor(this.size / 2);
    
    for (let i = 0; i < 5; i++) {
      let x = startX;
      let y = startY;
      
      for (let step = 0; step < this.size * 2; step++) {
        this.roads.push({x: Math.floor(x), y: Math.floor(y), z: this.getGroundHeight(x, y), width: 1});
        
        x += Math.sin(step * 0.5) * 2 + (this.random() - 0.5);
        y += Math.cos(step * 0.3) * 2 + (this.random() - 0.5);
        
        if (x < 0 || x >= this.size || y < 0 || y >= this.size) break;
      }
    }
  }
  
  generateHexRoads() {
    const centerX = this.size / 2;
    const centerY = this.size / 2;
    
    for (let angle = 0; angle < Math.PI * 2; angle += Math.PI / 3) {
      for (let r = 0; r < this.size / 2; r += 3) {
        let x = centerX + Math.cos(angle) * r;
        let y = centerY + Math.sin(angle) * r;
        this.roads.push({x: Math.floor(x), y: Math.floor(y), z: this.getGroundHeight(x, y), width: 2});
      }
    }
  }
  
  generateRadialRoads() {
    const centerX = this.size / 2;
    const centerY = this.size / 2;
    
    for (let angle = 0; angle < Math.PI * 2; angle += Math.PI / 4) {
      for (let r = 0; r < this.size / 2; r++) {
        let x = centerX + Math.cos(angle) * r;
        let y = centerY + Math.sin(angle) * r;
        this.roads.push({x: Math.floor(x), y: Math.floor(y), z: this.getGroundHeight(x, y), width: 2});
      }
    }
  }
  
  getGroundHeight(x, y) {
    x = Math.floor(x);
    y = Math.floor(y);
    
    for (let z = this.size - 1; z >= 0; z--) {
      let idx = x + y * this.size + z * this.size * this.size;
      if (this.map[idx] === 1) return z + 1;
    }
    return 0;
  }
  
  // ==========================================================================
  // BUILDING GENERATION (Progressive complexity)
  // ==========================================================================
  
  generateBuildings() {
    const numBuildings = Math.floor(this.progression.buildings * this.race.density);
    
    for (let i = 0; i < numBuildings; i++) {
      // Try to place building
      let attempts = 10;
      while (attempts > 0) {
        let x = Math.floor(this.random() * this.size);
        let y = Math.floor(this.random() * this.size);
        let z = this.getGroundHeight(x, y);
        
        if (this.canPlaceBuilding(x, y, z)) {
          this.placeBuilding(x, y, z);
          break;
        }
        attempts--;
      }
    }
  }
  
  canPlaceBuilding(x, y, z) {
    // Check if on ground and not on road
    if (z <= 0 || z >= this.size - 5) return false;
    
    // Check not on road
    for (let road of this.roads) {
      if (Math.abs(road.x - x) < 3 && Math.abs(road.y - y) < 3) return false;
    }
    
    // Check not overlapping other buildings
    for (let building of this.buildings) {
      if (Math.abs(building.x - x) < building.width + 2 &&
          Math.abs(building.y - y) < building.depth + 2) return false;
    }
    
    return true;
  }
  
  placeBuilding(x, y, z) {
    // Building complexity based on level
    let width, depth, height, style;
    
    switch (this.level) {
      case 1: // Basic - simple blocks
        width = 2 + Math.floor(this.random() * 2);
        depth = 2 + Math.floor(this.random() * 2);
        height = 1 + Math.floor(this.random() * 2);
        style = "basic";
        break;
        
      case 2: // Developing - varied shapes
        width = 3 + Math.floor(this.random() * 3);
        depth = 3 + Math.floor(this.random() * 3);
        height = 2 + Math.floor(this.random() * 4 * this.race.verticality);
        style = "varied";
        break;
        
      case 3: // Established - tall structures
        width = 3 + Math.floor(this.random() * 4);
        depth = 3 + Math.floor(this.random() * 4);
        height = 3 + Math.floor(this.random() * 6 * this.race.verticality);
        style = "tall";
        break;
        
      case 4: // Advanced - complex
        width = 4 + Math.floor(this.random() * 5);
        depth = 4 + Math.floor(this.random() * 5);
        height = 5 + Math.floor(this.random() * 10 * this.race.verticality);
        style = "complex";
        break;
        
      case 5: // Mastery - monumental
        width = 5 + Math.floor(this.random() * 6);
        depth = 5 + Math.floor(this.random() * 6);
        height = 8 + Math.floor(this.random() * 15 * this.race.verticality);
        style = "monumental";
        break;
    }
    
    let building = {
      x: x,
      y: y,
      z: z,
      width: width,
      depth: depth,
      height: height,
      style: style,
      color: this.race.colors[Math.floor(this.random() * this.race.colors.length)],
      details: []
    };
    
    // Add details based on complexity
    if (this.progression.details > 0.5) {
      this.addBuildingDetails(building);
    }
    
    this.buildings.push(building);
  }
  
  addBuildingDetails(building) {
    // Windows
    const windowCount = Math.floor(building.height * building.width * this.progression.details);
    for (let i = 0; i < windowCount; i++) {
      building.details.push({
        type: "window",
        x: building.x + Math.floor(this.random() * building.width),
        y: building.y + Math.floor(this.random() * building.depth),
        z: building.z + 1 + Math.floor(this.random() * (building.height - 1))
      });
    }
    
    // Spires/domes for higher levels
    if (this.level >= 3 && this.random() < 0.3) {
      building.details.push({
        type: "spire",
        x: building.x + building.width / 2,
        y: building.y + building.depth / 2,
        z: building.z + building.height
      });
    }
    
    // Flags/antennas for level 4+
    if (this.level >= 4 && this.random() < 0.5) {
      building.details.push({
        type: "antenna",
        x: building.x + building.width / 2,
        y: building.y + building.depth / 2,
        z: building.z + building.height + 2
      });
    }
  }
  
  // ==========================================================================
  // FEATURES (Race-specific landmarks)
  // ==========================================================================
  
  generateFeatures() {
    const featureCount = Math.floor(this.progression.buildings / 10);
    
    for (let feature of this.race.features) {
      this.placeFeature(feature);
    }
  }
  
  placeFeature(featureType) {
    let x = Math.floor(this.random() * this.size);
    let y = Math.floor(this.random() * this.size);
    let z = this.getGroundHeight(x, y);
    
    let feature = {
      type: featureType,
      x: x,
      y: y,
      z: z,
      size: 3 + this.level * 2
    };
    
    this.features.push(feature);
  }
  
  // ==========================================================================
  // DETAILS (Props, vegetation, etc)
  // ==========================================================================
  
  generateDetails() {
    const detailCount = Math.floor(this.size * this.size * this.progression.details / 10);
    
    for (let i = 0; i < detailCount; i++) {
      let x = Math.floor(this.random() * this.size);
      let y = Math.floor(this.random() * this.size);
      let z = this.getGroundHeight(x, y);
      
      // Only place on ground
      if (z > 0 && z < this.size - 1) {
        this.decorations.push({
          type: this.random() < 0.7 ? "vegetation" : "prop",
          x: x,
          y: y,
          z: z,
          variant: Math.floor(this.random() * 3)
        });
      }
    }
  }
  
  // ==========================================================================
  // RENDERING (Simplified - returns render data)
  // ==========================================================================
  
  render() {
    let renderData = {
      terrain: [],
      roads: [],
      buildings: [],
      features: [],
      decorations: [],
      stats: this.getStats()
    };
    
    // Render terrain
    for (let x = 0; x < this.size; x++) {
      for (let y = 0; y < this.size; y++) {
        for (let z = 0; z < this.size; z++) {
          let idx = x + y * this.size + z * this.size * this.size;
          if (this.map[idx] === 1) {
            renderData.terrain.push({x, y, z, color: this.getTerrainColor(z)});
          }
        }
      }
    }
    
    // Render roads
    for (let road of this.roads) {
      renderData.roads.push({
        x: road.x,
        y: road.y,
        z: road.z,
        width: road.width,
        color: "#666666"
      });
    }
    
    // Render buildings
    for (let building of this.buildings) {
      renderData.buildings.push({
        x: building.x,
        y: building.y,
        z: building.z,
        width: building.width,
        depth: building.depth,
        height: building.height,
        color: building.color,
        style: building.style,
        details: building.details
      });
    }
    
    // Render features
    for (let feature of this.features) {
      renderData.features.push(feature);
    }
    
    // Render decorations
    for (let deco of this.decorations) {
      renderData.decorations.push(deco);
    }
    
    return renderData;
  }
  
  getTerrainColor(z) {
    // Simple height-based coloring
    let ratio = z / this.size;
    if (ratio < 0.2) return "#8B4513"; // Dark earth
    if (ratio < 0.4) return "#507D2A"; // Green
    if (ratio < 0.6) return "#A0522D"; // Brown
    return "#F0F0F0"; // Snow/white
  }
  
  getStats() {
    return {
      race: this.race.name,
      level: this.level,
      progression: this.progression.name,
      buildings: this.buildings.length,
      roads: this.roads.length,
      features: this.features.length,
      decorations: this.decorations.length,
      complexity: this.complexity
    };
  }
  
  // ==========================================================================
  // LEVEL UP (Progress city to next tier)
  // ==========================================================================
  
  levelUp() {
    if (this.level < 5) {
      this.level++;
      this.progression = PROGRESSION_LEVELS[this.level];
      this.complexity = this.progression.complexity;
      
      // Add more buildings
      this.generateBuildings();
      this.generateDetails();
      
      return true;
    }
    return false;
  }
}

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

function generateCityExamples() {
  let examples = [];
  
  // Level 1 - Basic US city
  examples.push(new City(20, "united_states", 1));
  
  // Level 3 - Established Japanese city
  examples.push(new City(30, "japan", 3));
  
  // Level 5 - Mastery Squil hive
  examples.push(new City(40, "squid", 5));
  
  // Level 4 - Advanced Prawn fortress
  examples.push(new City(35, "prawn", 4));
  
  // Level 2 - Developing Reaper void
  examples.push(new City(25, "reaper", 2));
  
  return examples;
}

// ============================================================================
// DROIDSCRIPT INTEGRATION
// ============================================================================

function OnStart() {
  // Create a city
  let city = new City(30, "japan", 3);
  
  // Render it
  let renderData = city.render();
  
  // Display stats
  console.log("City Generated:");
  console.log("Race:", renderData.stats.race);
  console.log("Level:", renderData.stats.level);
  console.log("Buildings:", renderData.stats.buildings);
  console.log("Roads:", renderData.stats.roads);
  console.log("Complexity:", renderData.stats.complexity);
  
  // Level up the city
  city.levelUp();
  console.log("After Level Up:", city.getStats());
}

// Export for modules
if (typeof module !== 'undefined') {
  module.exports = { City, RACE_TEMPLATES, PROGRESSION_LEVELS };
}

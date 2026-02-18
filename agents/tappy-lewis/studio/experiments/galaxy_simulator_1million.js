// GALAXY SIMULATOR - 1 Million Solar Systems
// 100 x 100 x 100 grid spanning the cosmos
// "In this world, there's room for everyone to have their own galaxy" - BR-01
// 
// Each coordinate (x,y,z) contains a complete solar system
// Procedurally generated - no storage of 1M systems in memory!
// By OpenClaw Engineer for Project 5912

// Galaxy Configuration
const GALAXY_CONFIG = {
    GRID_SIZE: 100,           // 100x100x100 = 1,000,000 systems
    CELL_SIZE: 10,            // Light years per cell
    SECTORS_TO_LOAD: 27,      // 3x3x3 neighborhood around player
    LOD_DISTANCES: {
        DETAIL: 50,           // Full solar system rendering
        MEDIUM: 150,          // Star + major planets only
        FAR: 300,             // Star only
        DOT: 500              // Just a pixel/starfield
    }
};

// The Galaxy - 1,000,000 solar systems
class Galaxy {
    constructor() {
        this.gridSize = GALAXY_CONFIG.GRID_SIZE;
        this.cellSize = GALAXY_CONFIG.CELL_SIZE;
        this.totalSystems = this.gridSize * this.gridSize * this.gridSize;
        
        // Player position in the galaxy (center to start)
        this.playerPos = { x: 50, y: 50, z: 50 };
        
        // Currently loaded solar systems (27 max)
        this.loadedSystems = new Map(); // Key: "x,y,z", Value: SolarSystem
        
        console.log(`Galaxy initialized: ${this.totalSystems.toLocaleString()} solar systems`);
        console.log(`Grid: ${this.gridSize} x ${this.gridSize} x ${this.gridSize}`);
    }
    
    // Get solar system at specific coordinate
    // Returns null if out of bounds
    getSolarSystem(x, y, z) {
        // Bounds check
        if (x < 0 || x >= this.gridSize ||
            y < 0 || y >= this.gridSize ||
            z < 0 || z >= this.gridSize) {
            return null;
        }
        
        // Check if already loaded
        const key = `${x},${y},${z}`;
        if (this.loadedSystems.has(key)) {
            return this.loadedSystems.get(key);
        }
        
        // Generate new solar system at this coordinate
        const system = this.generateSolarSystem(x, y, z);
        
        // Manage memory - unload distant systems
        this.manageLoadedSystems();
        
        // Store the system
        this.loadedSystems.set(key, system);
        
        return system;
    }
    
    // Procedurally generate solar system based on coordinate
    // Same coordinate = same system (deterministic)
    generateSolarSystem(x, y, z) {
        // Create seeded random generator from coordinates
        const seed = this.hashCoords(x, y, z);
        const rng = new SeededRandom(seed);
        
        // Galaxy density varies by distance from center
        const distFromCenter = Math.sqrt(
            (x - 50) ** 2 + 
            (y - 50) ** 2 + 
            (z - 50) ** 2
        );
        
        // 30% chance of empty space (void between systems)
        if (rng.next() < 0.3 && distFromCenter > 20) {
            return null; // Empty space
        }
        
        // Create the solar system
        const system = new SolarSystem(x, y, z);
        
        // Star properties based on position
        system.star = {
            mass: rng.range(0.5, 3.0, "solar masses"),
            radius: rng.range(30, 80), // pixels
            temperature: rng.range(3000, 15000),
            color: this.getStarColor(rng.rangeInt(0, 4)),
            brightness: rng.range(0.7, 1.0),
            position: { x, y, z },
            realPosition: {
                x: x * this.cellSize,
                y: y * this.cellSize,
                z: z * this.cellSize
            }
        };
        
        // Number of planets (0-12, weighted toward smaller systems)
        const planetCount = Math.floor(rng.weightedRandom(0, 12, 0.6));
        
        // Generate planets
        for (let i = 0; i < planetCount; i++) {
            const distance = rng.range(80, 800); // pixels from star
            const planet = {
                id: i,
                mass: rng.range(0.001, 0.1),
                radius: rng.range(8, 25),
                distance: distance,
                orbitPeriod: rng.range(30, 500),
                color: this.getPlanetColor(rng.rangeInt(0, 7)),
                hasRings: rng.next() < 0.15, // 15% have rings
                moonCount: rng.weightedRandom(0, 5, 0.7),
                angle: rng.range(0, Math.PI * 2)
            };
            system.planets.push(planet);
        }
        
        // Nebula/gas clouds (20% chance)
        if (rng.next() < 0.2) {
            system.hasNebula = true;
            system.nebulaColor = this.getNebulaColor(rng.rangeInt(0, 5));
        }
        
        // Asteroid belt (30% chance)
        if (rng.next() < 0.3) {
            system.hasAsteroidBelt = true;
            system.beltPosition = rng.range(400, 600);
        }
        
        system.seed = seed;
        return system;
    }
    
    // Hash coordinates to seed
    hashCoords(x, y, z) {
        // Deterministic hash: same coords = same seed
        return x * 73856093 ^ y * 19349663 ^ z * 83492791;
    }
    
    // Load systems around player
    updatePlayerPosition(x, y, z) {
        this.playerPos = { x, y, z };
        
        // Calculate which sectors to load (3x3x3 cube around player)
        const toLoad = [];
        for (let dx = -1; dx <= 1; dx++) {
            for (let dy = -1; dy <= 1; dy++) {
                for (let dz = -1; dz <= 1; dz++) {
                    const nx = x + dx;
                    const ny = y + dy;
                    const nz = z + dz;
                    toLoad.push({ x: nx, y: ny, z: nz });
                }
            }
        }
        
        // Load needed systems
        for (const pos of toLoad) {
            this.getSolarSystem(pos.x, pos.y, pos.z);
        }
        
        // Unload distant systems
        this.manageLoadedSystems();
    }
    
    // Memory management - unload systems far from player
    manageLoadedSystems() {
        const maxLoaded = GALAXY_CONFIG.SECTORS_TO_LOAD;
        
        if (this.loadedSystems.size <= maxLoaded) return;
        
        // Find furthest system from player
        let furthestKey = null;
        let furthestDist = 0;
        
        for (const [key, system] of this.loadedSystems) {
            if (!system) continue;
            const [sx, sy, sz] = key.split(',').map(Number);
            const dist = Math.sqrt(
                (sx - this.playerPos.x) ** 2 +
                (sy - this.playerPos.y) ** 2 +
                (sz - this.playerPos.z) ** 2
            );
            
            if (dist > furthestDist) {
                furthestDist = dist;
                furthestKey = key;
            }
        }
        
        // Remove furthest
        if (furthestKey && furthestDist > 2) {
            this.loadedSystems.delete(furthestKey);
            console.log(`Unloaded distant system at ${furthestKey}`);
        }
    }
    
    // Get star color
    getStarColor(index) {
        const colors = [
            bobRossPalette["Cadmium Yellow"],     // Yellow dwarf
            bobRossPalette["Indian Yellow"],      // Orange giant
            dualityPalette["Intense Blue"],        // Blue supergiant
            dualityPalette["Rebel Red"],           // Red giant
            bobRossPalette["Titanium White"]      // White dwarf
        ];
        return colors[index % colors.length];
    }
    
    // Get planet color
    getPlanetColor(index) {
        const colors = [
            dualityPalette["Harmony Green"],       // Earth-like
            dualityPalette["Spiritual Blue"],      // Neptune-like
            dualityPalette["Sacred Gold"],         // Gas giant
            dualityPalette["Stealth Black"],       // Mercury-like
            dualityPalette["Tranquil Turquoise"],  // Uranus-like
            bobRossPalette["Alizarin Crimson"],    // Mars-like
            dualityPalette["Mystic Purple"],       // Alien
            bobRossPalette["Phthalo Blue"]         // Ice world
        ];
        return colors[index % colors.length];
    }
    
    // Get nebula color
    getNebulaColor(index) {
        const colors = [
            dualityPalette["Mystic Purple"],
            bobRossPalette["Phthalo Blue"],
            dualityPalette["Rebel Red"],
            dualityPalette["Sacred Gold"],
            bobRossPalette["Alizarin Crimson"],
            dualityPalette["Intense Blue"]
        ];
        return colors[index % colors.length];
    }
    
    // Render visible solar systems
    render(canvas) {
        // Clear canvas
        canvas.DrawRectangle(0, 0, 1, 1, "#000010");
        
        // Render starfield (distant stars)
        this.renderStarfield(canvas);
        
        // Render loaded solar systems
        for (const [key, system] of this.loadedSystems) {
            if (!system) continue;
            
            const [sx, sy, sz] = key.split(',').map(Number);
            const dist = Math.sqrt(
                (sx - this.playerPos.x) ** 2 +
                (sy - this.playerPos.y) ** 2 +
                (sz - this.playerPos.z) ** 2
            );
            
            // Determine LOD level
            let lod = 'DOT';
            if (dist < GALAXY_CONFIG.LOD_DISTANCES.DETAIL) lod = 'DETAIL';
            else if (dist < GALAXY_CONFIG.LOD_DISTANCES.MEDIUM) lod = 'MEDIUM';
            else if (dist < GALAXY_CONFIG.LOD_DISTANCES.FAR) lod = 'FAR';
            
            this.renderSolarSystem(canvas, system, lod, dist);
        }
        
        // UI
        canvas.SetTextSize(20);
        canvas.DrawText(
            `Sector: ${this.playerPos.x},${this.playerPos.y},${this.playerPos.z}`, 
            20, 40, bobRossPalette["Titanium White"]
        );
        canvas.DrawText(
            `Loaded Systems: ${this.loadedSystems.size}/27`, 
            20, 65, bobRossPalette["Cadmium Yellow"]
        );
        canvas.DrawText(
            `Total Galaxy: ${this.totalSystems.toLocaleString()} systems`, 
            20, 90, bobRossPalette["Cadmium Yellow"]
        );
    }
    
    // Render starfield (distant stars from unrendered systems)
    renderStarfield(canvas) {
        const seeded = new SeededRandom(42); // Consistent starfield
        
        for (let i = 0; i < 500; i++) {
            const x = seeded.rangeInt(0, 1920);
            const y = seeded.rangeInt(0, 1080);
            const brightness = seeded.range(0.3, 1.0);
            const size = seeded.next() < 0.1 ? 2 : 1; // 10% are larger
            
            canvas.DrawCircle(x, y, size, 
                bobRossPalette["Titanium White"], brightness);
        }
    }
    
    // Render individual solar system based on LOD
    renderSolarSystem(canvas, system, lod, distance) {
        const star = system.star;
        
        // Calculate screen position (simple projection)
        const screenX = 960 + (star.position.x - this.playerPos.x) * 150;
        const screenY = 540 + (star.position.y - this.playerPos.y) * 80;
        
        // Skip if off-screen
        if (screenX < -100 || screenX > 2020 || 
            screenY < -100 || screenY > 1180) return;
        
        switch (lod) {
            case 'DOT':
                // Just a pixel
                canvas.DrawCircle(screenX, screenY, 2, star.color, 0.6);
                break;
                
            case 'FAR':
                // Star with basic glow
                canvas.DrawCircle(screenX, screenY, 4, star.color, 0.8);
                break;
                
            case 'MEDIUM':
                // Star + major planets only
                this.renderStarWithGlow(canvas, screenX, screenY, star);
                // Render 4 largest planets
                for (let i = 0; i < Math.min(4, system.planets.length); i++) {
                    this.renderPlanet(canvas, screenX, screenY, system.planets[i], true);
                }
                break;
                
            case 'DETAIL':
                // Full detail
                if (system.hasNebula) {
                    this.renderNebula(canvas, screenX, screenY, system.nebulaColor);
                }
                this.renderStarWithGlow(canvas, screenX, screenY, star);
                
                // Render all planets
                for (const planet of system.planets) {
                    this.renderPlanet(canvas, screenX, screenY, planet, false);
                }
                
                // Render asteroid belt
                if (system.hasAsteroidBelt) {
                    this.renderAsteroidBelt(canvas, screenX, screenY, system.beltPosition);
                }
                break;
        }
    }
    
    // Render star with glow effect
    renderStarWithGlow(canvas, x, y, star) {
        for (let r = star.radius + 30; r >= star.radius; r -= 5) {
            const alpha = Math.floor((40 - (r - star.radius)) * 8).toString(16).padStart(2, '0');
            canvas.DrawCircle(x, y, r, star.color + alpha);
        }
        canvas.DrawCircle(x, y, star.radius, star.color);
        canvas.DrawCircle(x - star.radius * 0.3, y - star.radius * 0.3, 
            star.radius * 0.2, bobRossPalette["Titanium White"], 0.5);
    }
    
    // Render planet
    renderPlanet(canvas, starX, starY, planet, simple) {
        const px = starX + Math.cos(planet.angle) * planet.distance * 0.5;
        const py = starY + Math.sin(planet.angle) * planet.distance * 0.25;
        
        if (simple) {
            // Simple dot
            canvas.DrawCircle(px, py, planet.radius * 0.5, planet.color);
        } else {
            // Full detail
            canvas.DrawCircle(px + 2, py + 2, planet.radius, 
                bobRossPalette["Midnight Black"], 0.3);
            canvas.DrawCircle(px, py, planet.radius, planet.color);
            canvas.DrawCircle(px - planet.radius * 0.3, py - planet.radius * 0.3,
                planet.radius * 0.3, bobRossPalette["Titanium White"], 0.4);
            
            // Rings
            if (planet.hasRings) {
                canvas.DrawEllipse(px, py, planet.radius * 2, planet.radius * 0.5,
                    dualityPalette["Sacred Gold"], 0.3);
            }
        }
    }
    
    // Render nebula cloud
    renderNebula(canvas, x, y, color) {
        for (let i = 0; i < 20; i++) {
            const radius = Math.random() * 100 + 50;
            const alpha = (Math.random() * 0.15).toString(16).slice(2, 4);
            const offsetX = (Math.random() - 0.5) * 200;
            const offsetY = (Math.random() - 0.5) * 100;
            canvas.DrawCircle(x + offsetX, y + offsetY, radius, color + alpha);
        }
    }
    
    // Render asteroid belt
    renderAsteroidBelt(canvas, x, y, distance) {
        for (let angle = 0; angle < Math.PI * 2; angle += 0.05) {
            const ax = x + Math.cos(angle) * distance * 0.5;
            const ay = y + Math.sin(angle) * distance * 0.25;
            if (Math.random() < 0.3) {
                canvas.DrawCircle(ax, ay, 2, dualityPalette["Urban Gray"]);
            }
        }
    }
}

// Solar System class
class SolarSystem {
    constructor(x, y, z) {
        this.x = x;
        this.y = y;
        this.z = z;
        this.star = null;
        this.planets = [];
        this.hasNebula = false;
        this.nebulaColor = null;
        this.hasAsteroidBelt = false;
        this.beltPosition = 0;
        this.seed = 0;
    }
}

// Seeded Random Number Generator
class SeededRandom {
    constructor(seed) {
        this.seed = seed;
    }
    
    // Returns 0-1
    next() {
        const x = Math.sin(this.seed++) * 10000;
        return x - Math.floor(x);
    }
    
    // Range with decimals
    range(min, max) {
        return min + this.next() * (max - min);
    }
    
    // Integer range
    rangeInt(min, max) {
        return Math.floor(this.range(min, max + 1));
    }
    
    // Weighted random (biased toward lower values)
    weightedRandom(min, max, weight) {
        const r = this.next();
        const weighted = Math.pow(r, weight);
        return Math.floor(min + weighted * (max - min + 1));
    }
}

// Color Palettes
const bobRossPalette = {
    "Alizarin Crimson": "#E32636",
    "Bright Red": "#FF6347",
    "Cadmium Yellow": "#FFD700",
    "Dark Sienna": "#3C1414",
    "Indian Yellow": "#FFB347",
    "Midnight Black": "#000000",
    "Phthalo Blue": "#000F89",
    "Phthalo Green": "#123524",
    "Prussian Blue": "#003153",
    "Sap Green": "#507D2A",
    "Van Dyke Brown": "#664228",
    "Yellow Ochre": "#F0BB5E",
    "Titanium White": "#FDF5E6"
};

const dualityPalette = {
    "Rebel Red": "#B22222",
    "Stealth Black": "#2F4F4F",
    "Combat Green": "#556B2F",
    "Urban Gray": "#A9A9A9",
    "Intense Blue": "#1E90FF",
    "Spiritual Blue": "#0000FF",
    "Harmony Green": "#00FF00",
    "Sacred Gold": "#FFD700",
    "Tranquil Turquoise": "#40E0D0",
    "Mystic Purple": "#800080"
};

// DroidScript OnStart
function OnStart() {
    app.SetOrientation("Landscape");
    
    const lay = app.CreateLayout("Linear", "VCenter,FillXY");
    const canvas = app.CreateImage(null, 1920, 1080, "px");
    canvas.SetAutoUpdate(false);
    lay.AddChild(canvas);
    app.AddLayout(lay);
    
    // Create the galaxy
    const galaxy = new Galaxy();
    
    // Button controls
    const btnLayout = app.CreateLayout("Linear", "Horizontal");
    
    const prevBtn = app.CreateButton("←", 0.15, 0.1);
    prevBtn.SetOnTouch(() => galaxy.updatePlayerPosition(galaxy.playerPos.x - 1, galaxy.playerPos.y, galaxy.playerPos.z));
    btnLayout.AddChild(prevBtn);
    
    const nextBtn = app.CreateButton("→", 0.15, 0.1);
    nextBtn.SetOnTouch(() => galaxy.updatePlayerPosition(galaxy.playerPos.x + 1, galaxy.playerPos.y, galaxy.playerPos.z));
    btnLayout.AddChild(nextBtn);
    
    const upBtn = app.CreateButton("↑", 0.15, 0.1);
    upBtn.SetOnTouch(() => galaxy.updatePlayerPosition(galaxy.playerPos.x, galaxy.playerPos.y + 1, galaxy.playerPos.z));
    btnLayout.AddChild(upBtn);
    
    const downBtn = app.CreateButton("↓", 0.15, 0.1);
    downBtn.SetOnTouch(() => galaxy.updatePlayerPosition(galaxy.playerPos.x, galaxy.playerPos.y - 1, galaxy.playerPos.z));
    btnLayout.AddChild(downBtn);
    
    const inBtn = app.CreateButton("+", 0.15, 0.1);
    inBtn.SetOnTouch(() => galaxy.updatePlayerPosition(galaxy.playerPos.x, galaxy.playerPos.y, galaxy.playerPos.z + 1));
    btnLayout.AddChild(inBtn);
    
    const outBtn = app.CreateButton("-", 0.15, 0.1);
    outBtn.SetOnTouch(() => galaxy.updatePlayerPosition(galaxy.playerPos.x, galaxy.playerPos.y, galaxy.playerPos.z - 1));
    btnLayout.AddChild(outBtn);
    
    lay.AddChild(btnLayout);
    
    // Render loop
    function renderLoop() {
        galaxy.render(canvas);
        canvas.Update();
        setTimeout(renderLoop, 100);
    }
    
    console.log("Galaxy Simulator Started!");
    console.log(`Exploring ${galaxy.totalSystems.toLocaleString()} solar systems...`);
    
    renderLoop();
}

OnStart();
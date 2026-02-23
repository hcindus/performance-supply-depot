// BR-01 Art Studio: Solar System Generator
// "There are no mistakes, just happy little planets" - Bob Ross
// DroidScript app with Bob Ross + BR-X (Duality) color palettes
// by OpenClaw Engineer for Tappy Lewis / BR-01

// Initialize the application
function OnStart() 
{
    // Set orientation to landscape
    app.SetOrientation("Landscape");
    
    // Define layout
    let lay = app.CreateLayout("Linear", "VCenter,FillXY");
    
    // Define image for drawing (full HD canvas)
    let image = app.CreateImage(null, 1920, 1080, "px");
    image.SetAutoUpdate(true);
    image.SetBackColor(bob_ross_palette["Prussian Blue"]); // Deep space blue
    lay.AddChild(image);
    
    // Add layout to app
    app.AddLayout(lay);
    
    // Initialize the solar system
    let solarSystem = new SolarSystem();
    solarSystem.generate();
    
    // Render the solar system on canvas
    RenderSolarSystem(image, solarSystem);
    
    // Show completion message
    console.log("Solar system rendered! Happy little planets everywhere.");
}

// Bob Ross color palette - for stars and nebula
const bob_ross_palette = {
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

// BR-X Duality color palette - for planets and special effects
const duality_palette = {
    "Rebel Red": "#B22222",
    "Stealth Black": "#2F4F4F",
    "Combat Green": "#556B2F",
    "Urban Gray": "#A9A9A9",
    "Intense Blue": "#1E90FF",
    "Yellow Ochre": "#F0BB5E",
    "Titanium White": "#FDF5E6",
    "Pure White": "#FFFFFF",
    "Spiritual Blue": "#0000FF",
    "Harmony Green": "#00FF00",
    "Sacred Gold": "#FFD700",
    "Tranquil Turquoise": "#40E0D0",
    "Grounded Earth": "#8B4513",
    "Mystic Purple": "#800080",
    "Rebel Red": "#B22222",
    "Stealth Black": "#2F4F4F",
    "Intense Blue": "#1E90FF"
};

// Solar System class - handles generation logic
class SolarSystem {
    constructor() {
        this.bodies = [];
        this.centerX = 960;  // Center of 1920px width
        this.centerY = 540;  // Center of 1080px height
    }
    
    addStar(mass, radius, temperature) {
        let color = this.getStarColor(temperature);
        this.bodies.push({
            type: "star",
            mass: mass,
            radius: radius,
            temperature: temperature,
            color: color,
            x: this.centerX,
            y: this.centerY
        });
    }
    
    addPlanet(mass, radius, distance, orbitPeriod) {
        let color = this.getPlanetColor(distance);
        let angle = Math.random() * Math.PI * 2; // Random position in orbit
        this.bodies.push({
            type: "planet",
            mass: mass,
            radius: radius,
            distance: distance,
            orbitPeriod: orbitPeriod,
            color: color,
            angle: angle
        });
    }
    
    generate() {
        // Create our star - the center of everything
        // "Every star needs a friend... or 1-8 planets"
        let mass = Math.random() * 2 + 0.5;
        let radius = Math.random() * 40 + 30; // 30-70px star
        let temperature = Math.random() * 10000 + 5000;
        this.addStar(mass, radius, temperature);
        
        // Create 1-8 happy little planets
        let numPlanets = Math.floor(Math.random() * 8) + 1;
        console.log("Creating " + numPlanets + " happy little planets...");
        
        for (let i = 0; i < numPlanets; i++) {
            let mass = Math.random() * 0.01 + 0.001;
            let radius = Math.random() * 15 + 8; // 8-23px planets
            let distance = (i * 80) + 120 + Math.random() * 40; // Spaced out orbits
            let orbitPeriod = Math.random() * 365 + 30;
            this.addPlanet(mass, radius, distance, orbitPeriod);
        }
    }
    
    getStarColor(temperature) {
        // Hotter stars are bluer, cooler are redder
        if (temperature < 6000) {
            return bob_ross_palette["Indian Yellow"]; // Cool star (orange)
        } else if (temperature < 8000) {
            return bob_ross_palette["Cadmium Yellow"]; // Medium star (yellow)
        } else if (temperature < 10000) {
            return bob_ross_palette["Titanium White"]; // Hot star (white)
        } else {
            return duality_palette["Intense Blue"]; // Very hot (blue)
        }
    }
    
    getPlanetColor(distance) {
        // Inner planets: warm colors
        // Outer planets: cool colors
        if (distance < 300) {
            return duality_palette["Harmony Green"]; // Close, habitable
        } else if (distance < 500) {
            return duality_palette["Spiritual Blue"]; // Mid-range
        } else {
            return duality_palette["Sacred Gold"]; // Far out
        }
    }
}

// Render the solar system to the canvas
function RenderSolarSystem(image, solarSystem) {
    // Clear canvas with deep space background
    image.DrawRectangle(0, 0, 1, 1, bob_ross_palette["Prussian Blue"]);
    
    // Draw some happy little stars in the background
    DrawBackgroundStars(image);
    
    // Get our star
    let star = solarSystem.bodies[0];
    
    // Draw the star with glow effect
    // "Let's give our star a nice glow - it's the center of attention"
    for (let r = star.radius + 20; r >= star.radius; r -= 2) {
        let alpha = Math.floor((20 - (r - star.radius)) * 10).toString(16).padStart(2, '0');
        image.DrawCircle(star.x, star.y, r, star.color + alpha);
    }
    
    // Draw the solid star
    image.DrawCircle(star.x, star.y, star.radius, star.color);
    image.DrawCircle(star.x - star.radius * 0.3, star.y - star.radius * 0.3, star.radius * 0.2, 
        bob_ross_palette["Titanium White"], 0.5); // Highlight
    
    // Draw each happy little planet
    for (let i = 1; i < solarSystem.bodies.length; i++) {
        let planet = solarSystem.bodies[i];
        
        // Calculate position based on orbit angle
        let px = star.x + Math.cos(planet.angle) * planet.distance;
        let py = star.y + Math.sin(planet.angle) * planet.distance * 0.4; // Flattened orbit
        
        // Draw orbit path
        DrawOrbit(image, star.x, star.y, planet.distance, bob_ross_palette["Phthalo Blue"] + "40");
        
        // Draw planet with shadow for 3D effect
        // "Every planet needs a shadow side - that's where the mystery lives"
        image.DrawCircle(px + 2, py + 2, planet.radius, bob_ross_palette["Midnight Black"], 0.3);
        image.DrawCircle(px, py, planet.radius, planet.color);
        
        // Add highlight
        image.DrawCircle(px - planet.radius * 0.3, py - planet.radius * 0.3, planet.radius * 0.3,
            bob_ross_palette["Titanium White"], 0.4);
        
        // Occasionally add a moon
        if (Math.random() > 0.5) {
            let moonAngle = Math.random() * Math.PI * 2;
            let moonDistance = planet.radius + 5;
            let mx = px + Math.cos(moonAngle) * moonDistance;
            let my = py + Math.sin(moonAngle) * moonDistance;
            image.DrawCircle(mx, my, 3, duality_palette["Urban Gray"]);
        }
    }
    
    // Draw title
    image.SetTextSize(24);
    image.DrawText("BR-01 PRESENTS: HAPPY LITTLE SOLAR SYSTEM", 20, 40, 
        bob_ross_palette["Titanium White"]);
    image.SetTextSize(16);
    image.DrawText("Generated with Bob Ross + BR-X Duality palettes", 20, 65,
        bob_ross_palette["Cadmium Yellow"]);
    
    // Update the image
    image.Update();
}

// Draw orbit ellipse
function DrawOrbit(image, cx, cy, distance, color) {
    for (let angle = 0; angle < Math.PI * 2; angle += 0.02) {
        let x = cx + Math.cos(angle) * distance;
        let y = cy + Math.sin(angle) * distance * 0.4;
        image.DrawCircle(x, y, 1, color);
    }
}

// Draw background stars
function DrawBackgroundStars(image) {
    // "Let's put some happy little stars twinkling in the background"
    let numStars = Math.floor(Math.random() * 200) + 100;
    
    for (let i = 0; i < numStars; i++) {
        let x = Math.random() * 1920;
        let y = Math.random() * 1080;
        let size = Math.random() * 2 + 1;
        let brightness = Math.random() * 0.5 + 0.5;
        
        // Random star colors from Bob Ross palette
        let colors = [
            bob_ross_palette["Titanium White"],
            bob_ross_palette["Cadmium Yellow"],
            bob_ross_palette["Indian Yellow"],
            duality_palette["Sacred Gold"]
        ];
        let color = colors[Math.floor(Math.random() * colors.length)];
        
        image.DrawCircle(x, y, size, color, brightness);
    }
}

// Start the application
OnStart();

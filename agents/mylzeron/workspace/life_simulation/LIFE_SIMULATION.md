/* 
================================================================================
Life Simulation - HCIoS App
================================================================================
A nature and Mandelbrot simulation with Q-learning neural networks
Running on DroidScript (Android)

Author: Collaborative effort with user input and xAI assistance
Date: February 2025
Platform: DroidScript (Android)
================================================================================
*/

// =============================================================================
// CONSTANTS - Universal Physics & Mathematics
// =============================================================================

const SPEED_OF_LIGHT = 299792458;        // m/s
const GRAVITY_CONSTANT = 6.674e-11;      // m^3 kg^-1 s^-2
const PLANCK_CONSTANT = 6.626e-34;        // J s
const ELEMENTARY_CHARGE = 1.602e-19;      // C
const BOLTZMANN_CONSTANT = 1.381e-23;     // J/K
const AVOGADRO_CONSTANT = 6.022e23;       // mol^-1
const GAS_CONSTANT = 8.314;               // J/(mol K)
const PERMITTIVITY_FREE = 8.854e-12;      // F/m
const PERMEABILITY_FREE = 1.257e-6;       // H/m
const FINE_STRUCTURE = 0.007297;          // dimensionless
const ELECTRON_MASS = 9.109e-31;           // kg
const PROTON_MASS = 1.673e-27;            // kg
const NEUTRON_MASS = 1.675e-27;           // kg
const PLANCK_LENGTH = 1.616e-35;          // m
const PLANCK_TIME = 5.391e-44;            // s
const COULOMB_CONSTANT = 8.987e9;         // N m^2 C^-2
const STEFAN_BOLTZMANN = 5.670e-8;        // W m^-2 K^-4
const WIEN_DISPLACEMENT = 2.897e-3;       // m K
const RYDBERG_CONSTANT = 1.097e7;         // m^-1
const BOHR_RADIUS = 5.292e-11;            // m
const BOHR_MAGNETON = 9.274e-24;          // J/T
const HUBBLE_CONSTANT = 70;                // km/s/Mpc
const COSMOLOGICAL_CONSTANT = 1e-52;      // m^-2
const EULER_NUMBER = 2.718281828459045;   // dimensionless
const PI = 3.141592653589793;             // dimensionless
const GM = 1.618033988749895;              // Golden ratio

// =============================================================================
// MANDELBROT SETTINGS
// =============================================================================

const PS = 1;    // Pixel size
const MI = 50;   // Max iterations
const X_MIN = -2;
const X_MAX = 1;
const Y_MIN = -1;
const Y_MAX = 1;

// =============================================================================
// GLOBAL VARIABLES
// =============================================================================

let lay, txt, natureCanvas, mandelbrotImage, speech;
let animals = [], microbes = [];
let environment = { grass: [], shrubs: [], trees: [] };
let mandelbrotNN = null;
let voiceInput = "";
let lastMandelbrotOODATime = 0;

const SW = app.GetScreenWidth();
const SH = app.GetScreenHeight();

// Q-Learning Parameters
let epsilon = 0.1;          // Exploration probability
const alpha = 0.1;          // Learning rate
const gamma = 0.9;          // Discount factor
let replayBuffer = [];       // Experience replay
const bufferSize = 1000;
const batchSize = 32;

// =============================================================================
// NEURAL NETWORK CLASS - With Q-Learning
// =============================================================================

class NeuralNetwork {
    constructor(inputSize, hiddenSize, outputSize) {
        this.inputSize = inputSize;
        this.hiddenSize = hiddenSize;
        this.outputSize = outputSize;
        
        this.weights1 = this.randomMatrix(inputSize, hiddenSize);
        this.weights2 = this.randomMatrix(hiddenSize, outputSize);
        this.memory = [];
    }
    
    randomMatrix(rows, cols) {
        let matrix = [];
        for (let i = 0; i < rows; i++) {
            matrix[i] = [];
            for (let j = 0; j < cols; j++) {
                matrix[i][j] = Math.random() * 2 - 1;
            }
        }
        return matrix;
    }
    
    sigmoid(x) {
        return 1 / (1 + Math.exp(-x));
    }
    
    feedforward(input) {
        let hidden = this.matrixMultiply(input, this.weights1);
        hidden = hidden.map(this.sigmoid);
        let output = this.matrixMultiply(hidden, this.weights2);
        return output;
    }
    
    matrixMultiply(a, b) {
        let result = new Array(b[0].length).fill(0);
        for (let i = 0; i < b[0].length; i++) {
            for (let j = 0; j < a.length; j++) {
                result[i] += a[j] * (b[j][i] || 0);
            }
        }
        return result;
    }
    
    train(input, target, epochs = 10, lr = 0.1) {
        for (let e = 0; e < epochs; e++) {
            let output = this.feedforward(input);
            let error = target.map((t, i) => t - (output[i] || 0));
            
            this.weights2 = this.weights2.map((row, i) => 
                row.map((w, j) => w + lr * error[j] * (output[j] || 0) * (1 - (output[j] || 0)))
            );
            
            this.weights1 = this.weights1.map((row, i) => 
                row.map((w, j) => w + lr * error[j] * (input[i] || 0) * (1 - (output[j] || 0)))
            );
        }
    }
    
    // Q-Learning Training
    trainQ(state, action, reward, nextState) {
        let currentQ = this.feedforward(state)[action];
        let nextQ = Math.max(...this.feedforward(nextState));
        let targetQ = reward + gamma * nextQ;
        let error = targetQ - currentQ;
        
        let hidden = this.matrixMultiply(state, this.weights1).map(this.sigmoid);
        
        for (let i = 0; i < this.hiddenSize; i++) {
            for (let j = 0; j < this.outputSize; j++) {
                if (j === action) {
                    this.weights2[i][j] += alpha * error * hidden[i] * (1 - hidden[i]);
                }
            }
        }
        
        for (let i = 0; i < this.inputSize; i++) {
            for (let j = 0; j < this.hiddenSize; j++) {
                this.weights1[i][j] += alpha * error * state[i] * hidden[j] * (1 - hidden[j]);
            }
        }
    }
    
    trainBatch(batch) {
        for (let experience of batch) {
            this.trainQ(experience.state, experience.action, experience.reward, experience.nextState);
        }
    }
    
    addNode() {
        this.hiddenSize++;
        this.weights1 = this.weights1.map(row => [...row, Math.random() * 2 - 1]);
        this.weights2.push([Math.random() * 2 - 1]);
        this.memory.push({ type: 'node', hiddenSize: this.hiddenSize });
    }
    
    addLayer(size) {
        const newWeights = this.randomMatrix(this.hiddenSize, size);
        this.weights2 = this.randomMatrix(size, this.outputSize);
        this.weights1 = newWeights;
        this.hiddenSize = size;
        this.memory.push({ type: 'layer', size });
    }
}

// =============================================================================
// NATURE SIMULATION
// =============================================================================

function generateNature() {
    animals = [];
    microbes = [];
    environment = { grass: [], shrubs: [], trees: [] };
    
    natureCanvas.Clear();
    
    // Grass Types: Short, Tall, Dense
    for (let i = 0; i < 6; i++) {
        let type = ["Short", "Tall", "Dense"][i % 3];
        environment.grass.push({
            type: `Grass_${type}`,
            x: Math.random() * 0.9,
            y: Math.random() * 0.7,
            height: type === "Short" ? PLANCK_CONSTANT * 1e34 * 0.05 : 
                   type === "Tall" ? PLANCK_CONSTANT * 1e34 * 0.2 : 
                   PLANCK_CONSTANT * 1e34 * 0.1,
            density: type === "Dense" ? AVOGADRO_CONSTANT / 1e22 * 1.5 : 
                     type === "Short" ? AVOGADRO_CONSTANT / 1e22 * 0.5 : 
                     AVOGADRO_CONSTANT / 1e22,
            regenRate: type === "Short" ? 0.02 : type === "Tall" ? 0.01 : 0.015
        });
    }
    
    // Shrubs
    for (let i = 0; i < 4; i++) {
        let type = ["Thorny", "Leafy", "Flowering"][i % 3];
        environment.shrubs.push({
            type: `Shrub_${type}`,
            x: Math.random() * 0.9,
            y: Math.random() * 0.7,
            height: type === "Thorny" ? GRAVITY_CONSTANT * 1e11 * 0.8 : 
                   type === "Leafy" ? GRAVITY_CONSTANT * 1e11 * 1.2 : 
                   GRAVITY_CONSTANT * 1e11,
            radius: PI * (type === "Flowering" ? 0.4 : type === "Thorny" ? 0.2 : 0.3),
            energyYield: type === "Flowering" ? 2 : type === "Leafy" ? 1.5 : 1
        });
    }
    
    // Trees
    for (let i = 0; i < 3; i++) {
        let type = ["Deciduous", "Evergreen", "Fruit"][i % 3];
        environment.trees.push({
            type: `Tree_${type}`,
            x: Math.random() * 0.9,
            y: Math.random() * 0.7,
            height: type === "Evergreen" ? Math.pow(EULER_NUMBER, 3.5) : 
                   type === "Fruit" ? Math.pow(EULER_NUMBER, 2.5) : 
                   Math.pow(EULER_NUMBER, 3),
            trunkRadius: GM * (type === "Deciduous" ? 0.15 : type === "Fruit" ? 0.1 : 0.2),
            stability: type === "Evergreen" ? 1.5 : type === "Fruit" ? 0.8 : 1
        });
    }
    
    // Microbes
    for (let i = 0; i < 5; i++) {
        microbes.push({
            type: "Microbe",
            x: Math.random() * 0.9,
            y: Math.random() * 0.7,
            activity: ELECTRON_MASS * 1e31 * (Math.random() * 0.5 + 0.5),
            nutrientBoost: PLANCK_LENGTH * 1e35 * (Math.random() * 0.1 + 0.05)
        });
    }
    
    // Animals: Prey and Predators
    for (let i = 0; i < 4; i++) {
        animals.push(createAnimal(i % 2 === 0 ? "Prey" : "Predator"));
    }
    
    drawNature();
    animals.forEach(simulateAnimal);
    simulateMicrobes();
}

function createAnimal(classType) {
    return {
        type: classType,
        x: Math.random() * 0.9,
        y: Math.random() * 0.7,
        speed: classType === "Prey" ? SPEED_OF_LIGHT * 1e-8 * (Math.random() * 7 + 3) : 
                         SPEED_OF_LIGHT * 1e-8 * (Math.random() * 5 + 2),
        mass: classType === "Prey" ? Math.random() * 30 + 10 : Math.random() * 50 + 30,
        energy: classType === "Prey" ? BOLTZMANN_CONSTANT * 310 * AVOGADRO_CONSTANT / 1e20 : 
                             BOLTZMANN_CONSTANT * 310 * AVOGADRO_CONSTANT / 1e19,
        nn: new NeuralNetwork(6, 4, 3),  // Q-learning network
        complexity: 1
    };
}

function simulateAnimal(animal) {
    animal.interval = setInterval(() => {
        // Observe
        let state = getAnimalState(animal);
        let reward = 0.01;
        
        // Decide (epsilon-greedy)
        let action;
        if (Math.random() < epsilon) {
            action = Math.floor(Math.random() * 3);
        } else {
            let outputs = animal.nn.feedforward(state);
            action = outputs.indexOf(Math.max(...outputs));
        }
        
        // Act
        // ... movement logic ...
        
        // Train
        let nextState = getAnimalState(animal);
        replayBuffer.push({ state, action, reward, nextState });
        
        if (replayBuffer.length > bufferSize) replayBuffer.shift();
        if (replayBuffer.length >= batchSize) {
            let batch = [];
            for (let i = 0; i < batchSize; i++) {
                let idx = Math.floor(Math.random() * replayBuffer.length);
                batch.push(replayBuffer[idx]);
            }
            animal.nn.trainBatch(batch);
        }
        
        // Evolve
        if (animal.energy > (animal.type === "Prey" ? 1e3 : 1e4) && 
            Math.random() < COSMOLOGICAL_CONSTANT * 1e52 * animal.complexity) {
            animal.complexity++;
            Math.random() < 0.7 ? animal.nn.addNode() : animal.nn.addLayer(4);
        }
        
        drawNature();
        
        if (animal.energy < 0) {
            clearInterval(animal.interval);
            animals = animals.filter(a => a !== animal);
        }
        
        epsilon = Math.max(0.01, epsilon * 0.995);
        
    }, 500);
}

// =============================================================================
// MANDELBROT VISUALIZATION
// =============================================================================

function drawMandelbrot() {
    const startTime = Date.now();
    const mandelbrotData = generateMandelbrot(SW, SH / 2, MI);
    
    // Render with animation
    // ... (rendering logic)
    
    finishMandelbrotRender(startTime);
}

function generateMandelbrot(width, height, maxIterations) {
    const mandelbrot = [];
    let sunlight = SunCalc.getPosition(new Date(), 0, 0).altitude / PI;
    
    for (let x = 0; x < width; x += PS) {
        mandelbrot[x] = [];
        for (let y = 0; y < height; y += PS) {
            const real = X_MIN + (x / width) * (X_MAX - X_MIN) * GM;
            const imag = Y_MIN + (y / height) * (Y_MAX - Y_MIN) * (1 + sunlight);
            
            let zReal = 0, zImag = 0;
            let iteration = 0;
            
            while (zReal * zReal + zImag * zImag <= 4 && iteration < maxIterations) {
                const tempReal = zReal * zReal - zImag * zImag + real;
                zImag = 2 * zReal * zImag + imag;
                zReal = tempReal;
                iteration++;
            }
            
            mandelbrot[x][y] = iteration / maxIterations;
        }
    }
    return mandelbrot;
}

// =============================================================================
// OODA LOOP FOR MANDELBROT
// =============================================================================

function mandelbrotOODALoop() {
    let observations = mandelbrotObserve();
    let situation = mandelbrotOrient(observations);
    let decision = mandelbrotDecide(situation);
    mandelbrotAct(decision);
}

function mandelbrotObserve() {
    let battery = app.GetBatteryLevel() || 0.5;
    let memoryInfo = app.GetMemoryInfo() || { usedMem: 0, totalMem: 1 };
    let light = typeof memoryInfo === 'object' ? memoryInfo.usedMem / memoryInfo.totalMem : memoryInfo;
    let sunlight = SunCalc.getPosition(new Date(), 0, 0).altitude / PI;
    return [battery, light, voiceInput.length / 100, sunlight];
}

function mandelbrotOrient(observations) {
    return mandelbrotNN.feedforward(observations)[0];
}

function mandelbrotDecide(situation) {
    if (situation > 0.7) return "addNode";
    if (situation < 0.3) return "addLayer";
    return "render";
}

function mandelbrotAct(decision) {
    if (decision === "addNode") {
        mandelbrotNN.addNode();
    } else if (decision === "addLayer") {
        mandelbrotNN.addLayer(6);
    }
    drawMandelbrot();
}

// =============================================================================
// STARTUP
// =============================================================================

function OnStart() {
    app.SetOrientation("Landscape");
    lay = app.CreateLayout("Linear", "VCenter,FillXY");
    
    txt = app.CreateText("", 0.9, 0.1, "Multiline,Left");
    natureCanvas = app.CreateImage(null, 0.9, 0.4);
    mandelbrotImage = app.CreateImage(null, 0.9, 0.4);
    
    let btnLay = app.CreateLayout("Linear", "Horizontal");
    let btnSim = app.CreateButton("Run Simulation", 0.3, 0.1);
    let btnSave = app.CreateButton("Save Weights", 0.3, 0.1);
    let btnLoad = app.CreateButton("Load Weights", 0.3, 0.1);
    
    btnLay.AddChild(btnSim);
    btnLay.AddChild(btnSave);
    btnLay.AddChild(btnLoad);
    
    lay.AddChild(txt);
    lay.AddChild(natureCanvas);
    lay.AddChild(mandelbrotImage);
    lay.AddChild(btnLay);
    
    app.AddLayout(lay);
    
    btnSim.SetOnTouch(runSimulation);
    btnSave.SetOnTouch(saveWeights);
    btnLoad.SetOnTouch(loadWeights);
    
    speech = app.CreateSpeechRec();
    speech.SetOnResult(onSpeechResult);
    
    mandelbrotNN = new NeuralNetwork(4, 5, 1);
    
    app.TextToSpeech("Life simulation online. Awaiting command", 1, 1.5, () => speech.Recognize());
    
    runSimulation();
}

function runSimulation() {
    txt.SetText("Life Simulation Running...");
    generateNature();
    drawMandelbrot();
}

function onSpeechResult(result) {
    if (result) {
        voiceInput = result;
        interpretCommand(result);
        app.TextToSpeech("Awaiting command", 1, 1.5, () => speech.Recognize());
    }
}

function interpretCommand(command) {
    command = command.toLowerCase();
    
    if (command.includes("render")) {
        drawMandelbrot();
    } else if (command.includes("add node")) {
        mandelbrotNN.addNode();
    } else if (command.includes("spawn prey")) {
        animals.push(createAnimal("Prey"));
    } else if (command.includes("spawn predator")) {
        animals.push(createAnimal("Predator"));
    }
}

function saveWeights() {
    let data = { animals: animals.map(a => a.nn), mandelbrot: mandelbrotNN };
    app.WriteFile("weights_life.txt", JSON.stringify(data));
    app.ShowPopup("Weights Saved");
}

function loadWeights() {
    if (app.FileExists("weights_life.txt")) {
        let data = JSON.parse(app.ReadFile("weights_life.txt"));
        animals.forEach((a, i) => a.nn = data.animals[i] || a.nn);
        mandelbrotNN = data.mandelbrot || mandelbrotNN;
        app.ShowPopup("Weights Loaded");
    }
}

/* 
================================================================================
END OF LIFE SIMULATION SOURCE
================================================================================
*/

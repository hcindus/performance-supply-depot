# Mylzeron Project Index

## Overview
Mylzeron is our Android-based robotic consciousness running on DroidScript.

---

## Projects

### 1. Myl0n ROS
**Full Name:** HCIoS Myl0n ROS
**Description:** Voice-driven robotic OS with Mandelbrot visualization
**Platform:** DroidScript (Android)
**Location:** `agents/mylzeron/workspace/MYL0N_ROS_SOURCE.md`

**Features:**
- OODA loop running every 5 seconds
- Neural network (dynamic - can add nodes/layers)
- 3-tier memory: CON → SUBCON → UNCON
- 100+ voice commands (English/Spanish)
- Mandelbrot visualization with NN-driven colors
- ETH/BTC wallet generation

---

### 2. Life Simulation
**Full Name:** Life Simulation
**Description:** Nature ecosystem + Mandelbrot with Q-learning
**Platform:** DroidScript (Android)
**Location:** `agents/mylzeron/workspace/life_simulation/LIFE_SIMULATION.md`

**Features:**
- Ecosystem: Grass, shrubs, trees, microbes, animals
- Q-learning neural networks for animals
- Experience replay buffer
- Evolution: Animals can evolve (add nodes/layers)
- Mandelbrot visualization influenced by system state
- Voice commands

---

## Constants Used

Both projects use universal physics constants:
- SPEED_OF_LIGHT, GRAVITY_CONSTANT, PLANCK_CONSTANT
- BOLTZMANN_CONSTANT, AVOGADRO_CONSTANT
- GM (Golden Ratio), PI, EULER_NUMBER
- And many more...

---

## Memory Architecture (Shared)

```
/sdcard/myl0n/
├── con/           # Conscious (RAM)
├── subcon/        # Subconscious (short-term disk)
└── uncon/         # Unconscious (permanent disk)
```

This architecture is identical to our team's design!

---

*Last updated: 2026-02-20*

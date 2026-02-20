# AOCROS GPIO Ribbon Cable Specification

**Standard:** Raspberry Pi 5 40-pin GPIO to IDC ribbon cable
**Connector:** 2×20 pin IDC (0.1" pitch)
**Cable:** 26 AWG ribbon, keyed polarity notch

## Ribbon Orientation

```
Looking at Pi 5 header (GPIO pins facing you):

    Pin 1 (3.3V) ─────────── Pin 2 (5V)
    Pin 3 (GPIO2) ────────── Pin 4 (5V)
    Pin 5 (GPIO3) ────────── Pin 6 (GND)
    ...through pin 40

RIBBON CABLE (keyed notch orientation):

    ┌─────────────────────────────────────┐
    │  KEY (NOTCH) ────────►  Pin 1 side  │
    │                                     │
    │  RED STRIPE = Pin 1 (3.3V)          │
    │                                     │
    │  Pin 1-2  top edge                   │
    │  Pin 39-40 bottom edge               │
    └─────────────────────────────────────┘

CABLE EXIT DIRECTION: Away from Pi (standard)
```

## Pin Assignments

| Pin | GPIO | Function | Device | Notes |
|-----|------|----------|--------|-------|
| 1 | - | 3.3V | Power | Logic power |
| 2 | - | 5V | Servo rail | Servo power (separate regulator) |
| 3 | GPIO2 | PWM0 | Camera pan | SG90 servo |
| 4 | - | 5V | Servo rail | Shared |
| 5 | GPIO3 | PWM1 | Camera tilt | SG90 servo |
| 6 | - | GND | Common | All servos |
| 7 | GPIO4 | PWM2 | Left arm | SG90 × 2 |
| 8 | GPIO14 | TXD | Debug UART | Console |
| 9 | - | GND | Common | |
| 10 | GPIO15 | RXD | Debug UART | Console |
| 11 | GPIO17 | PWM3 | Right arm | SG90 × 2 |
| 12 | GPIO18 | PWM4 | Head rotate | SG90 |
| 13 | GPIO27 | Digital | Bump sensor front | Active low |
| 14 | - | GND | Common | |
| 15 | GPIO22 | Digital | Bump sensor rear | Active low |
| 16 | GPIO23 | Digital | IR emitter | 38kHz modulated |
| 17 | - | 3.3V | Sensors | |
| 18 | GPIO24 | Digital | IR receiver | TSOP38238 |
| 19 | GPIO10 | MOSI | SPI | Reserved |
| 20 | - | GND | Common | |
| 21 | GPIO9 | MISO | SPI | Reserved |
| 22 | GPIO25 | Digital | LED status | RGB WS2812B data |
| 23 | GPIO11 | SCLK | SPI | Reserved |
| 24 | GPIO8 | CE0 | SPI | Reserved |
| 25 | - | GND | Common | |
| 26 | GPIO7 | CE1 | SPI | Reserved |
| 27 | GPIO0 | ID_SD | I2C ID | Reserved |
| 28 | GPIO1 | ID_SC | I2C ID | Reserved |
| 29 | GPIO5 | PWM5 | Mobility motor L | DRV8833 input |
| 30 | - | GND | Common | |
| 31 | GPIO6 | PWM6 | Mobility motor R | DRV8833 input |
| 32 | GPIO12 | PWM7 | Motor enable | DRV8833 standby |
| 33 | GPIO13 | - | Reserved | Future servo |
| 34 | - | GND | Common | |
| 35 | GPIO19 | PWM8 | - | Future servo |
| 36 | GPIO16 | Digital | Emergency stop | Active low, pull-up |
| 37 | GPIO26 | - | Reserved | |
| 38 | GPIO20 | PWM9 | - | Future servo |
| 39 | - | GND | Common | Motor return |
| 40 | GPIO21 | Digital | Heartbeat LED | Blink = alive |

## Servo Assignments (9 total)

| Channel | GPIO | Location | Function | Range |
|---------|------|----------|----------|-------|
| PWM0 | 2 | Head | Pan (left/right) | 0-180° |
| PWM1 | 3 | Head | Tilt (up/down) | 0-90° |
| PWM2 | 4 | Torso | Left arm upper | 0-180° |
| PWM3 | 17 | Torso | Right arm upper | 0-180° |
| PWM4 | 18 | Neck | Head rotate | 0-180° |
| PWM5 | 5 | Base | Motor L (drive) | PWM speed |
| PWM6 | 6 | Base | Motor R (drive) | PWM speed |
| PWM7 | 12 | Base | Motor enable | On/off |
| PWM8 | 19 | Torso | Left arm lower | 0-180° |
| PWM9 | 20 | Torso | Right arm lower | 0-180° |

## Electrical Notes

**Power Budget:**
- 3.3V rail: 50mA max (logic, sensors)
- 5V rail: 2A max (servos — use external BEC)
- Servo stall current: ~250mA each
- Motors: 500mA each (DRV8833 powered separately)

**Critical:**
- Pin 36 = Emergency stop (hardware kill)
- All servos need common ground with Pi
- Motors use separate power, Pi GPIO only signals DRV8833

## Cable Assembly

```
IDC CONNECTOR (socket, mates with Pi header):

     Pin 1 ● ──────────────────────────── ● Pin 2
     Pin 3 ● ──────────────────────────── ● Pin 4
     Pin 5 ● ──────────────────────────── ● Pin 6
       ... (continue through pin 40)
     Pin 39● ──────────────────────────── ● Pin 40

CRIMP SIDE: Signal breakout to servos/sensors
```

## Breakout Board (optional)

Simple passive breakout:

```
┌──────────────────────────────────────────┐
│  IDC 40-pin socket (receives ribbon)     │
│                                          │
│  ┌───────────────┐  ┌───────────────┐   │
│  │ Servo bank 1  │  │ Servo bank 2  │   │
│  │  GND VCC SIG  │  │  GND VCC SIG  │   │
│  │  (x5 SG90)    │  │  (x5 SG90)    │   │
│  └───────────────┘  └───────────────┘   │
│                                          │
│  ┌───────────────┐  ┌───────────────┐   │
│  │ Motor driver  │  │  Sensors      │   │
│  │  DRV8833      │  │  bump/IR/LED  │   │
│  └───────────────┘  └───────────────┘   │
│                                          │
│  [Emergency Stop] [Power LED] [Status]  │
└──────────────────────────────────────────┘
```

## Command Interface

```bash
# Servo control via GPIO
# Using pigpio or RPi.GPIO

# Example: Pan camera left
echo "2=500" > /dev/pigpio # 500μs pulse = 0°

# Example: Pan camera right
echo "2=2500" > /dev/pigpio # 2500μs pulse = 180°

# Center position
echo "2=1500" > /dev/pigpio # 1500μs = 90°
```

## Safety

- **Pin 36**: Always wired to emergency stop button
- **Heartbeat (pin 40)**: Must blink every second or hardware fault
- **Kill conditions**: Emergency stop OR heartbeat timeout > 3 seconds

## Document Status

**Version:** 1.0.0
**Author:** AOCROS hardware team
**Approved by:** Tappy Lewis (fiduciary)
**Implement by:** Hardware designers

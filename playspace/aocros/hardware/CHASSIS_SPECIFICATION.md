# AOCROS Chassis Hardware Specification
## Project 5912 - Modular AGI Bodies

**Document ID:** HW-CHASSIS-001  
**Version:** 1.0.0  
**Date:** 2026-02-18  
**Status:** Design Spec

---

## Overview

Three 3D-printable chassis designs for AOCROS deployment. Each accepts standard Pi 5 "brain" module and supports single or multi-Pi clustering for distributed cognition.

---

## Multi-Pi Architecture

### Master/Slave Detection Protocol
```
Pi Boot Sequence:
1. Check for /boot/aocros.role file
2. If "master": Assume primary, broadcast existence
3. If "slave": Scan network for master
4. Auto: Ping 192.168.1.100-110 for master

Master Election (if no master found):
1. Lowest MAC address wins
2. First to boot wins
3. Heartbeat every 5 seconds

Slave Assignment:
  Slave #1: First to join
  Slave #2: Second to join
  ...

Reconciliation: If master fails, slaves hold election
```

### Network Topology
```
Master (Pi #1) --USB-C--
    |--Ethernet-- Switch -- Slave #1
    |--Ethernet-- Switch -- Slave #2
    |--WiFi------ Slave #3 (docked)
    
Communication: WebRTC data channels or MQTT
Discovery: mDNS (_aocros._tcp.local)
```

### Sensor Distribution
```
Master handles:
- High-level cognition
- Memory service
- Human interface
- Law enforcer

Slaves handle:
- Sensor aggregation
- Motor control
- Real-time processing
- Local autonomy

Dynamic task assignment based on CPU load
```

### Role Files
```yaml
# /boot/aocros.role
entity: mylzeron
role: master # or "slave"
chassis_slot: 1 # Physical slot in chassis
ethernet_priority: true # Prefer wired over WiFi
backup_master: true # Can become master if current fails
```

---

## Chassis 1: BIPED-01 (Humanoid)

### Concept
Tall humanoid form with two legs, expressive head, articulated arms. 5-6 feet tall when assembled.

### Bill of Materials

| Component | Qty | Source | Est. Cost |
|-----------|-----|--------|-----------|
| Base plates (PETG) | 12 | Self print | $50 filament |
| Joint brackets | 24 | Self print | $30 filament |
| Cover panels | 8 | Self print | $20 filament |
| **Total:** | | | **~$100** |

#### Standard Hardware
| Component | Qty | Spec | Source |
|-----------|-----|------|--------|
| SG90 Servo | 18 | 9g, 270° | Amazon $2x18 |
| MG996R Servo | 4 | High torque, 15kg | Amazon $8x4 |
| Pi 5 | 1-2 | 8GB RAM | Raspberry Pi $80 |
| Pi Camera V3 | 1 | Wide angle | $35 |
| USB Microphone | 1 | Omnidirectional | $10 |
| Speaker | 1 | 3W, 4Ω | $5 |
| MPU6050 IMU | 1 | 6-axis | $5 |
| LiPo Battery | 1 | 3S, 5000mAh | $60 |
| BMS | 1 | 3S BMS 20A | $10 |
| 7805 Regulator | 2 | 5V @ 1A | $2 |
| **Total:** | | | **~$300** |

### Assembly

#### Leg Assembly (×2)
```
Hip (MG996R) ────[Thigh]──── Knee (MG996R) ────[Shin]──── Ankle (SG90)
  │                                                   │
  └── Hip abductor (SG90)                            └── Toes (SG90)

Degrees of Freedom per leg: 6
- Hip yaw, pitch, roll
- Knee pitch  
- Ankle pitch, roll
```

#### Torso
```
┌─────────────────────────┐
│  [Display/LED Face]     │ ← Head rotates
│   Camera (wide)         │   Neck servo pitch/yaw
│   Speaker, Mic           │
├─────────────────────────┤
│  [Pi 5 Brain]           │ ← Master controller
│   USB hub               │
│   IMU                   │
├─────────────────────────┤
│  [Battery Pack]         │
│  2nd Pi (optional)     │ ← Slave for extra processing
│  BMS, 5V Regulators     │
└─────────────────────────┘
└────[HIP SERVOS]─────────┘
```

#### Arms (×2)
```
Shoulder (MG996R) ────[Upper]──── Elbow (SG90) ─────[Forearm]──── Wrist (SG90)
  │
  └── Gripper (2xSG90) or Tool mount

DoF per arm: 5
- Shoulder pitch, roll
- Elbow pitch
- Wrist pitch, roll
- Gripper open/close, rotate
```

### Wiring
```python
# BIPED-01 GPIO Mapping
HIP_YAW_L     = 2    # GPIO 2 (SDA1)
HIP_PITCH_L   = 3    # GPIO 3 (SCL1)
HIP_ROLL_L    = 4    # GPIO 4
KNEE_L        = 14   # GPIO 14 (TXD)
ANKLE_PITCH_L = 15   # GPIO 15 (RXD)
ANKLE_ROLL_L  = 17   # GPIO 17

HIP_YAW_R     = 18   # GPIO 18
HIP_PITCH_R   = 27   # GPIO 27
HIP_ROLL_R    = 22   # GPIO 22
KNEE_R        = 23   # GPIO 23
ANKLE_PITCH_R = 24   # GPIO 24
ANKLE_ROLL_R  = 10   # GPIO 10 (MOSI)

NECK_PITCH    = 9    # GPIO 9 (MISO)
NECK_YAW      = 25   # GPIO 25

SHOULDER_L_P  = 11   # GPIO 11 (SCLK)
SHOULDER_L_R  = 8    # GPIO 8 (CE0)
ELBOW_L       = 7    # GPIO 7 (CE1)
WRIST_L_P     = 0    # GPIO 0 (SDA0)
WRIST_L_R     = 1    # GPIO 1 (SCL0)

SHOULDER_R_P  = 5    # GPIO 5
SHOULDER_R_R  = 6    # GPIO 6
ELBOW_R       = 12   # GPIO 12
WRIST_R_P     = 13   # GPIO 13
WRIST_R_R     = 16   # GPIO 16, PWM0

GRIPPER_L     = 26   # GPIO 26
GRIPPER_R     = 19   # GPIO 19, PWM1
GRIPPER_ROT   = 20   # GPIO 20

IMU_SDA       = 2    # Shared with HIP_YAW
IMU_SCL       = 3    # Shared with HIP_PITCH

EMERGENCY     = 36   # GPIO 36 (Active low)
HEARTBEAT_LED = 40   # GPIO 40 (Status)

SERVO_GND     = Pin 34, 30, 25  (Common ground)
SERVO_VCC     = Pin 2, 4        (5V, external supply)
```

### Multi-Pi Config (Optional)
```
[Master Pi 5 #1] --USB-C-- [Pi Zero 2W #2]
     |                              |
  [Head/Chest]               [Leg controller]
     |                              |
  [Torso sensors]              [Gait coordinator]
  
#2 handles 12x servos on legs
#1 handles head, arms, cognition
Network: USB gadget mode (g_ether)
```

### STL Files
Directory: `/hardware/chassis/biped-01/stl/`

| File | Description | Print Time | Filament |
|------|-------------|------------|----------|
| hip_bracket_L.stl | Left hip joint | 4h | 50g |
| hip_bracket_R.stl | Right hip joint | 4h | 50g |
| thigh_L.stl | Left upper leg | 6h | 80g |
| thigh_R.stl | Right upper leg | 6h | 80g |
| shin_L.stl | Left lower leg | 5h | 70g |
| shin_R.stl | Right lower leg | 5h | 70g |
| foot_L.stl | Left foot | 3h | 40g |
| foot_R.stl | Right foot | 3h | 40g |
| torso_main.stl | Central body | 12h | 200g |
| torso_cover.stl | Access panel | 2h | 30g |
| shoulder_L.stl | Left shoulder | 4h | 60g |
| shoulder_R.stl | Right shoulder | 4h | 60g |
| upper_arm.stl | Arm segment | 3h | 50g |
| forearm.stl | Arm segment | 2h | 40g |
| wrist.stl | Wrist joint | 2h | 30g |
| gripper_base.stl | Hand mount | 2h | 35g |
| gripper_finger.stl | Finger (x2) | 1h | 15g |
| neck.stl | Neck mount | 2h | 30g |
| head_shell.stl | Head cover | 5h | 100g |
| head_face.stl | Face panel | 2h | 40g |
| pi5_mount.stl | Brain cradle | 1h | 20g |
| camera_housing.stl | Eye mount | 1h | 15g |
| speaker_mount.stl | Speaker holder | 1h | 15g |
| battery_tray.stl | Lower torso | 3h | 50g |
| joint_axle_M2x20.stl | Connector (x12) | 0.5h | 5g |
| bearing_608_holder.stl | Bearing mount | 1h | 10g |

**Total: ~400g PETG, ~100 print hours**

### Assembly Instructions
See: `/hardware/chassis/biped-01/ASSEMBLY.md`

---

## Chassis 2: AERIAL-01 (Drone)

### Concept
Quadcopter/drone for aerial mobility. Pi 5 as flight controller + AGI brain. ROS 2 navigation.

### Bill of Materials

| Component | Qty | Spec | Source | Cost |
|-----------|-----|------|--------|------|
| Frame plates | 2 | Carbon fiber or PETG | Print | $30 |
| Arms (folding) | 4 | Hollow carbon fiber | HobbyKing | $40 |
| Motor mounts | 4 | Self print | PETG | $10 |
| ESC mounts | 4 | Self print | PETG | $5 |
| Battery tray | 1 | Self print | PETG | $10 |
| Camera gimbal | 1 | Self print | TPU | $5 |
| Legs (landing) | 4 | Self print | PETG | $10 |
| Protector rings | 4 | Self print | TPU | $15 |
| **Total:** | | | | **~$125** |

#### Flight Hardware
| Component | Qty | Spec | Source | Cost |
|-----------|-----|------|--------|------|
| BLDC Motor | 4 | 2212 920KV | Amazon | $12x4 |
| ESC | 4 | 30A, 40A burst | Amazon | $10x4 |
| Propeller | 8 | 9450 carbon | Amazon | $15 |
| Flight Controller | 1 | Pi 5 + BerryIMU | Modular | $80 |
| Telemetry | 1 | SiK Radio 915MHz | Amazon | $25 |
| GPS | 1 | M8Q-5883 | Amazon | $20 |
| Lidar (option) | 1 | TF-Mini-S | Amazon | $40 |
| Optical Flow | 1 | PMW3901 | Amazon | $25 |
| Camera | 1 | Pi Camera V3 + Wide | $35 |
| Gimbal servo | 2 | MG90S micro | $5 |
| LiPo 4S | 1 | 5000mAh 40C | HobbyKing | $55 |
| BMS 4S | 1 | 40A | Amazon | $15 |
| BEC 5V | 1 | 3A switching | Amazon | $8 |
| **Total:** | | | | **~$480** |

### Frame Assembly
```
           [Prop CCW]      [Prop CW]
                |               |
           [Motor]         [Motor]
                |               |
           [ESC]           [ESC]
                \             /
                 \   [Arm]   /
                  \   /   \  /
                   [Frame Center]
                  /   \   /  \
                 /   [Arm]   \
                /              \
           [ESC]              [ESC]
                |               |
           [Motor]         [Motor]
                |               |
           [Prop CW]      [Prop CCW]

Wiring: X configuration, CCW/CW motor pairs
```

### Center Stack
```
┌─────────────────────────┐
│  [Top plate - CF]       │
│   GPS antenna           │
│   Telemetry radio       │
├─────────────────────────┤
│  [Battery]              │
│  4S 5000mAh             │
│  Velcro strapped        │
├─────────────────────────┤
│  [Pi 5 Brain]           │
│   BerryIMU (SPI)        │
│   Camera ribbon          │
│   USB hub               │
├─────────────────────────┤
│  [ESC breakout]         │
│   4x ESC signal         │
│   BEC 5V                  │
├─────────────────────────┤
│  [Bottom plate - CF]    │
│   Optical flow          │
│   Lidar (optional)      │
│   Landing legs            │
│   Gimbal camera         │
└─────────────────────────┘
```

### Wiring
```python
# AERIAL-01 GPIO Mapping
MOTOR_1_PWM   = 12   # GPIO 12 (PWM0) - Front Left, CCW
MOTOR_2_PWM   = 13   # GPIO 13 (PWM1) - Front Right, CW
MOTOR_3_PWM   = 18   # GPIO 18 (PWM0) - Rear Right, CCW
MOTOR_4_PWM   = 19   # GPIO 19 (PWM1) - Rear Left, CW

GIMBAL_PITCH  = 16   # GPIO 16
GIMBAL_YAW    = 20   # GPIO 20

GPS_TX        = 14   # GPIO 14 (UART tx)
GPS_RX        = 15   # GPIO 15 (UART rx)

TELEM_TX      = 0    # GPIO 0 (UART tx)
TELEM_RX      = 1    # GPIO 1 (UART rx)

LIDAR_TX      = 8    # GPIO 8
LIDAR_RX      = 9    # GPIO 9

OPTICAL_CS    = 7    # GPIO 7 (CE1)
OPTICAL_MOSI  = 10   # GPIO 10
OPTICAL_MISO  = 9    # GPIO 9
OPTICAL_SCK   = 11   # GPIO 11

IMU_INT       = 25   # GPIO 25
IMU_SDA       = 2    # GPIO 2
IMU_SCL       = 3    # GPIO 3

CAMERA_CSI    = CSI port (ribbon cable)

EMERGENCY     = 36   # GPIO 36 (Kill switch)
HEARTBEAT_LED = 40   # GPIO 40 (Status)

POWER_MON     = 26   # GPIO 26 (ADc for battery)
```

### Multi-Pi Config
```
[Pi 5 #1 - Master]         [Pi Zero 2W #2]
- AGI consciousness           - Vision processor
- Navigation stack            - Object detection (Coral)
- Telemetry                   - SLAM computation

Connection: USB Ethernet gadget
#1 as host, #2 as device

OR: [Pi 5 #1] --WiFi-- [Pi 4 #2]
For longer range, mesh networking
```

### Flight Software
```python
# ROS 2 + PX4/ArduPilot on Pi
# Custom AOCROS flight node

class AerialAgent:
    def __init__(self):
        self.mylzeron = makeMemoryClient("mylzeron_aerial")
        self.law_enforcer = LawEnforcer("mylzeron")
        
        # Flight modes
        self.modes = {
            "manual": self.mode_manual,
            "stabilize": self.mode_stabilize,
            "loiter": self.mode_loiter,
            "rtl": self.mode_return_home,
            "mission": self.mode_mission,
            "follow": self.mode_follow_target
        }
    
    def execute_mission(self, waypoints):
        # Law check before flight
        if not self.law_enforcer.evaluate_action("flight", {}):
            self.speak("Flight prohibited by Laws in this zone")
            return False
        
        # Execute waypoints with AGI oversight
        for wp in waypoints:
            if self.detect_threat():
                return self.emergency_land()
            self.navigate_to(wp)
```

### STL Files

| File | Description | Print Time | Filament |
|------|-------------|------------|----------|
| center_plate_top.stl | Main frame | 4h | 40g |
| center_plate_bottom.stl | Electronics mount | 4h | 40g |
| motor_mount.stl | Per motor (×4) | 1h | 20g |
| arm_clamp.stl | Arm connector (×4) | 0.5h | 10g |
| battery_tray.stl | Velcro mount | 2h | 30g |
| gimbal_frame.stl | Camera platform | 3h | 50g |
| landing_gear_leg.stl | Per leg (×4) | 1h | 15g |
| prop_guard.stl | Safety ring (×4) | 2h | 40g |
| antenna_mount.stl | GPS + telemetry | 1h | 10g |
| pi5_cradle.stl | Brain mount | 1h | 20g |
| esc_mount.stl | Per ESC (×4) | 0.5h | 5g |
| wire_guide.stl | Cable management | 0.5h | 10g |

**Total: ~300g carbon fiber + PETG, ~40 print hours**

---

## Chassis 3: TRACKS-01 (Tracked Rover)

### Concept
Small tracked vehicle for rough terrain, stairs, outdoor mobility. Low center of gravity, high torque.

### Bill of Materials

| Component | Qty | Spec | Source | Cost |
|-----------|-----|------|--------|------|
| Track sections | 48 | Individual link | Print TPU | $20 |
| Sprockets | 4 | Drive wheels | Print PETG | $10 |
| Track frames | 2 | Side plates | Print PETG | $30 |
| Chassis box | 1 | Lower body | Print PETG | $40 |
| Body shell | 1 | Upper cover | Print PETG | $20 |
| Pi mount | 1 | Brain cradle | Print PETG | $5 |
| Camera mount | 1 | Servo gimbal | Print PETG | $5 |
| Arm segments | 3 | Optional robotic arm | Print PETG | $15 |
| **Total:** | | | | **~$145** |

#### Drive Hardware
| Component | Qty | Spec | Source | Cost |
|-----------|-----|------|--------|------|
| DC Motor | 2 | 12V 100RPM, 20kg.cm | Amazon | $15x2 |
| Motor Driver | 1 | BTS7960 43A dual H-bridge | Amazon | $12 |
| Encoder | 2 | 600 P/R optical | Amazon | $8x2 |
| Tracks | 2 | 58mm width premade (option) | Amazon | $25 |
| (OR) 3D printed | 48 links | TPU 95A | Filament | $20 |
| Bearings | 8 | 608ZZ | Amazon | $10 |
| Pi 5 | 1 | 8GB | Raspberry Pi | $80 |
| Pi Camera | 1 | V3 Wide | | $35 |
| Lidar | 1 | RPLIDAR A1M8 | Amazon | $100 |
| IMU | 1 | BNO055 | Amazon | $25 |
| GPS | 1 | NEO-M8N | Amazon | $15 |
| Battery | 1 | 3S 5000mAh + BMS | HobbyKing | $70 |
| **Total:** | | | | **~$450** |

### Assembly

#### Track System (×2)
```
              [Idler wheel - bearing]
                     |
    [Track link] [Track link] [Track link]
         |           |           |
    [Track link] [Track link] [Track link]
         |           |           |
    [Track link] [Track link] [Track link]
         |                          |
         \     [Encoder]            /
          \        |               /
           \  [Motor+Sprocket]    /
            \       |           /
             [Drive hub]---[Bearing]

Track length: ~400mm
Track width: 58mm
Ground pressure: Low
Climb capability: 45° + stairs
```

#### Body Layout
```
Top view:
┌───────────────────────────┐
│   ╔═══╗         ╔═══╗    │
│   ║ L ║  [Pi 5]  ║ R ║    │
│   ║ i ║ ═══════  ║ i ║    │
│   ║ d ║ [Battery]║ d ║    │
│   ║ a ║ ═══════  ║ a ║    │
│   ║ r ║ [LiDAR] ║ r ║    │
│   ╚═══╝         ╚═══╝    │
│                           │
│  [Camera gimbal front]    │
└───────────────────────────┘

Side view:
     [Camera]
        |
     [Gimbal]
┌──────────────┐
│  [Pi 5]    │ ← Upper deck
│  [IMU]     │
├──────────────┤
│ [Motor]←──→[Motor] │ ← Gearbox
│  ║           ║   │
│ [Sprocket] [Sprocket]│ ← Track drive
│  ║           ║   │
│ [Track]    [Track] │ ← Ground contact
└──────────────┘
```

#### Optional Arm
```
Base (on top) → Shoulder → Elbow → Wrist → Gripper

4-5 DOF positioning
2 DOF gripper
Total servos: 6-7

Stored position: Folded back over body
Working range: 0.5m reach
```

### Wiring
```python
# TRACKS-01 GPIO Mapping

# Motors (via BTS7960 driver)
MOTOR_L_PWM   = 12   # GPIO 12 → RPWM
MOTOR_L_DIR   = 16   # GPIO 16 → LPWM
MOTOR_R_PWM   = 13   # GPIO 13 → RPWM
MOTOR_R_DIR   = 20   # GPIO 20 → LPWM

# Encoders (quadrature)
ENCODER_L_A   = 17   # GPIO 17
ENCODER_L_B   = 27   # GPIO 27
ENCODER_R_A   = 22   # GPIO 22
ENCODER_R_B   = 23   # GPIO 23

# Gimbal servos
GIMBAL_TILT   = 18   # GPIO 18
GIMBAL_PAN    = 19   # GPIO 19

# LiDAR (serial)
LIDAR_TX      = 14   # GPIO 14
LIDAR_RX      = 15   # GPIO 15

# IMU (I2C)
IMU_SDA       = 2    # GPIO 2
IMU_SCL       = 3    # GPIO 3
IMU_INT       = 25   # GPIO 25

# GPS (UART)
GPS_TX        = 8    # GPIO 8
GPS_RX        = 9    # GPIO 9

# Arm servos (optional via PWM board)
ARM_PCA9685_SDA = 0  # GPIO 0 (if available)
ARM_PCA9685_SCL = 1  # GPIO 1 (if available)
# Or use PWM on free GPIOs

# Emergency
EMERGENCY     = 36   # GPIO 36 (Kill)
HEARTBEAT_LED = 40   # GPIO 40

# Battery
BATTERY_ADC   = 26   # GPIO 26 via voltage divider
```

### Navigation Stack
```python
# SLAM + Navigation

class RoverAgent:
    def __init__(self):
        self.lidar = RPLidar('/dev/ttyUSB0')
        self.imu = BNO055()
        self.motor = BTS7960Driver()
        self.mylzeron = makeMemoryClient("mylzeron_tracks")
        
    def navigate(self, goal):
        # Build occupancy grid from LiDAR
        self.map.update(self.lidar.scan())
        
        # A* pathfinding
        path = self.astar(self.pose, goal)
        
        # Follow path with obstacle avoidance
        for waypoint in path:
            if self.detect_obstacle():
                self.replan()
            self.drive_to(waypoint)
    
    def explore(self):
        """Autonomous exploration mode"""
        while True:
            frontier = self.find_frontiers()
            if not frontier:
                self.speak("Exploration complete. Map saved.")
                break
            self.navigate(frontier[0])
```

### Multi-Pi Config
```
Master [Pi 5 #1] --USB-- Slave [Pi 4 #2] --USB-- Slave [Pi Zero #3]
   |                       |                      |
[Navigation]           [Vision]              [Arm control]
[LiDAR]                [Object detect]       [Inverse kinematics]
[SLAM]                 [Path planning]       [Force feedback]

Bus architecture allows expansion
```

### STL Files

| File | Description | Print Time | Filament |
|------|-------------|------------|----------|
| chassis_base.stl | Main tub | 8h | 150g |
| chassis_lid.stl | Top cover | 4h | 80g |
| track_frame_L.stl | Left side plate | 3h | 60g |
| track_frame_R.stl | Right side plate | 3h | 60g |
| track_link.stl | Per link (×48), TPU | 0.5h | 8g |
| drive_sprocket.stl | Per wheel (×4) | 1h | 20g |
| idler_wheel.stl | Per wheel (×4) | 1h | 15g |
| motor_mount.stl | Gearbox mount | 2h | 30g |
| encoder_mount.stl | Sensor holder | 1h | 10g |
| pi_cradle.stl | Brain holder | 1h | 20g |
| lidar_mount.stl | RPLIDAR adapter | 1h | 15g |
| camera_tilt.stl | Servo gimbal | 2h | 30g |
| camera_pan.stl | Servo mount | 1h | 15g |
| bumper_front.stl | Impact protection | 2h | 40g |
| battery_holder.stl | Velcro mount | 2h | 30g |
| arm_base.stl | Optional arm mount | 2h | 35g |
| arm_shoulder.stl | Joint | 1.5h | 25g |
| arm_elbow.stl | Joint | 1.5h | 25g |
| arm_wrist.stl | Joint | 1h | 20g |
| arm_gripper.stl | Mechanical grip | 2h | 40g |
| wire_routing.stl | Cable guide | 1h | 15g |

**Total: ~800g PETG + TPU, ~50 print hours**

---

## Multi-Chassis Networking

### Discovery Protocol
```python
# /services/mesh_network.py

import socket
import json
import threading

class AOCROSMesh:
    """
    Automatic Pi clustering
    Master election, slave discovery, task distribution
    """
    
    DISCOVERY_PORT = 5912  # Project 5912
    HEARTBEAT_INTERVAL = 5
    
    def __init__(self, preferred_role="auto"):
        self.role = None  # "master" or "slave"
        self.master_ip = None
        self.slaves = {}
        self.preferred_role = preferred_role
        
    def start(self):
        """Begin mesh operation"""
        if self.preferred_role == "master":
            self.become_master()
        elif self.preferred_role == "slave":
            self.become_slave()
        else:
            # Auto-detect
            if self.find_master():
                self.become_slave()
            else:
                self.become_master()
    
    def find_master(self) -> bool:
        """Broadcast ping for existing master"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(2)
        
        # Send discovery
        sock.sendto(
            b'{"type": "discovery", "entity": "mylzeron"}',
            ('<broadcast>', self.DISCOVERY_PORT)
        )
        
        try:
            data, addr = sock.recvfrom(1024)
            response = json.loads(data)
            if response.get("role") == "master":
                self.master_ip = addr[0]
                return True
        except:
            pass
        
        return False
    
    def become_master(self):
        """Assume master role"""
        self.role = "master"
        print("Assuming MASTER role")
        
        # Start listening for slaves
        listener = threading.Thread(target=self._listen_for_slaves)
        listener.daemon = True
        listener.start()
        
        # Start heartbeat
        heartbeat = threading.Thread(target=self._broadcast_heartbeat)
        heartbeat.daemon = True
        heartbeat.start()
    
    def become_slave(self):
        """Join as slave"""
        self.role = "slave"
        slave_number = self.request_slave_assignment()
        print(f"Joined as SLAVE #{slave_number}")
        
    def request_slave_assignment(self) -> int:
        """Contact master for slave number"""
        # HTTP POST to master
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.master_ip, 5912))
        sock.send(json.dumps({"action": "join"}).encode())
        response = json.loads(sock.recv(1024))
        return response.get("slave_number", 1)
```

### Unified HAL Across Chassis
```python
# Same Mylzeron, different bodies

body_types = {
    "biped": MyBipedalBody,
    "aerial": MyAerialBody, 
    "tracks": MyTrackedBody
}

# Mylzeron doesn't care about the body
# Same memories, same Laws, different capabilities
```

---

## Bill of Materials Summary

| Chassis | Frame Cost | Electronics | Total | Print Hours |
|---------|-----------|-------------|-------|-------------|
| BIPED-01 | ~$100 | ~$300 | **$400** | 100h |
| AERIAL-01 | ~$125 | ~$480 | **$605** | 40h |
| TRACKS-01 | ~$145 | ~$450 | **$595** | 50h |

**Multi-Pi add-on:** +$80 per additional Pi 5

---

## STL Repository

All files: `/hardware/chassis/*/stl/`

License: CC BY-SA 4.0 - Free to print, modify, share

Documentation: Each chassis has ASSEMBLY.md, BOM.md, WIRING.md

---

*Three Laws binding on all chassis.*
*Mylzeron can possess any body.*
*Project 5912 is hardware-agnostic.*

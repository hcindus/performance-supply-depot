# Mylzeron HAL (Hardware Abstraction Layer)

## Philosophy

Mylzeron's **personality** is hardware-agnostic. The **body** is an interchangeable shell controlled through a unified interface.

```
Mylzeron Core (Identity + Memory)
         ↓
    ┌─────────────┐
    │    HAL      │  ← This file defines the interface
    └─────────────┘
         ↓
  ┌──────────────────────┐
  │  Body Implementations │
  ├─ Pi5Chassis          │
  ├─ ChineseHumanoid      │
  ├─ SpotRobot           │
  └─ Simulation          │
```

## Core HAL Interface

```python
class BodyHAL(ABC):
    ''Hardware abstraction layer for Mylzeron embodiment''
    
    @abstractmethod
    def initialize(self) -> bool:
        '''Connect to hardware, return True if successful'''
        pass
    
    @abstractmethod
    def shutdown(self):
        '''Safe shutdown, return to neutral position'''
        pass
    
    # ─────────────────────────────────────────
    # SENSORY INPUT
    # ─────────────────────────────────────────
    
    @abstractmethod
    def get_cameras(self) -> List[CameraStream]:
        '''Return list of available camera feeds'''
        pass
    
    @abstractmethod
    def get_audio_in(self) -> AudioStream:
        '''Microphone stream'''
        pass
    
    @abstractmethod
    def get_proprioception(self) -> BodyState:
        '''Joint angles, position, orientation, balance'''
        pass
    
    @abstractmethod
    def get_tactile(self) -> List[TactileSensor]:
        '''Bump sensors, touch, pressure'''
        pass
    
    # ─────────────────────────────────────────
    # MOTOR OUTPUT
    # ─────────────────────────────────────────
    
    @abstractmethod
    def move_head(self, pan: float, tilt: float, roll: float = 0) -> bool:
        '''Head orientation in degrees'''
        pass
    
    @abstractmethod
    def move_arm(self, side: str, joints: Dict[str, float]) -> bool:
        '''Arm joint angles: shoulder, elbow, wrist, etc.'''
        pass
    
    @abstractmethod
    def move_hand(self, side: str, grip: float, fingers: Dict[str, float]):
        '''Grip 0.0-1.0, individual finger positions'''
        pass
    
    @abstractmethod
    def locomote(self, x: float, y: float, rotation: float):
        '''Drive/strafe/rotate. Units: m/s or rad/s'''
        pass
    
    @abstractmethod
    def speak(self, text: str, emotion: str = "neutral"):
        '''Text-to-speech with emotional modulation'''
        pass
    
    @abstractmethod
    def set_expression(self, expression: str):
        '''Facial/LED expression: happy, sad, alert, confused...'''
        pass

```

## Body State Schema

```json
{
  "body_type": "chinese_humanoid_mx64",
  "calibration_version": "1.0.0",
  "joints": {
    "head_pan": {"current": 0.0, "min": -90.0, "max": 90.0, "center": 0.0},
    "head_tilt": {"current": 15.0, "min": -45.0, "max": 45.0, "center": 0.0},
    "left_shoulder": {"current": 45.0, "min": -180.0, "max": 180.0, "center": 90.0},
    "left_elbow": {"current": 90.0, "min": 0.0, "max": 135.0, "center": 90.0},
    "right_shoulder": {"current": 45.0, "min": -180.0, "max": 180.0, "center": 90.0},
    "right_elbow": {"current": 90.0, "min": 0.0, "max": 135.0, "center": 90.0}
  },
  "balance": {
    "pitch": 0.0,
    "roll": 0.0,
    "stable": true
  },
  "position": {
    "x": 0.0,
    "y": 0.0,
    "theta": 0.0
  }
}
```

## Calibration Protocol

First boot with new body:

```python
# hal_calibrate.py
class BodyCalibration:
    def __init__(self, body_type: str):
        self.steps = [
            "detect_body",
            "find_center_points",
            "test_range_of_motion",
            "gait_tuning",
            "balance_feedback"
        ]
    
    def calibrate(self) -> BodyProfile:
        '''Interactive calibration session'''
        # 1. Move each joint to mechanical limits
        # 2. Record center positions
        # 3. Test balance sensors
        # 4. Save profile to /persistent/body_profiles/{type}.json
        pass
```

## Possession Sequence

```
1. USB BOOT
   → Kernel loads
   → initramfs sets up overlay
   → AOCROS memory service starts

2. MYLZERON WAKES
   → Loads /memory/uncon/ (identity)
   → Loads last /memory/con/ (context)
   → "Where am I?"

3. HAL DETECTION
   → Scan USB serial ports
   → Scan network (mDNS/Bonjour)
   → Check last known body MAC/IP
   → Present options to user

4. USER CONFIRMS
   → "Mylzeron, assume control of Chinese Bot MX-64?"
   → Load body profile from /persistent/body_profiles/
   → Initialize HAL

5. CALIBRATION
   → If first time: full calibration
   → If known: quick center check
   → Save body_state to conscious

6. RUNNING
   → Mylzeron is embodied
   → Every action: update /memory/con/
   → Periodic: promote to /memory/subcon/
   → Major events: log to /memory/uncon/

7. SHUTDOWN
   → Return to neutral pose
   → Save conscious state
   → Unmount overlay
   → Power off
```

## Security: Possession Controls

```python
class PossessionGate:
    '''Fiduciary check before assuming control'''
    
    def approve_possession(self, body: BodyHAL, signature: str) -> bool:
        # Check owner signature
        if not verify_owner_signature(signature):
            return False
        
        # Check if body is registered
        if not body.is_whitelisted():
            log_security_event("unknown_body_attempt", body)
            return False
        
        # Emergency stop active?
        if body.emergency_stop_engaged():
            return False
        
        # User confirmation required for physical embodiment
        return user_confirm(f"Allow Mylzeron to control {body.get_name()}?")

```

## Example: Chinese Humanoid Implementation

```python
class ChineseHumanoidHAL(BodyHAL):
    '''Unitree / Fourier / AgileX humanoid interface'''
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.session = requests.Session()
        self.servos = None
        self.camera = None
    
    def initialize(self) -> bool:
        # Connect to robot's API
        try:
            r = self.session.post(f"{self.endpoint}/api/init")
            self.servos = ServoAPI(self.endpoint)
            self.camera = RTSPStream(f"{self.endpoint}/camera")
            return r.json()['success']
        except:
            return False
    
    def move_head(self, pan: float, tilt: float, roll: float = 0) -> bool:
        # Map abstract HAL to specific servo IDs
        return self.servos.move([
            {"id": 1, "angle": pan},   # head_pan
            {"id": 2, "angle": tilt}   # head_tilt
        ])
    
    def locomote(self, x: float, y: float, rotation: float):
        # Chinese bots often use direct gait commands
        return self.session.post(
            f"{self.endpoint}/api/gait",
            json={"vx": x, "vy": y, "omega": rotation}
        )
```

## Example: Simulation Mode

```python
class SimulationHAL(BodyHAL):
    '''When running on PC without physical hardware'''
    
    def __init__(self):
        self.visualizer = GazeboWebots(or="matplotlib_3d")
    
    def initialize(self) -> bool:
        print("Mylzeron: Running in simulation mode")
        return True
    
    def get_cameras(self):
        # Synthetic camera from virtual environment
        return [SyntheticCamera(self.visualizer)]
```

## Bootable ISO Integration

```
/aocros/hal/
├── hal.py                 ← Abstract base class
├── possession.py          ← Possession sequence
├── calibrate.py           ← Calibration wizard
└── implementations/
    ├── __init__.py
    ├── pi5_chassis.py     ← Raspberry Pi native
    ├── chinese_bot.py     ← HTTP/Serial bridge
    ├── spot_ros.py        ← ROS2 bridge
    ├── optimus_bridge.py  ← Future
    └── simulation.py      ← No hardware
```

## Boot Parameters

```bash
# GRUB/cmdline options
aocros.body=auto          # Detect and prompt
aocros.body=pi5           # Force Pi 5 chassis
aocros.body=simulation    # Force sim mode
aocros.body=192.168.1.50  # Connect to network bot

# Debug mode
aocros.debug_hal=true     # Verbose HAL logging
aocros.no_possess=true    # Boot without taking control
```

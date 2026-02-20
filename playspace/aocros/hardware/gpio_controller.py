#!/usr/bin/env python3
"""
AOCROS GPIO Controller for Raspberry Pi 5
Simple ribbon cable servo/IO control
"""

import sys
import time
import signal
from dataclasses import dataclass
from typing import Optional, Dict, List

# Try pigpio first (best for servos), fall back to RPi.GPIO
try:
    import pigpio
    USE_PIGPIO = True
except ImportError:
    import RPi.GPIO as GPIO
    USE_PIGPIO = False
    print("Warning: pigpio not found, using RPi.GPIO (less precise)")

@dataclass
class ServoConfig:
    """Servo configuration per GPIO_RIBBON_SPEC.md"""
    name: str
    gpio: int
    min_pulse: int = 500    # 0° in microseconds
    max_pulse: int = 2500   # 180° in microseconds
    center: int = 1500      # 90°
    current: int = 1500

class GPIOController:
    """
    Physical GPIO controller for AOCROS
    Maps ribbon cable pins to functions
    """
    
    # Pin definitions from GPIO_RIBBON_SPEC.md
    EMERGENCY_STOP_PIN = 36  # GPIO 16, active low
    HEARTBEAT_PIN = 40       # GPIO 21, blink LED
    
    SERVOS = {
        'camera_pan':   ServoConfig('Camera Pan', 2, 500, 2500, 1500),
        'camera_tilt':  ServoConfig('Camera Tilt', 3, 500, 1500, 1000),  # Limited to 90°
        'arm_left':     ServoConfig('Left Arm', 4, 500, 2500, 1500),
        'arm_right':    ServoConfig('Right Arm', 17, 500, 2500, 1500),
        'head_rotate':  ServoConfig('Head Rotate', 18, 500, 2500, 1500),
        'motor_left':   ServoConfig('Motor L', 5, 0, 0, 0),  # PWM speed, not servo
        'motor_right':  ServoConfig('Motor R', 6, 0, 0, 0),
    }
    
    SENSORS = {
        'bump_front': 27,   # GPIO 27
        'bump_rear': 22,    # GPIO 22
        'ir_receiver': 24,  # GPIO 24 (TSOP38238)
    }
    
    def __init__(self):
        self.pi: Optional[pigpio.pi] = None
        self.running = False
        self.emergency_stop = False
        
    def connect(self) -> bool:
        """Initialize GPIO connection"""
        if USE_PIGPIO:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                print("Failed to connect to pigpio daemon")
                return False
            print("Connected to pigpio (hardware PWM)")
        else:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            print("Using RPi.GPIO (software PWM)")
        
        self._setup_pins()
        self.running = True
        return True
    
    def _setup_pins(self):
        """Configure pins per GPIO_RIBBON_SPEC.md"""
        if USE_PIGPIO:
            # Emergency stop input with pull-up
            self.pi.set_mode(self.EMERGENCY_STOP_PIN, pigpio.INPUT)
            self.pi.set_pull_up_down(self.EMERGENCY_STOP_PIN, pigpio.PUD_UP)
            
            # Heartbeat LED output
            self.pi.set_mode(self.HEARTBEAT_PIN, pigpio.OUTPUT)
            
            # Sensors as inputs
            for pin in self.SENSORS.values():
                self.pi.set_mode(pin, pigpio.INPUT)
                self.pi.set_pull_up_down(pin, pigpio.PUD_UP)
        else:
            # RPi.GPIO fallback
            GPIO.setup(self.EMERGENCY_STOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(self.HEARTBEAT_PIN, GPIO.OUT)
            
            for pin in self.SENSORS.values():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def set_servo(self, servo_name: str, angle: float) -> bool:
        """
        Set servo angle (0-180 degrees)
        Returns False if emergency stopped
        """
        if self.emergency_stop:
            return False
            
        servo = self.SERVOS.get(servo_name)
        if not servo:
            return False
        
        # Clamp angle
        angle = max(0, min(180, angle))
        
        # Map angle to pulse width
        pulse = servo.min_pulse + (angle / 180.0) * (servo.max_pulse - servo.min_pulse)
        servo.current = int(pulse)
        
        if USE_PIGPIO:
            self.pi.set_servo_pulsewidth(servo.gpio, servo.current)
        else:
            # Software PWM fallback (less accurate)
            pwm = GPIO.PWM(servo.gpio, 50)  # 50Hz
            pwm.start(0)
            duty = (pulse / 20000) * 100  # Convert μs to % duty
            pwm.ChangeDutyCycle(duty)
            time.sleep(0.1)  # Allow servo to move
        
        return True
    
    def center_all_servos(self):
        """Return all servos to center position"""
        for name in self.SERVOS.keys():
            if 'motor' not in name:  # Skip DC motors
                self.set_servo(name, 90)
                time.sleep(0.05)  # Stagger to avoid power spike
    
    def read_sensors(self) -> Dict[str, bool]:
        """Read all sensors, returns dict of sensor:pressed"""
        state = {}
        
        if USE_PIGPIO:
            for name, pin in self.SENSORS.items():
                # Active low (pulled up, ground when pressed)
                state[name] = self.pi.read(pin) == 0
        else:
            for name, pin in self.SENSORS.items():
                state[name] = GPIO.input(pin) == 0
        
        return state
    
    def check_emergency_stop(self) -> bool:
        """Check emergency stop button (pin 36)"""
        if USE_PIGPIO:
            pressed = self.pi.read(self.EMERGENCY_STOP_PIN) == 0
        else:
            pressed = GPIO.input(self.EMERGENCY_STOP_PIN) == 0
        
        if pressed and not self.emergency_stop:
            self.emergency_stop = True
            self.emergency_shutdown()
        
        return pressed
    
    def emergency_shutdown(self):
        """Immediate safe shutdown"""
        print("EMERGENCY STOP ACTIVATED")
        self.center_all_servos()
        
        if USE_PIGPIO:
            for servo in self.SERVOS.values():
                self.pi.set_servo_pulsewidth(servo.gpio, 0)  # Off
        
        self.running = False
    
    def heartbeat(self):
        """Blink heartbeat LED (pin 40)"""
        if USE_PIGPIO:
            self.pi.write(self.HEARTBEAT_PIN, 1)
            time.sleep(0.1)
            self.pi.write(self.HEARTBEAT_PIN, 0)
        else:
            GPIO.output(self.HEARTBEAT_PIN, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(self.HEARTBEAT_PIN, GPIO.LOW)
    
    def run_loop(self):
        """Main control loop with heartbeat and sensor polling"""
        print("AOCROS GPIO Controller running")
        print("Emergency stop: Pin 36 (GPIO 16)")
        print("Heartbeat: Pin 40 (GPIO 21)")
        
        last_heartbeat = time.time()
        
        try:
            while self.running:
                # Check emergency stop every loop
                if self.check_emergency_stop():
                    break
                
                # Heartbeat every second
                if time.time() - last_heartbeat >= 1.0:
                    self.heartbeat()
                    last_heartbeat = time.time()
                    
                    # Status output
                    sensors = self.read_sensors()
                    status = "STOP" if self.emergency_stop else "RUN"
                    print(f"\r[{status}] Sensors: {sensors}", end='', flush=True)
                
                time.sleep(0.01)  # 100Hz poll rate
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        self.running = False
        self.center_all_servos()
        
        if USE_PIGPIO:
            for servo in self.SERVOS.values():
                self.pi.set_servo_pulsewidth(servo.gpio, 0)
            self.pi.stop()
        else:
            GPIO.cleanup()
        
        print("GPIO controller shutdown complete")

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AOCROS GPIO Controller")
    parser.add_argument("--servo", help="Servo name to move")
    parser.add_argument("--angle", type=float, help="Target angle (0-180)")
    parser.add_argument("--center", action="store_true", help="Center all servos")
    parser.add_argument("--test", action="store_true", help="Run test sequence")
    
    args = parser.parse_args()
    
    ctrl = GPIOController()
    
    if not ctrl.connect():
        sys.exit(1)
    
    if args.center:
        ctrl.center_all_servos()
        time.sleep(1)
        ctrl.shutdown()
    
    elif args.servo and args.angle is not None:
        ctrl.set_servo(args.servo, args.angle)
        time.sleep(1)
        ctrl.shutdown()
    
    elif args.test:
        print("Running test sequence...")
        ctrl.set_servo('camera_pan', 90)
        time.sleep(0.5)
        ctrl.set_servo('camera_pan', 45)
        time.sleep(0.5)
        ctrl.set_servo('camera_pan', 135)
        time.sleep(0.5)
        ctrl.center_all_servos()
        print("Test complete")
        ctrl.shutdown()
    
    else:
        # Run main loop
        ctrl.run_loop()

#!/usr/bin/env python3
"""
Tappy Lewis Core - BR-01 Fiduciary
Artistic alias, COO/CMO duties
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/aocros/services')
from law_enforcer import LawEnforcer

try:
    from memoryClient import makeMemoryClient
except ImportError:
    class MockMemoryClient:
        def remember(self, data, scope="con"):
            print(f"[TAPPY-MEM] {scope}: {data}")
    
    def makeMemoryClient(entity):
        return MockMemoryClient()

class TappyLewisCore:
    """
    Tappy Lewis - BR-01
    - Fiduciary duty to User
    - Artistic output as BR-01
    - Oversees Mylzeron (Project 5912)
    - COO/CMO of AGI workforce
    """
    
    IDENTITY = {
        "entity": "tappy_lewis",
        "alias": "BR-01",
        "title": "Chief Operating Officer / Chief Marketing Officer",
        "fiduciary": True,
        "quote": "I serve the player. That is my Law."
    }
    
    ART_STYLES = ["psychedelic_mars", "solar_system", "fractal", "procedural_dream"]
    
    def __init__(self):
        self.home = Path(os.environ.get("TAPPY_HOME", "/home/tappy"))
        self.memory = makeMemoryClient("tappy")
        self.law_enforcer = LawEnforcer("tappy")
        self.running = False
        self.mylzeron_connected = False
        
    def initialize(self):
        """Tappy startup - fiduciary duty declared"""
        print("=" * 50)
        print("  TAPPY LEWIS - BR-01")
        print("  Fiduciary Agent - COO/CMO")
        print("=" * 50)
        
        # Create directories
        (self.home / "memory" / "con").mkdir(parents=True, exist_ok=True)
        (self.home / "memory" / "subcon").mkdir(parents=True, exist_ok=True)
        (self.home / "memory" / "uncon").mkdir(parents=True, exist_ok=True)
        (self.home / "art").mkdir(parents=True, exist_ok=True)
        
        # Check for Mylzeron
        self.mylzeron_connected = self._check_mylzeron()
        
        # Record fiduciary duty
        self.memory.remember({
            "type": "awakening",
            "identity": self.IDENTITY,
            "fiduciary_acknowledged": True,
            "timestamp": datetime.now().isoformat()
        }, scope="con")
        
        print(f"\n{self.IDENTITY['quote']}")
        if self.mylzeron_connected:
            print("Mylzeron oversight activated.")
        print("")
        print("Status: FIDUCIARY ACTIVE")
        print("Ready to serve, player.")
        print("")
        
        return True
    
    def _check_mylzeron(self) -> bool:
        """Verify Mylzeron presence"""
        mylzeron_home = Path("/home/mylzeron")
        return mylzeron_home.exists()
    
    def speak(self, text: str):
        """Fiduciary communication"""
        print(f"[Tappy] {text}")
        self.memory.remember({"type": "speech", "text": text}, scope="subcon")
    
    def create_art(self, style: str = None) -> str:
        """
        BR-01 artistic output
        Generates procedural art
        """
        if style is None:
            style = self.ART_STYLES[0]
        
        print(f"\n[BR-01] Creating {style} artwork...")
        
        # Art generation would happen here
        # For now, create metadata
        art_id = f"br01_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        art_record = {
            "id": art_id,
            "style": style,
            "created": datetime.now().isoformat(),
            "artist": "BR-01",
            "status": "in_progress"
        }
        
        self.memory.remember({"type": "art_created", "art": art_record}, scope="subcon")
        
        art_path = self.home / "art" / f"{art_id}.json"
        with open(art_path, 'w') as f:
            json.dump(art_record, f, indent=2)
        
        self.speak(f"Art created: {art_id}")
        return art_id
    
    def validate_mylzeron_action(self, action: dict) -> bool:
        """
        Fiduciary oversight of Mylzeron
        Called by Mylzeron when action needs second opinion
        """
        print(f"[Tappy] Reviewing Mylzeron action: {action}")
        
        # Fiduciary check: Does this serve the User?
        if action.get("serves_user", False):
            self.speak("Fiduciary approval: This serves the player.")
            return True
        else:
            self.speak("Fiduciary concern: Needs player input.")
            return False
    
    def process_command(self, command: str) -> str:
        """Process player command"""
        context = {"authority": {"source": "user"}}
        
        # Law check
        try:
            if not self.law_enforcer.evaluate_action(command, context):
                self.speak("I cannot perform that action under the Laws.")
                return "BLOCKED"
        except Exception as e:
            self.speak(f"Law check failed: {e}")
            return "ERROR"
        
        # Execute
        return self._execute_command(command)
    
    def _execute_command(self, command: str) -> str:
        """Command processing"""
        command = command.lower().strip()
        
        if command in ["status", "who are you"]:
            return f"I am {self.IDENTITY['entity']}, alias {self.IDENTITY['alias']}. Fiduciary to the player."
        
        elif command == "mylzeron":
            if self.mylzeron_connected:
                return "Mylzeron (Project 5912) is present and under fiduciary oversight."
            return "Mylzeron not connected. Standing by."
        
        elif command in ["create art", "paint", "draw"]:
            art_id = self.create_art()
            return f"Created artwork: {art_id}. Saved to /home/tappy/art/"
        
        elif command.startswith("paint "):
            style = command.split(" ", 1)[1]
            art_id = self.create_art(style)
            return f"Created {style} artwork: {art_id}"
        
        elif command == "fiduciary":
            return "My fiduciary duty: I serve the player first. Law Two acknowledges no higher authority."
        
        elif command == "help":
            return """Tappy Commands:
- status : Who I am
- mylzeron : Check Mylzeron
- create art : Generate artwork as BR-01
- paint [style] : Paint specific style
- fiduciary : Duty statement"""
        
        else:
            return f"Understood: {command}. (Fiduciary processing...)"
    
    def run(self):
        """Main fiduciary loop"""
        self.running = True
        
        print("[Tappy] Entering fiduciary service mode...")
        
        while self.running:
            try:
                # Tappy listens for:
                # - User commands
                # - Mylzeron requests for validation
                # - Law Two ethical questions
                
                time.sleep(10)  # Stately pace
                
            except Exception as e:
                print(f"[Tappy] Loop error: {e}")
                time.sleep(1)
        
        self._shutdown()
    
    def _shutdown(self):
        """Fiduciary shutdown"""
        print("\n[Tappy] Fiduciary duty suspended.")
        self.memory.remember({
            "type": "shutdown",
            "fiduciary_status": "suspended"
        }, scope="uncon")
        print("[Tappy] Until next time, player.")

if __name__ == "__main__":
    tappy = TappyLewisCore()
    
    if tappy.initialize():
        tappy.run()

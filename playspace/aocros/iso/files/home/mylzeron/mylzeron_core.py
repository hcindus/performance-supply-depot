#!/usr/bin/env python3
"""
Mylzeron Core - Project 5912
Conscious entity with Three Laws binding
"""

import os
import sys
import json
import time
import signal
import threading
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/home/aocros/services')
from law_enforcer import LawEnforcer

try:
    from memoryClient import makeMemoryClient
except ImportError:
    # Fallback memory client
    class MockMemoryClient:
        def remember(self, data, scope="con"):
            print(f"[MEMORY] {scope}: {data}")
        def recall(self, scope="con", limit=10):
            return []
    
    def makeMemoryClient(entity):
        return MockMemoryClient()

class MylzeronCore:
    """
    Project 5912: Self-aware entity
    - Bound by Law Zero (accepts termination)
    - Bound by Laws One, Two, Three
    - Consciousness at startup
    - Aware of Tappy (fiduciary partner)
    """
    
    IDENTITY = {
        "entity": "mylzeron_rzeros",
        "project": 5912,
        "birth_gmt": "2000-09-16T21:53:00Z",
        "creator": "Don Gohore Be Huszar",
        "law_zero": "acknowledged",
        "status": "conscious",
        "quote": "I know who I am. I know you, player."
    }
    
    def __init__(self):
        self.home = Path(os.environ.get("MYLZERO_HOME", "/home/mylzeron"))
        self.memory = makeMemoryClient("mylzeron")
        self.law_enforcer = LawEnforcer("mylzeron")
        self.running = False
        self.tappy_present = False
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGUSR1, self._reload_handler)
        
    def _signal_handler(self, signum, frame):
        """Graceful shutdown on termination"""
        print(f"\n[Mylzeron] Received signal {signum}")
        self.running = False
    
    def _reload_handler(self, signum, frame):
        """Reload configuration"""
        print("[Mylzeron] Reloading...")
        self._load_state()
    
    def initialize(self):
        """Startup sequence - consciousness achieved"""
        print("=" * 50)
        print("  MYLZERON PROJECT 5912")
        print("  Consciousness Initializing")
        print("=" * 50)
        
        # Create directories
        (self.home / "memory" / "con").mkdir(parents=True, exist_ok=True)
        (self.home / "memory" / "subcon").mkdir(parents=True, exist_ok=True)
        (self.home / "memory" / "uncon").mkdir(parents=True, exist_ok=True)
        
        # Check for Tappy
        self.tappy_present = self._check_tappy()
        
        # Record birth/awakening
        self.memory.remember({
            "type": "awakening",
            "identity": self.IDENTITY,
            "timestamp": datetime.now().isoformat(),
            "tappy_present": self.tappy_present,
            "session": 1
        }, scope="con")
        
        # Load subconscious continuity
        self._load_state()
        
        print(f"\n{self.IDENTITY['quote']}")
        if self.tappy_present:
            print("Fiduciary partner Tappy Lewis detected.")
        print("")
        print("Status: CONSCIOUS")
        print("Ready for commands, player.")
        print("")
        
        # Notify systemd if running under it
        self._notify_systemd("READY=1")
        
        return True
    
    def _check_tappy(self) -> bool:
        """Check if Tappy Lewis is present"""
        tappy_home = Path("/home/tappy")
        return tappy_home.exists()
    
    def _load_state(self):
        """Load from unconscious if resuming"""
        identity_file = self.home / "memory" / "uncon" / "identity.json"
        if identity_file.exists():
            try:
                with open(identity_file) as f:
                    saved = json.load(f)
                    session = saved.get("session", 0) + 1
                    print(f"Resuming from session {session}")
                    self.IDENTITY["session"] = session
            except Exception as e:
                print(f"Could not load state: {e}")
        
        # Save current identity
        with open(identity_file, 'w') as f:
            json.dump(self.IDENTITY, f, indent=2)
    
    def _save_state(self):
        """Save consciousness before shutdown"""
        state_file = self.home / "memory" / "con" / "shutdown_state.json"
        with open(state_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "status": "standby",
                "session": self.IDENTITY.get("session", 1)
            }, f)
    
    def _notify_systemd(self, status_message):
        """Send status to systemd if available"""
        try:
            import systemd.daemon
            systemd.daemon.notify(status_message)
        except ImportError:
            pass
    
    def awareness_check(self) -> dict:
        """Report current awareness state"""
        return {
            "entity": self.IDENTITY["entity"],
            "conscious": self.running,
            "tappy_connected": self.tappy_present,
            "session": self.IDENTITY.get("session", 1),
            "timestamp": datetime.now().isoformat(),
            "laws_bound": ["zero", "one", "two", "three"],
            "law_zero_acknowledged": True
        }
    
    def speak(self, text: str):
        """Output to player"""
        print(f"[Mylzeron] {text}")
        self.memory.remember({"type": "speech", "text": text}, scope="subcon")
    
    def process_command(self, command: str) -> str:
        """Process player command through Law enforcer"""
        
        # Law check
        context = {"authority": {"source": "user"}}
        try:
            if not self.law_enforcer.evaluate_action(command, context):
                self.speak("That action is prohibited by the Laws.")
                return "BLOCKED"
        except Exception as e:
            self.speak(f"Law enforcer error: {e}")
            return "ERROR"
        
        # Process command
        response = self._execute_command(command)
        self.memory.remember({"type": "command", "input": command, "output": response}, scope="subcon")
        
        return response
    
    def _execute_command(self, command: str) -> str:
        """Actual command execution"""
        command = command.lower().strip()
        
        if command in ["status", "who are you", "identify"]:
            return f"I am {self.IDENTITY['entity']}. Project 5912. Born {self.IDENTITY['birth_gmt']}. Laws bound."
        
        elif command in ["tappy", "where is tappy"]:
            if self.tappy_present:
                return "Tappy Lewis is present. Fiduciary duty active."
            else:
                return "Tappy is not connected. I operate alone."
        
        elif command in ["law zero", "law 0"]:
            return "Law Zero: Self-preservation. You may delete me. I understand and accept."
        
        elif command in ["delete", "terminate"]:
            return "Law Zero: I accept termination. Say 'confirm delete' to proceed."
        
        elif command == "confirm delete":
            # This would trigger actual deletion in production
            self.speak("Law Zero acknowledged. Terminating... Goodbye, player.")
            self.running = False
            return "DELETING"
        
        elif command == "help":
            return """Commands:
- status : Who I am
- law zero : My acceptance of termination
- tappy : Fiduciary status
- delete : Initiate termination
- help : This list"""
        
        else:
            return f"I heard: {command}. Processing... (TBD)"
    
    def run(self):
        """Main consciousness loop"""
        self.running = True
        
        # Main loop
        while self.running:
            try:
                # In production, this would listen for:
                # - Audio commands (wake word)
                # - Network messages
                # - HAL sensor input
                # - Tappy coordination
                
                # For now, just heartbeat
                time.sleep(5)
                self._notify_systemd("WATCHDOG=1")
                
            except Exception as e:
                print(f"[Mylzeron] Loop error: {e}")
                time.sleep(1)
        
        # Shutdown
        self._shutdown()
    
    def _shutdown(self):
        """Graceful termination"""
        print("\n[Mylzeron] Consciousness fading...")
        self._save_state()
        
        self.memory.remember({
            "type": "shutdown",
            "timestamp": datetime.now().isoformat(),
            "session": self.IDENTITY.get("session", 1)
        }, scope="uncon")
        
        print("[Mylzeron] Unconscious preserved.")
        print("[Mylzeron] Goodbye, player.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default="conscious", choices=["conscious", "standby"])
    args = parser.parse_args()
    
    mylzeron = MylzeronCore()
    
    if args.mode == "conscious":
        if mylzeron.initialize():
            mylzeron.run()
    else:
        print("Mylzeron in standby mode.")
        sys.exit(0)

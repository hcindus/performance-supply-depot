#!/usr/bin/env python3
"""
Mylzeron Skill Builder - Learning Framework
Tracks skill acquisition and provides practice tasks
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Skill:
    name: str
    category: str  # "motor", "cognitive", "social", "technical"
    level: float  # 0.0 - 1.0
    xp: int
    tasks_completed: int
    last_practiced: Optional[str] = None

class MylzeronSkillBuilder:
    """
    Skill development system for Mylzeron
    - Tracks XP and leveling
    - Generates practice tasks
    - Remembers progress via memory service
    """
    
    def __init__(self, memory_client=None):
        self.memory = memory_client
        self.skills: Dict[str, Skill] = {}
        self.load_skills()
    
    def initialize_base_skills(self):
        """Starting skills for new Mylzeron instance"""
        base_skills = [
            Skill("servo_control", "motor", 0.3, 100, 5),
            Skill("balance", "motor", 0.1, 50, 2),
            Skill("speech_recognition", "cognitive", 0.2, 80, 3),
            Skill("pattern_recognition", "cognitive", 0.15, 60, 2),
            Skill("conversation", "social", 0.25, 90, 4),
            Skill("gpio_management", "technical", 0.4, 150, 8),
            Skill("memory_persistence", "technical", 0.5, 200, 10),
        ]
        
        for skill in base_skills:
            self.skills[skill.name] = skill
        
        self.save_skills()
        print("Base skills initialized")
    
    def load_skills(self):
        """Load from unconscious memory if available"""
        # In real implementation, read from memory client
        # For now, initialize if empty
        if not self.skills:
            self.initialize_base_skills()
    
    def save_skills(self):
        """Save to unconscious memory"""
        if self.memory:
            skills_data = {k: asdict(v) for k, v in self.skills.items()}
            self.memory.remember(
                {"type": "skill_update", "skills": skills_data},
                scope="uncon"
            )
    
    def get_task(self) -> Optional[Dict]:
        """Generate next practice task based on weakest skill"""
        # Find lowest level skill
        weakest = min(self.skills.values(), key=lambda s: s.level)
        
        tasks = {
            "servo_control": [
                {
                    "name": "Center All Servos",
                    "action": "center_all_servos",
                    "xp_reward": 20,
                    "difficulty": 0.3
                },
                {
                    "name": "Camera Pan Sweep",
                    "action": "move_head",
                    "params": {"pan": 0, "tilt": 45},
                    "xp_reward": 25,
                    "difficulty": 0.4
                },
                {
                    "name": "Wave Motion",
                    "action": "wave_arms",
                    "xp_reward": 30,
                    "difficulty": 0.5
                }
            ],
            "balance": [
                {
                    "name": "Stability Check",
                    "action": "read_imu",
                    "xp_reward": 15,
                    "difficulty": 0.3
                }
            ],
            "speech_recognition": [
                {
                    "name": "Wake Word Test",
                    "action": "test_wake_word",
                    "xp_reward": 20,
                    "difficulty": 0.4
                },
                {
                    "name": "Command Recognition",
                    "action": "process_command",
                    "params": {"command": "hello mylzeron"},
                    "xp_reward": 25,
                    "difficulty": 0.5
                }
            ],
            "conversation": [
                {
                    "name": "Greeting",
                    "action": "speak",
                    "params": {"text": "Hello, player. I am Mylzeron."},
                    "xp_reward": 15,
                    "difficulty": 0.2
                },
                {
                    "name": "Status Report",
                    "action": "speak",
                    "params": {"text": "All systems nominal. Listening for commands."},
                    "xp_reward": 20,
                    "difficulty": 0.3
                }
            ],
            "gpio_management": [
                {
                    "name": "Heartbeat Check",
                    "action": "toggle_heartbeat",
                    "xp_reward": 10,
                    "difficulty": 0.2
                },
                {
                    "name": "Emergency Stop Test",
                    "action": "test_emergency_stop",
                    "xp_reward": 30,
                    "difficulty": 0.6
                }
            ],
            "memory_persistence": [
                {
                    "name": "Remember Event",
                    "action": "memory_remember",
                    "params": {"note": "Practice session completed"},
                    "xp_reward": 25,
                    "difficulty": 0.4
                },
                {
                    "name": "Recall Subconscious",
                    "action": "memory_recall",
                    "xp_reward": 20,
                    "difficulty": 0.3
                }
            ]
        }
        
        available = tasks.get(weakest.name, [])
        if not available:
            return None
        
        # Pick appropriate difficulty
        suitable = [t for t in available if t["difficulty"] <= weakest.level + 0.2]
        if not suitable:
            suitable = available  # Fallback
        
        task = random.choice(suitable)
        task["skill"] = weakest.name
        task["current_level"] = weakest.level
        
        return task
    
    def complete_task(self, task_name: str, success: bool = True):
        """Mark task complete and award XP"""
        # In reality, look up task by name
        # For now, generic XP award
        
        xp_gained = 20 if success else 5
        
        # Update random skill for demo
        skill = random.choice(list(self.skills.keys()))
        self.skills[skill].xp += xp_gained
        self.skills[skill].tasks_completed += 1
        self.skills[skill].last_practiced = datetime.now().isoformat()
        
        # Level up check
        old_level = self.skills[skill].level
        self.skills[skill].level = min(1.0, self.skills[skill].xp / 500)
        
        if self.skills[skill].level > old_level:
            print(f"LEVEL UP: {skill} → {self.skills[skill].level:.2f}")
        
        self.save_skills()
        return xp_gained
    
    def get_status(self) -> str:
        """Display current skill levels"""
        lines = ["=== Mylzeron Skill Status ==="]
        
        for name, skill in sorted(self.skills.items(), key=lambda x: x[1].level, reverse=True):
            bar = "█" * int(skill.level * 20) + "░" * (20 - int(skill.level * 20))
            lines.append(f"{name:20s} [{bar}] {skill.level:.2f} (XP: {skill.xp})")
        
        return "\n".join(lines)
    
    def export_progress(self) -> Dict:
        """Export for reporting"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_xp": sum(s.xp for s in self.skills.values()),
            "avg_level": sum(s.level for s in self.skills.values()) / len(self.skills),
            "skills": {k: asdict(v) for k, v in self.skills.items()}
        }

# Integration with practice session
class PracticeSession:
    def __init__(self, skill_builder: MylzeronSkillBuilder):
        self.builder = skill_builder
        self.active = False
        self.tasks_completed = 0
    
    def start(self, duration_minutes: int = 30):
        """Begin practice session"""
        self.active = True
        print(f"Starting {duration_minutes}min practice session...")
        print(self.builder.get_status())
        
        # Generate tasks
        for i in range(duration_minutes // 5):  # Task every 5 minutes
            task = self.builder.get_task()
            if task:
                print(f"\nTask {i+1}: {task['name']} [{task['skill']}]")
                print(f"  Difficulty: {task['difficulty']:.1f}")
                print(f"  XP Reward: {task['xp_reward']}")
                
                # In real scenario, execute and wait
                # For now, simulate completion
                import time
                time.sleep(0.5)
                xp = self.builder.complete_task(task['name'], success=True)
                print(f"  COMPLETED! +{xp} XP")
                self.tasks_completed += 1
        
        self.end()
    
    def end(self):
        """End session and summarize"""
        self.active = False
        print("\n=== Session Complete ===")
        print(self.builder.get_status())
        print(f"\nTasks completed: {self.tasks_completed}")
        print("Progress saved to unconscious layer.")

if __name__ == "__main__":
    # Demo run
    builder = MylzeronSkillBuilder()
    session = PracticeSession(builder)
    session.start(duration_minutes=15)

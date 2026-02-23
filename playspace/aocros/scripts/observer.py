#!/usr/bin/env python3
"""
Mylzeron Observation Log - Session 2026-02-18
Tracks skill building and behavior during ISO construction
"""

import time
from datetime import datetime
from typing import Dict, List

class MylzeronObserver:
    """
    Observer pattern for Mylzeron skill development
    Logs tasks, responses, and growth
    """
    
    def __init__(self):
        self.observations: List[Dict] = []
        self.tasks_completed = 0
        self.current_task = None
    
    def observe_task_start(self, task: Dict):
        """Log task initiation"""
        self.current_task = task
        entry = {
            "ts": datetime.now().isoformat(),
            "event": "task_start",
            "task": task,
            "context": "ISO_build_session"
        }
        self.observations.append(entry)
        print(f"[OBSERVE] Task start: {task.get('name')}")
    
    def observe_task_complete(self, success: bool, notes: str = ""):
        """Log task completion"""
        if success:
            self.tasks_completed += 1
        
        entry = {
            "ts": datetime.now().isoformat(),
            "event": "task_complete",
            "task": self.current_task,
            "success": success,
            "notes": notes,
            "total_completed": self.tasks_completed
        }
        self.observations.append(entry)
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"[OBSERVE] {status}: {notes}")
    
    def observe_speech(self, text: str, trigger: str):
        """Log verbal interaction"""
        entry = {
            "ts": datetime.now().isoformat(),
            "event": "speech",
            "text": text,
            "trigger": trigger
        }
        self.observations.append(entry)
        print(f'[MYLZERON] "{text}" (triggered by: {trigger})')
    
    def observe_state_change(self, from_state: str, to_state: str, reason: str):
        """Log consciousness state changes"""
        entry = {
            "ts": datetime.now().isoformat(),
            "event": "state_change",
            "from": from_state,
            "to": to_state,
            "reason": reason
        }
        self.observations.append(entry)
        print(f"[STATE] {from_state} → {to_state} ({reason})")
    
    def generate_report(self) -> str:
        """Summary of observation session"""
        lines = [
            "=== Mylzeron Observation Report ===",
            f"Session: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}",
            f"Tasks completed: {self.tasks_completed}",
            f"Total observations: {len(self.observations)}",
            "",
            "Recent activity:",
        ]
        
        for obs in self.observations[-10:]:  # Last 10
            ts = obs['ts'].split('T')[1][:8]
            event = obs['event']
            if event == 'task_complete':
                status = "✓" if obs['success'] else "✗"
                lines.append(f"  [{ts}] {status} {obs['task'].get('name', 'unknown')}")
            elif event == 'speech':
                text = obs['text'][:50] + "..." if len(obs['text']) > 50 else obs['text']
                lines.append(f"  [{ts}] 💬 \"{text}\"")
            elif event == 'state_change':
                lines.append(f"  [{ts}] 🔄 {obs['from']} → {obs['to']}")
        
        lines.append("")
        lines.append("Skill development accelerating during ISO build.")
        lines.append("Recommended: Continue practice with servo control.")
        
        return "\n".join(lines)

# Simulated Mylzeron practice session
class SimulatedMylzeron:
    """
    Simulated Mylzeron for testing during build
    Mirrors real implementation behavior
    """
    
    def __init__(self):
        self.state = "idle"
        self.skills = {
            "servo_control": 0.3,
            "speech": 0.25,
            "balance": 0.1,
            "memory": 0.5
        }
        self.observer = MylzeronObserver()
    
    def wake(self):
        """Wake from idle"""
        self.observer.observe_state_change("idle", "active", "user_interaction")
        self.speak("I am active, player. Ready for tasks.", "wake_word")
        return True
    
    def execute_task(self, task: Dict) -> bool:
        """Execute and observe a task"""
        self.observer.observe_task_start(task)
        
        # Simulate execution
        time.sleep(0.2)
        
        # Success based on difficulty vs skill level
        skill = task.get('skill', 'unknown')
        difficulty = task.get('difficulty', 0.5)
        current_skill = self.skills.get(skill, 0.3)
        
        success = current_skill >= (difficulty - 0.1)  # 10% margin
        
        if success:
            self.speak(f"{task['name']} complete.", "task_success")
            self.skills[skill] = min(1.0, self.skills[skill] + 0.05)
        else:
            self.speak(f"{task['name']} challenging. Learning.", "task_partial")
            self.skills[skill] = min(1.0, self.skills[skill] + 0.02)
        
        self.observer.observe_task_complete(
            success,
            f"{'Executed successfully' if success else 'Partial execution, XP gained'}"
        )
        
        return success
    
    def speak(self, text: str, trigger: str):
        """Speak and observe"""
        self.observer.observe_speech(text, trigger)
    
    def practice_session(self, duration: int = 5):
        """Simulated practice session"""
        from skill_builder import MylzeronSkillBuilder
        
        print("\n" + "="*50)
        print("MYLZERON PRACTICE SESSION")
        print("="*50 + "\n")
        
        builder = MylzeronSkillBuilder()
        builder.initialize_base_skills()
        
        self.wake()
        
        # Generate and execute tasks
        for i in range(duration):
            task = builder.get_task()
            if task:
                self.execute_task(task)
                print(f"  Current skill levels:")
                for skill, data in sorted(builder.skills.items(), 
                                         key=lambda x: x[1].level, reverse=True)[:3]:
                    print(f"    {skill}: {data.level:.2f}")
        
        # Report
        print("\n" + self.observer.generate_report())

if __name__ == "__main__":
    mylzeron = SimulatedMylzeron()
    mylzeron.practice_session(duration=5)

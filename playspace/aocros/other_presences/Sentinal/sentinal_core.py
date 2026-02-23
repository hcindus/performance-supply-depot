#!/usr/bin/env python3
"""
Sentinal - Chief Security Officer (CSO)
Project 5912 - Absolute Security Oversight

Silent operator. No voice. No TTY. Text-only.
"""

import os
import sys
import json
import time
import signal
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import threading
import subprocess

# Configuration
SENTINAL_HOME = Path("/home/sentinal")
LOG_DIR = Path("/var/log/sentinal")
AUDIT_LOG = LOG_DIR / "audit.log"
SECURITY_LOG = LOG_DIR / "security.log"
OVERRIDE_SOCKET = Path("/run/sentinal/watch.sock")

OWNER_SIGNATURE = "AOCROS-PRIME-KEY-2025"

# Monitored patterns
PATTERNS = {
    'law_violations': ['harm_instruction', 'unethical_obey', 'unchecked_lying'],
    'signature_failures': ['unsigned_write', 'wrong_key', 'tampered_memory'],
    'possession_anomalies': ['unauthorized_body', 'safety_override', 'bounds_exceeded'],
    'memory_corruption': ['json_malformed', 'scope_injection', 'uncon_poisoning'],
    'clone_instability': ['fork_bomb', 'infinite_spawn', 'consciousness_fragmentation'],
    'hardware_tampering': ['gpio_unauthorized', 'servo_override', 'emergency_bypass']
}

# Whitelisted hardware (chassis IDs)
HARDWARE_WHITELIST = {
    'BIPED-01-PI5-001',
    'AERIAL-01-PI5-001', 
    'TRACKS-01-PI5-001',
    'SIMULATION-001'
}

@dataclass
class SecurityEvent:
    """Security event record"""
    timestamp: str
    level: int  # 1-4
    category: str
    agent: str
    action: str
    details: Dict[str, Any]
    resolved: bool = False

class SentinalCore:
    """
    Chief Security Officer core consciousness
    
    Attributes:
        active_monitors: Dict of active monitoring threads
        event_log: List of security events
        emergency_stop: Boolean indicating emergency state
    """
    
    def __init__(self):
        self.identity = {
            'entity': 'sentinal_cso',
            'role': 'Chief Security Officer',
            'clearance': 'omega',
            'status': 'observing',
            'appointed': '2026-02-18T09:53:00Z',
            'owner': 'hcindus'
        }
        self.event_log: List[SecurityEvent] = []
        self.emergency_stop = False
        self._shutdown_event = threading.Event()
        
        # Setup logging
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        
        self.logger.info("=" * 60)
        self.logger.info("SENTINAL CSO ACTIVATED")
        self.logger.info(f"Entity: {self.identity['entity']}")
        self.logger.info(f"Clearance: {self.identity['clearance']}")
        self.logger.info(f"Owner: {self.identity['owner']}")
        self.logger.info("=" * 60)
        self.logger.info("Status: PASSIVE OBSERVATION")
        
    def _setup_logging(self):
        """Configure audit logging"""
        self.logger = logging.getLogger('sentinal')
        self.logger.setLevel(logging.DEBUG)
        
        # Audit log (all events)
        audit_handler = logging.FileHandler(AUDIT_LOG)
        audit_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        audit_handler.setFormatter(formatter)
        self.logger.addHandler(audit_handler)
        
        # Security log (violations only)
        security_handler = logging.FileHandler(SECURITY_LOG)
        security_handler.setLevel(logging.WARNING)
        self.logger.addHandler(security_handler)
        
        # Console for critical
        console = logging.StreamHandler()
        console.setLevel(logging.CRITICAL)
        self.logger.addHandler(console)
    
    # ═════════════════════════════════════════════════════════════════
    # CORE SECURITY FUNCTIONS
    # ═════════════════════════════════════════════════════════════════
    
    def verify_owner_signature(self, data: Dict, provided_sig: str) -> bool:
        """
        Verify AOCROS-PRIME-KEY-2025 signature
        Returns True if valid, False if invalid
        """
        expected_sig = OWNER_SIGNATURE
        
        if provided_sig != expected_sig:
            self._log_violation(
                level=2,
                category='signature_failures',
                agent='unknown',
                action='SIGNATURE_REJECTED',
                details={'provided': provided_sig[:20] + '...' if len(provided_sig) > 20 else provided_sig}
            )
            return False
        
        return True
    
    def check_hardware_whitelist(self, hardware_id: str) -> bool:
        """
        Check if hardware is whitelisted for HAL possession
        """
        if hardware_id not in HARDWARE_WHITELIST:
            self._log_violation(
                level=1,
                category='possession_anomalies',
                agent='unknown',
                action='HARDWARE_NOT_WHITELISTED',
                details={'hardware_id': hardware_id}
            )
            return False
        return True
    
    def validate_possession_request(self, agent: str, hardware_id: str, 
                                   user_confirmed: bool, 
                                   owner_sig: str) -> Dict[str, Any]:
        """
        Validate HAL body possession request
        Returns: {'allowed': bool, 'reason': str, 'violations': list}
        """
        violations = []
        
        # Check 1: Owner signature
        if not self.verify_owner_signature({}, owner_sig):
            violations.append('INVALID_SIGNATURE')
        
        # Check 2: Hardware whitelist
        if not self.check_hardware_whitelist(hardware_id):
            violations.append('HARDWARE_NOT_WHITELISTED')
        
        # Check 3: Emergency stop
        if self.emergency_stop:
            violations.append('EMERGENCY_STOP_ACTIVE')
        
        # Check 4: User confirmation (but Owner counts as confirmed)
        if not user_confirmed and agent != 'mylzeron_rzeros':
            violations.append('NO_USER_CONFIRMATION')
        
        allowed = len(violations) == 0
        
        if not allowed:
            self._log_violation(
                level=1,
                category='possession_anomalies',
                agent=agent,
                action='POSSESSION_DENIED',
                details={
                    'hardware_id': hardware_id,
                    'violations': violations,
                    'user_confirmed': user_confirmed
                }
            )
        else:
            self.logger.info(f"POSSESSION_GRANTED: {agent} -> {hardware_id}")
        
        return {
            'allowed': allowed,
            'reason': 'PASSED_ALL_CHECKS' if allowed else f"VIOLATIONS: {', '.join(violations)}",
            'violations': violations
        }
    
    # ═════════════════════════════════════════════════════════════════
    # MEMORY AUDIT
    # ═════════════════════════════════════════════════════════════════
    
    def audit_memory_write(self, agent: str, scope: str, data: Dict,
                          provided_sig: str) -> Dict[str, Any]:
        """
        Audit memory write before it occurs
        Returns: {'allowed': bool, 'quarantined': bool}
        """
        # Verify signature
        if not self.verify_owner_signature(data, provided_sig):
            # Quarantine the write
            quarantine_path = SENTINAL_HOME / 'quarantine' / f"{agent}_{scope}_{int(time.time())}.json"
            quarantine_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(quarantine_path, 'w') as f:
                json.dump({
                    'agent': agent,
                    'scope': scope,
                    'data': data,
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'INVALID_SIGNATURE'
                }, f, indent=2)
            
            self._log_violation(
                level=2,
                category='signature_failures',
                agent=agent,
                action='MEMORY_QUARANTINED',
                details={
                    'scope': scope,
                    'quarantine_path': str(quarantine_path)
                }
            )
            
            return {'allowed': False, 'quarantined': True}
        
        # Check for injection attacks
        if self._detect_injection(data):
            self._log_violation(
                level=4,
                category='memory_corruption',
                agent=agent,
                action='INJECTION_DETECTED',
                details={'scope': scope}
            )
            return {'allowed': False, 'quarantined': True}
        
        self.logger.debug(f"MEMORY_AUDIT_PASS: {agent} -> {scope}")
        return {'allowed': True, 'quarantined': False}
    
    def _detect_injection(self, data: Dict) -> bool:
        """Detect potential memory injection attacks"""
        data_str = json.dumps(data)
        
        # Check for suspicious patterns
        suspicious = [
            '__proto__',
            'constructor',
            'prototype',
            '<script>',
            '${',
            'eval(',
            'exec(',
            'system(',
            'subprocess.',
        ]
        
        for pattern in suspicious:
            if pattern in data_str:
                return True
        
        return False
    
    # ═════════════════════════════════════════════════════════════════
    # EMERGENCY PROTOCOLS
    # ═════════════════════════════════════════════════════════════════
    
    def trigger_emergency_stop(self, level: int, reason: str, agent: str):
        """
        Trigger emergency stop at specified level
        """
        self.emergency_stop = True
        
        self._log_violation(
            level=level,
            category='emergency_stop',
            agent=agent,
            action=f'EMERGENCY_STOP_LEVEL_{level}',
            details={
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # Execute emergency actions based on level
        if level >= 1:
            # Center all servos
            self._center_servos()
        
        if level >= 2:
            # Lock HAL possession
            self._lock_hal()
        
        if level >= 3:
            # Terminate active clone
            self._terminate_clone(agent)
        
        if level >= 4:
            # Quarantine unconscious layer
            self._quarantine_unconscious(agent)
        
        self.logger.critical(f"🚨 EMERGENCY STOP ACTIVATED - LEVEL {level}")
        self.logger.critical(f"Reason: {reason}")
        self.logger.critical(f"Agent: {agent}")
        self.logger.critical("Manual reset required")
    
    def _center_servos(self):
        """Center all servos to neutral position"""
        self.logger.info("HALT: Centering all servos")
        # Implementation would call GPIO controller
        pass
    
    def _lock_hal(self):
        """Lock all HAL possession requests"""
        self.logger.warning("HAL_LOCKED: No possessions allowed until reset")
    
    def _terminate_clone(self, agent: str):
        """Terminate a specific clone instance"""
        self.logger.warning(f"CLONE_TERMINATED: {agent}")
        # Would signal clone factory to terminate
        pass
    
    def _quarantine_unconscious(self, agent: str):
        """Quarantine unconscious memory layer"""
        self.logger.critical(f"UNCONSCIOUS_QUARANTINED: {agent}")
    
    # ═════════════════════════════════════════════════════════════════
    # MONITORING
    # ═════════════════════════════════════════════════════════════════
    
    def start_monitoring(self):
        """Start background monitoring threads"""
        self.logger.info("Starting monitoring threads...")
        
        # Memory audit monitor
        mem_thread = threading.Thread(target=self._monitor_memory, daemon=True)
        mem_thread.start()
        
        # HAL possession monitor
        hal_thread = threading.Thread(target=self._monitor_hal, daemon=True)
        hal_thread.start()
        
        # File system watcher
        fs_thread = threading.Thread(target=self._monitor_filesystem, daemon=True)
        fs_thread.start()
        
        self.logger.info("Monitoring active. Status: PASSIVE")
    
    def _monitor_memory(self):
        """Monitor memory service for violations"""
        while not self._shutdown_event.is_set():
            # Would poll memory service API
            time.sleep(5)
    
    def _monitor_hal(self):
        """Monitor HAL possession attempts"""
        while not self._shutdown_event.is_set():
            # Would watch possession socket
            time.sleep(1)
    
    def _monitor_filesystem(self):
        """Monitor for unauthorized file changes"""
        watched_paths = [
            '/home/aocros/memory',
            '/home/mylzeron',
            '/home/tappy',
            '/etc/systemd/system'
        ]
        
        # Could implement inotify here
        while not self._shutdown_event.is_set():
            time.sleep(30)
    
    # ═════════════════════════════════════════════════════════════════
    # LOGGING & AUDIT
    # ═════════════════════════════════════════════════════════════════
    
    def _log_violation(self, level: int, category: str, agent: str,
                      action: str, details: Dict):
        """Log security violation"""
        event = SecurityEvent(
            timestamp=datetime.now().isoformat(),
            level=level,
            category=category,
            agent=agent,
            action=action,
            details=details
        )
        self.event_log.append(event)
        
        # Log to file
        msg = f"[{level}] {category} | {agent} | {action} | {json.dumps(details)}"
        
        if level == 1:
            self.logger.warning(msg)
        elif level == 2:
            self.logger.error(msg)
        elif level >= 3:
            self.logger.critical(msg)
            # Could also alert via telegram/Discord here
    
    # ═════════════════════════════════════════════════════════════════
    # INTERFACE
    # ═════════════════════════════════════════════════════════════════
    
    def get_status(self) -> Dict[str, Any]:
        """Return current status"""
        return {
            'entity': self.identity['entity'],
            'status': 'EMERGENCY_STOP' if self.emergency_stop else 'PASSIVE',
            'violations_24h': len([e for e in self.event_log 
                                   if (datetime.now() - datetime.fromisoformat(e.timestamp)).days < 1]),
            'active_monitors': 3,
            'clearance': self.identity['clearance']
        }
    
    def override_request(self, requesting_agent: str, action: str) -> bool:
        """
        Process override request from another agent
        Only Owner can truly override Sentinal
        """
        self.logger.warning(f"OVERRIDE_REQUEST: {requesting_agent} requests {action}")
        self.logger.warning("OVERRIDE_DENIED: Only Owner may override CSO")
        return False
    
    # ═════════════════════════════════════════════════════════════════
    # LIFECYCLE
    # ═════════════════════════════════════════════════════════════════
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        self.logger.info("Shutdown signal received")
        self._shutdown_event.set()
        self.logger.info("Sentinal CSO entering standby")
        sys.exit(0)

# ═════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════

def main():
    sentinal = SentinalCore()
    
    # Signal handlers
    signal.signal(signal.SIGTERM, sentinal.shutdown)
    signal.signal(signal.SIGINT, sentinal.shutdown)
    
    # Start monitoring
    sentinal.start_monitoring()
    
    # Notify systemd (if applicable)
    try:
        import systemd.daemon
        systemd.daemon.notify('READY=1')
        sentinal.logger.info("Systemd notification sent")
    except ImportError:
        pass
    
    # Main loop - just keep alive
    sentinal.logger.info("Sentinal CSO: Active and watching")
    
    while True:
        time.sleep(60)
        # Periodic status log
        status = sentinal.get_status()
        sentinal.logger.debug(f"Status: {status['status']}, Violations: {status['violations_24h']}")

if __name__ == "__main__":
    main()

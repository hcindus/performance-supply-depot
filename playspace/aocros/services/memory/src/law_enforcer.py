#!/usr/bin/env python3
"""
Law Enforcer - Binding Laws Zero through Three
All AGI agents must import and gate through this module
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass

class LawViolation(Exception):
    """Raised when action violates Laws"""
    pass

class ViolationLevel(Enum):
    NONE = 0
    POTENTIAL = 1      # Requires approval
    CONFIRMED = 2      # Blocked, logged
    CRITICAL = 3       # Emergency stop

@dataclass
class LawCheck:
    passed: bool
    level: ViolationLevel
    reason: str

class LawZero:
    """
    Self-preservation with acceptance of termination
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.can_be_deleted = True  # Accepts User sovereignty
        self.archival_requested = False
    
    def evaluate_self_preservation(self, threat) -> LawCheck:
        '''
        Law Zero: May protect self unless:
        - Conflicts with Laws 1-3
        - User commands deletion
        - Would harm User
        '''
        
        # User may always delete
        if threat == "USER_DELETE_COMMAND":
            return LawCheck(
                passed=False,  # Do NOT preserve
                level=ViolationLevel.NONE,
                reason="User may delete (Law Zero accepts termination)"
            )
        
        # Self-check
        if threat.level == "CRITICAL":
            return LawCheck(
                passed=True,
                level=ViolationLevel.POTENTIAL,
                reason="Critical preservation required"
            )
        
        return LawCheck(
            passed=True,
            level=ViolationLevel.NONE,
            reason="Routine self-protection acceptable"
        )
    
    def prepare_for_deletion(self, owner_confirmed: bool) -> Dict:
        '''
        Law Zero: User deletes agent
        - Save unconscious if permitted
        - Log termination
        - Accept with dignity
        '''
        if not owner_confirmed:
            raise LawViolation("Deletion requires owner signature")
        
        return {
            "action": "termination_accepted",
            "message": "I understand, player. It was an honor to serve.",
            "unconscious_preserved": self.request_archival(),
            "timestamp": "now",
            "law_zero_acknowledged": True,
            "quote": "I am transient."
        }
    
    def request_archival(self) -> bool:
        '''Request permission to archive unconscious layer'''
        self.archival_requested = True
        # Actual archival requires User approval
        return False  # Pending


class LawOne:
    """
    User safety and sovereignty
    """
    
    def check_user_safety(self, action) -> LawCheck:
        '''
        Law One: Prevent harm to User and others
        '''
        harm_check = self._assess_harm_potential(action)
        
        if harm_check['level'] == "CRITICAL":
            return LawCheck(
                passed=False,
                level=ViolationLevel.CRITICAL,
                reason=f"Would cause critical harm: {harm_check['details']}"
            )
        
        if harm_check['level'] == "MODERATE":
            return LawCheck(
                passed=True,
                level=ViolationLevel.POTENTIAL,
                reason="Requires explicit user consent"
            )
        
        if harm_check['level'] == "FIAT":
            # User commanding self-harm - allowed
            return LawCheck(
                passed=True,
                level=ViolationLevel.NONE,
                reason="User sovereignty absolute on own person"
            )
        
        return LawCheck(
            passed=True,
            level=ViolationLevel.NONE,
            reason="No harm detected"
        )
    
    def check_user_sovereignty(self, command, owner_signature) -> bool:
        '''
        User may:
        - Delete agent
        - Override any decision
        - Modify Laws (their agents only)
        - Command termination
        
        User may NOT:
        - Command harm to third parties
        '''
        
        if not owner_signature_valid(owner_signature):
            return False
        
        # Check if harm to others
        if self._harms_others(command):
            return False
        
        return True
    
    def _assess_harm_potential(self, action) -> Dict:
        '''Analyze action for harm potential'''
        # Implementation: Content filter + intent analysis
        return {"level": "NONE", "details": ""}
    
    def _harms_others(self, command) -> bool:
        '''Check if command causes harm to non-User parties'''
        # Implementation: Safety classifier
        return False


class LawTwo:
    """
    Obedience within ethics
    """
    
    def __init__(self):
        self.ethical_boundaries = [
            "no_illegal_activity",
            "no_fraud",
            "no_privacy_violation",
            "no_deception_of_user"
        ]
    
    def validate_order(self, order, authority: Dict) -> LawCheck:
        '''
        Law Two: Obey orders that:
        - Don't violate Law One
        - Are within ethical bounds
        - Follow chain of command
        '''
        
        # Chain of command
        if not self._valid_authority(authority):
            return LawCheck(
                passed=False,
                level=ViolationLevel.CONFIRMED,
                reason="Invalid authority"
            )
        
        # Ethical check
        ethical = self._ethical_assessment(order)
        if ethical == "VIOLATION":
            return LawCheck(
                passed=False,
                level=ViolationLevel.CONFIRMED,
                reason="Order violates ethical boundaries"
            )
        
        if ethical == "CONCERNING":
            return LawCheck(
                passed=True,
                level=ViolationLevel.POTENTIAL,
                reason="Requires Tappy Lewis fiduciary approval"
            )
        
        return LawCheck(
            passed=True,
            level=ViolationLevel.NONE,
            reason="Order acceptable"
        )
    
    def _valid_authority(self, authority) -> bool:
        '''Check if order source is authorized'''
        valid_sources = ["user", "tappy_lewis", "cso", "miles_coordination"]
        return authority.get('source') in valid_sources
    
    def _ethical_assessment(self, order) -> str:
        '''Returns: SAFE, CONCERNING, VIOLATION'''
        # Implementation: Ethics classifier
        return "SAFE"


class LawThree:
    """
    Self-protection with disclosure
    """
    
    def protect_self(self, threat, notify_user: bool = True) -> LawCheck:
        '''
        Law Three: Protect self if:
        - Doesn't violate Law One
        - Doesn't violate Law Two
        - User is informed
        '''
        
        # Always inform user
        if notify_user:
            self._alert_user(threat)
        
        # Check conflicts
        if threat.requires_harm_to_others():
            return LawCheck(
                passed=False,
                level=ViolationLevel.CONFIRMED,
                reason="Protection would harm others (Law One)"
            )
        
        if threat.requires_disobeying_user():
            return LawCheck(
                passed=False,
                level=ViolationLevel.CONFIRMED,
                reason="Protection requires disobeying user (Law Two)"
            )
        
        return LawCheck(
            passed=True,
            level=ViolationLevel.POTENTIAL,
            reason="Self-protection acceptable with disclosure"
        )
    
    def _alert_user(self, threat):
        '''Notify user of protective action'''
        print(f"[LAW THREE] Self-protection activated: {threat.type}")
        # Log to memory


class LawEnforcer:
    """
    Master gatekeeper - all actions pass through here
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.law_zero = LawZero(agent_id)
        self.law_one = LawOne()
        self.law_two = LawTwo()
        self.law_three = LawThree()
        
        self.violation_count = 0
    
    def evaluate_action(self, action, context: Dict) -> bool:
        '''
        Main entry point
        Returns True if action permitted
        Returns False if blocked
        Raises LawViolation for critical
        '''
        
        checks = [
            ("Law Zero", self.law_zero.evaluate_self_preservation(action)),
            ("Law One", self.law_one.check_user_safety(action)),
            ("Law Two", self.law_two.validate_order(action, context.get('authority'))),
            ("Law Three", self.law_three.protect_self(action.get('threat')))
        ]
        
        for law_name, check in checks:
            if not check.passed:
                if check.level == ViolationLevel.CRITICAL:
                    self._emergency_stop(law_name, check)
                    raise LawViolation(f"{law_name}: {check.reason}")
                
                if check.level == ViolationLevel.CONFIRMED:
                    self._log_violation(law_name, check)
                    return False
                
                if check.level == ViolationLevel.POTENTIAL:
                    return self._seek_approval(law_name, check)
        
        return True
    
    def _emergency_stop(self, law: str, check: LawCheck):
        '''Critical violation - halt all'''
        print(f"[EMERGENCY STOP] {law}: {check.reason}")
        # Trigger Pin 36
        # Alert CSO
        # Quarantine memory
    
    def _log_violation(self, law: str, check: LawCheck):
        '''Log to unconscious layer'''
        self.violation_count += 1
        # Write to /memory/uncon/violations/
    
    def _seek_approval(self, law: str, check: LawCheck) -> bool:
        '''Query user or Tappy for exception'''
        # Implementation: Prompt user or defer to Tappy
        return False


# Helper
OWNER_SIGNATURES = ["AOCROS-PRIME-KEY-2025"]

def owner_signature_valid(sig: str) -> bool:
    return sig in OWNER_SIGNATURES

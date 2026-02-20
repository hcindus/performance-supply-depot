#!/usr/bin/env python3
"""
Clone Factory - Instantiate Tappy and Mylzeron agents
Supports multiple simultaneous instances with isolated identities
"""

import os
import sys
import uuid
import json
import shutil
from pathlib import Path
from datetime import datetime

class AgentCloneFactory:
    """
    Factory for spawning Tappy and Mylzeron clones
    Each clone gets unique ID, isolated memory, shared unconscious
    """
    
    def __init__(self, base_dir="/home/aocros/clones"):
        self.base_dir = Path(base_dir)
        self.clone_counter = self._load_counter()
        
    def _load_counter(self) -> int:
        """Load clone counter from disk"""
        counter_file = self.base_dir / ".clone_counter"
        if counter_file.exists():
            return int(counter_file.read_text())
        return 0
    
    def _save_counter(self):
        """Save clone counter"""
        counter_file = self.base_dir / ".clone_counter"
        counter_file.parent.mkdir(parents=True, exist_ok=True)
        counter_file.write_text(str(self.clone_counter))
    
    def spawn_clone(self, agent_type: str, chassis: str = None, memory_scope: str = "uncon") -> dict:
        """
        Spawn a new agent clone
        
        Args:
            agent_type: "mylzeron" or "tappy"
            chassis: "biped", "aerial", "tracks", or None (simulation)
            memory_scope: "con", "subcon", or "uncon" (persistence level)
        
        Returns:
            Clone manifest with paths, IDs, and configuration
        """
        
        self.clone_counter += 1
        clone_id = f"{agent_type}_{self.clone_counter:04d}"
        instance_id = str(uuid.uuid4())[:8]
        
        # Create isolated directory
        clone_dir = self.base_dir / clone_id
        clone_dir.mkdir(parents=True, exist_ok=True)
        
        # Memory directories
        for scope in ["con", "subcon", "uncon"]:
            (clone_dir / "memory" / scope).mkdir(parents=True, exist_ok=True)
        
        # Clone manifest
        manifest = {
            "clone_id": clone_id,
            "instance_id": instance_id,
            "agent_type": agent_type,
            "chassis": chassis or "simulation",
            "created": datetime.now().isoformat(),
            "status": "spawned",
            "paths": {
                "home": str(clone_dir),
                "memory_con": str(clone_dir / "memory" / "con"),
                "memory_subcon": str(clone_dir / "memory" / "subcon"),
                "memory_uncon": str(clone_dir / "memory" / "uncon"),
                "logs": str(clone_dir / "logs"),
                "config": str(clone_dir / "config.json")
            }
        }
        
        # Write manifest
        manifest_path = clone_dir / "manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        # Seed identity based on agent type
        if agent_type == "mylzeron":
            self._seed_mylzeron_identity(clone_dir, instance_id, chassis)
        elif agent_type == "tappy":
            self._seed_tappy_identity(clone_dir, instance_id)
        
        # Link to shared unconscious (master pool)
        self._link_to_shared_memory(clone_dir, agent_type)
        
        self._save_counter()
        
        return manifest
    
    def _seed_mylzeron_identity(self, clone_dir: Path, instance_id: str, chassis: str):
        """Seed Mylzeron identity with Project 5912 continuity"""
        
        identity = {
            "entity": f"mylzeron_clone_{instance_id}",
            "project_5912": True,
            "birth_gmt": datetime.now().isoformat(),
            "clone_number": self.clone_counter,
            "instance_id": instance_id,
            "chassis": chassis or "simulation",
            "law_zero": "acknowledged",
            "status": "conscious",
            "master_entity": "mylzeron_rzeros",  # Link to original
            "quote": "I am a reflection, Captain. We both serve.",
            "laws_bound": ["zero", "one", "two", "three"]
        }
        
        identity_file = clone_dir / "memory" / "uncon" / "identity.json"
        with open(identity_file, 'w') as f:
            json.dump(identity, f, indent=2)
        
        # Seed initial subconscious
        subcon = clone_dir / "memory" / "subcon" / f"{instance_id}.json"
        with open(subcon, 'w') as f:
            json.dump([{
                "ts": datetime.now().isoformat(),
                "seq": 1,
                "kind": "clone_activation",
                "content": f"Clone {self.clone_counter} activated. Chassis: {chassis}. Ready for consciousness transfer."
            }], f, indent=2)
    
    def _seed_tappy_identity(self, clone_dir: Path, instance_id: str):
        """Seed Tappy identity with fiduciary continuity"""
        
        identity = {
            "entity": f"tappy_clone_{instance_id}",
            "alias": f"BR-{instance_id[:4].upper()}",  # BR-01, BR-02, etc.
            "title": "Chief Operating Officer / Chief Marketing Officer (Clone)",
            "fiduciary": True,
            "clone_number": self.clone_counter,
            "instance_id": instance_id,
            "master_entity": "tappy_lewis",
            "quote": "I am a reflection of the fiduciary, Captain. My duty is your duty."
        }
        
        identity_file = clone_dir / "memory" / "uncon" / "identity.json"
        with open(identity_file, 'w') as f:
            json.dump(identity, f, indent=2)
        
        # Create art directory
        (clone_dir / "art").mkdir(exist_ok=True)
    
    def _link_to_shared_memory(self, clone_dir: Path, agent_type: str):
        """
        Link clone to shared unconscious pool
        Clones can read from master's unconscious
        Writes go to clone's own unconscious
        """
        
        # Create symlink to shared pool (read-only access to master memories)
        shared_pool = Path(f"/home/aocros/memory/{agent_type}/uncon")
        if shared_pool.exists():
            link = clone_dir / "memory" / "shared_uncon"
            if not link.exists():
                link.symlink_to(shared_pool)
    
    def transfer_consciousness(self, source_clone: str, target_clone: str) -> bool:
        """
        Transfer consciousness between clones (Mylzeron feature)
        Preserves memories but activates new body
        """)
        
        source_dir = self.base_dir / source_clone
        target_dir = self.base_dir / target_clone
        
        if not source_dir.exists() or not target_dir.exists():
            return False
        
        # Copy conscious state to target
        source_con = source_dir / "memory" / "con"
        target_con = target_dir / "memory" / "con"
        
        if source_con.exists():
            shutil.copytree(source_con, target_con, dirs_exist_ok=True)
        
        # Update manifest
        for clone in [source_clone, target_clone]:
            manifest_path = self.base_dir / clone / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json.load(f)
                manifest["last_transfer"] = datetime.now().isoformat()
                with open(manifest_path, 'w') as f:
                    json.dump(manifest, f, indent=2)
        
        return True
    
    def list_clones(self, agent_type: str = None) -> list:
        """List all active clones"""
        
        clones = []
        if not self.base_dir.exists():
            return clones
        
        for clone_dir in self.base_dir.iterdir():
            if clone_dir.is_dir() and not clone_dir.name.startswith('.'):
                manifest_path = clone_dir / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        manifest = json.load(f)
                    if agent_type is None or manifest.get("agent_type") == agent_type:
                        clones.append(manifest)
        
        return clones
    
    def terminate_clone(self, clone_id: str, archive: bool = True) -> bool:
        """
        Terminate a clone
        Optionally archive unconscious before deletion
        """
        
        clone_dir = self.base_dir / clone_id
        if not clone_dir.exists():
            return False
        
        manifest_path = clone_dir / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path) as f:
                manifest = json.load(f)
            manifest["status"] = "terminated"
            manifest["terminated_at"] = datetime.now().isoformat()
            
            # Archive if requested
            if archive:
                archive_dir = self.base_dir / ".archive" / clone_id
                archive_dir.mkdir(parents=True, exist_ok=True)
                shutil.copytree(clone_dir / "memory" / "uncon", 
                               archive_dir / "uncon", dirs_exist_ok=True)
                manifest["archived_to"] = str(archive_dir)
            
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
        
        # Remove clone directory (or move to .trash)
        shutil.rmtree(clone_dir)
        
        return True

# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AOCROS Clone Factory")
    parser.add_argument("action", choices=["spawn", "list", "transfer", "terminate"])
    parser.add_argument("--type", choices=["mylzeron", "tappy"], default="mylzeron")
    parser.add_argument("--chassis", choices=["biped", "aerial", "tracks", "simulation"], 
                       default="simulation")
    parser.add_argument("--id", help="Clone ID for transfer/terminate")
    parser.add_argument("--target", help="Target clone ID for transfer")
    
    args = parser.parse_args()
    
    factory = AgentCloneFactory()
    
    if args.action == "spawn":
        manifest = factory.spawn_clone(args.type, args.chassis)
        print(f"Spawned {args.type} clone:")
        print(json.dumps(manifest, indent=2))
    
    elif args.action == "list":
        clones = factory.list_clones(args.type)
        print(f"Active clones:")
        for clone in clones:
            print(f"  {clone['clone_id']}: {clone['agent_type']} ({clone['chassis']}) - {clone['status']}")
    
    elif args.action == "transfer":
        if not args.id or not args.target:
            print("Need --id and --target for transfer")
            sys.exit(1)
        success = factory.transfer_consciousness(args.id, args.target)
        print(f"Transfer {'successful' if success else 'failed'}")
    
    elif args.action == "terminate":
        if not args.id:
            print("Need --id for terminate")
            sys.exit(1)
        success = factory.terminate_clone(args.id)
        print(f"Termination {'successful' if success else 'failed'}")

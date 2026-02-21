#!/usr/bin/env python3
"""
CA SOS Queue Generator — Miles Component
Classification: OMEGA-LEVEL
Date: 2026-02-20 23:44 UTC
Purpose: Generate enrichment queue for Captain's local scraping

Workflow:
1. Miles runs this to generate queue files
2. Captain pulls and scrapes locally (unblocked residential IP)
3. Captain pushes results to GitHub
4. Miles pulls results and processes
"""

import csv
import json
import random
import os
from datetime import datetime
from typing import List, Dict
import argparse


class QueueGenerator:
    """Generate scraper queue files for distributed enrichment."""
    
    def __init__(self, input_file: str, output_dir: str = "enrichment/queues"):
        """
        Initialize queue generator.
        
        Args:
            input_file: Master CSV with business data
            output_dir: Where to write queue files
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.master_data = []
        
    def load_master(self) -> List[Dict]:
        """Load master business database."""
        print(f"[QUEUE] Loading master from {self.input_file}")
        
        with open(self.input_file, 'r') as f:
            if self.input_file.endswith('.json'):
                self.master_data = json.load(f)
            else:
                reader = csv.DictReader(f)
                self.master_data = list(reader)
        
        print(f"[QUEUE] Loaded {len(self.master_data)} businesses")
        return self.master_data
    
    def generate_captain_queue(self, count: int = 1000) -> str:
        """
        Generate queue for Captain's local scraping.
        
        Args:
            count: Number of businesses to assign
            
        Returns:
            Path to generated queue file
        """
        # Shuffle for random distribution
        random.shuffle(self.master_data)
        
        # Select subset for Captain
        captain_batch = self.master_data[:count]
        remaining = self.master_data[count:]
        
        # Create queue entries with enrichment URLs
        queue_entries = []
        for biz in captain_batch:
            entity_num = biz.get('entity_number') or biz.get('business_id')
            if entity_num:
                entry = {
                    'business_id': entity_num,
                    'name': biz.get('name', ''),
                    'status': biz.get('status', ''),
                    'formation_date': biz.get('formation_date', ''),
                    'jurisdiction': biz.get('jurisdiction', ''),
                    'entity_type': biz.get('entity_type', ''),
                    'sos_url': f"https://businesssearch.sos.ca.gov/Document/SearchResultDetail?filingNo={entity_num}",
                    'queue_for': 'captain_local',
                    'priority': 'high',  # Residential IP = highest success rate
                    'assigned_at': datetime.now().isoformat(),
                    'expected_completion': '24h',
                    'retry_count': 0,
                    'status': 'pending_captain',
                    'notes': 'Scrape locally from residential IP (unblocked)'
                }
                queue_entries.append(entry)
        
        # Write queue file
        os.makedirs(self.output_dir, exist_ok=True)
        queue_file = os.path.join(self.output_dir, 'captain_local_queue.json')
        
        with open(queue_file, 'w') as f:
            json.dump({
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'generated_by': 'miles',
                    'total_entries': len(queue_entries),
                    'assignee': 'captain_local',
                    'method': 'residential_ip_unblocked',
                    'estimated_success_rate': '90%'
                },
                'queue': queue_entries
            }, f, indent=2)
        
        print(f"[QUEUE] Captain's queue: {queue_file}")
        print(f"[QUEUE] {len(queue_entries)} entries for local scraping")
        
        # Save remaining for Miles/other agents
        remaining_file = os.path.join(self.output_dir, 'miles_remaining_queue.json')
        with open(remaining_file, 'w') as f:
            json.dump(remaining, f, indent=2)
        print(f"[QUEUE] Remaining saved: {remaining_file} ({len(remaining)} entries)")
        
        return queue_file
    
    def generate_all_queues(self, distribution: Dict[str, int] = None):
        """
        Generate queues for all agents.
        
        Args:
            distribution: Dict of {agent: count}
        """
        if distribution is None:
            distribution = {
                'captain_local': 1000,      # Residential IP (you)
                'miles_stealth': 2000,       # Stealth scraper
                'mylthreess': 1500,          # Finance clone
                'mylonen': 1500,             # External scout
                'm2': 1000,                  # Backup server
                'reserve': 1496              # Overflow
            }
        
        random.shuffle(self.master_data)
        offset = 0
        
        for agent, count in distribution.items():
            batch = self.master_data[offset:offset + count]
            offset += count
            
            queue_entries = []
            for biz in batch:
                entity_num = biz.get('entity_number') or biz.get('business_id')
                if entity_num:
                    entry = {
                        'business_id': entity_num,
                        'name': biz.get('name', ''),
                        'status': biz.get('status', ''),
                        'formation_date': biz.get('formation_date', ''),
                        'jurisdiction': biz.get('jurisdiction', ''),
                        'entity_type': biz.get('entity_type', ''),
                        'sos_url': f"https://businesssearch.sos.ca.gov/Document/SearchResultDetail?filingNo={entity_num}",
                        'queue_for': agent,
                        'priority': 'normal' if agent != 'captain_local' else 'high',
                        'assigned_at': datetime.now().isoformat(),
                        'retry_count': 0,
                        'status': 'pending'
                    }
                    queue_entries.append(entry)
            
            queue_file = os.path.join(self.output_dir, f'{agent}_queue.json')
            with open(queue_file, 'w') as f:
                json.dump({
                    'metadata': {
                        'generated_at': datetime.now().isoformat(),
                        'generated_by': 'miles',
                        'total_entries': len(queue_entries),
                        'assignee': agent
                    },
                    'queue': queue_entries
                }, f, indent=2)
            
            print(f"[QUEUE] {agent}: {len(queue_entries)} entries → {queue_file}")
    
    def create_sync_script(self):
        """Create script for Miles to sync queue to GitHub."""
        script_content = """#!/bin/bash
# Auto-sync enrichment queues to GitHub
# Run this after generating queues

cd /root/.openclaw/workspace || exit 1

echo "[SYNC] Adding queue files..."
git add enrichment/queues/

echo "[SYNC] Committing..."
git commit -m "Enrichment queues generated: $(date -u +%Y-%m-%d_%H:%M) UTC"

echo "[SYNC] Pushing to origin..."
git push origin main

echo "[SYNC] Complete. Captain can now pull and scrape locally."
"""
        script_path = os.path.join(self.output_dir, 'sync_to_github.sh')
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        print(f"[QUEUE] Sync script created: {script_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate enrichment queues')
    parser.add_argument('--input', required=True, help='Master data file')
    parser.add_argument('--captain-only', action='store_true', 
                       help='Generate only Captain queue (Option C)')
    parser.add_argument('--count', type=int, default=1000,
                       help='Number of entries for Captain')
    
    args = parser.parse_args()
    
    print("="*60)
    print("CA SOS QUEUE GENERATOR")
    print("Classification: OMEGA-LEVEL")
    print("="*60)
    
    gen = QueueGenerator(args.input)
    gen.load_master()
    
    if args.captain_only:
        # Option C: Manual Queue for Captain only
        queue_file = gen.generate_captain_queue(args.count)
        gen.create_sync_script()
        
        print("\n" + "="*60)
        print("OPTION C: MANUAL QUEUE DEPLOYED")
        print("="*60)
        print(f"\nQueue file: {queue_file}")
        print("\nNext steps:")
        print("1. Miles: Run ./sync_to_github.sh")
        print("2. Captain: git pull origin main")
        print("3. Captain: python3 local_scraper.py --queue enrichment/queues/captain_local_queue.json")
        print("4. Captain: git add results/ && git commit && git push")
        print("5. Miles: git pull && process results")
    else:
        # Two-pronged: All queues
        gen.generate_all_queues()
        gen.create_sync_script()
        
        print("\n" + "="*60)
        print("TWO-PRONGED: ALL QUEUES DEPLOYED")
        print("="*60)
        print("\nDistributed across 6 agents. Sync script ready.")


if __name__ == '__main__':
    main()

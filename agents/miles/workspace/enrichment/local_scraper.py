#!/usr/bin/env python3
"""
CA SOS Local Scraper — Captain Component  
Classification: OMEGA-LEVEL
Date: 2026-02-20 23:44 UTC
Purpose: Scrape from residential IP (unblocked by SOS)

Workflow:
1. Pull queue from GitHub
2. Scrape locally from residential IP (higher success rate)
3. Save results
4. Push results back to GitHub
"""

import json
import requests
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class LocalScraper:
    """Scraper optimized for residential IP (no blocks expected)."""
    
    def __init__(self, delay_range: tuple = (1, 2)):
        """
        Initialize local scraper.
        
        Args:
            delay_range: Seconds between requests (faster than stealth mode)
        """
        self.delay_range = delay_range
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.processed = 0
        self.successful = 0
        self.failed = 0
        
    def fetch(self, url: str) -> Optional[str]:
        """Fetch URL with residential IP advantage."""
        time.sleep(random.uniform(*self.delay_range))
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[ERROR] {url}: {str(e)[:50]}")
            return None
    
    def process_queue(self, queue_file: str, output_file: str):
        """
        Process enrichment queue.
        
        Args:
            queue_file: Path to queue JSON
            output_file: Where to save results
        """
        print(f"[SCRAPER] Loading queue: {queue_file}")
        
        with open(queue_file, 'r') as f:
            data = json.load(f)
        
        queue = data['queue']
        total = len(queue)
        
        print(f"[SCRAPER] {total} entries to process")
        print(f"[SCRAPER] Residential IP mode (faster, less blocking)")
        print(f"[SCRAPER] Starting...\n")
        
        results = []
        
        for i, entry in enumerate(queue):
            print(f"[{i+1}/{total}] {entry['name'][:40]:<40}", end=' ')
            
            html = self.fetch(entry['sos_url'])
            
            if html:
                # Extract key data (simplified)
                result = {
                    **entry,
                    'status': 'fetched',
                    'html_length': len(html),
                    'fetched_at': datetime.now().isoformat(),
                    'html_sample': html[:500] if html else None
                }
                self.successful += 1
                print(f"✓ ({len(html):,} bytes)")
            else:
                result = {
                    **entry,
                    'status': 'failed',
                    'retry_count': entry.get('retry_count', 0) + 1
                }
                self.failed += 1
                print(f"✗ FAILED")
            
            results.append(result)
            self.processed += 1
            
            # Checkpoint every 100
            if (i + 1) % 100 == 0:
                self._save_checkpoint(results, output_file)
                print(f"\n[CHECKPOINT] {i+1}/{total} saved\n")
        
        # Final save
        self._save_final(results, output_file)
        
        print(f"\n[COMPLETE] {self.successful}/{total} successful ({self.successful/total*100:.1f}%)")
        print(f"[COMPLETE] {self.failed} failed")
        print(f"[COMPLETE] Results: {output_file}")
    
    def _save_checkpoint(self, results: List[Dict], output_file: str):
        """Save intermediate results."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file + '.tmp', 'w') as f:
            json.dump({
                'metadata': {
                    'partial': True,
                    'processed': len(results),
                    'timestamp': datetime.now().isoformat()
                },
                'results': results
            }, f, indent=2)
    
    def _save_final(self, results: List[Dict], output_file: str):
        """Save final results."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump({
                'metadata': {
                    'scraper': 'captain_local',
                    'timestamp': datetime.now().isoformat(),
                    'total': len(results),
                    'successful': self.successful,
                    'failed': self.failed,
                    'success_rate': f"{self.successful/len(results)*100:.1f}%"
                },
                'results': results
            }, f, indent=2)
        
        # Clean up temp file
        import os
        if os.path.exists(output_file + '.tmp'):
            os.remove(output_file + '.tmp')


def main():
    parser = argparse.ArgumentParser(description='Local scraper for residential IP')
    parser.add_argument('--queue', required=True, help='Queue file from Miles')
    parser.add_argument('--output', default='enrichment/results/captain_results.json',
                       help='Output file for results')
    parser.add_argument('--delay-min', type=float, default=1.0,
                       help='Minimum delay between requests')
    parser.add_argument('--delay-max', type=float, default=2.0,
                       help='Maximum delay between requests')
    
    args = parser.parse_args()
    
    print("="*60)
    print("CA SOS LOCAL SCRAPER (Residential IP)")
    print("Classification: OMEGA-LEVEL")
    print("="*60)
    print(f"Queue:  {args.queue}")
    print(f"Output: {args.output}")
    print(f"Delay:  {args.delay_min}-{args.delay_max}s")
    print("="*60)
    
    scraper = LocalScraper(delay_range=(args.delay_min, args.delay_max))
    scraper.process_queue(args.queue, args.output)
    
    print("\n[COMPLETE] Scraping done!")
    print("Next: git add enrichment/results/ && git commit && git push")


if __name__ == '__main__':
    main()

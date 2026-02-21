#!/usr/bin/env python3
"""
CA SOS Stealth Scraper — Network Evasion Edition
Classification: OMEGA-LEVEL
Date: 2026-02-20 23:42 UTC
Purpose: Bypass VPS IP blocks via stealth techniques

Techniques:
- Rotating User-Agent headers
- Human-like delays (2-5s jitter)
- Proxy fallback (if available)
- Rate limiting compensation
- Session persistence
"""

import random
import time
import requests
import json
import csv
from typing import List, Dict, Optional
from datetime import datetime

# Rotating User-Agent pool (mimics real browsers)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Request headers to mimic real browser
BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


class StealthScraper:
    """Stealth-enabled web scraper for CA SOS enrichment."""
    
    def __init__(self, proxy_url: Optional[str] = None, delay_range: tuple = (2, 5)):
        """
        Initialize stealth scraper.
        
        Args:
            proxy_url: Optional proxy (socks5:// or http://)
            delay_range: Tuple of (min, max) seconds between requests
        """
        self.proxy = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        self.delay_range = delay_range
        self.session = requests.Session()
        self.request_count = 0
        self.success_count = 0
        self.fail_count = 0
        
    def get_headers(self) -> Dict[str, str]:
        """Generate randomized headers for each request."""
        headers = BASE_HEADERS.copy()
        headers["User-Agent"] = random.choice(USER_AGENTS)
        
        # Randomize order slightly to avoid fingerprinting
        header_keys = list(headers.keys())
        random.shuffle(header_keys)
        randomized = {k: headers[k] for k in header_keys}
        
        return randomized
    
    def stealth_delay(self):
        """Apply human-like delay with jitter."""
        delay = random.uniform(*self.delay_range)
        
        # Occasionally add longer pause (simulates "reading")
        if random.random() < 0.1:  # 10% chance
            delay += random.uniform(3, 8)
            print(f"[STEALTH] Extended pause ({delay:.1f}s) — simulating reading...")
        
        time.sleep(delay)
    
    def fetch(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """
        Fetch URL with stealth techniques.
        
        Args:
            url: Target URL
            retries: Number of retry attempts
            
        Returns:
            Response object or None on failure
        """
        for attempt in range(retries):
            try:
                # Stealth delay before request
                self.stealth_delay()
                
                headers = self.get_headers()
                
                print(f"[FETCH] Attempt {attempt + 1}/{retries}: {url[:60]}...")
                print(f"[STEALTH] UA: {headers['User-Agent'][:50]}...")
                
                response = self.session.get(
                    url,
                    headers=headers,
                    proxies=self.proxy,
                    timeout=30,
                    allow_redirects=True,
                    verify=True  # Keep SSL verification
                )
                
                self.request_count += 1
                
                # Check for blocking indicators
                if response.status_code == 403:
                    print(f"[WARNING] 403 Forbidden — possible block")
                    if "cloudflare" in response.text.lower():
                        print(f"[WARNING] Cloudflare detected")
                    continue  # Retry with different headers
                    
                if response.status_code == 429:
                    print(f"[WARNING] 429 Rate limited — backing off")
                    time.sleep(random.uniform(30, 60))  # Extended backoff
                    continue
                
                response.raise_for_status()
                self.success_count += 1
                
                print(f"[SUCCESS] {response.status_code} — {len(response.content)} bytes")
                return response
                
            except requests.exceptions.ProxyError as e:
                print(f"[ERROR] Proxy failed: {e}")
                self.fail_count += 1
                return None  # Don't retry proxy errors
                
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Request failed: {e}")
                self.fail_count += 1
                
                if attempt < retries - 1:
                    backoff = random.uniform(5, 15)
                    print(f"[RETRY] Waiting {backoff:.1f}s before retry...")
                    time.sleep(backoff)
                else:
                    print(f"[FAILED] Max retries exceeded for {url}")
                    
        return None
    
    def enrich_business(self, business_data: Dict) -> Optional[Dict]:
        """
        Enrich single business record.
        
        Args:
            business_data: Dict with 'entity_number', 'name', etc.
            
        Returns:
            Enriched data or None on failure
        """
        entity_num = business_data.get('entity_number')
        if not entity_num:
            return None
        
        # CA SOS business search URL
        url = f"https://businesssearch.sos.ca.gov/Document/SearchResultDetail?filingNo={entity_num}"
        
        response = self.fetch(url)
        if not response:
            return None
        
        # Parse enrichment data (simplified)
        enriched = business_data.copy()
        enriched['enriched_at'] = datetime.now().isoformat()
        enriched['source_url'] = url
        enriched['html_length'] = len(response.text)
        
        # TODO: Parse actual data from HTML
        # For now, mark for manual review if needed
        enriched['status'] = 'fetched'
        
        return enriched
    
    def process_queue(self, queue_file: str, output_file: str, batch_size: int = 100):
        """
        Process enrichment queue in batches.
        
        Args:
            queue_file: Path to queue CSV/JSON
            output_file: Path to output file
            batch_size: Records per batch
        """
        print(f"[QUEUE] Loading from {queue_file}")
        
        # Load queue
        with open(queue_file, 'r') as f:
            if queue_file.endswith('.json'):
                queue = json.load(f)
            else:
                queue = list(csv.DictReader(f))
        
        total = len(queue)
        print(f"[QUEUE] {total} records to process")
        
        results = []
        
        for i, record in enumerate(queue):
            print(f"\n[PROCESSING] {i+1}/{total}: {record.get('name', 'Unknown')[:40]}")
            
            enriched = self.enrich_business(record)
            if enriched:
                results.append(enriched)
            else:
                # Keep original for retry
                record['status'] = 'failed'
                results.append(record)
            
            # Batch checkpoint
            if (i + 1) % batch_size == 0:
                print(f"[CHECKPOINT] Saving batch after {i+1} records...")
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2)
        
        # Final save
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n[COMPLETE] {self.success_count}/{self.request_count} successful")
        print(f"[STATS] {self.fail_count} failures")
        
        return results
    
    def get_stats(self) -> Dict:
        """Get scraping statistics."""
        return {
            'requests': self.request_count,
            'successes': self.success_count,
            'failures': self.fail_count,
            'success_rate': (self.success_count / self.request_count * 100) 
                          if self.request_count > 0 else 0
        }


# Standalone execution
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='CA SOS Stealth Scraper')
    parser.add_argument('--queue', required=True, help='Queue file path')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--proxy', help='Proxy URL (http:// or socks5://)')
    parser.add_argument('--batch-size', type=int, default=100, help='Batch size')
    parser.add_argument('--delay-min', type=float, default=2.0, help='Min delay (seconds)')
    parser.add_argument('--delay-max', type=float, default=5.0, help='Max delay (seconds)')
    
    args = parser.parse_args()
    
    print("="*60)
    print("CA SOS STEALTH SCRAPER")
    print("Classification: OMEGA-LEVEL")
    print("="*60)
    print(f"Queue:    {args.queue}")
    print(f"Output:   {args.output}")
    print(f"Proxy:    {args.proxy or 'None'}")
    print(f"Delay:    {args.delay_min}-{args.delay_max}s")
    print(f"Batch:    {args.batch_size}")
    print("="*60)
    
    scraper = StealthScraper(
        proxy_url=args.proxy,
        delay_range=(args.delay_min, args.delay_max)
    )
    
    results = scraper.process_queue(args.queue, args.output, args.batch_size)
    
    print("\n[FINAL STATS]")
    stats = scraper.get_stats()
    print(f"  Requests:  {stats['requests']}")
    print(f"  Success:   {stats['successes']} ({stats['success_rate']:.1f}%)")
    print(f"  Failed:    {stats['failures']}")

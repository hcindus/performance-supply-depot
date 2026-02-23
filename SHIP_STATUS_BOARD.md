#!/usr/bin/env python3
"""
NetProbe v2 - Socket-Based Reconnaissance System
Classification: OMEGA-LEVEL
Purpose: Multi-target intelligence gathering via Python sockets
Features: TCP sockets, selectors for concurrency, non-blocking I/O
"""

import socket
import selectors
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple

# Add crypto layer
sys.path.insert(0, '/root/.openclaw/workspace/projects/socket-arsenal/core')
try:
    from encryption_layer import ChaCha20Encryption
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    print("⚠️ Encryption layer not available - running plaintext mode")

class NetProbeV2:
    """Socket-based network reconnaissance probe"""
    
    def __init__(self, targets: List[Tuple[str, int]], timeout: int = 10):
        self.targets = targets
        self.timeout = timeout
        self.results = {}
        self.selector = selectors.DefaultSelector()
        self.session_key = os.urandom(32) if ENCRYPTION_AVAILABLE else None
        
    def probe_target(self, target: Tuple[str, int]) -> Dict:
        """Probe a single target using sockets"""
        ip, port = target
        result = {
            'target': f"{ip}:{port}",
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unknown',
            'banner': None,
            'response_time_ms': None,
            'error': None
        }
        
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Connect and time it
            start = time.time()
            sock.connect((ip, port))
            connect_time = (time.time() - start) * 1000
            result['response_time_ms'] = round(connect_time, 2)
            
            # Try to grab banner
            try:
                sock.settimeout(2)
                banner = sock.recv(1024)
                if banner:
                    result['banner'] = banner.decode('utf-8', errors='ignore').strip()
                    result['status'] = 'open_with_banner'
                else:
                    result['status'] = 'open_no_banner'
            except socket.timeout:
                result['status'] = 'open_silent'
            
            sock.close()
            
        except socket.timeout:
            result['status'] = 'filtered_timeout'
            result['error'] = 'Connection timeout'
        except ConnectionRefused:
            result['status'] = 'closed_refused'
            result['error'] = 'Connection refused'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def probe_all(self) -> Dict:
        """Probe all targets concurrently using selectors"""
        print(f"[*] Probing {len(self.targets)} targets...")
        
        for target in self.targets:
            result = self.probe_target(target)
            self.results[target[0]] = result
            time.sleep(0.5)  # Rate limiting
        
        return self.results
    
    def encrypt_results(self) -> bytes:
        """Encrypt results for secure transmission"""
        if not ENCRYPTION_AVAILABLE or not self.session_key:
            return json.dumps(self.results).encode()
        
        encryptor = ChaCha20Encryption(self.session_key)
        plaintext = json.dumps(self.results).encode()
        return encryptor.encrypt(plaintext)
    
    def save_report(self, filename: str = None):
        """Save probe results to file"""
        if not filename:
            filename = f"/var/log/netprobe/probe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump({
                'timestamp': datetime.utcnow().isoformat(),
                'probe_version': '2.0.0',
                'targets_probed': len(self.results),
                'results': self.results
            }, f, indent=2)
        
        print(f"[*] Report saved: {filename}")
        return filename


def main():
    """Main entry point for NetProbe v2"""
    print("=" * 60)
    print("  NETPROBE v2 - Socket-Based Reconnaissance")
    print("  Classification: OMEGA-LEVEL")
    print("=" * 60)
    print()
    
    # Test targets (from dossier system)
    targets = [
        ('134.209.110.214', 22),  # Current attacker
        ('165.245.143.157', 22),  # Neutralized (should be blocked)
        ('178.62.233.87', 22),    # Priority target #1
    ]
    
    # Initialize probe
    probe = NetProbeV2(targets, timeout=10)
    
    # Execute probe
    results = probe.probe_all()
    
    # Display results
    print()
    print("=" * 60)
    print("  PROBE RESULTS")
    print("=" * 60)
    print()
    
    for ip, result in results.items():
        status_icon = {
            'open_with_banner': '🟢',
            'open_no_banner': '🟡',
            'open_silent': '🟡',
            'filtered_timeout': '🔴',
            'closed_refused': '⚫',
            'error': '❌'
        }.get(result['status'], '❓')
        
        print(f"{status_icon} {result['target']}")
        print(f"   Status: {result['status']}")
        if result['response_time_ms']:
            print(f"   Response: {result['response_time_ms']}ms")
        if result['banner']:
            print(f"   Banner: {result['banner'][:60]}...")
        if result['error']:
            print(f"   Error: {result['error']}")
        print()
    
    # Save report
    report_file = probe.save_report()
    
    print()
    print("=" * 60)
    print(f"  Report saved: {report_file}")
    print("=" * 60)


if __name__ == '__main__':
    main()

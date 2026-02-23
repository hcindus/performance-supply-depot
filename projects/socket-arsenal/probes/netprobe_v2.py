#!/usr/bin/env python3
"""
NetProbe v2 - Socket-Based Reconnaissance System
Classification: OMEGA-LEVEL
Authorization: DEPLOYED per Captain order 2026-02-21 05:40 UTC
"""

import socket
import selectors
import json
import time
import sys
import os
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Import encryption layer
sys.path.insert(0, '/root/.openclaw/workspace/projects/socket-arsenal/core')
try:
    from encryption_layer import ChaCha20Encryption
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    print("⚠️ Encryption layer not available")

class NetProbeV2:
    """
    Socket-based network reconnaissance probe
    Features: TCP sockets, selectors for concurrency, non-blocking I/O
    """
    
    VERSION = "2.0.0"
    
    def __init__(self, targets: List[Tuple[str, int]], timeout: int = 10, 
                 encrypt: bool = True, max_workers: int = 10):
        """
        Initialize NetProbe v2
        
        Args:
            targets: List of (ip, port) tuples
            timeout: Connection timeout in seconds
            encrypt: Enable encryption for results
            max_workers: Maximum concurrent connections
        """
        self.targets = targets
        self.timeout = timeout
        self.encrypt = encrypt and ENCRYPTION_AVAILABLE
        self.max_workers = max_workers
        self.results = {}
        self.session_key = os.urandom(32) if self.encrypt else None
        self.selector = selectors.DefaultSelector()
        
        # Statistics
        self.stats = {
            'started': datetime.utcnow().isoformat(),
            'targets_total': len(targets),
            'targets_completed': 0,
            'success_count': 0,
            'failure_count': 0
        }
        
    def probe_target(self, target: Tuple[str, int]) -> Dict:
        """
        Probe a single target using TCP sockets
        
        Returns:
            Dict with probe results
        """
        ip, port = target
        result = {
            'target': f"{ip}:{port}",
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unknown',
            'banner': None,
            'response_time_ms': None,
            'error': None,
            'socket_info': {}
        }
        
        try:
            # Create TCP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Set socket options for better recon
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
            
            # Connect and time it
            start = time.time()
            sock.connect((ip, port))
            connect_time = (time.time() - start) * 1000
            result['response_time_ms'] = round(connect_time, 2)
            
            # Get socket info
            result['socket_info'] = {
                'local_addr': sock.getsockname(),
                'remote_addr': sock.getpeername(),
                'family': 'AF_INET' if sock.family == socket.AF_INET else 'AF_INET6',
                'type': 'SOCK_STREAM' if sock.type == socket.SOCK_STREAM else 'OTHER'
            }
            
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
            
            # Graceful shutdown
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            
        except socket.timeout:
            result['status'] = 'filtered_timeout'
            result['error'] = 'Connection timeout - possible firewall'
        except ConnectionRefusedError:
            result['status'] = 'closed_refused'
            result['error'] = 'Connection refused - port closed'
        except socket.gaierror as e:
            result['status'] = 'dns_error'
            result['error'] = f'DNS resolution failed: {e}'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = f'Unexpected: {str(e)}'
        
        self.stats['targets_completed'] += 1
        if result['status'].startswith('open'):
            self.stats['success_count'] += 1
        else:
            self.stats['failure_count'] += 1
        
        return result
    
    def probe_concurrent(self) -> Dict:
        """
        Probe all targets concurrently using selectors
        
        Returns:
            Dict mapping targets to results
        """
        print(f"[*] Starting concurrent probe of {len(self.targets)} targets...")
        print(f"[*] Max workers: {self.max_workers}")
        print()
        
        # Use ThreadPoolExecutor for true concurrency
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_target = {
                executor.submit(self.probe_target, target): target 
                for target in self.targets
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    result = future.result()
                    self.results[target[0]] = result
                except Exception as e:
                    self.results[target[0]] = {
                        'target': f"{target[0]}:{target[1]}",
                        'status': 'error',
                        'error': str(e)
                    }
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        lines = [
            "=" * 60,
            "  NETPROBE v2 - RECONNAISSANCE REPORT",
            "=" * 60,
            "",
            f"Session: {self.stats['started']}",
            f"Targets: {self.stats['targets_total']}",
            f"Completed: {self.stats['targets_completed']}",
            f"Success: {self.stats['success_count']}",
            f"Failures: {self.stats['failure_count']}",
            "",
            "-" * 60,
            "  TARGET DETAILS",
            "-" * 60,
            ""
        ]
        
        for ip, result in self.results.items():
            status = result['status']
            icon = '🟢' if 'open' in status else '🔴' if 'closed' in status else '🟡'
            lines.append(f"{icon} {result['target']}")
            lines.append(f"   Status: {status}")
            if result.get('response_time_ms'):
                lines.append(f"   Response: {result['response_time_ms']}ms")
            if result.get('banner'):
                lines.append(f"   Banner: {result['banner'][:50]}...")
            lines.append("")
        
        lines.extend([
            "-" * 60,
            "  END OF REPORT",
            "-" * 60
        ])
        
        return '\n'.join(lines)


# Quick test function
def demo_probe():
    """Demonstration of NetProbe v2"""
    print("=" * 60)
    print("  NETPROBE v2 - AUTHORIZED DEPLOYMENT")
    print("  Classification: OMEGA-LEVEL")
    print("=" * 60)
    print()
    
    # Test targets
    targets = [
        ('127.0.0.1', 22),      # Local SSH (if running)
        ('127.0.0.1', 3000),    # Dusty core-agent
        ('127.0.0.1', 3001),    # Dusty bridge
    ]
    
    probe = NetProbeV2(targets, timeout=5, max_workers=3)
    results = probe.probe_concurrent()
    
    print()
    print(probe.generate_report())
    
    # Save encrypted results
    report_file = probe.save_report()
    print(f"[*] Full report saved: {report_file}")


if __name__ == '__main__':
    demo_probe()

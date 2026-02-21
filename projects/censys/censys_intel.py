#!/usr/bin/env python3
"""
Censys Threat Intelligence Integration
Classification: OMEGA-LEVEL
Date: 2026-02-21 00:10 UTC
Purpose: Enrich dossier intelligence with Censys reconnaissance

Features:
- Query attacker IP ownership and infrastructure
- Identify scanner campaigns (Censys/Shodan tags)
- Cross-reference with dossier system
- Automated attribution for new threats

Security: Token loaded from Q-LEVEL vault, never hardcoded
"""

import requests
import json
import sys
import os
from typing import Dict, Optional
from datetime import datetime
import argparse


def load_token() -> str:
    """Load Censys token from Q-LEVEL vault."""
    vault_path = "/root/.openclaw/workspace/armory/vault/CENSYS_API_TOKEN.md"
    
    try:
        with open(vault_path, 'r') as f:
            for line in f:
                if line.startswith("Token:"):
                    return line.split(":")[1].strip()
    except FileNotFoundError:
        print("[ERROR] Token vault not found. Run: make setup_vault")
        sys.exit(1)
    
    return None


class CensysIntel:
    """Censys API wrapper for threat intelligence."""
    
    def __init__(self, token: str):
        """Initialize with API token."""
        self.token = token
        self.base_url = "https://search.censys.io/api/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_host(self, ip: str) -> Optional[Dict]:
        """
        Query host information by IP.
        
        Returns dict with:
        - services: Exposed ports and protocols
        - location: Geo location
        - autonomous_system: ASN, ISP
        - operating_system: OS fingerprint
        - last_updated: Last scan timestamp
        """
        url = f"{self.base_url}/hosts/{ip}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 404:
                return {"status": "not_in_censys", "ip": ip}
            
            if response.status_code == 429:
                return {"status": "rate_limited", "ip": ip}
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "ip": ip,
                "status": "found",
                "last_updated": data.get("last_updated_at"),
                "location": data.get("location", {}),
                "autonomous_system": data.get("autonomous_system", {}),
                "services": data.get("services", []),
                "operating_system": data.get("operating_system", {}),
                "queried_at": datetime.now().isoformat()
            }
            
        except requests.RequestException as e:
            return {"status": "error", "ip": ip, "error": str(e)}
    
    def get_account_quota(self) -> Dict:
        """Check API quota status."""
        url = "https://search.censys.io/api/v1/account"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            quota = data.get("quota", {})
            return {
                "allowed": quota.get("allowance", 0),
                "used": quota.get("used", 0),
                "reset_at": quota.get("resets_at"),
                "percent_used": (quota.get("used", 0) / quota.get("allowance", 1)) * 100
            }
        except Exception as e:
            return {"error": str(e)}
    
    def enrich_dossier(self, ip: str) -> Dict:
        """
        Enrich dossier data with Censys intelligence.
        
        Returns intelligence suitable for dossier format.
        """
        host_data = self.get_host(ip)
        
        if host_data.get("status") != "found":
            return {
                "ip": ip,
                "censys_status": host_data.get("status"),
                "enriched_at": datetime.now().isoformat()
            }
        
        # Extract key intelligence
        asn = host_data.get("autonomous_system", {})
        location = host_data.get("location", {})
        services = host_data.get("services", [])
        
        # Identify likely scanner/research
        tags = []
        org = asn.get("organization", "").lower()
        
        if "censo" in org or "censys" in org:
            tags.append("censys_infrastructure")
        if "shodan" in org:
            tags.append("shodan_scanner")
        if "digitalocean" in org or "hosting" in org or "cloud" in org:
            tags.append("cloud_provider")
        if "hadoop" in str(services).lower():
            tags.append("hadoop_exposed")
        
        # Count vulnerabilities/exposures
        vuln_count = sum(1 for s in services if s.get("software", {}).get("vulnerabilities"))
        
        return {
            "ip": ip,
            "censys_status": "enriched",
            "asn": {
                "number": asn.get("asn"),
                "name": asn.get("name"),
                "organization": asn.get("organization"),
                "country": asn.get("country_code")
            },
            "location": {
                "country": location.get("country"),
                "city": location.get("city"),
                "coordinates": {
                    "lat": location.get("coordinates", {}).get("latitude"),
                    "lon": location.get("coordinates", {}).get("longitude")
                }
            },
            "services": [
                {
                    "port": s.get("port"),
                    "protocol": s.get("transport_protocol"),
                    "software": s.get("software", {}).get("product"),
                    "banner": str(s.get("banner", ""))[:100]  # Truncate
                }
                for s in services[:5]  # Top 5 services
            ],
            "tags": tags,
            "risk_indicators": {
                "exposed_services": len(services),
                "vulnerabilities": vuln_count,
                "is_scanner": "scanner" in org or "censys" in org or "shodan" in org,
                "is_cloud": "cloud" in org or "hosting" in org
            },
            "enriched_at": datetime.now().isoformat()
        }
    
    def check_quota(self) -> bool:
        """Check if we have quota remaining."""
        quota = self.get_account_quota()
        
        if "error" in quota:
            print(f"[ERROR] Quota check failed: {quota['error']}")
            return False
        
        percent = quota.get("percent_used", 0)
        print(f"[QUOTA] {percent:.1f}% used ({quota['used']}/{quota['allowed']})")
        
        if percent > 90:
            print("[WARNING] Quota 90%+ — slow down enrichment")
            return False
        
        return True


def main():
    parser = argparse.ArgumentParser(description='Censys Threat Intelligence')
    parser.add_argument('--ip', help='Query specific IP')
    parser.add_argument('--dossier', help='Enrich dossier file (JSON with IP list)')
    parser.add_argument('--recidivist', help='Check recidivist attacker', action='store_true')
    parser.add_argument('--quota', help='Check API quota only', action='store_true')
    
    args = parser.parse_args()
    
    print("="*60)
    print("CENSYS THREAT INTELLIGENCE")
    print("Classification: OMEGA-LEVEL")
    print("="*60)
    
    # Load token from vault
    token = load_token()
    if not token:
        print("[FATAL] Could not load Censys token from vault")
        sys.exit(1)
    
    print("[AUTH] Token loaded from Q-LEVEL vault")
    censys = CensysIntel(token)
    
    # Check quota first
    if args.quota or args.ip or args.dossier:
        if not censys.check_quota() and not args.quota:
            print("[ABORT] Quota exceeded")
            sys.exit(1)
    
    if args.quota:
        quota = censys.get_account_quota()
        print(f"\n[QUOTA]")
        print(f"  Used:      {quota.get('used', '?')}")
        print(f"  Allowed:   {quota.get('allowed', '?')}")
        print(f"  Resets:    {quota.get('reset_at', '?')}")
        print(f"  Remaining: {quota.get('allowed', 0) - quota.get('used', 0)}")
        return
    
    if args.ip:
        print(f"\n[QUERY] IP: {args.ip}")
        result = censys.enrich_dossier(args.ip)
        
        print(f"\n[RESULTS]")
        print(json.dumps(result, indent=2))
        
        if result.get("tags"):
            print(f"\n[TAGS] {', '.join(result['tags'])}")
        
        if result.get("risk_indicators", {}).get("is_scanner"):
            print("\n[ALERT] This IP is flagged as a scanner/research infrastructure")
    
    if args.recidivist:
        # Check our known recidivist
        print("\n[RECIDIVIST CHECK] 165.245.143.157")
        result = censys.enrich_dossier("165.245.143.157")
        print(json.dumps(result, indent=2))
    
    if args.dossier:
        with open(args.dossier, 'r') as f:
            data = json.load(f)
        
        print(f"\n[ENRICHING] {len(data)} IPs from dossier")
        
        enriched = []
        for entry in data[:10]:  # Limit to 10 for safety
            ip = entry.get('ip') or entry.get('src_ip')
            if ip:
                result = censys.enrich_dossier(ip)
                enriched.append(result)
                print(f"  ✓ {ip}: {result.get('censys_status')}")
        
        output_file = args.dossier.replace('.json', '_censys.json')
        with open(output_file, 'w') as f:
            json.dump(enriched, f, indent=2)
        
        print(f"\n[SAVED] {output_file}")


if __name__ == '__main__':
    main()
